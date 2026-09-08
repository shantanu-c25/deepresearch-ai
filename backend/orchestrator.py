import logging
import time
from collections.abc import Callable

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
    build_citation_registry,
    sanitize_invalid_citations,
)
from backend.validation import (
    SourceValidator,
)


logger = logging.getLogger(__name__)


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
        registry = build_citation_registry(cited_sources)
        context_text = langchain_documents_to_context(
            documents,
            registry.source_to_citation,
        )
        cited_sources = registry.sources

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


def run_deep_research(
    question: str,
) -> dict[str, object]:
    (
        evidence_context,
        cited_sources,
    ) = _prepare_research_evidence(
        question
    )
    citation_registry = build_citation_registry(
        cited_sources
    )

    research_brief = _run_stage(
        "Research Agent",
        lambda: run_research_agent(
            question,
            evidence_context,
        ),
    )
    research_brief = _sanitize_stage_output(
        "Research Agent",
        research_brief,
        citation_registry,
    )

    critical_analysis = _run_stage(
        "Critical Analysis Agent",
        lambda: run_analysis_agent(
            question,
            research_brief,
        ),
    )
    critical_analysis = _sanitize_stage_output(
        "Critical Analysis Agent",
        critical_analysis,
        citation_registry,
    )

    insights = _run_stage(
        "Insight Agent",
        lambda: run_insight_agent(
            question,
            research_brief,
            critical_analysis,
        ),
    )
    insights = _sanitize_stage_output(
        "Insight Agent",
        insights,
        citation_registry,
    )

    final_report = _run_stage(
        "Report Builder Agent",
        lambda: run_report_builder_agent(
            question,
            research_brief,
            critical_analysis,
            insights,
            evidence_context,
            sorted(citation_registry.allowed_ids),
        ),
    )
    final_report = _sanitize_stage_output(
        "Report Builder Agent",
        final_report,
        citation_registry,
    )

    return {
        "question": question,
        "research_brief": (
            research_brief
        ),
        "critical_analysis": (
            critical_analysis
        ),
        "insights": insights,
        "final_report": (
            final_report
        ),
        "sources": citation_registry.sources,
    }