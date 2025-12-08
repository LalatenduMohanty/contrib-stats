"""Custom exceptions for contrib_stats."""


class ContribStatsError(Exception):
    """Base exception for contrib_stats."""

    pass


class AuthenticationError(ContribStatsError):
    """Raised when authentication fails (401 Unauthorized)."""

    def __init__(self, provider: str, message: str | None = None):
        self.provider = provider
        if message:
            self.message = message
        elif provider == "gitlab":
            self.message = (
                "Authentication failed (401 Unauthorized).\n\n"
                "Please check your GitLab token:\n"
                "  1. Ensure the token is valid and not expired\n"
                "  2. Ensure the token has 'read_api' scope\n"
                "  3. Create a new token at: GitLab → Settings → Access Tokens"
            )
        else:
            self.message = (
                "Authentication failed (401 Unauthorized).\n\n"
                "Please check your GitHub token:\n"
                "  1. Ensure the token is valid and not expired\n"
                "  2. Ensure the token has 'repo' or 'public_repo' scope\n"
                "  3. Create a new token at: GitHub → Settings → Developer settings → Personal access tokens"
            )
        super().__init__(self.message)


class ProjectNotFoundError(ContribStatsError):
    """Raised when project/repository is not found (404 Not Found)."""

    def __init__(self, project_id: str, provider: str, message: str | None = None):
        self.project_id = project_id
        self.provider = provider
        if message:
            self.message = message
        elif provider == "gitlab":
            self.message = (
                f"Project not found (404 Not Found): {project_id}\n\n"
                "Please check:\n"
                "  1. The project path is correct (e.g., 'group/project' or 'group/subgroup/project')\n"
                "  2. You have access to this project\n"
                "  3. For private projects, ensure your token has appropriate permissions"
            )
        else:
            self.message = (
                f"Repository not found (404 Not Found): {project_id}\n\n"
                "Please check:\n"
                "  1. The repository path is correct (e.g., 'owner/repo')\n"
                "  2. You have access to this repository\n"
                "  3. For private repos, ensure your token has 'repo' scope"
            )
        super().__init__(self.message)


class RateLimitError(ContribStatsError):
    """Raised when API rate limit is exceeded (429 Too Many Requests)."""

    def __init__(self, provider: str, retry_after: int | None = None):
        self.provider = provider
        self.retry_after = retry_after
        retry_msg = f" Try again in {retry_after} seconds." if retry_after else ""
        self.message = (
            f"API rate limit exceeded (429 Too Many Requests).{retry_msg}\n\n"
            "Suggestions:\n"
            "  1. Wait a few minutes before retrying\n"
            "  2. Reduce parallel workers with --workers 5\n"
            "  3. Use a narrower date range"
        )
        super().__init__(self.message)


class ForbiddenError(ContribStatsError):
    """Raised when access is forbidden (403 Forbidden)."""

    def __init__(self, project_id: str, provider: str):
        self.project_id = project_id
        self.provider = provider
        self.message = (
            f"Access forbidden (403 Forbidden): {project_id}\n\n"
            "Please check:\n"
            "  1. You have permission to access this project/repository\n"
            "  2. Your token has sufficient permissions\n"
            "  3. IP restrictions or organization policies may be blocking access"
        )
        super().__init__(self.message)


class APIError(ContribStatsError):
    """Raised for other API errors."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = f"API error ({status_code}): {message}"
        super().__init__(self.message)
