"""GitLab-specific review analyzer."""

from typing import Any
from urllib.parse import quote

from contrib_stats.providers.base import ReviewAnalyzer


class GitLabAnalyzer(ReviewAnalyzer):
    """GitLab-specific review analyzer."""

    def __init__(
        self,
        project_id: str,
        token: str,
        gitlab_url: str = "https://gitlab.com",
        rate_limit_delay: float = 0.05,
        max_workers: int = 10,
    ):
        """
        Initialize GitLab analyzer.

        Args:
            project_id: GitLab project path (e.g., 'group/project')
            token: GitLab personal access token with 'read_api' scope
            gitlab_url: GitLab instance URL
            rate_limit_delay: Delay between API requests in seconds
            max_workers: Maximum number of parallel threads
        """
        super().__init__(project_id, token, gitlab_url, rate_limit_delay, max_workers)
        self.api_base = f"{self.base_url}/api/v4"

    def _setup_auth(self) -> None:
        """Set up GitLab authentication."""
        self.session.headers.update({"PRIVATE-TOKEN": self.token})

    @property
    def mr_prefix(self) -> str:
        """GitLab uses '!' prefix for merge requests."""
        return "!"

    @property
    def mr_term(self) -> str:
        """GitLab uses 'MR' for merge requests."""
        return "MR"

    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "gitlab"

    def get_merge_requests(self, start_date: str, end_date: str | None = None) -> list[dict[str, Any]]:
        """
        Get all merge requests within date range.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format (optional)

        Returns:
            List of merge request data
        """
        encoded_project_id = quote(str(self.project_id), safe="")
        url = f"{self.api_base}/projects/{encoded_project_id}/merge_requests"

        params: dict[str, Any] = {
            "state": "all",
            "created_after": f"{start_date}T00:00:00Z",
            "order_by": "created_at",
            "sort": "asc",
        }

        if end_date:
            params["created_before"] = f"{end_date}T23:59:59Z"

        print(f"\nFetching merge requests from {start_date} to {end_date or 'now'}...")
        return self.get_paginated_data(url, params)

    def get_mr_notes(self, mr_iid: int, silent: bool = False) -> list[dict[str, Any]]:
        """
        Get all notes for a merge request.

        Args:
            mr_iid: Merge request IID
            silent: If True, suppress progress output

        Returns:
            List of note data
        """
        encoded_project_id = quote(str(self.project_id), safe="")
        url = f"{self.api_base}/projects/{encoded_project_id}/merge_requests/{mr_iid}/notes"
        params = {"sort": "asc", "order_by": "created_at"}
        return self.get_paginated_data(url, params, silent=silent)

    def _get_mr_identifier(self, mr: dict[str, Any]) -> int:
        """Get the merge request IID."""
        return int(mr["iid"])

    def _get_mr_author(self, mr: dict[str, Any]) -> str:
        """Get the merge request author username."""
        return str(mr["author"]["username"])

    def _get_note_author(self, note: dict[str, Any]) -> str | None:
        """Get the note author username, or None for system notes."""
        # Skip system notes (e.g., "changed the description")
        if note.get("system", False):
            return None
        return str(note["author"]["username"])
