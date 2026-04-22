"""Tests for promotion threshold evaluation."""

from contrib_stats.aggregator import UserPromotionData
from contrib_stats.promotion import PromotionTracker, Role


def make_user(username="alice", mrs_commented=0, mrs_approved=0, active_months=0):
    user = UserPromotionData(username=username)
    for i in range(mrs_commented):
        user.mrs_commented_set.add(("proj", i))
    for i in range(mrs_approved):
        user.mrs_approved_set.add(("proj", i + 1000))
    for m in range(active_months):
        user.active_months.add(f"2025-{m + 1:02d}")
    user.total_mrs_commented = len(user.mrs_commented_set)
    user.total_mrs_approved = len(user.mrs_approved_set)
    return user


class TestEvaluate:
    def test_known_maintainer(self):
        tracker = PromotionTracker(known_maintainers={"alice"})
        status = tracker.evaluate(make_user("alice", mrs_commented=50))
        assert status.current_role == Role.MAINTAINER
        assert status.next_role is None

    def test_observer_default(self):
        tracker = PromotionTracker(known_maintainers=set())
        status = tracker.evaluate(make_user("bob", mrs_commented=10))
        assert status.current_role == Role.OBSERVER
        assert status.next_role == Role.CO_REVIEWER

    def test_progress_contains_counts(self):
        tracker = PromotionTracker(known_maintainers=set())
        status = tracker.evaluate(make_user("bob", mrs_commented=15, mrs_approved=8, active_months=3))
        assert status.progress["mrs_commented"] == "15"
        assert status.progress["mrs_approved"] == "8"
        assert status.progress["active_months"] == "3"


class TestEvaluateAll:
    def test_sorted_maintainers_first(self):
        tracker = PromotionTracker(known_maintainers={"alice"})
        users = {
            "bob": make_user("bob", mrs_commented=50),
            "alice": make_user("alice", mrs_commented=10),
        }
        statuses = tracker.evaluate_all(users)
        assert statuses[0].username == "alice"
        assert statuses[0].current_role == Role.MAINTAINER

    def test_candidates_sorted_by_activity(self):
        tracker = PromotionTracker(known_maintainers=set())
        users = {
            "low": make_user("low", mrs_commented=5),
            "high": make_user("high", mrs_commented=50),
        }
        statuses = tracker.evaluate_all(users)
        assert statuses[0].username == "high"
        assert statuses[1].username == "low"
