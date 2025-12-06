"""
Contrib Stats - Contributor Statistics & Code Review Analytics

Analyze repository activity, contributor statistics, and code review metrics
across GitLab and GitHub.
"""

__version__ = "0.1.0"
__author__ = "Lalatendu Mohanty"
__email__ = ""

from contrib_stats.providers.base import ReviewAnalyzer
from contrib_stats.providers.github import GitHubAnalyzer
from contrib_stats.providers.gitlab import GitLabAnalyzer

__all__ = [
    "ReviewAnalyzer",
    "GitLabAnalyzer",
    "GitHubAnalyzer",
    "__version__",
]
