import logging
import time
from collections.abc import Callable
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from backend.agents.analysis_agent import (
    run_analysis_agent,
)
from backend.agents.insight_agent import (
    run_insight_agent,
)
from backend.agents.report_builder_agent import (
    run_report_builder_agent,
)
from backend.agents.research_agent import (
    run_research_agent,
)
from backend.models.source import (
    ResearchSource,
)
from backend.rag.langchain_adapter import (
    RAGPipelineRetriever,
    build_retrieval_context_chain,
    langchain_documents_to_context,
)
from backend.rag.service import (
    RAGPipelineService,
)
from backend.retrieval import (
    MultiSourceRetriever,
    prepare_evidence,
)
from backend.retrieval.citations import (
    CitationRegistry,
    CitationValidation,
    build_citation_registry,
    normalize_evidence_context,
    sanitize_invalid_citations,
)
from backend.validation import (
    SourceValidator,
)


logger = logging.getLogger(__name__)


class ResearchGraphState(TypedDict, total=False):
    question: str
    evidence_context: str
    sources: list[ResearchSource]
    citation_registry: CitationRegistry
    allowed_citation_ids: list[str]
    research_brief: str
    critical_analysis: str
    insights: str
    final_report: str
    citation_validation: CitationValidation


def _get_shared_rag_service() -> RAGPipelineService:
    try:
        import backend.main as main_module
    except Exception:
        main_module = None

    if main_module is not None and getattr(main_module, "rag_pipeline_service", None) is not None:
        return main_module.rag_pipeline_service

    return RAGPipelineService(
        source_retriever=MultiSourceRetriever(),
        validator=SourceValidator(),
    )


def _run_stage(
    stage_name: str,
    action: Callable[[], str],
) -> str:
    logger.info(
        "[%s] STARTED",
        stage_name,
    )

    started_at = time.perf_counter()

    try:
        result = action()
    except Exception:
        logger.exception(
            "[%s] FAILED",
            stage_name,
        )

        raise

    logger.info(
        "[%s] COMPLETED",
        stage_name,
    )

    elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)
    logger.info(
        "[%s] COMPLETED in %.2fms",
        stage_name,
        elapsed_ms,
    )

    return result


def _documents_to_sources(
    documents: list[object],
) -> list[ResearchSource]:
    sources: list[ResearchSource] = []

    for document in documents:
        metadata = getattr(document, "metadata", {}) or {}
        if not isinstance(metadata, dict):
            continue

        source_id = (
            metadata.get("source_id")
            or metadata.get("chunk_id")
            or metadata.get("filename")
            or "source"
        )
        title = (
            metadata.get("source_title")
            or metadata.get("filename")
            or str(source_id)
        )
        url = metadata.get("source_url") or ""
        source_type = metadata.get("source_type") or "unknown"
        if source_type == "uploaded_document":
            source_type = "documentation"
        provider = metadata.get("provider") or "manual"
        authors = metadata.get("authors", [])
        if not isinstance(authors, list):
            authors = [str(authors)] if authors else []

        sources.append(
            ResearchSource(
                id=str(source_id),
                citation_id=metadata.get("citation_id"),
                title=str(title),
                url=str(url),
                domain=str(metadata.get("domain") or ""),
                source_type=str(source_type),
                provider=str(provider),
                snippet=getattr(document, "page_content", "") or "",
                content=getattr(document, "page_content", "") or "",
                authors=[str(author) for author in authors],
                published_date=metadata.get("published_date"),
                relevance_score=float(metadata.get("relevance_score", 0.0)),
                credibility=str(metadata.get("credibility") or "unrated"),
                validation_status=str(metadata.get("validation_status") or "accepted"),
            )
        )

    return sources


def _prepare_research_evidence(
    question: str,
) -> tuple[
    str,
    list[ResearchSource],
]:
    logger.info(
        "[RAG Retrieval] STARTED"
    )

    try:
        rag_service = _get_shared_rag_service()
        retriever = RAGPipelineRetriever(
            rag_service=rag_service,
            top_k=5,
        )
        retrieval_context = build_retrieval_context_chain(
            retriever
        ).invoke(question)
        documents = retrieval_context.get("documents", [])
        cited_sources = _documents_to_sources(
            documents
        )
        context_text = langchain_documents_to_context(
            documents,
        )

        logger.info(
            (
                "[RAG Retrieval] "
                "COMPLETED - %s "
                "retrieved sources"
            ),
            len(cited_sources),
        )

        return (
            context_text,
            cited_sources,
        )

    except Exception:
        logger.exception(
            (
                "[RAG Retrieval] "
                "FAILED - continuing "
                "without external evidence"
            )
        )

        try:
            collection = (
                MultiSourceRetriever()
                .search(
                    question,
                    web_results=5,
                    paper_results=5,
                    max_sources=10,
                )
            )
            validated = (
                SourceValidator()
                .validate_collection(
                    collection
                )
            )
            evidence_context, cited_sources = prepare_evidence(
                validated.accepted_sources
            )
            return (
                evidence_context,
                cited_sources,
            )
        except Exception:
            logger.exception(
                (
                    "[Legacy Source Retrieval] "
                    "FAILED - continuing "
                    "without external evidence"
                )
            )
            return (
                "",
                [],
            )

def _sanitize_stage_output(
    stage_name: str,
    output: str,
    registry: CitationRegistry,
) -> str:
    sanitized, validation = sanitize_invalid_citations(
        output,
        registry,
    )
    if validation.invalid_ids:
        logger.warning(
            "[%s] removed unknown citation IDs: %s",
            stage_name,
            ", ".join(validation.invalid_ids),
        )
    return sanitized


def _retrieve_evidence_node(
    state: ResearchGraphState,
) -> ResearchGraphState:
    evidence_context, sources = _prepare_research_evidence(
        state["question"]
    )
    return {
        "evidence_context": evidence_context,
        "sources": sources,
    }


def _normalize_citations_node(
    state: ResearchGraphState,
) -> ResearchGraphState:
    registry = build_citation_registry(
        state.get("sources", [])
    )
    return {
        "citation_registry": registry,
        "sources": registry.sources,
        "evidence_context": normalize_evidence_context(
            state.get("evidence_context", ""),
            registry,
        ),
        "allowed_citation_ids": sorted(registry.allowed_ids),
    }


def _research_node(
    state: ResearchGraphState,
) -> ResearchGraphState:
    registry = state["citation_registry"]
    output = _run_stage(
        "Research Agent",
        lambda: run_research_agent(
            state["question"],
            state.get("evidence_context", ""),
        ),
    )
    return {
        "research_brief": _sanitize_stage_output(
            "Research Agent",
            output,
            registry,
        )
    }


def _critical_analysis_node(
    state: ResearchGraphState,
) -> ResearchGraphState:
    output = _run_stage(
        "Critical Analysis Agent",
        lambda: run_analysis_agent(
            state["question"],
            state["research_brief"],
        ),
    )
    return {
        "critical_analysis": _sanitize_stage_output(
            "Critical Analysis Agent",
            output,
            state["citation_registry"],
        )
    }


def _insights_node(
    state: ResearchGraphState,
) -> ResearchGraphState:
    output = _run_stage(
        "Insight Agent",
        lambda: run_insight_agent(
            state["question"],
            state["research_brief"],
            state["critical_analysis"],
        ),
    )
    return {
        "insights": _sanitize_stage_output(
            "Insight Agent",
            output,
            state["citation_registry"],
        )
    }


def _report_node(
    state: ResearchGraphState,
) -> ResearchGraphState:
    output = _run_stage(
        "Report Builder Agent",
        lambda: run_report_builder_agent(
            state["question"],
            state["research_brief"],
            state["critical_analysis"],
            state["insights"],
            state.get("evidence_context", ""),
            state.get("allowed_citation_ids", []),
        ),
    )
    return {"final_report": output}


def _validate_citations_node(
    state: ResearchGraphState,
) -> ResearchGraphState:
    sanitized_report, validation = sanitize_invalid_citations(
        state["final_report"],
        state["citation_registry"],
    )
    if validation.invalid_ids:
        logger.warning(
            "[Report Builder Agent] removed unknown citation IDs: %s",
            ", ".join(validation.invalid_ids),
        )
    return {
        "final_report": sanitized_report,
        "citation_validation": validation,
        "sources": state["citation_registry"].sources,
    }


def build_research_graph():
    """Compile the explicit in-process research workflow."""
    graph = StateGraph(ResearchGraphState)
    graph.add_node("retrieve_evidence", _retrieve_evidence_node)
    graph.add_node("normalize_citations", _normalize_citations_node)
    graph.add_node("research", _research_node)
    graph.add_node("critical_analysis", _critical_analysis_node)
    graph.add_node("generate_insights", _insights_node)
    graph.add_node("build_report", _report_node)
    graph.add_node("validate_citations", _validate_citations_node)

    graph.add_edge(START, "retrieve_evidence")
    graph.add_edge("retrieve_evidence", "normalize_citations")
    graph.add_edge("normalize_citations", "research")
    graph.add_edge("research", "critical_analysis")
    graph.add_edge("critical_analysis", "generate_insights")
    graph.add_edge("generate_insights", "build_report")
    graph.add_edge("build_report", "validate_citations")
    graph.add_edge("validate_citations", END)
    return graph.compile()


def run_deep_research(
    question: str,
) -> dict[str, object]:
    started_at = time.perf_counter()
    final_state = build_research_graph().invoke(
        {"question": question}
    )
    elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)
    logger.info(
        "[Research Graph] COMPLETED in %.2fms",
        elapsed_ms,
    )

    return {
        "question": final_state["question"],
        "research_brief": final_state["research_brief"],
        "critical_analysis": final_state["critical_analysis"],
        "insights": final_state["insights"],
        "final_report": final_state["final_report"],
        "sources": final_state["sources"],
    }