"""Multi-project aggregation for promotion tracking."""

import json
import logging
import os
import re
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime

from contrib_stats.providers.gitlab import GitLabAnalyzer

log = logging.getLogger("contrib_stats.aggregator")

BOT_PATTERNS = [
    re.compile(r"_bot[_\b]", re.IGNORECASE),
    re.compile(r"bot$", re.IGNORECASE),
    re.compile(r"cicd", re.IGNORECASE),
    re.compile(r"\bproject_\d+_bot\b", re.IGNORECASE),
    re.compile(r"^group_\d+_bot", re.IGNORECASE),
]


def is_bot(username: str) -> bool:
    return any(p.search(username) for p in BOT_PATTERNS)


@dataclass
class CommentRecord:
    """A single review comment with context."""

    project: str
    mr_id: int
    mr_author: str
    username: str
    body: str
    created_at: str
    month: str


@dataclass
class UserPromotionData:
    """Aggregated per-user promotion metrics across projects."""

    username: str = ""
    total_mrs_commented: int = 0
    total_mrs_approved: int = 0
    mrs_commented_set: set[tuple[str, int]] = field(default_factory=set)
    mrs_approved_set: set[tuple[str, int]] = field(default_factory=set)
    active_months: set[str] = field(default_factory=set)
    comments_by_month: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    projects_active_in: set[str] = field(default_factory=set)
    comments: list[CommentRecord] = field(default_factory=list)


class MultiProjectAggregator:
    """Orchestrate analysis across multiple GitLab projects."""

    def __init__(
        self,
        project_ids: list[str],
        token: str,
        gitlab_url: str = "https://gitlab.com",
        max_workers: int = 10,
        exclude_users: list[str] | None = None,
        known_maintainers: list[str] | None = None,
    ):
        self.project_ids = project_ids
        self.token = token
        self.gitlab_url = gitlab_url
        self.max_workers = max_workers
        self.exclude_users = set(exclude_users or [])
        self.known_maintainers = set(known_maintainers or [])
        self.user_data: dict[str, UserPromotionData] = {}
        self._total_notes = 0
        self._total_mrs = 0
        self._skipped_bots: set[str] = set()

    def _should_skip(self, username: str) -> bool:
        if username in self.exclude_users:
            return True
        if is_bot(username):
            self._skipped_bots.add(username)
            return True
        return False

    def _get_or_create_user(self, username: str) -> UserPromotionData:
        if username not in self.user_data:
            self.user_data[username] = UserPromotionData(username=username)
        return self.user_data[username]

    def analyze_all(self, start_date: str, end_date: str) -> dict[str, UserPromotionData]:
        """Run analysis across all projects sequentially, return per-user data."""
        overall_start = time.time()
        log.info(
            "Starting analysis: %d projects, %s to %s, %d workers",
            len(self.project_ids),
            start_date,
            end_date,
            self.max_workers,
        )
        log.info("Known maintainers: %s", ", ".join(sorted(self.known_maintainers)))

        for i, project_id in enumerate(self.project_ids, 1):
            log.info(
                "[%d/%d] === Project: %s ===",
                i,
                len(self.project_ids),
                project_id,
            )
            self._analyze_project(project_id, start_date, end_date)

        self._finalize()

        elapsed = time.time() - overall_start
        if self._skipped_bots:
            log.info("Filtered bots: %s", ", ".join(sorted(self._skipped_bots)))
        log.info(
            "Analysis complete in %.1fs: %d projects, %d total MRs, "
            "%d total notes, %d unique contributors (excl. bots)",
            elapsed,
            len(self.project_ids),
            self._total_mrs,
            self._total_notes,
            len(self.user_data),
        )
        return self.user_data

    def _analyze_project(self, project_id: str, start_date: str, end_date: str) -> None:
        proj_start = time.time()
        analyzer = GitLabAnalyzer(
            project_id,
            self.token,
            self.gitlab_url,
            max_workers=self.max_workers,
        )
        log.info("  Fetching MRs for %s ...", project_id)
        merge_requests = analyzer.get_merge_requests(start_date, end_date)
        if not merge_requests:
            log.info("  No MRs found for %s, skipping", project_id)
            return

        mr_count = len(merge_requests)
        self._total_mrs += mr_count
        log.info("  Found %d MRs, fetching notes+approvals ...", mr_count)

        completed = 0
        errors = 0
        proj_notes = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_mr = {executor.submit(analyzer._process_mr_data, mr): mr for mr in merge_requests}
            for future in as_completed(future_to_mr):
                completed += 1
                try:
                    mr_id, mr_author, notes, approvers = future.result()
                    proj_notes += len(notes)
                    self._process_results(project_id, mr_id, mr_author, notes, approvers, analyzer)
                    if completed % 25 == 0 or completed == mr_count:
                        log.info(
                            "  Progress: %d/%d MRs (%d notes so far)",
                            completed,
                            mr_count,
                            proj_notes,
                        )
                except Exception as e:
                    errors += 1
                    log.warning("  Error on MR: %s", e)

        self._total_notes += proj_notes
        elapsed = time.time() - proj_start
        log.info(
            "  Done: %s — %d MRs, %d notes, %d errors, %.1fs",
            project_id,
            mr_count,
            proj_notes,
            errors,
            elapsed,
        )

    def _process_results(
        self,
        project_id: str,
        mr_id: int,
        mr_author: str,
        notes: list[dict],
        approvers: list[str],
        analyzer: GitLabAnalyzer,
    ) -> None:
        mr_key = (project_id, mr_id)

        for note in notes:
            username = analyzer._get_note_author(note)
            if username is None or username == mr_author:
                continue
            if self._should_skip(username):
                continue

            body = note.get("body", "")
            created_at_str = note.get("created_at", "")
            try:
                created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                month_key = created_at.strftime("%Y-%m")
            except (ValueError, AttributeError):
                month_key = "unknown"

            user = self._get_or_create_user(username)
            user.mrs_commented_set.add(mr_key)
            user.active_months.add(month_key)
            user.comments_by_month[month_key] += 1
            user.projects_active_in.add(project_id)

            user.comments.append(
                CommentRecord(
                    project=project_id,
                    mr_id=mr_id,
                    mr_author=mr_author,
                    username=username,
                    body=body,
                    created_at=created_at_str,
                    month=month_key,
                )
            )

        for approver in approvers:
            if approver == mr_author:
                continue
            if self._should_skip(approver):
                continue
            user = self._get_or_create_user(approver)
            user.mrs_approved_set.add(mr_key)
            user.projects_active_in.add(project_id)

    def _finalize(self) -> None:
        for user in self.user_data.values():
            user.total_mrs_commented = len(user.mrs_commented_set)
            user.total_mrs_approved = len(user.mrs_approved_set)

        top5 = sorted(
            self.user_data.values(),
            key=lambda u: u.total_mrs_commented,
            reverse=True,
        )[:5]
        log.info("Top 5 commenters: %s", ", ".join(f"{u.username}({u.total_mrs_commented})" for u in top5))

    def export_comments(self, export_dir: str, min_comments: int = 3) -> list[str]:
        """Export per-user comment files to export_dir. Returns list of paths."""
        os.makedirs(export_dir, exist_ok=True)
        exported: list[str] = []

        for username, user in sorted(self.user_data.items()):
            if len(user.comments) < min_comments:
                continue

            is_maintainer = username in self.known_maintainers
            data = {
                "username": username,
                "is_maintainer": is_maintainer,
                "summary": {
                    "total_mrs_commented": user.total_mrs_commented,
                    "total_mrs_approved": user.total_mrs_approved,
                    "active_months": sorted(user.active_months),
                    "projects_active_in": sorted(user.projects_active_in),
                    "comments_by_month": dict(sorted(user.comments_by_month.items())),
                },
                "comments": [
                    {
                        "project": c.project,
                        "mr_id": c.mr_id,
                        "mr_author": c.mr_author,
                        "body": c.body,
                        "created_at": c.created_at,
                    }
                    for c in sorted(user.comments, key=lambda c: c.created_at)
                ],
            }

            path = os.path.join(export_dir, f"{username}.json")
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            exported.append(path)
            log.info(
                "Exported %d comments for %s%s -> %s",
                len(user.comments),
                username,
                " (maintainer)" if is_maintainer else "",
                path,
            )

        log.info("Exported %d user files to %s", len(exported), export_dir)
        return exported
