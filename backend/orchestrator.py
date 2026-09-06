import logging
from collections.abc import Callable

from backend.agents.analysis_agent import run_analysis_agent
from backend.agents.insight_agent import run_insight_agent
from backend.agents.report_builder_agent import run_report_builder_agent
from backend.agents.research_agent import run_research_agent


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


def run_deep_research(
    question: str,
) -> dict[str, str]:
    research_brief = _run_stage(
        "Research Agent",
        lambda: run_research_agent(
            question
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
        "research_brief": research_brief,
        "critical_analysis": critical_analysis,
        "insights": insights,
        "final_report": final_report,
    }