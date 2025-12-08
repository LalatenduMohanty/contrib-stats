"""Base class for review analyzers."""

import sys
import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any

import requests

from contrib_stats.exceptions import (
    APIError,
    AuthenticationError,
    ForbiddenError,
    ProjectNotFoundError,
    RateLimitError,
)


class ReviewAnalyzer(ABC):
    """Abstract base class for review analyzers."""

    def __init__(
        self,
        project_id: str,
        token: str,
        base_url: str,
        rate_limit_delay: float = 0.05,
        max_workers: int = 10,
    ):
        """
        Initialize the analyzer.

        Args:
            project_id: Project identifier (GitLab: group/project, GitHub: owner/repo)
            token: Personal access token
            base_url: API base URL
            rate_limit_delay: Delay between API requests in seconds
            max_workers: Maximum number of parallel threads
        """
        self.project_id = project_id
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.rate_limit_delay = rate_limit_delay
        self.max_workers = max_workers
        self._print_lock = threading.Lock()
        self.session = requests.Session()
        self._setup_auth()

    @abstractmethod
    def _setup_auth(self) -> None:
        """Set up authentication headers for the session."""
        pass

    @abstractmethod
    def get_merge_requests(self, start_date: str, end_date: str | None = None) -> list[dict[str, Any]]:
        """Get all merge/pull requests within date range."""
        pass

    @abstractmethod
    def get_mr_notes(self, mr_id: int, silent: bool = False) -> list[dict[str, Any]]:
        """Get all notes/comments for a merge/pull request."""
        pass

    @abstractmethod
    def get_mr_approvals(self, mr_id: int) -> list[str]:
        """
        Get list of usernames who approved the merge/pull request.

        Args:
            mr_id: MR/PR identifier

        Returns:
            List of usernames who approved
        """
        pass

    @abstractmethod
    def _get_mr_identifier(self, mr: dict[str, Any]) -> int:
        """Get the MR/PR identifier from the response."""
        pass

    @abstractmethod
    def _get_mr_author(self, mr: dict[str, Any]) -> str:
        """Get the MR/PR author username from the response."""
        pass

    @abstractmethod
    def _get_note_author(self, note: dict[str, Any]) -> str | None:
        """Get the note/comment author username, or None if should be skipped."""
        pass

    @property
    @abstractmethod
    def mr_prefix(self) -> str:
        """Return the prefix for MR/PR display (e.g., '!' for GitLab, '#' for GitHub)."""
        pass

    @property
    @abstractmethod
    def mr_term(self) -> str:
        """Return the term for MR/PR (e.g., 'MR' or 'PR')."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name (e.g., 'gitlab' or 'github')."""
        pass

    def _handle_http_error(self, response: requests.Response) -> None:
        """
        Handle HTTP errors and raise appropriate exceptions.

        Args:
            response: The HTTP response object

        Raises:
            AuthenticationError: For 401 errors
            ForbiddenError: For 403 errors
            ProjectNotFoundError: For 404 errors
            RateLimitError: For 429 errors
            APIError: For other HTTP errors
        """
        status_code = response.status_code

        if status_code == 401:
            raise AuthenticationError(self.provider_name)
        elif status_code == 403:
            raise ForbiddenError(self.project_id, self.provider_name)
        elif status_code == 404:
            raise ProjectNotFoundError(self.project_id, self.provider_name)
        elif status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_seconds = int(retry_after) if retry_after and retry_after.isdigit() else None
            raise RateLimitError(self.provider_name, retry_seconds)
        else:
            raise APIError(status_code, response.text[:200])

    def get_paginated_data(
        self, url: str, params: dict[str, Any] | None = None, silent: bool = False
    ) -> list[dict[str, Any]]:
        """
        Fetch all pages of data from API.

        Args:
            url: API endpoint URL
            params: Query parameters
            silent: If True, suppress progress output

        Returns:
            List of all items across all pages

        Raises:
            AuthenticationError: For 401 errors
            ForbiddenError: For 403 errors
            ProjectNotFoundError: For 404 errors
            RateLimitError: For 429 errors
            APIError: For other HTTP errors
        """
        if params is None:
            params = {}

        params["per_page"] = 100
        all_data: list[dict[str, Any]] = []
        page = 1

        while True:
            params["page"] = page
            if not silent:
                with self._print_lock:
                    print(f"  Fetching page {page}...", end="\r")

            try:
                response = self.session.get(url, params=params)

                # Handle HTTP errors with user-friendly messages
                if not response.ok:
                    self._handle_http_error(response)

            except requests.exceptions.ConnectionError as e:
                raise APIError(0, f"Connection error: Unable to connect to {self.base_url}. {e}") from e
            except requests.exceptions.Timeout as e:
                raise APIError(0, f"Request timed out. {e}") from e
            except requests.exceptions.RequestException as e:
                # Re-raise our custom exceptions
                if hasattr(e, "response") and e.response is not None:
                    self._handle_http_error(e.response)
                raise APIError(0, str(e)) from e

            data = response.json()
            if not data:
                break

            all_data.extend(data)

            # Check for more pages (works for both GitLab and GitHub)
            if not self._has_next_page(response):
                break

            page += 1

            if self.rate_limit_delay > 0:
                time.sleep(self.rate_limit_delay)

        if not silent:
            with self._print_lock:
                print(f"  Fetched {len(all_data)} items across {page} pages")
        return all_data

    def _has_next_page(self, response: requests.Response) -> bool:
        """Check if there are more pages of data."""
        # GitLab uses x-next-page header
        if "x-next-page" in response.headers and response.headers["x-next-page"]:
            return True
        # GitHub uses Link header
        link_header = response.headers.get("Link", "")
        return 'rel="next"' in link_header

    def _process_mr_data(self, mr: dict[str, Any]) -> tuple[int, str, list[dict[str, Any]], list[str]]:
        """
        Fetch and return notes and approvals for a single MR/PR.

        Args:
            mr: Merge/pull request data

        Returns:
            Tuple of (mr_id, mr_author, notes, approvers)
        """
        mr_id = self._get_mr_identifier(mr)
        mr_author = self._get_mr_author(mr)
        notes = self.get_mr_notes(mr_id, silent=True)
        approvers = self.get_mr_approvals(mr_id)
        return mr_id, mr_author, notes, approvers

    def analyze_reviews(self, start_date: str, end_date: str | None = None) -> dict[str, Any]:
        """
        Analyze who reviewed the most merge/pull requests.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format (optional)

        Returns:
            Dictionary with review statistics
        """
        merge_requests = self.get_merge_requests(start_date, end_date)

        if not merge_requests:
            print(f"[INFO] No {self.mr_term}s found in the specified date range.")
            sys.exit(0)

        print(f"\nAnalyzing {len(merge_requests)} {self.mr_term}s using {self.max_workers} threads...")

        user_commented_mrs: dict[str, set[int]] = defaultdict(set)
        user_approved_mrs: dict[str, set[int]] = defaultdict(set)
        total_comments = 0
        total_approvals = 0
        completed = 0
        errors = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_mr = {executor.submit(self._process_mr_data, mr): mr for mr in merge_requests}

            for future in as_completed(future_to_mr):
                mr = future_to_mr[future]
                completed += 1

                try:
                    mr_id, mr_author, notes, approvers = future.result()

                    # Process comments
                    for note in notes:
                        username = self._get_note_author(note)
                        if username is None:
                            continue

                        # Skip if the commenter is the MR/PR author (self-review)
                        if username != mr_author:
                            user_commented_mrs[username].add(mr_id)
                            total_comments += 1

                    # Process approvals
                    for approver in approvers:
                        # Skip if the approver is the MR/PR author (self-approval)
                        if approver != mr_author:
                            user_approved_mrs[approver].add(mr_id)
                            total_approvals += 1

                except Exception as e:
                    errors += 1
                    with self._print_lock:
                        print(
                            f"\n[WARN] Error processing {self.mr_term} {self.mr_prefix}{self._get_mr_identifier(mr)}: {e}"
                        )

                with self._print_lock:
                    print(f"  Progress: {completed}/{len(merge_requests)} {self.mr_term}s processed...", end="\r")

        if errors > 0:
            print(f"\n[WARN] {errors} {self.mr_term}s failed to process")

        print("\n[OK] Analysis complete!")

        # Calculate comment counts
        comment_counts = {username: len(mr_set) for username, mr_set in user_commented_mrs.items()}
        sorted_commenters = sorted(comment_counts.items(), key=lambda x: x[1], reverse=True)

        # Calculate approval counts
        approval_counts = {username: len(mr_set) for username, mr_set in user_approved_mrs.items()}
        sorted_approvers = sorted(approval_counts.items(), key=lambda x: x[1], reverse=True)

        # Combine for total unique MRs reviewed (commented OR approved)
        all_reviewers: dict[str, set[int]] = defaultdict(set)
        for username, mr_set in user_commented_mrs.items():
            all_reviewers[username].update(mr_set)
        for username, mr_set in user_approved_mrs.items():
            all_reviewers[username].update(mr_set)

        return {
            "total_mrs": len(merge_requests),
            "total_comments": total_comments,
            "total_approvals": total_approvals,
            "total_reviewers": len(all_reviewers),
            "commenters": sorted_commenters,
            "approvers": sorted_approvers,
            "user_commented_mrs": user_commented_mrs,
            "user_approved_mrs": user_approved_mrs,
            # Legacy field for backward compatibility
            "reviewers": sorted_commenters,
        }

    def print_report(self, stats: dict[str, Any], start_date: str, end_date: str | None = None) -> None:
        """Print a formatted report of review statistics."""
        print("\n" + "=" * 80)
        print(f"{self.mr_term} REVIEW STATISTICS")
        print("=" * 80)
        print(f"\nPeriod: {start_date} to {end_date or datetime.now().strftime('%Y-%m-%d')}")
        print(f"Total {self.mr_term}s: {stats['total_mrs']}")
        print(f"Total Review Comments: {stats['total_comments']}")
        print(f"Total Approvals: {stats['total_approvals']}")
        print(f"Total Reviewers: {stats['total_reviewers']}")

        # Commenters section
        print("\n" + "-" * 80)
        print(f"TOP COMMENTERS (by unique {self.mr_term}s commented on)")
        print("-" * 80)
        print(f"{'Rank':<6} {'Username':<30} {self.mr_term + 's Commented':<15}")
        print("-" * 80)

        for rank, (username, count) in enumerate(stats["commenters"][:20], 1):
            print(f"{rank:<6} {username:<30} {count:<15}")

        if len(stats["commenters"]) > 20:
            print(f"\n... and {len(stats['commenters']) - 20} more commenters")

        # Approvers section
        print("\n" + "-" * 80)
        print(f"TOP APPROVERS (by unique {self.mr_term}s approved)")
        print("-" * 80)
        print(f"{'Rank':<6} {'Username':<30} {self.mr_term + 's Approved':<15}")
        print("-" * 80)

        if stats["approvers"]:
            for rank, (username, count) in enumerate(stats["approvers"][:20], 1):
                print(f"{rank:<6} {username:<30} {count:<15}")

            if len(stats["approvers"]) > 20:
                print(f"\n... and {len(stats['approvers']) - 20} more approvers")
        else:
            print("(No approvals found)")

        print("\n" + "-" * 80)
        print("Notes:")
        print(f"  - Commenters: Users who commented on at least one {self.mr_term} (excluding self-comments)")
        print(f"  - Approvers: Users who approved at least one {self.mr_term} (excluding self-approvals)")
        print("=" * 80)
