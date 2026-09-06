import re


_QUERY_STOP_WORDS = {
    "a",
    "about",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "could",
    "do",
    "does",
    "for",
    "from",
    "how",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "their",
    "to",
    "using",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
}


_ANALYSIS_INTENT_WORDS = {
    "advantage",
    "advantages",
    "benefit",
    "benefits",
    "challenge",
    "challenges",
    "compare",
    "comparison",
    "disadvantage",
    "disadvantages",
    "effect",
    "effects",
    "future",
    "impact",
    "impacts",
    "key",
    "main",
    "opportunities",
    "opportunity",
    "risk",
    "risks",
    "trend",
    "trends",
}


def _extract_keywords(
    question: str,
    max_terms: int = 6,
) -> list[str]:
    words = re.findall(
        r"[a-zA-Z0-9-]+",
        question.lower(),
    )

    keywords: list[str] = []

    for word in words:
        if word in _QUERY_STOP_WORDS:
            continue

        if word in _ANALYSIS_INTENT_WORDS:
            continue

        if (
            len(word) < 3
            and word != "ai"
        ):
            continue

        if word in keywords:
            continue

        keywords.append(word)

        if len(keywords) >= max_terms:
            break

    return keywords


def build_arxiv_query(
    question: str,
) -> str:
    clean_question = question.strip()

    if not clean_question:
        return ""

    keywords = _extract_keywords(
        clean_question
    )

    if not keywords:
        return clean_question

    return " AND ".join(
        f"all:{keyword}"
        for keyword in keywords
    )