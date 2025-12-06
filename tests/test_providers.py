"""Tests for provider implementations."""

from contrib_stats.providers.github import GitHubAnalyzer
from contrib_stats.providers.gitlab import GitLabAnalyzer


class TestGitLabAnalyzer:
    """Tests for GitLabAnalyzer."""

    def test_mr_prefix(self):
        """Test GitLab MR prefix is '!'."""
        analyzer = GitLabAnalyzer("group/project", "fake-token")
        assert analyzer.mr_prefix == "!"

    def test_mr_term(self):
        """Test GitLab MR term is 'MR'."""
        analyzer = GitLabAnalyzer("group/project", "fake-token")
        assert analyzer.mr_term == "MR"

    def test_default_url(self):
        """Test default GitLab URL."""
        analyzer = GitLabAnalyzer("group/project", "fake-token")
        assert analyzer.base_url == "https://gitlab.com"

    def test_custom_url(self):
        """Test custom GitLab URL."""
        analyzer = GitLabAnalyzer("group/project", "fake-token", "https://gitlab.example.com")
        assert analyzer.base_url == "https://gitlab.example.com"

    def test_url_trailing_slash_removed(self):
        """Test trailing slash is removed from URL."""
        analyzer = GitLabAnalyzer("group/project", "fake-token", "https://gitlab.com/")
        assert analyzer.base_url == "https://gitlab.com"

    def test_get_mr_identifier(self, sample_gitlab_mr):
        """Test extracting MR identifier."""
        analyzer = GitLabAnalyzer("group/project", "fake-token")
        assert analyzer._get_mr_identifier(sample_gitlab_mr) == 123

    def test_get_mr_author(self, sample_gitlab_mr):
        """Test extracting MR author."""
        analyzer = GitLabAnalyzer("group/project", "fake-token")
        assert analyzer._get_mr_author(sample_gitlab_mr) == "alice"

    def test_get_note_author(self, sample_gitlab_note):
        """Test extracting note author."""
        analyzer = GitLabAnalyzer("group/project", "fake-token")
        assert analyzer._get_note_author(sample_gitlab_note) == "charlie"

    def test_get_note_author_system_note(self):
        """Test system notes return None."""
        analyzer = GitLabAnalyzer("group/project", "fake-token")
        system_note = {
            "id": 1,
            "body": "changed the description",
            "system": True,
            "author": {"username": "system"},
        }
        assert analyzer._get_note_author(system_note) is None


class TestGitHubAnalyzer:
    """Tests for GitHubAnalyzer."""

    def test_mr_prefix(self):
        """Test GitHub PR prefix is '#'."""
        analyzer = GitHubAnalyzer("owner/repo", "fake-token")
        assert analyzer.mr_prefix == "#"

    def test_mr_term(self):
        """Test GitHub PR term is 'PR'."""
        analyzer = GitHubAnalyzer("owner/repo", "fake-token")
        assert analyzer.mr_term == "PR"

    def test_default_url(self):
        """Test default GitHub URL."""
        analyzer = GitHubAnalyzer("owner/repo", "fake-token")
        assert analyzer.base_url == "https://api.github.com"

    def test_custom_url(self):
        """Test custom GitHub URL (Enterprise)."""
        analyzer = GitHubAnalyzer("owner/repo", "fake-token", "https://github.example.com/api/v3")
        assert analyzer.base_url == "https://github.example.com/api/v3"

    def test_get_mr_identifier(self, sample_github_pr):
        """Test extracting PR number."""
        analyzer = GitHubAnalyzer("owner/repo", "fake-token")
        assert analyzer._get_mr_identifier(sample_github_pr) == 456

    def test_get_mr_author(self, sample_github_pr):
        """Test extracting PR author."""
        analyzer = GitHubAnalyzer("owner/repo", "fake-token")
        assert analyzer._get_mr_author(sample_github_pr) == "bob"

    def test_get_note_author(self, sample_github_comment):
        """Test extracting comment author."""
        analyzer = GitHubAnalyzer("owner/repo", "fake-token")
        assert analyzer._get_note_author(sample_github_comment) == "david"

    def test_get_note_author_bot(self, sample_github_bot_comment):
        """Test bot comments return None."""
        analyzer = GitHubAnalyzer("owner/repo", "fake-token")
        assert analyzer._get_note_author(sample_github_bot_comment) is None

    def test_get_note_author_no_user(self):
        """Test comment with no user returns None."""
        analyzer = GitHubAnalyzer("owner/repo", "fake-token")
        comment = {"id": 1, "body": "test"}
        assert analyzer._get_note_author(comment) is None

    def test_get_note_author_no_login(self):
        """Test comment with user but no login returns None."""
        analyzer = GitHubAnalyzer("owner/repo", "fake-token")
        comment = {"id": 1, "body": "test", "user": {"id": 1}}
        assert analyzer._get_note_author(comment) is None
