"""Tests for validation utilities."""

import argparse

import pytest

from contrib_stats.utils.validation import (
    VALID_PROVIDERS,
    validate_date,
    validate_project_id,
    validate_provider,
    validate_workers,
)


class TestValidateProvider:
    """Tests for validate_provider function."""

    def test_valid_gitlab(self):
        """Test valid gitlab provider."""
        assert validate_provider("gitlab") == "gitlab"
        assert validate_provider("GITLAB") == "gitlab"
        assert validate_provider("GitLab") == "gitlab"

    def test_valid_github(self):
        """Test valid github provider."""
        assert validate_provider("github") == "github"
        assert validate_provider("GITHUB") == "github"
        assert validate_provider("GitHub") == "github"

    def test_invalid_provider(self):
        """Test invalid provider raises error."""
        with pytest.raises(argparse.ArgumentTypeError) as exc_info:
            validate_provider("bitbucket")
        assert "Invalid provider" in str(exc_info.value)

    def test_empty_provider(self):
        """Test empty provider raises error."""
        with pytest.raises(argparse.ArgumentTypeError):
            validate_provider("")


class TestValidateProjectId:
    """Tests for validate_project_id function."""

    def test_valid_simple_project_id(self):
        """Test valid simple project ID."""
        assert validate_project_id("owner/repo") == "owner/repo"

    def test_valid_nested_project_id(self):
        """Test valid nested project ID (GitLab groups)."""
        assert validate_project_id("group/subgroup/project") == "group/subgroup/project"

    def test_invalid_project_id_no_slash(self):
        """Test project ID without slash raises error."""
        with pytest.raises(argparse.ArgumentTypeError) as exc_info:
            validate_project_id("invalid")
        assert "Invalid project ID" in str(exc_info.value)

    def test_empty_project_id(self):
        """Test empty project ID raises error."""
        with pytest.raises(argparse.ArgumentTypeError):
            validate_project_id("")


class TestValidateDate:
    """Tests for validate_date function."""

    def test_valid_date(self):
        """Test valid date format."""
        assert validate_date("2025-01-15") == "2025-01-15"
        assert validate_date("2025-12-31") == "2025-12-31"

    def test_invalid_date_format(self):
        """Test invalid date format raises error."""
        with pytest.raises(argparse.ArgumentTypeError) as exc_info:
            validate_date("01-15-2025")
        assert "Invalid date" in str(exc_info.value)

    def test_invalid_date_wrong_separator(self):
        """Test date with wrong separator raises error."""
        with pytest.raises(argparse.ArgumentTypeError):
            validate_date("2025/01/15")

    def test_invalid_date_nonsense(self):
        """Test nonsense date raises error."""
        with pytest.raises(argparse.ArgumentTypeError):
            validate_date("not-a-date")


class TestValidateWorkers:
    """Tests for validate_workers function."""

    def test_valid_workers(self):
        """Test valid worker counts."""
        assert validate_workers("1") == 1
        assert validate_workers("10") == 10
        assert validate_workers("50") == 50

    def test_workers_too_low(self):
        """Test worker count below minimum raises error."""
        with pytest.raises(argparse.ArgumentTypeError) as exc_info:
            validate_workers("0")
        assert "at least 1" in str(exc_info.value)

    def test_workers_too_high(self):
        """Test worker count above maximum raises error."""
        with pytest.raises(argparse.ArgumentTypeError) as exc_info:
            validate_workers("51")
        assert "cannot exceed 50" in str(exc_info.value)

    def test_workers_not_integer(self):
        """Test non-integer worker count raises error."""
        with pytest.raises(argparse.ArgumentTypeError) as exc_info:
            validate_workers("ten")
        assert "Must be an integer" in str(exc_info.value)


class TestValidProviders:
    """Tests for VALID_PROVIDERS constant."""

    def test_valid_providers_contains_expected(self):
        """Test that VALID_PROVIDERS contains expected providers."""
        assert "gitlab" in VALID_PROVIDERS
        assert "github" in VALID_PROVIDERS

    def test_valid_providers_is_tuple(self):
        """Test that VALID_PROVIDERS is immutable."""
        assert isinstance(VALID_PROVIDERS, tuple)
