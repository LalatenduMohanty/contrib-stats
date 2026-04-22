"""Tests for multi-project aggregation."""

from unittest.mock import MagicMock

import pytest

from contrib_stats.aggregator import MultiProjectAggregator, UserPromotionData, is_bot


@pytest.fixture
def sample_notes():
    return [
        {
            "id": 1,
            "body": "this has a bug, need to fix the error handling",
            "author": {"username": "alice"},
            "system": False,
            "created_at": "2025-02-15T10:00:00Z",
        },
        {
            "id": 2,
            "body": "naming is confusing, refactor this",
            "author": {"username": "bob"},
            "system": False,
            "created_at": "2025-03-20T14:00:00Z",
        },
        {
            "id": 3,
            "body": "looks good to me",
            "author": {"username": "charlie"},
            "system": False,
            "created_at": "2025-03-25T09:00:00Z",
        },
        {
            "id": 4,
            "body": "changed the description",
            "author": {"username": "alice"},
            "system": True,
            "created_at": "2025-03-25T10:00:00Z",
        },
    ]


class TestBotDetection:
    def test_bot_patterns(self):
        assert is_bot("group_87536996_bot_f3e85806b29af1de37dd4c7e7a121d1c")
        assert is_bot("aipcc-cicd-bot")
        assert is_bot("project_123_bot")

    def test_not_bot(self):
        assert not is_bot("alice")
        assert not is_bot("regular_user")
        assert not is_bot("JaneDoe123")


class TestUserPromotionData:
    def test_defaults(self):
        user = UserPromotionData(username="test")
        assert user.total_mrs_commented == 0
        assert user.total_mrs_approved == 0
        assert len(user.comments) == 0

    def test_mr_dedup_across_projects(self):
        user = UserPromotionData(username="alice")
        user.mrs_commented_set.add(("proj-a", 1))
        user.mrs_commented_set.add(("proj-b", 1))
        user.mrs_commented_set.add(("proj-a", 1))
        assert len(user.mrs_commented_set) == 2


class TestProcessResults:
    def test_basic_note_processing(self, sample_notes):
        agg = MultiProjectAggregator([], "token")
        analyzer = MagicMock()
        analyzer._get_note_author.side_effect = lambda n: None if n.get("system") else n["author"]["username"]

        agg._process_results("proj/a", 42, "mr_author", sample_notes, [], analyzer)

        assert "alice" in agg.user_data
        assert "bob" in agg.user_data
        assert "charlie" in agg.user_data
        assert ("proj/a", 42) in agg.user_data["alice"].mrs_commented_set

    def test_comments_stored(self, sample_notes):
        agg = MultiProjectAggregator([], "token")
        analyzer = MagicMock()
        analyzer._get_note_author.side_effect = lambda n: None if n.get("system") else n["author"]["username"]

        agg._process_results("proj/a", 42, "mr_author", sample_notes, [], analyzer)

        alice = agg.user_data["alice"]
        assert len(alice.comments) == 1
        assert "bug" in alice.comments[0].body

    def test_self_comments_skipped(self, sample_notes):
        agg = MultiProjectAggregator([], "token")
        analyzer = MagicMock()
        analyzer._get_note_author.side_effect = lambda n: None if n.get("system") else n["author"]["username"]

        agg._process_results("proj/a", 42, "alice", sample_notes, [], analyzer)

        assert "alice" not in agg.user_data
        assert "bob" in agg.user_data

    def test_monthly_bucketing(self, sample_notes):
        agg = MultiProjectAggregator([], "token")
        analyzer = MagicMock()
        analyzer._get_note_author.side_effect = lambda n: None if n.get("system") else n["author"]["username"]

        agg._process_results("proj/a", 42, "mr_author", sample_notes, [], analyzer)

        alice = agg.user_data["alice"]
        assert "2025-02" in alice.active_months
        bob = agg.user_data["bob"]
        assert "2025-03" in bob.active_months

    def test_approvals_tracked(self):
        agg = MultiProjectAggregator([], "token")
        analyzer = MagicMock()

        agg._process_results("proj/a", 42, "mr_author", [], ["r1", "r2"], analyzer)

        assert ("proj/a", 42) in agg.user_data["r1"].mrs_approved_set
        assert ("proj/a", 42) in agg.user_data["r2"].mrs_approved_set

    def test_self_approval_skipped(self):
        agg = MultiProjectAggregator([], "token")
        analyzer = MagicMock()

        agg._process_results("proj/a", 42, "alice", [], ["alice", "bob"], analyzer)

        assert "alice" not in agg.user_data
        assert "bob" in agg.user_data

    def test_bots_filtered(self):
        bot_note = {
            "id": 99,
            "body": "automated check passed",
            "author": {"username": "group_123_bot_abc"},
            "system": False,
            "created_at": "2025-03-25T10:00:00Z",
        }
        agg = MultiProjectAggregator([], "token")
        analyzer = MagicMock()
        analyzer._get_note_author.side_effect = lambda n: None if n.get("system") else n["author"]["username"]

        agg._process_results("proj/a", 42, "mr_author", [bot_note], [], analyzer)
        assert "group_123_bot_abc" not in agg.user_data


class TestFinalize:
    def test_counts_computed(self):
        agg = MultiProjectAggregator([], "token")
        user = agg._get_or_create_user("alice")
        user.mrs_commented_set = {("a", 1), ("a", 2), ("b", 1)}
        user.mrs_approved_set = {("a", 1), ("b", 2)}

        agg._finalize()

        assert user.total_mrs_commented == 3
        assert user.total_mrs_approved == 2
