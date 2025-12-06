"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def sample_gitlab_mr():
    """Sample GitLab merge request data."""
    return {
        "iid": 123,
        "title": "Fix bug in parser",
        "state": "merged",
        "created_at": "2025-01-15T10:30:00Z",
        "author": {
            "username": "alice",
            "id": 1,
        },
    }


@pytest.fixture
def sample_github_pr():
    """Sample GitHub pull request data."""
    return {
        "number": 456,
        "title": "Add new feature",
        "state": "closed",
        "created_at": "2025-02-20T14:45:00Z",
        "user": {
            "login": "bob",
            "id": 2,
            "type": "User",
        },
    }


@pytest.fixture
def sample_gitlab_note():
    """Sample GitLab note/comment data."""
    return {
        "id": 789,
        "body": "LGTM!",
        "system": False,
        "created_at": "2025-01-15T11:00:00Z",
        "author": {
            "username": "charlie",
            "id": 3,
        },
    }


@pytest.fixture
def sample_github_comment():
    """Sample GitHub comment data."""
    return {
        "id": 101112,
        "body": "Great work!",
        "created_at": "2025-02-20T15:30:00Z",
        "user": {
            "login": "david",
            "id": 4,
            "type": "User",
        },
        "_type": "issue_comment",
    }


@pytest.fixture
def sample_github_bot_comment():
    """Sample GitHub bot comment data."""
    return {
        "id": 131415,
        "body": "CI passed",
        "created_at": "2025-02-20T15:35:00Z",
        "user": {
            "login": "github-actions[bot]",
            "id": 5,
            "type": "Bot",
        },
        "_type": "issue_comment",
    }
