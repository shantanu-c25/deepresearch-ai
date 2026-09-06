import backend.orchestrator as orchestrator

from backend.models.source import (
    ResearchSource,
)


def test_run_deep_research(
    monkeypatch,
):
    cited_source = ResearchSource(
        id="source-1",
        citation_id="S1",
        title="Test Source",
        url="https://example.com/source",
        domain="example.com",
        provider="tavily",
        relevance_score=0.8,
        credibility="medium",
        validation_status="accepted",
        content="Test evidence.",
    )

    monkeypatch.setattr(
        orchestrator,
        "_prepare_research_evidence",
        lambda question: (
            (
                "[S1]\n"
                "Title: Test Source\n"
                "Evidence: Test evidence."
            ),
            [cited_source],
        ),
    )

    def fake_research_agent(
        question,
        evidence_context="",
    ):
        return "research brief"

    def fake_analysis_agent(
        question,
        research_brief,
    ):
        return "critical analysis"

    def fake_insight_agent(
        question,
        research_brief,
        critical_analysis,
    ):
        return "insights"

    def fake_report_builder_agent(
        question,
        research_brief,
        critical_analysis,
        insights,
    ):
        return "final report"

    monkeypatch.setattr(
        orchestrator,
        "run_research_agent",
        fake_research_agent,
    )

    monkeypatch.setattr(
        orchestrator,
        "run_analysis_agent",
        fake_analysis_agent,
    )

    monkeypatch.setattr(
        orchestrator,
        "run_insight_agent",
        fake_insight_agent,
    )

    monkeypatch.setattr(
        orchestrator,
        "run_report_builder_agent",
        fake_report_builder_agent,
    )

    result = (
        orchestrator.run_deep_research(
            "What is agentic AI?"
        )
    )

    assert (
        result["question"]
        == "What is agentic AI?"
    )

    assert (
        result["research_brief"]
        == "research brief"
    )

    assert (
        result["critical_analysis"]
        == "critical analysis"
    )

    assert (
        result["insights"]
        == "insights"
    )

    assert (
        result["final_report"]
        == "final report"
    )

    assert len(
        result["sources"]
    ) == 1

    assert (
        result["sources"][0].citation_id
        == "S1"
    )

    assert (
        result["sources"][0].title
        == "Test Source"
    )