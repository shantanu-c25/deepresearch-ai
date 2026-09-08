from backend.services.gemini_service import generate_response


def run_analysis_agent(question: str, research_brief: str) -> str:
    prompt = f"""
You are the Critical Analysis Agent for DeepResearch AI.

Your job is to critically examine an initial research brief.

Original research question:
{question}

Research brief:
{research_brief}

Analyze the brief and return:

1. Strong points in the research brief
2. Weak or unsupported claims
3. Possible contradictions or missing perspectives
4. Facts that require verification
5. Risks of bias or overgeneralization
6. Recommendations for improving the research

Be critical, precise, and evidence-oriented.
Do not simply repeat the research brief.
Preserve valid [S<number>] citations from the research brief where useful.
Do not invent citation IDs, URLs, or sources.
"""

    return generate_response(prompt)