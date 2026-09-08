import backend.orchestrator as orchestrator
from backend.models.source import ResearchSource


def test_research_graph_contains_expected_nodes_and_edges():
    graph = orchestrator.build_research_graph()
    graph_view = graph.get_graph()

    assert set(
        {
            "retrieve_evidence",
            "normalize_citations",
            "research",
            "critical_analysis",
            "generate_insights",
            "build_report",
            "validate_citations",
        }
    ).issubset(graph_view.nodes)

    expected_edges = {
        ("__start__", "retrieve_evidence"),
        ("retrieve_evidence", "normalize_citations"),
        ("normalize_citations", "research"),
        ("research", "critical_analysis"),
        ("critical_analysis", "generate_insights"),
        ("generate_insights", "build_report"),
        ("build_report", "validate_citations"),
        ("validate_citations", "__end__"),
    }
    assert {
        (edge.source, edge.target)
        for edge in graph_view.edges
    } == expected_edges


def test_research_graph_executes_nodes_in_order(monkeypatch):
    order = []
    node_names = [
        "retrieve_evidence",
        "normalize_citations",
        "research",
        "critical_analysis",
        "insights",
        "build_report",
        "validate_citations",
    ]

    graph_node_names = [
        ("retrieve_evidence", "retrieve_evidence"),
        ("normalize_citations", "normalize_citations"),
        ("research", "research"),
        ("critical_analysis", "critical_analysis"),
        ("insights", "insights"),
        ("build_report", "report"),
        ("validate_citations", "validate_citations"),
    ]

    for node_name, function_name in graph_node_names:
        monkeypatch.setattr(
            orchestrator,
            f"_{function_name}_node",
            lambda state, name=node_name: (
                order.append(name) or state
            ),
        )

    orchestrator.build_research_graph().invoke(
        {"question": "order"}
    )

    assert order == node_names


def test_graph_executes_blue_orchid_once_and_preserves_upload_provenance(monkeypatch):
    calls = {"retrieval": 0}
    captured = {}
    source = ResearchSource(
        id="upload-blue-orchid",
        title="blue-orchid-test.txt",
        url="uploaded://upload-blue-orchid/blue-orchid-test.txt",
        domain="",
        source_type="documentation",
        provider="manual",
        content="The internal codename is BLUE ORCHID 742.",
    )
    evidence = (
        "[upload-blue-orchid]\n"
        "Title: blue-orchid-test.txt\n"
        "Evidence: BLUE ORCHID 742"
    )

    def retrieve(question):
        calls["retrieval"] += 1
        return evidence, [source]

    def research(question, context):
        captured["research_context"] = context
        return "The codename is BLUE ORCHID 742 [S1]."

    monkeypatch.setattr(
        orchestrator,
        "_prepare_research_evidence",
        retrieve,
    )
    monkeypatch.setattr(
        orchestrator,
        "run_research_agent",
        research,
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
    monkeypatch.setattr(
        orchestrator,
        "run_report_builder_agent",
        lambda question, brief, analysis, insights, evidence_context, allowed_ids: (
            "The codename is BLUE ORCHID 742 [S1]."
        ),
    )

    result = orchestrator.run_deep_research(
        "What is the internal codename?"
    )

    assert calls["retrieval"] == 1
    assert "BLUE ORCHID 742" in captured["research_context"]
    assert "[S1]" in captured["research_context"]
    assert result["final_report"].endswith("[S1].")
    assert result["sources"][0].citation_id == "S1"
    assert result["sources"][0].id == "upload-blue-orchid"
    assert result["sources"][0].url == source.url


def test_graph_validates_unknown_report_citations_after_report_builder(monkeypatch):
    source = ResearchSource(
        id="source-1",
        title="Trusted source",
        url="https://example.com/source-1",
        domain="example.com",
        provider="tavily",
        content="Trusted evidence.",
    )

    monkeypatch.setattr(
        orchestrator,
        "_prepare_research_evidence",
        lambda question: ("[S1] Trusted evidence.", [source]),
    )
    monkeypatch.setattr(
        orchestrator,
        "run_research_agent",
        lambda question, context: "Brief [S1]",
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
    monkeypatch.setattr(
        orchestrator,
        "run_report_builder_agent",
        lambda question, brief, analysis, insights, evidence_context, allowed_ids: (
            "Fact A [S1]. Fact B [S99]."
        ),
    )

    state = orchestrator.build_research_graph().invoke(
        {"question": "What is trusted?"}
    )

    assert state["final_report"] == "Fact A [S1]. Fact B."
    assert state["citation_validation"].valid_ids == ["S1"]
    assert state["citation_validation"].invalid_ids == ["S99"]
    assert [source.citation_id for source in state["sources"]] == ["S1"]
