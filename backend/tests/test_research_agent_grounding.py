import backend.agents.research_agent as research_agent


def test_research_agent_includes_evidence(
    monkeypatch,
):
    captured = {
        "prompt": "",
    }

    def fake_generate_response(
        prompt: str,
    ) -> str:
        captured["prompt"] = prompt

        return "Grounded brief"

    monkeypatch.setattr(
        research_agent,
        "generate_response",
        fake_generate_response,
    )

    evidence = """
[S1]
Title: AI Agents in Healthcare
Domain: ibm.com
Evidence: AI agents can support
healthcare workflows.
""".strip()

    result = (
        research_agent
        .run_research_agent(
            (
                "What are the benefits "
                "of AI agents in "
                "healthcare?"
            ),
            evidence,
        )
    )

    assert result == (
        "Grounded brief"
    )

    assert (
        "[S1]"
        in captured["prompt"]
    )

    assert (
        "AI Agents in Healthcare"
        in captured["prompt"]
    )

    assert (
        "Never invent a citation ID"
        in captured["prompt"]
    )


def test_research_agent_remains_backward_compatible(
    monkeypatch,
):
    captured = {
        "prompt": "",
    }

    def fake_generate_response(
        prompt: str,
    ) -> str:
        captured["prompt"] = prompt

        return "Research brief"

    monkeypatch.setattr(
        research_agent,
        "generate_response",
        fake_generate_response,
    )

    result = (
        research_agent
        .run_research_agent(
            "Explain RAG."
        )
    )

    assert result == (
        "Research brief"
    )

    assert (
        "No external evidence "
        "was provided"
        in captured["prompt"]
    )