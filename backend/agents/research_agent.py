from backend.services.gemini_service import generate_response


def run_research_agent(question: str) -> str:
    prompt = f"""
You are the Research Agent for DeepResearch AI.

Your job is to create a clear initial research brief for the user's question.

Research question:
{question}

Return:
1. A short overview
2. Important concepts
3. Key questions that should be investigated
4. Possible facts or claims that need verification
5. Suggested directions for deeper research

Keep the response structured and concise.
"""

    return generate_response(prompt)