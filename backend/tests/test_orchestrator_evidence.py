import backend.orchestrator as orchestrator

from backend.models.source import (
    ResearchSource,
    SourceCollection,
    ValidatedSourceCollection,
)


class FakeRetriever:
    def search(
        self,
        question,
        web_results=5,
        paper_results=5,
        max_sources=10,
    ):
        source = ResearchSource(
            id="source-1",
            title="AI Agents in Healthcare",
            url="https://www.ibm.com/example",
            domain="ibm.com",
            provider="tavily",
            relevance_score=0.8,
            credibility="medium",
            validation_status="accepted",
            content=(
                "AI agents can support "
                "healthcare workflows."
            ),
        )

        return SourceCollection(
            question=question,
            sources=[source],
            total_found=1,
        )


class FakeValidator:
    def validate_collection(
        self,
        collection,
    ):
        source = (
            collection.sources[0]
            .model_copy(deep=True)
        )

        source.credibility = "medium"

        source.validation_status = (
            "accepted"
        )

        return ValidatedSourceCollection(
            question=collection.question,
            accepted_sources=[
                source
            ],
            review_sources=[],
            rejected_sources=[],
            total_evaluated=1,
        )


def test_orchestrator_passes_evidence_to_research_agent(
    monkeypatch,
):
    captured = {
        "evidence": "",
    }

    monkeypatch.setattr(
        orchestrator,
        "MultiSourceRetriever",
        lambda: FakeRetriever(),
    )

    monkeypatch.setattr(
        orchestrator,
        "SourceValidator",
        lambda: FakeValidator(),
    )

    def fake_research_agent(
        question,
        evidence_context="",
    ):
        captured["evidence"] = (
            evidence_context
        )

        return "Research brief"

    def fake_analysis_agent(
        question,
        brief,
    ):
        return "Critical analysis"

    def fake_insight_agent(
        question,
        brief,
        analysis,
    ):
        return "Insights"

    def fake_report_builder_agent(
        question,
        brief,
        analysis,
        insights,
        evidence_context="",
        allowed_citation_ids=None,
    ):
        return "Final report"

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
            "AI agents healthcare"
        )
    )

    assert (
        "[S1]"
        in captured["evidence"]
    )

    assert (
        "AI Agents in Healthcare"
        in captured["evidence"]
    )

    assert (
        result["research_brief"]
        == "Research brief"
    )

    assert (
        result["critical_analysis"]
        == "Critical analysis"
    )

    assert (
        result["insights"]
        == "Insights"
    )

    assert (
        result["final_report"]
        == "Final report"
    )


def test_orchestrator_survives_retrieval_failure(
    monkeypatch,
):
    captured = {
        "evidence": None,
    }

    class BrokenRetriever:
        def search(
            self,
            *args,
            **kwargs,
        ):
            raise RuntimeError(
                "Retrieval unavailable"
            )

    monkeypatch.setattr(
        orchestrator,
        "MultiSourceRetriever",
        lambda: BrokenRetriever(),
    )

    def fake_research_agent(
        question,
        evidence_context="",
    ):
        captured["evidence"] = (
            evidence_context
        )

        return "Research brief"

    def fake_analysis_agent(
        question,
        brief,
    ):
        return "Critical analysis"

    def fake_insight_agent(
        question,
        brief,
        analysis,
    ):
        return "Insights"

    def fake_report_builder_agent(
        question,
        brief,
        analysis,
        insights,
        evidence_context="",
        allowed_citation_ids=None,
    ):
        return "Final report"

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
            "AI agents healthcare"
        )
    )

    assert (
        captured["evidence"]
        == ""
    )

    assert (
        result["research_brief"]
        == "Research brief"
    )

    assert (
        result["critical_analysis"]
        == "Critical analysis"
    )

    assert (
        result["insights"]
        == "Insights"
    )

    assert (
        result["final_report"]
        == "Final report"
    )