"""Terminal and JSON output for promotion tracking dashboard."""

import json
from datetime import datetime

from contrib_stats.aggregator import UserPromotionData
from contrib_stats.promotion import PromotionStatus, Role


class PromotionDashboard:
    """Render promotion tracking results."""

    def render_text(
        self,
        statuses: list[PromotionStatus],
        user_data: dict[str, UserPromotionData],
        start_date: str,
        end_date: str,
        project_count: int,
    ) -> str:
        lines: list[str] = []
        w = 80

        maintainers = [s for s in statuses if s.current_role == Role.MAINTAINER]
        candidates = [s for s in statuses if s.current_role != Role.MAINTAINER]

        lines.append("=" * w)
        lines.append("PROMOTION TRACKING DASHBOARD")
        lines.append("=" * w)
        lines.append(f"Period: {start_date} to {end_date} | Projects: {project_count}")
        lines.append(f"Maintainers: {len(maintainers)} | Candidates: {len(candidates)} | Total: {len(statuses)}")

        lines.append("")
        lines.append("-" * w)
        lines.append("MAINTAINERS (known)")
        lines.append("-" * w)
        for status in maintainers:
            user = user_data.get(status.username)
            if not user:
                continue
            proj_count = len(user.projects_active_in)
            lines.append(
                f"  {status.username:<22} "
                f"commented: {user.total_mrs_commented:>4}  "
                f"approved: {user.total_mrs_approved:>4}  "
                f"projects: {proj_count:>2}  "
                f"months: {len(user.active_months)}"
            )

        lines.append("")
        lines.append("-" * w)
        lines.append("CANDIDATES (sorted by review activity)")
        lines.append("-" * w)

        for status in candidates:
            user = user_data.get(status.username)
            if not user:
                continue
            proj_count = len(user.projects_active_in)
            comment_count = len(user.comments)
            lines.append(
                f"  {status.username:<22} "
                f"commented: {user.total_mrs_commented:>4}  "
                f"approved: {user.total_mrs_approved:>4}  "
                f"projects: {proj_count:>2}  "
                f"months: {len(user.active_months):>2}  "
                f"raw comments: {comment_count:>5}"
            )

        lines.append("")
        lines.append("-" * w)
        lines.append("MONTHLY BREAKDOWN")
        lines.append("-" * w)
        lines.append(_monthly_table(statuses, user_data))
        lines.append("=" * w)

        output = "\n".join(lines)
        print(output)
        return output

    def render_json(
        self,
        statuses: list[PromotionStatus],
        user_data: dict[str, UserPromotionData],
        start_date: str,
        end_date: str,
        project_count: int,
    ) -> str:
        contributors: list[dict[str, object]] = []
        data = {
            "metadata": {
                "start_date": start_date,
                "end_date": end_date,
                "project_count": project_count,
                "generated_at": datetime.now().isoformat(),
            },
            "summary": {
                "total_contributors": len(statuses),
                "maintainers": sum(1 for s in statuses if s.current_role == Role.MAINTAINER),
                "candidates": sum(1 for s in statuses if s.current_role != Role.MAINTAINER),
            },
            "contributors": contributors,
        }

        for status in statuses:
            user = user_data.get(status.username)
            if not user:
                continue
            contributors.append(
                {
                    "username": status.username,
                    "current_role": status.current_role.value,
                    "mrs_commented": user.total_mrs_commented,
                    "mrs_approved": user.total_mrs_approved,
                    "active_months": sorted(user.active_months),
                    "projects_active_in": sorted(user.projects_active_in),
                    "comments_by_month": dict(sorted(user.comments_by_month.items())),
                    "total_comments": len(user.comments),
                }
            )

        return json.dumps(data, indent=2)


def _monthly_table(
    statuses: list[PromotionStatus],
    user_data: dict[str, UserPromotionData],
) -> str:
    all_months: set[str] = set()
    for user in user_data.values():
        all_months.update(user.comments_by_month.keys())

    if not all_months:
        return "  (no data)"

    months = sorted(all_months)
    month_labels = [m[5:] for m in months]

    name_width = 22
    col_width = 6
    header = " " * name_width + "".join(f"{label:>{col_width}}" for label in month_labels)
    lines = [header]

    for status in statuses[:25]:
        entry = user_data.get(status.username)
        if not entry:
            continue
        role_tag = "*" if status.current_role == Role.MAINTAINER else " "
        name = status.username[: name_width - 3]
        row = f" {role_tag}{name:<{name_width - 2}}"
        for month in months:
            count = entry.comments_by_month.get(month, 0)
            cell = str(count) if count else "--"
            row += f"{cell:>{col_width}}"
        lines.append(row)

    if len(statuses) > 25:
        lines.append(f"  ... and {len(statuses) - 25} more")
    lines.append("  (* = maintainer)")

    return "\n".join(lines)
