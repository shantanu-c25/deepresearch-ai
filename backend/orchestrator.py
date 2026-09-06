import logging
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
from backend.retrieval import (
    MultiSourceRetriever,
    prepare_evidence,
)
from backend.validation import (
    SourceValidator,
)


logger = logging.getLogger(__name__)


def _run_stage(
    stage_name: str,
    action: Callable[[], str],
) -> str:
    logger.info(
        "[%s] STARTED",
        stage_name,
    )

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

    return result


def _prepare_research_evidence(
    question: str,
) -> tuple[
    str,
    list[ResearchSource],
]:
    logger.info(
        "[Source Retrieval] STARTED"
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

        logger.info(
            (
                "[Source Retrieval] "
                "COMPLETED - %s "
                "unique sources found"
            ),
            collection.total_found,
        )

        validated = (
            SourceValidator()
            .validate_collection(
                collection
            )
        )

        logger.info(
            (
                "[Source Validation] "
                "COMPLETED - "
                "%s accepted, "
                "%s review, "
                "%s rejected"
            ),
            len(
                validated.accepted_sources
            ),
            len(
                validated.review_sources
            ),
            len(
                validated.rejected_sources
            ),
        )

        (
            evidence_context,
            cited_sources,
        ) = prepare_evidence(
            validated.accepted_sources
        )

        return (
            evidence_context,
            cited_sources,
        )

    except Exception:
        logger.exception(
            (
                "[Source Retrieval] "
                "FAILED - continuing "
                "without external evidence"
            )
        )

        return (
            "",
            [],
        )


def run_deep_research(
    question: str,
) -> dict[str, object]:
    (
        evidence_context,
        cited_sources,
    ) = _prepare_research_evidence(
        question
    )

    research_brief = _run_stage(
        "Research Agent",
        lambda: run_research_agent(
            question,
            evidence_context,
        ),
    )

    critical_analysis = _run_stage(
        "Critical Analysis Agent",
        lambda: run_analysis_agent(
            question,
            research_brief,
        ),
    )

    insights = _run_stage(
        "Insight Agent",
        lambda: run_insight_agent(
            question,
            research_brief,
            critical_analysis,
        ),
    )

    final_report = _run_stage(
        "Report Builder Agent",
        lambda: run_report_builder_agent(
            question,
            research_brief,
            critical_analysis,
            insights,
        ),
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
        "sources": cited_sources,
    }