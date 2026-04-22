"""Promotion threshold evaluation for reviewer ladder."""

from dataclasses import dataclass, field
from enum import Enum

from contrib_stats.aggregator import UserPromotionData

OBSERVER_TO_CO_REVIEWER_THRESHOLD = 30
CO_REVIEWER_TO_REVIEWER_THRESHOLD = 30
REVIEWER_TO_MAINTAINER_MONTHS = 3


class Role(Enum):
    OBSERVER = "Observer"
    CO_REVIEWER = "Co-reviewer"
    REVIEWER = "Reviewer"
    MAINTAINER = "Maintainer"


@dataclass
class PromotionStatus:
    username: str
    current_role: Role
    next_role: Role | None
    progress: dict[str, str] = field(default_factory=dict)
    ready: bool = False


class PromotionTracker:
    """Evaluate users against promotion thresholds."""

    def __init__(self, known_maintainers: set[str] | None = None):
        self.known_maintainers = known_maintainers or set()

    def evaluate(self, user: UserPromotionData) -> PromotionStatus:
        if user.username in self.known_maintainers:
            return PromotionStatus(
                username=user.username,
                current_role=Role.MAINTAINER,
                next_role=None,
                progress={},
                ready=False,
            )

        progress: dict[str, str] = {
            "mrs_commented": str(user.total_mrs_commented),
            "mrs_approved": str(user.total_mrs_approved),
            "active_months": str(len(user.active_months)),
        }

        return PromotionStatus(
            username=user.username,
            current_role=Role.OBSERVER,
            next_role=Role.CO_REVIEWER,
            progress=progress,
            ready=False,
        )

    def evaluate_all(self, users: dict[str, UserPromotionData]) -> list[PromotionStatus]:
        statuses = [self.evaluate(u) for u in users.values()]
        role_order = {
            Role.MAINTAINER: 0,
            Role.REVIEWER: 1,
            Role.CO_REVIEWER: 2,
            Role.OBSERVER: 3,
        }
        statuses.sort(
            key=lambda s: (
                role_order.get(s.current_role, 99),
                -users[s.username].total_mrs_commented,
            )
        )
        return statuses
