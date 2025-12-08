"""Tests for custom exceptions."""

from contrib_stats.exceptions import (
    APIError,
    AuthenticationError,
    ContribStatsError,
    ForbiddenError,
    ProjectNotFoundError,
    RateLimitError,
)


class TestContribStatsError:
    """Tests for base ContribStatsError."""

    def test_is_exception(self):
        """Test that ContribStatsError is an Exception."""
        assert issubclass(ContribStatsError, Exception)

    def test_can_raise(self):
        """Test that ContribStatsError can be raised."""
        try:
            raise ContribStatsError("test error")
        except ContribStatsError as e:
            assert str(e) == "test error"


class TestAuthenticationError:
    """Tests for AuthenticationError."""

    def test_gitlab_message(self):
        """Test GitLab authentication error message."""
        err = AuthenticationError("gitlab")
        assert "401 Unauthorized" in str(err)
        assert "read_api" in str(err)
        assert err.provider == "gitlab"

    def test_github_message(self):
        """Test GitHub authentication error message."""
        err = AuthenticationError("github")
        assert "401 Unauthorized" in str(err)
        assert "repo" in str(err)
        assert err.provider == "github"

    def test_custom_message(self):
        """Test custom error message."""
        err = AuthenticationError("gitlab", "Custom error message")
        assert str(err) == "Custom error message"

    def test_is_contrib_stats_error(self):
        """Test that AuthenticationError inherits from ContribStatsError."""
        assert issubclass(AuthenticationError, ContribStatsError)


class TestProjectNotFoundError:
    """Tests for ProjectNotFoundError."""

    def test_gitlab_message(self):
        """Test GitLab project not found message."""
        err = ProjectNotFoundError("group/project", "gitlab")
        assert "404 Not Found" in str(err)
        assert "group/project" in str(err)
        assert err.project_id == "group/project"
        assert err.provider == "gitlab"

    def test_github_message(self):
        """Test GitHub repository not found message."""
        err = ProjectNotFoundError("owner/repo", "github")
        assert "404 Not Found" in str(err)
        assert "owner/repo" in str(err)
        assert "Repository" in str(err)

    def test_custom_message(self):
        """Test custom error message."""
        err = ProjectNotFoundError("test/project", "gitlab", "Custom not found")
        assert str(err) == "Custom not found"


class TestRateLimitError:
    """Tests for RateLimitError."""

    def test_message_without_retry(self):
        """Test rate limit error without retry-after."""
        err = RateLimitError("gitlab")
        assert "429 Too Many Requests" in str(err)
        assert err.retry_after is None

    def test_message_with_retry(self):
        """Test rate limit error with retry-after."""
        err = RateLimitError("github", 60)
        assert "429 Too Many Requests" in str(err)
        assert "60 seconds" in str(err)
        assert err.retry_after == 60

    def test_suggestions(self):
        """Test that suggestions are included."""
        err = RateLimitError("gitlab")
        assert "--workers" in str(err)


class TestForbiddenError:
    """Tests for ForbiddenError."""

    def test_message(self):
        """Test forbidden error message."""
        err = ForbiddenError("group/project", "gitlab")
        assert "403 Forbidden" in str(err)
        assert "group/project" in str(err)
        assert err.project_id == "group/project"
        assert err.provider == "gitlab"


class TestAPIError:
    """Tests for APIError."""

    def test_message(self):
        """Test API error message."""
        err = APIError(500, "Internal Server Error")
        assert "500" in str(err)
        assert "Internal Server Error" in str(err)
        assert err.status_code == 500

    def test_connection_error(self):
        """Test connection error message."""
        err = APIError(0, "Connection refused")
        assert "Connection refused" in str(err)
        assert err.status_code == 0
