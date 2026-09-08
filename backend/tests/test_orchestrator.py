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
        evidence_context="",
        allowed_citation_ids=None,
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


def test_report_builder_receives_existing_evidence_and_allowed_ids(
    monkeypatch,
):
    source = ResearchSource(
        id="upload-blue-orchid",
        title="blue-orchid-test.txt",
        url="uploaded://upload-blue-orchid/blue-orchid-test.txt",
        domain="",
        source_type="documentation",
        provider="manual",
        content="The internal codename is BLUE ORCHID 742.",
    )
    evidence_context = (
        "[S1]\nTitle: blue-orchid-test.txt\n"
        "Evidence: BLUE ORCHID 742"
    )
    captured = {}

    monkeypatch.setattr(
        orchestrator,
        "_prepare_research_evidence",
        lambda question: (evidence_context, [source]),
    )
    monkeypatch.setattr(
        orchestrator,
        "run_research_agent",
        lambda question, evidence: "Brief [S1]",
    )
    monkeypatch.setattr(
        orchestrator,
        "run_analysis_agent",
        lambda question, brief: "Analysis [S1]",
    )
    monkeypatch.setattr(
        orchestrator,
        "run_insight_agent",
        lambda question, brief, analysis: "Insight [S1]",
    )

    def fake_report_builder(
        question,
        brief,
        analysis,
        insights,
        received_evidence,
        allowed_ids,
    ):
        captured["evidence"] = received_evidence
        captured["allowed_ids"] = allowed_ids
        return "Report [S1]"

    monkeypatch.setattr(
        orchestrator,
        "run_report_builder_agent",
        fake_report_builder,
    )

    result = orchestrator.run_deep_research("What is the codename?")

    assert captured["evidence"] == evidence_context
    assert captured["allowed_ids"] == ["S1"]
    assert result["sources"][0].citation_id == "S1"
    assert result["final_report"] == "Report [S1]"