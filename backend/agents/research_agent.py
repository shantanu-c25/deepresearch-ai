from backend.services.gemini_service import (
    generate_response,
)


def run_research_agent(
    question: str,
    evidence_context: str = "",
) -> str:
    clean_question = (
        question.strip()
    )

    clean_evidence = (
        evidence_context.strip()
    )


    if clean_evidence:
        evidence_section = f"""
EXTERNAL RESEARCH EVIDENCE

The following sources were retrieved
and validated before this research
stage.

{clean_evidence}
"""
    else:
        evidence_section = """
EXTERNAL RESEARCH EVIDENCE

No external evidence was provided for
this research run.
"""


    prompt = f"""
You are the Research Agent in a
multi-agent deep-research system.

Your job is to build a factual,
well-structured research brief that
will later be reviewed by a Critical
Analysis Agent.

RESEARCH QUESTION

{clean_question}


{evidence_section}


EVIDENCE RULES

1. When external evidence is provided,
   use it as the primary factual basis
   for the research brief.

2. Evidence sources are identified by
   citation IDs such as [S1], [S2],
   [S3].

3. Cite relevant factual claims using
   only citation IDs that actually
   appear in the provided evidence.

4. Never invent a citation ID.

5. Never invent a source, author,
   publication, statistic, study,
   quotation, or URL.

6. If the available sources do not
   support a claim, clearly identify
   that point as requiring further
   verification.

7. Distinguish between:
   - facts supported by sources,
   - reasonable analysis or inference,
   - claims that still need
     verification.

8. Consider source credibility.
   Vendor-authored material may provide
   useful industry information but
   should not automatically be treated
   as independent evidence.

9. arXiv papers may be preprints.
   Do not describe them as peer-reviewed
   unless the supplied evidence supports
   that claim.

10. Do not create a bibliography.
    Another part of the application will
    render the source list.


RESEARCH BRIEF FORMAT

## Research Overview

Explain the topic and directly address
the research question.


## Key Concepts

Identify and explain the important
concepts required to understand the
topic.


## Evidence-Based Findings

Present the strongest findings from the
available evidence.

Use citations such as [S1] and [S2]
where appropriate.


## Important Questions and Uncertainties

Identify unresolved questions,
limitations, conflicting evidence,
or important areas where the available
sources are insufficient.


## Claims Requiring Verification

List claims that should not yet be
treated as established facts.


## Directions for Deeper Research

Recommend what the next research stages
should investigate.


Keep the brief factual, analytical,
and concise enough for downstream
agents to use effectively.
"""

    return generate_response(
        prompt
    )