
"""Rule-based article categorization and prioritization."""

CATEGORIES = {
    "critical": "🔴 NAJWAŻNIEJSZE",
    "vulnerabilities": "🛡️ PODATNOŚCI",
    "poland": "🇵🇱 POLSKA",
}

CRITICAL_KEYWORDS = (
    "actively exploited",
    "critical vulnerability",
    "exploited in the wild",
    "zero-day",
    "zero day",
    "ransomware",
    "data breach",
    "major cyberattack",
    "critical security alert",
)

VULNERABILITY_KEYWORDS = (
    "cve-",
    "vulnerability",
    "vulnerabilities",
    "security patch",
    "security update",
    "exploit",
)

POLAND_KEYWORDS = (
    "poland",
    "polish",
    "polska",
    "polski",
    "polskie",
    "polskich",
    "warsaw",
    "warszawa",
)


def categorize_article(article):
    """Return all categories matching an article's text."""
    title = article.get("title", "")
    description = article.get("description", "")
    text = f"{title} {description}".casefold()

    categories = []

    if any(keyword in text for keyword in CRITICAL_KEYWORDS):
        categories.append("critical")

    if any(keyword in text for keyword in VULNERABILITY_KEYWORDS):
        categories.append("vulnerabilities")

    if any(keyword in text for keyword in POLAND_KEYWORDS):
        categories.append("poland")

    return categories


def prioritize_article(article):
    """Return a preliminary priority score based on matching keywords."""
    categories = categorize_article(article)
    score = 0

    if "critical" in categories:
        score += 3

    if "vulnerabilities" in categories:
        score += 2

    if "poland" in categories:
        score += 1

    return score

def select_top_articles(articles, limit=20):
    """Return the highest-priority articles, up to the requested limit."""
    if limit < 0:
        raise ValueError("limit must not be negative")

    ranked_articles = sorted(
        articles,
        key=prioritize_article,
        reverse=True,
    )

    return ranked_articles[:limit]
