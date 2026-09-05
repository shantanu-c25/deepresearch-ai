from backend import orchestrator


def test_run_deep_research(monkeypatch):
    monkeypatch.setattr(
        orchestrator,
        "run_research_agent",
        lambda question: "research brief",
    )

    monkeypatch.setattr(
        orchestrator,
        "run_analysis_agent",
        lambda question, research_brief: "critical analysis",
    )

    monkeypatch.setattr(
        orchestrator,
        "run_insight_agent",
        lambda question, research_brief, critical_analysis: "insights",
    )

    monkeypatch.setattr(
        orchestrator,
        "run_report_builder_agent",
        lambda question, research_brief, critical_analysis, insights: "final report",
    )

    result = orchestrator.run_deep_research(
        "What is agentic AI?"
    )

    assert result == {
        "question": "What is agentic AI?",
        "research_brief": "research brief",
        "critical_analysis": "critical analysis",
        "insights": "insights",
        "final_report": "final report",
    }