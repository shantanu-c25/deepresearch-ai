from backend.services.gemini_service import generate_response


def run_report_builder_agent(
    question: str,
    research_brief: str,
    critical_analysis: str,
    insights: str,
) -> str:
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
- Do not claim that information has been verified unless it actually has.
- Clearly distinguish findings from hypotheses or assumptions.
- Avoid unnecessary repetition.
- Use professional Markdown formatting.
"""

    return generate_response(prompt)