# Contrib Stats - Project Roadmap

A CLI tool to analyze contributor activity, code review metrics, and repository statistics across GitLab and GitHub.

**Project Name:** `contrib-stats`
**PyPI Package:** `contrib-stats`
**GitHub Repo:** `github.com/LalatenduMohanty/contrib-stats`

## Vision

Provide comprehensive insights into repository health and team productivity through:
- **Review metrics** - Who reviews the most? How fast?
- **Contributor metrics** - Who contributes the most? PR volume?
- **Release metrics** - Release frequency, commits per release
- **Activity trends** - Daily/weekly/monthly patterns

---

## Current Features (v0.1.0)

- [x] GitLab merge request analysis
- [x] GitHub pull request analysis
- [x] Count unique MRs/PRs per reviewer
- [x] Multi-threaded API fetching
- [x] Date range filtering
- [x] CLI arguments with validation
- [x] Environment variable support
- [x] Interactive mode
- [x] Text file output

---

## Planned Features

### Phase 1: PR/MR Contribution Metrics (v0.2.0)

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

### Phase 2: Release Metrics (v0.3.0)

#### Release Statistics
- [ ] **Releases per week/month** - Release cadence
- [ ] **Time between releases** - Release intervals
- [ ] **Commits per release** - Release size
- [ ] **PRs per release** - Features/fixes per release
- [ ] **Contributors per release** - Team involvement
- [ ] **Release timeline visualization** - Gantt-style view

### Phase 3: Review Metrics (v0.4.0)

#### Reviewer Statistics
- [ ] **Reviews per reviewer** - Review volume (current feature)
- [ ] **Review response time** - Time to first review comment
- [ ] **Review turnaround** - Time from review to merge
- [ ] **Comments per review** - Review depth/engagement
- [ ] **Approval rate** - % of reviews that approve

#### Review Health
- [ ] **Review coverage** - % of PRs that got reviewed
- [ ] **Unreviewed PRs** - PRs merged without review
- [ ] **Review bottlenecks** - PRs waiting for review
- [ ] **Reviewer load balance** - Distribution of reviews

### Phase 4: Commit Metrics (v0.5.0)

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

### Phase 5: Team & Organization (v0.6.0)

#### Team Features
- [ ] **Team grouping** - Define teams, aggregate by team
- [ ] **Team comparisons** - Compare team productivity
- [ ] **Cross-team collaboration** - Inter-team reviews
- [ ] **Bus factor** - Knowledge distribution risk

#### Multi-Repository
- [ ] **Multiple repos** - Analyze multiple repos at once
- [ ] **Organization-wide stats** - Aggregate across org
- [ ] **Project grouping** - Group related repos

### Phase 6: Output & Visualization (v0.7.0)

#### Output Formats
- [ ] **JSON output** (`--format json`)
- [ ] **CSV output** (`--format csv`)
- [ ] **HTML report** (`--format html`) - Beautiful dashboard
- [ ] **Markdown tables** (`--format markdown`)
- [ ] **Terminal charts** - ASCII bar charts

#### Dashboards
- [ ] **Summary dashboard** - Key metrics at a glance
- [ ] **Trend charts** - Activity over time
- [ ] **Leaderboards** - Top contributors/reviewers
- [ ] **Calendar heatmap** - GitHub-style contribution graph

### Phase 7: Integrations (v0.8.0)

#### Notifications
- [ ] **Slack integration** - Post reports to Slack
- [ ] **Email reports** - Scheduled email summaries
- [ ] **Webhook support** - POST to custom endpoints
- [ ] **Microsoft Teams** - Teams notifications

#### Monitoring
- [ ] **Prometheus metrics** - Export for Grafana
- [ ] **DataDog integration** - APM integration
- [ ] **Custom metrics endpoint** - REST API for metrics

### Phase 8: Distribution (v1.0.0)

- [ ] **PyPI package** (`pip install contrib-stats`)
- [ ] **Docker image** (`docker run contrib-stats`)
- [ ] **Homebrew formula** (`brew install contrib-stats`)
- [ ] **GitHub Action** - Run in CI/CD
- [ ] **Pre-built binaries** - Standalone executables

---

## CLI Design

### Commands Structure

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

### Common Options

```bash
--provider, -p      # gitlab, github (required)
--project-id        # Project identifier (required)
--token             # Access token (required)
--start-date        # Start date YYYY-MM-DD
--end-date          # End date YYYY-MM-DD
--format, -f        # Output format: text, json, csv, html, markdown
--output, -o        # Output file path
--workers, -w       # Parallel threads (1-50)
--no-interactive    # Skip prompts
--verbose, -v       # Verbose output
--config            # Config file path
```

### Example Outputs

#### Contributors Summary
```
================================================================================
CONTRIBUTOR STATISTICS
================================================================================

Period: 2025-01-01 to 2025-06-01
Total PRs: 234
Total Contributors: 18

--------------------------------------------------------------------------------
TOP CONTRIBUTORS (by PRs merged)
--------------------------------------------------------------------------------
Rank   Username            PRs Opened   PRs Merged   Merge Rate
--------------------------------------------------------------------------------
1      alice               45           42           93%
2      bob                 38           35           92%
3      charlie             29           25           86%
```

#### Release Summary
```
================================================================================
RELEASE STATISTICS
================================================================================

Period: 2025-01-01 to 2025-06-01
Total Releases: 12
Average Time Between Releases: 12.5 days
Average Commits Per Release: 47

--------------------------------------------------------------------------------
RECENT RELEASES
--------------------------------------------------------------------------------
Version     Date          Commits    PRs    Contributors
--------------------------------------------------------------------------------
v2.5.0      2025-05-28    52         15     8
v2.4.1      2025-05-15    23         7      5
v2.4.0      2025-05-01    61         18     12
```

#### Activity Summary
```
================================================================================
REPOSITORY ACTIVITY SUMMARY
================================================================================

Period: 2025-01-01 to 2025-06-01

PRs/MRs:
  Opened: 234
  Merged: 198 (85%)
  Closed: 36 (15%)
  Avg Time to Merge: 2.3 days

Reviews:
  Total Reviews: 512
  Reviewers: 15
  Avg Reviews per PR: 2.6

Releases:
  Total: 12
  Frequency: ~2 per month

Top Contributors:        Top Reviewers:
1. alice (42 PRs)       1. david (89 reviews)
2. bob (35 PRs)         2. eve (76 reviews)
3. charlie (25 PRs)     3. frank (54 reviews)
```

---

## Configuration File

Support a `.contrib-stats.yaml` config file:

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

### Proposed Project Structure

```
contrib-stats/
├── src/
│   └── contrib_stats/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py                 # Main CLI entry point
│       ├── config.py              # Configuration handling
│       │
│       ├── providers/             # API providers
│       │   ├── __init__.py
│       │   ├── base.py            # Abstract base provider
│       │   ├── gitlab.py          # GitLab API
│       │   └── github.py          # GitHub API
│       │
│       ├── analyzers/             # Metric analyzers
│       │   ├── __init__.py
│       │   ├── reviews.py         # Review statistics
│       │   ├── contributors.py    # Contributor statistics
│       │   ├── releases.py        # Release statistics
│       │   ├── commits.py         # Commit statistics
│       │   └── prs.py             # PR/MR statistics
│       │
│       ├── formatters/            # Output formatters
│       │   ├── __init__.py
│       │   ├── text.py
│       │   ├── json.py
│       │   ├── csv.py
│       │   ├── html.py
│       │   └── markdown.py
│       │
│       └── utils/
│           ├── __init__.py
│           ├── validation.py
│           ├── dates.py
│           └── threading.py
│
├── tests/
├── docs/
├── templates/                     # HTML report templates
│   └── report.html.jinja2
├── pyproject.toml
├── README.md
├── ROADMAP.md
├── CHANGELOG.md
├── LICENSE
└── .contrib-stats.yaml.example
```

---

## Metric Definitions

### PR/MR Metrics
| Metric | Definition |
|--------|------------|
| PRs Opened | Number of PRs created in period |
| PRs Merged | Number of PRs successfully merged |
| PRs Closed | Number of PRs closed without merge |
| Merge Rate | PRs Merged / PRs Opened * 100 |
| Time to Merge | Time from PR open to merge |
| Time to First Review | Time from PR open to first review |

### Review Metrics
| Metric | Definition |
|--------|------------|
| Reviews Given | Unique PRs a user commented on |
| Review Comments | Total comments across all reviews |
| Approval Rate | Reviews with approval / Total reviews |
| Review Coverage | PRs with reviews / Total PRs |

### Release Metrics
| Metric | Definition |
|--------|------------|
| Release Frequency | Releases per time period |
| Time Between Releases | Average days between releases |
| Commits per Release | Commits between release tags |
| PRs per Release | PRs merged between releases |

### Contributor Metrics
| Metric | Definition |
|--------|------------|
| Active Contributors | Users with merged PRs in period |
| First-time Contributors | New contributors in period |
| Bus Factor | Min contributors for 50% of commits |

---

## Priority Features for v0.2.0

Based on user request, prioritize these for the next release:

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
