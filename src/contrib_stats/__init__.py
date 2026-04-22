"""
Contrib Stats - Contributor Statistics & Code Review Analytics

Analyze repository activity, contributor statistics, and code review metrics
across GitLab and GitHub.
"""

__version__ = "0.1.0"
__author__ = "Lalatendu Mohanty"
__email__ = ""

from contrib_stats.aggregator import MultiProjectAggregator
from contrib_stats.exceptions import (
    APIError,
    AuthenticationError,
    ContribStatsError,
    ForbiddenError,
    ProjectNotFoundError,
    RateLimitError,
)
from contrib_stats.promotion import PromotionTracker
from contrib_stats.providers.base import ReviewAnalyzer
from contrib_stats.providers.github import GitHubAnalyzer
from contrib_stats.providers.gitlab import GitLabAnalyzer
from contrib_stats.tagging import KeywordTagger

__all__ = [
    "ReviewAnalyzer",
    "GitLabAnalyzer",
    "GitHubAnalyzer",
    "MultiProjectAggregator",
    "PromotionTracker",
    "KeywordTagger",
    "ContribStatsError",
    "AuthenticationError",
    "ProjectNotFoundError",
    "ForbiddenError",
    "RateLimitError",
    "APIError",
    "__version__",
]
