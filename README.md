# Contrib Stats

A CLI tool to analyze contributor activity, code review metrics, and repository statistics across GitLab and GitHub.

## Installation

### From PyPI (coming soon)

```bash
pip install contrib-stats
```

### From Source

```bash
git clone https://github.com/LalatenduMohanty/contrib-stats.git
cd contrib-stats
pip install -e .
```

### For Development

```bash
git clone https://github.com/LalatenduMohanty/contrib-stats.git
cd contrib-stats
pip install -e ".[dev]"
```

## What It Does

- Supports both **GitLab** and **GitHub** providers
- Tracks **reviewers** who commented on MRs/PRs
- Tracks **approvers** who approved MRs/PRs
- Filters by date range (configurable via CLI)
- Excludes system notes, bots, and self-reviews/approvals
- Generates ranked reports of top commenters and approvers
- Multiple output formats: **Text**, **JSON**, **CSV**
- Uses parallel threads for fast processing

## Prerequisites

- Python 3.10+
- Personal access token:
  - **GitLab**: `read_api` scope
  - **GitHub**: `repo` scope (private repos) or `public_repo` scope (public repos)

### Get Your Access Token

**GitLab:**
1. Go to GitLab -> Settings -> Access Tokens
2. Create a new token with `read_api` scope
3. Copy the token

**GitHub:**
1. Go to GitHub -> Settings -> Developer settings -> Personal access tokens -> Tokens (classic)
2. Generate new token with `repo` or `public_repo` scope
3. Copy the token

### Find Your Project ID

- **GitLab**: `group/project` (e.g., `redhat/rhel-ai/builder`)
- **GitHub**: `owner/repo` (e.g., `pytorch/pytorch`)

## Usage

### Basic Usage

```bash
# GitLab
contrib-stats --provider gitlab --project-id group/project --token your-token

# GitHub
contrib-stats --provider github --project-id owner/repo --token your-token
```

### With Custom Date Range

```bash
contrib-stats --provider github --project-id owner/repo --token xxx \
  --start-date 2025-01-01 --end-date 2025-06-30
```

### Save Results to File

```bash
# Save as text file
contrib-stats --provider gitlab --project-id group/project --token xxx \
  --output results.txt --no-interactive

# Save as JSON
contrib-stats --provider gitlab --project-id group/project --token xxx \
  --output results.json --format json --no-interactive

# Save as CSV files to a directory
contrib-stats --provider github --project-id owner/repo --token xxx \
  --output-dir ./reports --format csv --no-interactive
```

### Using Environment Variables

```bash
export CONTRIB_STATS_PROVIDER="gitlab"
export CONTRIB_STATS_PROJECT_ID="your/project/path"
export CONTRIB_STATS_TOKEN="your-token-here"
export GITLAB_URL="https://gitlab.com"  # Optional, for self-hosted

contrib-stats
```

For GitHub:
```bash
export CONTRIB_STATS_PROVIDER="github"
export CONTRIB_STATS_PROJECT_ID="owner/repo"
export CONTRIB_STATS_TOKEN="your-token-here"
export GITHUB_URL="https://api.github.com"  # Optional, for GitHub Enterprise

contrib-stats
```

### Interactive Mode

```bash
contrib-stats
```

The script will prompt you for:
- Provider (gitlab/github)
- Project ID
- Access token
- Output format and location

### As a Python Module

```bash
python -m contrib_stats --provider gitlab --project-id group/project --token xxx
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--provider`, `-p` | Provider: `gitlab` or `github` | (required) |
| `--project-id` | Project ID | (required) |
| `--token` | Personal access token | (required) |
| `--url` | API URL (for self-hosted/enterprise) | auto |
| `--start-date` | Start date (YYYY-MM-DD) | 2025-01-01 |
| `--end-date` | End date (YYYY-MM-DD) | today |
| `--output`, `-o` | Output file path (for text/json) | (none) |
| `--output-dir`, `-d` | Output directory (for csv) | (none) |
| `--format`, `-f` | Output format: `text`, `json`, `csv` | text |
| `--no-interactive` | Skip prompts (for automation) | false |
| `--workers`, `-w` | Number of parallel threads (1-50) | 10 |
| `--debug` | Show full stack traces on errors | false |

View all options:
```bash
contrib-stats --help
```

Check version:
```bash
contrib-stats --version
```

## Output Formats

### Text Output (Default)

Human-readable report saved to a single file.

### JSON Output

Machine-readable format with structured data:

```json
{
  "metadata": {
    "provider": "gitlab",
    "mr_term": "MR",
    "start_date": "2025-01-01",
    "end_date": "2025-12-08",
    "generated_at": "2025-12-08T16:05:30"
  },
  "summary": {
    "total_mrs": 1077,
    "total_comments": 2680,
    "total_approvals": 856,
    "total_reviewers": 42
  },
  "commenters": [
    {"rank": 1, "username": "alice", "count": 272}
  ],
  "approvers": [
    {"rank": 1, "username": "alice", "count": 189}
  ]
}
```

### CSV Output

Separate CSV files for each metric, saved to a directory with timestamped filenames:

```
./reports/
├── summary_20251208_160530.csv
├── commenters_by_mrs_commented_20251208_160530.csv
└── approvers_by_mrs_approved_20251208_160530.csv
```

## Output Example

```
================================================================================
MR REVIEW STATISTICS
================================================================================

Period: 2025-01-01 to 2025-12-08
Total MRs: 1077
Total Review Comments: 2680
Total Approvals: 856
Total Reviewers: 42

--------------------------------------------------------------------------------
TOP COMMENTERS (by unique MRs commented on)
--------------------------------------------------------------------------------
Rank   Username                       MRs Commented
--------------------------------------------------------------------------------
1      alice                          272
2      bob                            226
3      charlie                        161
...

--------------------------------------------------------------------------------
TOP APPROVERS (by unique MRs approved)
--------------------------------------------------------------------------------
Rank   Username                       MRs Approved
--------------------------------------------------------------------------------
1      alice                          189
2      bob                            156
3      charlie                        98
...

--------------------------------------------------------------------------------
Notes:
  - Commenters: Users who commented on at least one MR (excluding self-comments)
  - Approvers: Users who approved at least one MR (excluding self-approvals)
================================================================================
```

## How Metrics Are Counted

### Commenters
- Users who made **at least one comment** on a MR/PR
- Each MR/PR is counted only once per person
- Self-comments (by MR/PR author) are excluded
- Bot comments are excluded

### Approvers
- Users who **approved** a MR/PR
- Each MR/PR is counted only once per person
- Self-approvals are excluded
- GitLab: Uses the approvals API
- GitHub: Counts reviews with `APPROVED` state

## GitHub Comment Types

For GitHub, the script counts comments from:
- **Review comments**: Inline code comments on diffs
- **Issue comments**: General discussion comments
- **Reviews**: Formal PR reviews (approve, request changes, comment)

## Troubleshooting

### Authentication Errors (401)
- Check that your token is valid and not expired
- GitLab: Ensure token has `read_api` scope
- GitHub: Ensure token has `repo` or `public_repo` scope

### Project/Repository Not Found (404)
- Verify your project ID format is correct
- Ensure you have access to the repository
- For private repos, ensure your token has appropriate permissions

### Access Forbidden (403)
- Check you have permission to access the project
- Verify organization policies aren't blocking access

### Rate Limiting (429)
- GitLab: ~120 requests/minute for authenticated users
- GitHub: 5000 requests/hour for authenticated users
- Reduce workers with `--workers 5` if you hit rate limits

### Debug Mode

Use `--debug` flag to see full stack traces:
```bash
contrib-stats --provider gitlab --project-id group/project --token xxx --debug
```

## Advanced: Schedule Automatic Reports

### Using Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Run every Monday at 9 AM - save as CSV
0 9 * * 1 contrib-stats \
  --provider gitlab \
  --project-id your/project \
  --token your-token \
  --output-dir /path/to/reports \
  --format csv \
  --no-interactive

# Run every Monday at 9 AM - save as JSON
0 9 * * 1 contrib-stats \
  --provider github \
  --project-id owner/repo \
  --token your-token \
  --output /path/to/reports/stats_$(date +\%Y\%m\%d).json \
  --format json \
  --no-interactive
```

## Security Notes

- **Never commit your access token** to version control
- Use environment variables for tokens in automation
- Rotate tokens regularly
- Use tokens with minimal required permissions

## Development

### Running Tests

```bash
hatch run test
```

### Running Linting and Type Checks

```bash
hatch run check:all
```

### Fixing Linting Issues

```bash
hatch run check:fix
```

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features including:
- Contributor statistics (PRs per author)
- Release metrics (releases per week, commits per release)
- Activity trends (daily/weekly patterns)
- HTML dashboard reports
- And more!

## License

MIT License
