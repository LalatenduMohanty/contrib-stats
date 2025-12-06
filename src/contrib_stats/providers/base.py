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
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                with self._print_lock:
                    print(f"\n[ERROR] Error fetching data: {e}")
                raise

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

    def _process_mr_notes(self, mr: dict[str, Any]) -> tuple[int, str, list[dict[str, Any]]]:
        """
        Fetch and return notes for a single MR/PR.

        Args:
            mr: Merge/pull request data

        Returns:
            Tuple of (mr_id, mr_author, notes)
        """
        mr_id = self._get_mr_identifier(mr)
        mr_author = self._get_mr_author(mr)
        notes = self.get_mr_notes(mr_id, silent=True)
        return mr_id, mr_author, notes

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
            print(f"[ERROR] No {self.mr_term}s found in the specified date range.")
            sys.exit(0)

        print(f"\nAnalyzing {len(merge_requests)} {self.mr_term}s using {self.max_workers} threads...")

        user_reviewed_mrs: dict[str, set[int]] = defaultdict(set)
        total_comments = 0
        completed = 0
        errors = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_mr = {executor.submit(self._process_mr_notes, mr): mr for mr in merge_requests}

            for future in as_completed(future_to_mr):
                mr = future_to_mr[future]
                completed += 1

                try:
                    mr_id, mr_author, notes = future.result()

                    for note in notes:
                        username = self._get_note_author(note)
                        if username is None:
                            continue

                        # Skip if the commenter is the MR/PR author (self-review)
                        if username != mr_author:
                            user_reviewed_mrs[username].add(mr_id)
                            total_comments += 1

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

        review_counts = {username: len(mr_set) for username, mr_set in user_reviewed_mrs.items()}
        sorted_reviewers = sorted(review_counts.items(), key=lambda x: x[1], reverse=True)

        return {
            "total_mrs": len(merge_requests),
            "total_comments": total_comments,
            "total_reviewers": len(sorted_reviewers),
            "reviewers": sorted_reviewers,
            "user_reviewed_mrs": user_reviewed_mrs,
        }

    def print_report(self, stats: dict[str, Any], start_date: str, end_date: str | None = None) -> None:
        """Print a formatted report of review statistics."""
        print("\n" + "=" * 80)
        print(f"{self.mr_term} REVIEW STATISTICS")
        print("=" * 80)
        print(f"\nPeriod: {start_date} to {end_date or datetime.now().strftime('%Y-%m-%d')}")
        print(f"Total {self.mr_term}s: {stats['total_mrs']}")
        print(f"Total Review Comments: {stats['total_comments']}")
        print(f"Total Reviewers: {stats['total_reviewers']}")

        print("\n" + "-" * 80)
        print(f"TOP REVIEWERS (by number of {self.mr_term}s reviewed)")
        print("-" * 80)
        print(f"{'Rank':<6} {'Username':<30} {self.mr_term + 's Reviewed':<15}")
        print("-" * 80)

        for rank, (username, count) in enumerate(stats["reviewers"][:20], 1):
            print(f"{rank:<6} {username:<30} {count:<15}")

        if len(stats["reviewers"]) > 20:
            print(f"\n... and {len(stats['reviewers']) - 20} more reviewers")

        print("\n" + "=" * 80)
