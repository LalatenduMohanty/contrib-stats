# Contrib Stats - Project Roadmap

A CLI tool to analyze contributor activity, code review metrics, and repository statistics across GitLab and GitHub.

**Project Name:** `contrib-stats`
**PyPI Package:** `contrib-stats`
**GitHub Repo:** `github.com/LalatenduMohanty/contrib-stats`

## Vision

Provide comprehensive insights into repository health and team productivity through:
- **Review metrics** - Who reviews the most? Who approves the most?
- **Contributor metrics** - Who contributes the most? PR volume?
- **Release metrics** - Release frequency, commits per release
- **Activity trends** - Daily/weekly/monthly patterns

---

## Release History

| Version | Date | Highlights |
|---------|------|------------|
| v0.1.0 | Dec 2025 | Initial release with basic review metrics |
| v0.1.1 | Dec 2025 | Bug fixes and improvements |
| v1.2.0 | Dec 2025 | Approval tracking, JSON/CSV output, error handling |

---

## Current Release (v1.2.0) ✅

### Core Review Metrics
- [x] GitLab merge request analysis
- [x] GitHub pull request analysis
- [x] Count unique MRs/PRs per commenter
- [x] Count unique MRs/PRs per approver
- [x] Multi-threaded API fetching
- [x] Date range filtering
- [x] Exclude self-comments and self-approvals
- [x] Exclude bot comments

### CLI Features
- [x] CLI arguments with validation
- [x] Environment variable support
- [x] Interactive mode with prompts
- [x] `--debug` flag for troubleshooting

### Output Formats
- [x] Text file output (default)
- [x] JSON output (`--format json`)
- [x] CSV output (`--format csv`)
- [x] Separate CSV files per metric with timestamps
- [x] `--output-dir` for CSV directory

### Error Handling
- [x] User-friendly error messages
- [x] Specific handling for 401, 403, 404, 429 errors
- [x] Custom exception classes

### Development & Quality
- [x] Hatch-based project management
- [x] pytest test suite with coverage
- [x] mypy type checking
- [x] ruff linting and formatting
- [x] GitHub Actions CI pipeline
- [x] Automated release workflow with wheel/sdist artifacts

---

## Planned Releases

### Phase 1: PR/MR Contribution Metrics (v1.3.0)

#### PR/MR Author Statistics
- [ ] **PRs per author** - Who sent the most PRs/MRs
- [ ] **PRs merged per author** - Successfully merged contributions
- [ ] **PR merge rate** - % of PRs that get merged per author
- [ ] **Average PR size** - Lines added/removed per author

#### PR/MR Activity Metrics
- [ ] **PRs opened per day/week/month** - Activity trends
- [ ] **PRs merged per day/week/month** - Merge velocity
- [ ] **PRs closed without merge** - Rejected/abandoned PRs
- [ ] **Open PR age** - How long PRs stay open
- [ ] **Time to first review** - PR responsiveness
- [ ] **Time to merge** - End-to-end PR lifecycle

### Phase 2: Release Metrics (v1.4.0)

#### Release Statistics
- [ ] **Releases per week/month** - Release cadence
- [ ] **Time between releases** - Release intervals
- [ ] **Commits per release** - Release size
- [ ] **PRs per release** - Features/fixes per release
- [ ] **Contributors per release** - Team involvement
- [ ] **Release timeline visualization** - Gantt-style view

### Phase 3: Enhanced Review Metrics (v1.5.0)

#### Advanced Reviewer Statistics
- [ ] **Review response time** - Time to first review comment
- [ ] **Review turnaround** - Time from review to merge
- [ ] **Comments per review** - Review depth/engagement

#### Review Health
- [ ] **Review coverage** - % of PRs that got reviewed
- [ ] **Unreviewed PRs** - PRs merged without review
- [ ] **Review bottlenecks** - PRs waiting for review
- [ ] **Reviewer load balance** - Distribution of reviews

### Phase 4: Commit Metrics (v1.6.0)

#### Commit Statistics
- [ ] **Commits per author** - Contribution volume
- [ ] **Commits per day/week/month** - Activity patterns
- [ ] **Commit size** - Lines changed per commit
- [ ] **Commit frequency** - How often authors commit
- [ ] **First-time contributors** - New contributor tracking

#### Code Churn
- [ ] **Lines added/removed** - Code growth
- [ ] **Files changed** - Change scope
- [ ] **Hotspot files** - Most frequently changed files
- [ ] **Code ownership** - Who owns which parts

### Phase 5: Output & Visualization (v1.7.0)

#### Additional Output Formats
- [ ] **HTML report** (`--format html`) - Beautiful dashboard
- [ ] **Markdown tables** (`--format markdown`)
- [ ] **Terminal charts** - ASCII bar charts

#### Dashboards
- [ ] **Summary dashboard** - Key metrics at a glance
- [ ] **Trend charts** - Activity over time
- [ ] **Leaderboards** - Top contributors/reviewers
- [ ] **Calendar heatmap** - GitHub-style contribution graph

### Phase 6: Team & Organization (v1.8.0)

#### Team Features
- [ ] **Team grouping** - Define teams, aggregate by team
- [ ] **Team comparisons** - Compare team productivity
- [ ] **Cross-team collaboration** - Inter-team reviews
- [ ] **Bus factor** - Knowledge distribution risk

#### Multi-Repository
- [ ] **Multiple repos** - Analyze multiple repos at once
- [ ] **Organization-wide stats** - Aggregate across org
- [ ] **Project grouping** - Group related repos

### Phase 7: Integrations (v1.9.0)

#### Notifications
- [ ] **Slack integration** - Post reports to Slack
- [ ] **Email reports** - Scheduled email summaries
- [ ] **Webhook support** - POST to custom endpoints
- [ ] **Microsoft Teams** - Teams notifications

#### Monitoring
- [ ] **Prometheus metrics** - Export for Grafana
- [ ] **DataDog integration** - APM integration
- [ ] **Custom metrics endpoint** - REST API for metrics

### Phase 8: Distribution & Packaging (v2.0.0)

- [ ] **PyPI package** (`pip install contrib-stats`)
- [ ] **Docker image** (`docker run contrib-stats`)
- [ ] **Homebrew formula** (`brew install contrib-stats`)
- [ ] **GitHub Action** - Run in CI/CD
- [ ] **Pre-built binaries** - Standalone executables

---

## CLI Design

### Current Options

```bash
--provider, -p      # gitlab, github (required)
--project-id        # Project identifier (required)
--token             # Access token (required)
--start-date        # Start date YYYY-MM-DD
--end-date          # End date YYYY-MM-DD
--format, -f        # Output format: text, json, csv
--output, -o        # Output file path (text/json)
--output-dir, -d    # Output directory (csv)
--workers, -w       # Parallel threads (1-50)
--no-interactive    # Skip prompts
--debug             # Show stack traces
```

### Future Commands Structure

```bash
# Review statistics (current)
contrib-stats reviews --provider gitlab --project-id group/project --token xxx

# Contributor statistics
contrib-stats contributors --provider github --project-id owner/repo --token xxx

# Release statistics
contrib-stats releases --provider gitlab --project-id group/project --token xxx

# PR/MR statistics
contrib-stats prs --provider github --project-id owner/repo --token xxx

# Commit statistics
contrib-stats commits --provider gitlab --project-id group/project --token xxx

# Full report (all metrics)
contrib-stats report --provider github --project-id owner/repo --token xxx

# Summary (quick overview)
contrib-stats summary --provider gitlab --project-id group/project --token xxx
```

---

## Configuration File

Support a `.contrib-stats.yaml` config file (planned):

```yaml
# .contrib-stats.yaml
provider: gitlab
project_id: group/project
url: https://gitlab.example.com

# Default options
defaults:
  format: text
  workers: 10

# Team definitions
teams:
  backend:
    - alice
    - bob
    - charlie
  frontend:
    - david
    - eve
  devops:
    - frank

# Exclude patterns
exclude:
  users:
    - dependabot
    - renovate-bot
  labels:
    - wip
    - draft

# Report settings
reports:
  weekly:
    metrics:
      - contributors
      - reviews
      - releases
    output: reports/weekly-{date}.html
    format: html
```

---

## Technical Architecture

### Current Project Structure

```
contrib-stats/
├── .github/
│   └── workflows/
│       ├── ci.yml              # CI pipeline
│       └── release.yml         # Release automation
├── src/
│   └── contrib_stats/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py              # Main CLI entry point
│       ├── exceptions.py       # Custom exceptions
│       │
│       ├── providers/          # API providers
│       │   ├── __init__.py
│       │   ├── base.py         # Abstract base provider
│       │   ├── gitlab.py       # GitLab API
│       │   └── github.py       # GitHub API
│       │
│       └── utils/
│           ├── __init__.py
│           └── validation.py   # Input validation
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── test_exceptions.py
│   ├── test_providers.py
│   └── test_validation.py
│
├── pyproject.toml
├── README.md
├── ROADMAP.md
└── LICENSE
```

---

## Metric Definitions

### Review Metrics (v1.2.0 ✅)
| Metric | Definition |
|--------|------------|
| MRs/PRs Commented | Unique MRs/PRs a user commented on |
| MRs/PRs Approved | Unique MRs/PRs a user approved |
| Total Comments | Total comment count across all reviews |
| Total Approvals | Total approval count |

### PR/MR Metrics (v1.3.0)
| Metric | Definition |
|--------|------------|
| PRs Opened | Number of PRs created in period |
| PRs Merged | Number of PRs successfully merged |
| PRs Closed | Number of PRs closed without merge |
| Merge Rate | PRs Merged / PRs Opened * 100 |
| Time to Merge | Time from PR open to merge |
| Time to First Review | Time from PR open to first review |

### Release Metrics (v1.4.0)
| Metric | Definition |
|--------|------------|
| Release Frequency | Releases per time period |
| Time Between Releases | Average days between releases |
| Commits per Release | Commits between release tags |
| PRs per Release | PRs merged between releases |

### Contributor Metrics (v1.6.0)
| Metric | Definition |
|--------|------------|
| Active Contributors | Users with merged PRs in period |
| First-time Contributors | New contributors in period |
| Bus Factor | Min contributors for 50% of commits |

---

## Priority Features for v1.3.0

Based on user requests, prioritize these for the next release:

1. **PRs per author** - Who sent the most PRs
2. **PRs merged per day/week** - Merge velocity
3. **Release count** - Releases in period
4. **Time between releases** - Release intervals
5. **Commits per release** - Release size

---

## License

MIT License (permissive, widely used for CLI tools)

---

## Contributing

Priority areas for contributions:
1. New metric implementations
2. Output formatters (HTML dashboard)
3. Additional providers (Bitbucket)
4. Documentation and examples
