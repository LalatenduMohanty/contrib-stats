"""Keyword-based comment classification for review quality signals."""

import re

KEYWORD_CATEGORIES: dict[str, list[str]] = {
    "bug": ["bug", "fix", "broken", "crash", "error", "fail", "regression"],
    "security": [
        "security",
        "vulnerability",
        "cve",
        "injection",
        "auth",
        "permission",
        "credential",
    ],
    "test": ["test", "coverage", "assert", "mock", "fixture", "spec"],
    "design": [
        "refactor",
        "abstraction",
        "pattern",
        "architecture",
        "coupling",
        "complexity",
        "naming",
        "readability",
    ],
}


class KeywordTagger:
    """Classify MR comments by quality signal using keyword matching."""

    def __init__(self, categories: dict[str, list[str]] | None = None):
        self.categories = categories or KEYWORD_CATEGORIES
        self._patterns: dict[str, list[re.Pattern[str]]] = {}
        for category, keywords in self.categories.items():
            self._patterns[category] = [re.compile(r"\b" + re.escape(kw) + r"\b", re.IGNORECASE) for kw in keywords]

    def classify(self, body: str) -> set[str]:
        """Return set of category names matched in comment body."""
        if not body:
            return set()
        matched: set[str] = set()
        for category, patterns in self._patterns.items():
            for pattern in patterns:
                if pattern.search(body):
                    matched.add(category)
                    break
        return matched

    def has_quality_signal(self, categories: set[str]) -> bool:
        """True if design/quality category matched."""
        return "design" in categories

    def has_issue_signal(self, categories: set[str]) -> bool:
        """True if bug, security, or test category matched."""
        return bool(categories & {"bug", "security", "test"})
