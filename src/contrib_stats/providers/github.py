"""GitHub-specific review analyzer."""

from datetime import datetime
from typing import Any

import requests

from contrib_stats.providers.base import ReviewAnalyzer


class GitHubAnalyzer(ReviewAnalyzer):
    """GitHub-specific review analyzer."""

    def __init__(
        self,
        project_id: str,
        token: str,
        github_url: str = "https://api.github.com",
        rate_limit_delay: float = 0.05,
        max_workers: int = 10,
    ):
        """
        Initialize GitHub analyzer.

        Args:
            project_id: GitHub repository (e.g., 'owner/repo')
            token: GitHub personal access token with 'repo' scope
            github_url: GitHub API URL (for GitHub Enterprise)
            rate_limit_delay: Delay between API requests in seconds
            max_workers: Maximum number of parallel threads
        """
        super().__init__(project_id, token, github_url, rate_limit_delay, max_workers)

    def _setup_auth(self) -> None:
        """Set up GitHub authentication."""
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    @property
    def mr_prefix(self) -> str:
        """GitHub uses '#' prefix for pull requests."""
        return "#"

    @property
    def mr_term(self) -> str:
        """GitHub uses 'PR' for pull requests."""
        return "PR"

    def get_merge_requests(self, start_date: str, end_date: str | None = None) -> list[dict[str, Any]]:
        """
        Get all pull requests within date range.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format (optional)

        Returns:
            List of pull request data
        """
        url = f"{self.base_url}/repos/{self.project_id}/pulls"

        params: dict[str, Any] = {
            "state": "all",
            "sort": "created",
            "direction": "asc",
        }

        print(f"\nFetching pull requests from {start_date} to {end_date or 'now'}...")
        all_prs = self.get_paginated_data(url, params)

        # Filter by date (GitHub API doesn't support date filtering directly)
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date) if end_date else datetime.now()

        filtered_prs = []
        for pr in all_prs:
            created_at = datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00")).replace(tzinfo=None)
            if start_dt <= created_at <= end_dt.replace(hour=23, minute=59, second=59):
                filtered_prs.append(pr)

        print(f"  Filtered to {len(filtered_prs)} PRs in date range")
        return filtered_prs

    def get_mr_notes(self, pr_number: int, silent: bool = False) -> list[dict[str, Any]]:  # noqa: ARG002
        """
        Get all comments for a pull request.

        GitHub has multiple types of comments:
        - Review comments (inline code comments)
        - Issue comments (general discussion)
        - Reviews (approve/request changes)

        We fetch all of them and combine.

        Args:
            pr_number: Pull request number
            silent: If True, suppress progress output

        Returns:
            List of comment/review data
        """
        all_comments: list[dict[str, Any]] = []

        # 1. Get review comments (inline code comments)
        review_comments_url = f"{self.base_url}/repos/{self.project_id}/pulls/{pr_number}/comments"
        try:
            review_comments = self.get_paginated_data(review_comments_url, {}, silent=True)
            for comment in review_comments:
                comment["_type"] = "review_comment"
            all_comments.extend(review_comments)
        except requests.exceptions.RequestException:
            pass  # Continue even if this fails

        # 2. Get issue comments (general discussion)
        issue_comments_url = f"{self.base_url}/repos/{self.project_id}/issues/{pr_number}/comments"
        try:
            issue_comments = self.get_paginated_data(issue_comments_url, {}, silent=True)
            for comment in issue_comments:
                comment["_type"] = "issue_comment"
            all_comments.extend(issue_comments)
        except requests.exceptions.RequestException:
            pass

        # 3. Get reviews (approve/request changes/comment)
        reviews_url = f"{self.base_url}/repos/{self.project_id}/pulls/{pr_number}/reviews"
        try:
            reviews = self.get_paginated_data(reviews_url, {}, silent=True)
            for review in reviews:
                review["_type"] = "review"
            all_comments.extend(reviews)
        except requests.exceptions.RequestException:
            pass

        return all_comments

    def _get_mr_identifier(self, mr: dict[str, Any]) -> int:
        """Get the pull request number."""
        return int(mr["number"])

    def _get_mr_author(self, mr: dict[str, Any]) -> str:
        """Get the pull request author username."""
        return str(mr["user"]["login"])

    def _get_note_author(self, note: dict[str, Any]) -> str | None:
        """Get the comment author username, or None for bots."""
        user = note.get("user")
        if user is None:
            return None

        username = user.get("login")
        if not username:
            return None

        # Skip bot accounts
        if user.get("type") == "Bot":
            return None

        return str(username)
