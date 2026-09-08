from backend.services.gemini_service import generate_response


def run_report_builder_agent(
    question: str,
    research_brief: str,
    critical_analysis: str,
    insights: str,
    evidence_context: str = "",
    allowed_citation_ids: list[str] | None = None,
) -> str:
    allowed_ids = ", ".join(
        allowed_citation_ids or []
    ) or "none"
    prompt = f"""
You are the Report Builder Agent for DeepResearch AI.

Your job is to combine the outputs of the previous agents into one clear,
professional, structured research report.

Original research question:
{question}

Research brief:
{research_brief}

Critical analysis:
{critical_analysis}

Insights:
{insights}

Allowed citation IDs:
{allowed_ids}

Retrieved evidence available for citation support:
{evidence_context or "No external evidence was provided."}

Create a final report with these sections:

# DeepResearch AI Report

## 1. Executive Summary
Give a concise summary of the most important findings.

## 2. Research Overview
Explain the topic and the main concepts.

## 3. Key Findings
Present the most important findings clearly.

## 4. Critical Analysis
Summarize weaknesses, risks, contradictions, and areas requiring verification.

## 5. Key Insights and Trends
Present the strongest synthesized insights, patterns, and trends.

## 6. Practical Implications
Explain what the findings mean in practice.

## 7. Open Questions
List the most important unanswered questions.

## 8. Conclusion
Provide a balanced conclusion.

Important instructions:
- Do not invent citations or sources.
- Use only the allowed citation IDs listed above, preserving them exactly.
- Place citations immediately after supported factual claims where practical.
- Never invent a URL; the trusted source list supplies source URLs.
- Do not claim that information has been verified unless it actually has.
- Clearly distinguish findings from hypotheses or assumptions.
- Avoid unnecessary repetition.
- Use professional Markdown formatting.
"""

    return generate_response(
        prompt,
        agent="report",
    )