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
- Counts unique MRs/PRs each user has reviewed (by commenting)
- Filters for 2025 data (configurable via CLI)
- Excludes system notes, bots, and self-reviews
- Generates a ranked report of top reviewers
- Uses parallel threads for fast processing

## Prerequisites

- Python 3.10+
- Personal access token:
  - **GitLab**: `read_api` scope
  - **GitHub**: `repo` scope (private repos) or `public_repo` scope (public repos)

### 2. Get Your Access Token

**GitLab:**
1. Go to GitLab -> Settings -> Access Tokens
2. Create a new token with `read_api` scope
3. Copy the token

**GitHub:**
1. Go to GitHub -> Settings -> Developer settings -> Personal access tokens -> Tokens (classic)
2. Generate new token with `repo` or `public_repo` scope
3. Copy the token

### 3. Find Your Project ID

- **GitLab**: `group/project` (e.g., `redhat/rhel-ai/builder`)
- **GitHub**: `owner/repo` (e.g., `pytorch/pytorch`)

## Usage

### GitLab

```bash
contrib-stats --provider gitlab --project-id group/project --token your-token
```

### GitHub

```bash
contrib-stats --provider github --project-id owner/repo --token your-token
```

### With Custom Date Range

```bash
contrib-stats --provider github --project-id owner/repo --token xxx \
  --start-date 2025-01-01 --end-date 2025-06-30
```

### Save Results to File

```bash
contrib-stats --provider gitlab --project-id group/project --token xxx \
  --output results.txt --no-interactive
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

### As a Python Module

```bash
python -m contrib_stats --provider gitlab --project-id group/project --token xxx
```

The script will prompt you for:
- Provider (gitlab/github)
- Project ID
- Access token

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--provider`, `-p` | Provider: `gitlab` or `github` | (required) |
| `--project-id` | Project ID | (required) |
| `--token` | Personal access token | (required) |
| `--url` | API URL (for self-hosted/enterprise) | auto |
| `--start-date` | Start date (YYYY-MM-DD) | 2025-01-01 |
| `--end-date` | End date (YYYY-MM-DD) | today |
| `--output`, `-o` | Output file path | (none) |
| `--no-interactive` | Skip prompts (for automation) | false |
| `--workers`, `-w` | Number of parallel threads (1-50) | 10 |

View all options:
```bash
contrib-stats --help
```

Check version:
```bash
contrib-stats --version
```

## Input Validation

The script validates all inputs:

- **Provider**: Must be `gitlab` or `github` (case-insensitive)
- **Project ID**: Must contain `/` (e.g., `owner/repo`)
- **Date**: Must be in `YYYY-MM-DD` format
- **Workers**: Must be between 1 and 50

## Output Example

### GitLab

```
================================================================================
MR REVIEW STATISTICS
================================================================================

Period: 2025-01-01 to 2025-12-06
Total MRs: 456
Total Review Comments: 2341
Total Reviewers: 23

--------------------------------------------------------------------------------
TOP REVIEWERS (by number of MRs reviewed)
--------------------------------------------------------------------------------
Rank   Username                       MRs Reviewed   
--------------------------------------------------------------------------------
1      alice                          142            
2      bob                            98             
3      charlie                        76             
...
```

### GitHub

```
================================================================================
PR REVIEW STATISTICS
================================================================================

Period: 2025-01-01 to 2025-12-06
Total PRs: 289
Total Review Comments: 1523
Total Reviewers: 45

--------------------------------------------------------------------------------
TOP REVIEWERS (by number of PRs reviewed)
--------------------------------------------------------------------------------
Rank   Username                       PRs Reviewed   
--------------------------------------------------------------------------------
1      alice                          89             
2      bob                            67             
3      charlie                        54             
...
```

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

### Rate Limiting
- GitLab: ~120 requests/minute for authenticated users
- GitHub: 5000 requests/hour for authenticated users
- Reduce workers with `--workers 5` if you hit rate limits
- The script uses parallel threads (default: 10) for faster processing

### Invalid Provider Error
- Provider must be exactly `gitlab` or `github` (case-insensitive)

### Invalid Date Format
- Dates must be in `YYYY-MM-DD` format (e.g., `2025-01-15`)

## Advanced: Schedule Automatic Reports

### Using Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Run every Monday at 9 AM for GitLab
0 9 * * 1 python /path/to/review_stats.py \
  --provider gitlab \
  --project-id your/project \
  --token your-token \
  --output /path/to/gitlab_stats_$(date +\%Y\%m\%d).txt \
  --no-interactive

# Run every Monday at 9 AM for GitHub
0 9 * * 1 python /path/to/review_stats.py \
  --provider github \
  --project-id owner/repo \
  --token your-token \
  --output /path/to/github_stats_$(date +\%Y\%m\%d).txt \
  --no-interactive
```

## Security Notes

- **Never commit your access token** to version control
- Use environment variables for tokens in automation
- Rotate tokens regularly
- Use tokens with minimal required permissions

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features including:
- Contributor statistics (PRs per author)
- Release metrics (releases per week, commits per release)
- Activity trends (daily/weekly patterns)
- HTML dashboard reports
- And more!

## License

MIT License
