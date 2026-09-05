from backend.agents.analysis_agent import run_analysis_agent
from backend.agents.insight_agent import run_insight_agent
from backend.agents.report_builder_agent import run_report_builder_agent
from backend.agents.research_agent import run_research_agent


def run_deep_research(question: str) -> dict[str, str]:
    research_brief = run_research_agent(question)

    critical_analysis = run_analysis_agent(
        question,
        research_brief,
    )

    insights = run_insight_agent(
        question,
        research_brief,
        critical_analysis,
    )

    final_report = run_report_builder_agent(
        question,
        research_brief,
        critical_analysis,
        insights,
    )

    return {
        "question": question,
        "research_brief": research_brief,
        "critical_analysis": critical_analysis,
        "insights": insights,
        "final_report": final_report,
    }