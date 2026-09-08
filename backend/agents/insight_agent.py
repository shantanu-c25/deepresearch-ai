from backend.services.gemini_service import generate_response


def run_insight_agent(
    question: str,
    research_brief: str,
    critical_analysis: str,
) -> str:
    prompt = f"""
You are the Insight Generation Agent for DeepResearch AI.

Your job is to synthesize the initial research and critical analysis into
higher-level insights.

Original research question:
{question}

Research brief:
{research_brief}

Critical analysis:
{critical_analysis}

Return:

1. Key patterns and themes
2. Important trends
3. New insights that emerge from combining the research and critique
4. Possible hypotheses worth investigating
5. Practical implications
6. The most important unanswered questions

Do not simply summarize the previous outputs.
Focus on synthesis, connections, and useful new insights.
Preserve valid [S<number>] citations from the supplied material where useful.
Distinguish evidence-backed findings from inferences and hypotheses.
Do not invent citation IDs, URLs, or sources.
"""

    return generate_response(
        prompt,
        agent="insight",
    )