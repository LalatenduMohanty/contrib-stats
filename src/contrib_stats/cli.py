"""Command-line interface for contrib_stats."""

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from typing import Any

from contrib_stats import __version__
from contrib_stats.exceptions import ContribStatsError
from contrib_stats.providers.base import ReviewAnalyzer
from contrib_stats.providers.github import GitHubAnalyzer
from contrib_stats.providers.gitlab import GitLabAnalyzer
from contrib_stats.utils.validation import (
    VALID_PROVIDERS,
    validate_date,
    validate_project_id,
    validate_provider,
    validate_workers,
)

# Valid output formats
VALID_FORMATS = ("text", "csv", "json")


def validate_format(value: str) -> str:
    """Validate output format argument."""
    value_lower = value.lower()
    if value_lower not in VALID_FORMATS:
        raise argparse.ArgumentTypeError(f"Invalid format '{value}'. Must be one of: {', '.join(VALID_FORMATS)}")
    return value_lower


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="contrib-stats",
        description="Contrib Stats - Analyze contributor activity and code review metrics.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # GitLab
  contrib-stats --provider gitlab --project-id group/project --token xxx

  # GitHub
  contrib-stats --provider github --project-id owner/repo --token xxx

  # With custom date range
  contrib-stats --provider github --project-id owner/repo --token xxx \\
    --start-date 2025-01-01 --end-date 2025-06-30

  # Save as text file
  contrib-stats --provider gitlab --project-id group/project --token xxx \\
    --output results.txt --no-interactive

  # Save as JSON
  contrib-stats --provider gitlab --project-id group/project --token xxx \\
    --output results.json --format json --no-interactive

  # Save as CSV files to a directory
  contrib-stats --provider github --project-id owner/repo --token xxx \\
    --output-dir ./reports --format csv --no-interactive

Environment Variables:
  CONTRIB_STATS_PROVIDER     Provider (gitlab or github)
  CONTRIB_STATS_PROJECT_ID   Project ID (group/project or owner/repo)
  CONTRIB_STATS_TOKEN        Personal access token
  GITLAB_URL                 GitLab instance URL (for self-hosted)
  GITHUB_URL                 GitHub API URL (for GitHub Enterprise)
        """,
    )
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--provider",
        "-p",
        type=validate_provider,
        help="Provider: 'gitlab' or 'github' (required)",
    )
    parser.add_argument(
        "--project-id",
        type=validate_project_id,
        help="Project ID: 'group/project' (GitLab) or 'owner/repo' (GitHub)",
    )
    parser.add_argument(
        "--token",
        help="Personal access token (GitLab: read_api scope, GitHub: repo scope)",
    )
    parser.add_argument(
        "--url",
        help="API URL (default: https://gitlab.com or https://api.github.com)",
    )
    parser.add_argument(
        "--start-date",
        type=validate_date,
        default="2025-01-01",
        help="Start date in YYYY-MM-DD format (default: 2025-01-01)",
    )
    parser.add_argument(
        "--end-date",
        type=validate_date,
        default=datetime.now().strftime("%Y-%m-%d"),
        help="End date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path for text/json format",
    )
    parser.add_argument(
        "--output-dir",
        "-d",
        help="Output directory for CSV files (used with --format csv)",
    )
    parser.add_argument(
        "--format",
        "-f",
        type=validate_format,
        default="text",
        help="Output format: 'text', 'csv', or 'json' (default: text)",
    )
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Skip interactive prompts (useful for automation)",
    )
    parser.add_argument(
        "--workers",
        "-w",
        type=validate_workers,
        default=10,
        help="Number of parallel threads (1-50, default: 10)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show full stack traces on errors",
    )
    return parser.parse_args()


def save_results_text(stats: dict[str, Any], start_date: str, end_date: str, output_file: str, mr_term: str) -> None:
    """Save results in text format."""
    with open(output_file, "w") as f:
        f.write("=" * 80 + "\n")
        f.write(f"{mr_term} REVIEW STATISTICS - DETAILED REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"\nPeriod: {start_date} to {end_date}\n")
        f.write(f"Total {mr_term}s: {stats['total_mrs']}\n")
        f.write(f"Total Review Comments: {stats['total_comments']}\n")
        f.write(f"Total Approvals: {stats['total_approvals']}\n")
        f.write(f"Total Reviewers: {stats['total_reviewers']}\n\n")

        # Commenters section
        f.write("-" * 80 + "\n")
        f.write(f"TOP COMMENTERS (by unique {mr_term}s commented on)\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Rank':<6} {'Username':<30} {mr_term + 's Commented':<15}\n")
        f.write("-" * 80 + "\n")
        for rank, (username, count) in enumerate(stats["commenters"], 1):
            f.write(f"{rank:<6} {username:<30} {count:<15}\n")

        # Approvers section
        f.write("\n" + "-" * 80 + "\n")
        f.write(f"TOP APPROVERS (by unique {mr_term}s approved)\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Rank':<6} {'Username':<30} {mr_term + 's Approved':<15}\n")
        f.write("-" * 80 + "\n")
        if stats["approvers"]:
            for rank, (username, count) in enumerate(stats["approvers"], 1):
                f.write(f"{rank:<6} {username:<30} {count:<15}\n")
        else:
            f.write("(No approvals found)\n")

        f.write("\n" + "-" * 80 + "\n")
        f.write("Notes:\n")
        f.write(f"  - Commenters: Users who commented on at least one {mr_term} (excluding self-comments)\n")
        f.write(f"  - Approvers: Users who approved at least one {mr_term} (excluding self-approvals)\n")
        f.write("=" * 80 + "\n")


def save_results_json(
    stats: dict[str, Any], start_date: str, end_date: str, output_file: str, mr_term: str, provider: str
) -> None:
    """Save results in JSON format."""
    # Build JSON-serializable data
    output_data = {
        "metadata": {
            "provider": provider,
            "mr_term": mr_term,
            "start_date": start_date,
            "end_date": end_date,
            "generated_at": datetime.now().isoformat(),
        },
        "summary": {
            "total_mrs": stats["total_mrs"],
            "total_comments": stats["total_comments"],
            "total_approvals": stats["total_approvals"],
            "total_reviewers": stats["total_reviewers"],
        },
        "commenters": [
            {"rank": i + 1, "username": username, "count": count}
            for i, (username, count) in enumerate(stats["commenters"])
        ],
        "approvers": [
            {"rank": i + 1, "username": username, "count": count}
            for i, (username, count) in enumerate(stats["approvers"])
        ],
    }

    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)


def save_results_csv(
    stats: dict[str, Any],
    start_date: str,
    end_date: str,
    output_dir: str,
    mr_term: str,
    provider: str,
) -> list[str]:
    """
    Save results in CSV format with separate files for each metric.

    Creates CSV files with timestamped names:
    - summary_YYYYMMDD_HHMMSS.csv - Overall statistics
    - commenters_by_mrs_commented_YYYYMMDD_HHMMSS.csv - Commenter rankings
    - approvers_by_mrs_approved_YYYYMMDD_HHMMSS.csv - Approver rankings

    Args:
        stats: Statistics dictionary
        start_date: Start date of analysis
        end_date: End date of analysis
        output_dir: Output directory path
        mr_term: MR or PR term
        provider: Provider name

    Returns:
        List of created file paths
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    mr_term_lower = mr_term.lower()
    created_files: list[str] = []

    # Summary CSV
    summary_file = os.path.join(output_dir, f"summary_{timestamp}.csv")
    with open(summary_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Provider", provider])
        writer.writerow(["MR/PR Term", mr_term])
        writer.writerow(["Start Date", start_date])
        writer.writerow(["End Date", end_date])
        writer.writerow(["Generated At", datetime.now().isoformat()])
        writer.writerow([f"Total {mr_term}s", stats["total_mrs"]])
        writer.writerow(["Total Comments", stats["total_comments"]])
        writer.writerow(["Total Approvals", stats["total_approvals"]])
        writer.writerow(["Total Reviewers", stats["total_reviewers"]])
    created_files.append(summary_file)

    # Commenters CSV - users who commented on MRs/PRs
    commenters_file = os.path.join(output_dir, f"commenters_by_{mr_term_lower}s_commented_{timestamp}.csv")
    with open(commenters_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Rank", "Username", f"{mr_term}s_Commented"])
        for rank, (username, count) in enumerate(stats["commenters"], 1):
            writer.writerow([rank, username, count])
    created_files.append(commenters_file)

    # Approvers CSV - users who approved MRs/PRs
    approvers_file = os.path.join(output_dir, f"approvers_by_{mr_term_lower}s_approved_{timestamp}.csv")
    with open(approvers_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Rank", "Username", f"{mr_term}s_Approved"])
        for rank, (username, count) in enumerate(stats["approvers"], 1):
            writer.writerow([rank, username, count])
    created_files.append(approvers_file)

    return created_files


def save_results(
    stats: dict[str, Any],
    start_date: str,
    end_date: str,
    output_path: str,
    mr_term: str,
    provider: str,
    output_format: str,
) -> None:
    """
    Save detailed results to file(s).

    Args:
        stats: Statistics dictionary
        start_date: Start date of analysis
        end_date: End date of analysis
        output_path: Output file path (text/json) or directory (csv)
        mr_term: MR or PR term
        provider: Provider name (gitlab or github)
        output_format: Output format (text, csv, json)
    """
    if output_format == "json":
        save_results_json(stats, start_date, end_date, output_path, mr_term, provider)
        print(f"[OK] Results saved to: {output_path}")
    elif output_format == "csv":
        created_files = save_results_csv(stats, start_date, end_date, output_path, mr_term, provider)
        print(f"[OK] CSV files saved to directory: {output_path}")
        for file_path in created_files:
            print(f"  - {os.path.basename(file_path)}")
    else:
        save_results_text(stats, start_date, end_date, output_path, mr_term)
        print(f"[OK] Results saved to: {output_path}")


def main() -> None:
    """Main entry point for the CLI."""
    args = parse_args()

    print(f"Contrib Stats v{__version__} - Contributor & Review Analytics")
    print("=" * 80)

    # Configuration priority: CLI args > environment variables > interactive prompts
    provider = args.provider or os.environ.get("CONTRIB_STATS_PROVIDER")
    project_id = args.project_id or os.environ.get("CONTRIB_STATS_PROJECT_ID")
    token = args.token or os.environ.get("CONTRIB_STATS_TOKEN")

    # Prompt for missing configuration
    if not provider:
        if args.no_interactive:
            print("\n[ERROR] --provider is required in non-interactive mode.")
            print("        Valid options: gitlab, github")
            sys.exit(1)
        print("\nSelect provider:")
        print("  1. gitlab")
        print("  2. github")
        choice = input("Enter choice (1 or 2, or name): ").strip().lower()
        if choice == "1":
            provider = "gitlab"
        elif choice == "2":
            provider = "github"
        elif choice in VALID_PROVIDERS:
            provider = choice
        else:
            print(f"[ERROR] Invalid provider. Must be one of: {', '.join(VALID_PROVIDERS)}")
            sys.exit(1)

    if not project_id:
        if args.no_interactive:
            print("\n[ERROR] --project-id is required in non-interactive mode.")
            sys.exit(1)
        if provider == "gitlab":
            print("\nEnter your GitLab project path (e.g., 'group/project'):")
        else:
            print("\nEnter your GitHub repository (e.g., 'owner/repo'):")
        project_id = input("Project ID: ").strip()
        if "/" not in project_id:
            print("[ERROR] Invalid project ID format. Expected: owner/repo or group/project")
            sys.exit(1)

    if not token:
        if args.no_interactive:
            print("\n[ERROR] --token is required in non-interactive mode.")
            sys.exit(1)
        if provider == "gitlab":
            print("\nEnter your GitLab personal access token:")
            print("   (Create one at: GitLab -> Preferences -> Access Tokens)")
            print("   Required scopes: 'read_api'")
        else:
            print("\nEnter your GitHub personal access token:")
            print("   (Create one at: GitHub -> Settings -> Developer settings -> Personal access tokens)")
            print("   Required scopes: 'repo' (for private repos) or 'public_repo' (for public repos)")
        token = input("Token: ").strip()

    if not project_id or not token:
        print("\n[ERROR] Project ID and token are required.")
        sys.exit(1)

    # Determine API URL
    if provider == "gitlab":
        api_url = args.url or os.environ.get("GITLAB_URL", "https://gitlab.com")
    else:
        api_url = args.url or os.environ.get("GITHUB_URL", "https://api.github.com")

    start_date = args.start_date
    end_date = args.end_date

    print("\nConfiguration:")
    print(f"   Provider: {provider}")
    print(f"   API URL: {api_url}")
    print(f"   Project: {project_id}")
    print(f"   Date range: {start_date} to {end_date}")
    print(f"   Parallel workers: {args.workers}")

    # Initialize appropriate analyzer
    analyzer: ReviewAnalyzer
    if provider == "gitlab":
        analyzer = GitLabAnalyzer(project_id, token, api_url, max_workers=args.workers)
    else:
        analyzer = GitHubAnalyzer(project_id, token, api_url, max_workers=args.workers)

    # Run analysis
    try:
        stats = analyzer.analyze_reviews(start_date, end_date)
        analyzer.print_report(stats, start_date, end_date)

        # Determine output path based on format
        output_format = args.format
        # For CSV, use output_dir or output as directory; for text/json, use output as file path
        output_path = args.output_dir or args.output if args.format == "csv" else args.output

        if output_path:
            save_results(stats, start_date, end_date, output_path, analyzer.mr_term, provider, output_format)
        elif not args.no_interactive:
            print("\nWant to save detailed results to a file? (y/n): ", end="")
            if input().strip().lower() == "y":
                print("Select format:")
                print("  1. text")
                print("  2. json")
                print("  3. csv")
                fmt_choice = input("Enter choice (1, 2, 3, or name): ").strip().lower()

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                if fmt_choice == "2" or fmt_choice == "json":
                    output_format = "json"
                    output_path = f"contrib_stats_{provider}_{timestamp}.json"
                elif fmt_choice == "3" or fmt_choice == "csv":
                    output_format = "csv"
                    output_path = input("Enter output directory (default: ./reports): ").strip()
                    if not output_path:
                        output_path = "./reports"
                else:
                    output_format = "text"
                    output_path = f"contrib_stats_{provider}_{timestamp}.txt"

                save_results(stats, start_date, end_date, output_path, analyzer.mr_term, provider, output_format)

    except KeyboardInterrupt:
        print("\n\n[WARN] Analysis interrupted by user.")
        sys.exit(130)

    except ContribStatsError as e:
        # User-friendly error messages for known errors
        print(f"\n[ERROR] {e}")
        if args.debug:
            import traceback

            print("\n--- Debug Traceback ---")
            traceback.print_exc()
        sys.exit(1)

    except Exception as e:
        # Unexpected errors
        print(f"\n[ERROR] An unexpected error occurred: {e}")
        if args.debug:
            import traceback

            print("\n--- Debug Traceback ---")
            traceback.print_exc()
        else:
            print("\nRun with --debug flag for full stack trace.")
        sys.exit(1)


if __name__ == "__main__":
    main()
