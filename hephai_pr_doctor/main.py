"""
main.py

Entry point for running HEPHAI-PR-Doctor in different modes:

- **Standalone Mode (Python Package)**: Generates a repository report as an MD file if AI_API_KEY is provided.
- **GitHub Actions Mode**: Analyzes the repository and PR, generating structured reports.
- **Development Mode**: Simulates PR data for testing and debugging.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import os

from hephai_pr_doctor.repositories.analyze_repository import analyze_repo_with_ai
from hephai_pr_doctor.repositories.fetch_repository import fetch_repo_structure

from hephai_pr_doctor.reviews.pull_request import (
    fetch_pr_data,
    analyze_pr_changes,
)
from hephai_pr_doctor.reports.generate_reports import generate_markdown_report

from hephai_pr_doctor.debug.custom_logger import get_logger

logger = get_logger("hephai_action_logger")


def main():
    """
    Executes the HEPHAI-PR-Doctor analysis workflow based on the selected mode.
    """
    logger.info("🚀 Starting HEPHAI-PR-Doctor...")

    mode = os.getenv("HEPHAI_MODE", "standalone").lower()
    repo_name = os.getenv("GITHUB_REPO_NAME")

    if mode == "standalone":
        logger.info(
            "🔍 Running in Standalone Mode: Analysis of the cloned repository locally."
        )

        repo_structure = fetch_repo_structure(repo_name, local=True)
        analysis_result = analyze_repo_with_ai(repo_structure, repo_name, pr_data=None)

        report_filename = "repo_analysis_report.md"

        # Generate markdown report
        report = generate_markdown_report(analysis_result, is_pr_mode=False)
        with open(report_filename, "w") as f:
            f.write(report)

        logger.info(f"📄 Report Generated: {report_filename}")

    elif mode == "development":
        logger.info("🔍 Running in Development Mode: Simulating PR data.")
        pr_data = {
            "changed_files": 3,
            "additions": 50,
            "deletions": 10,
            "files": [{"filename": "src/auth.py"}, {"filename": "tests/test_auth.py"}],
        }

        logger.info("🔍 Comparing PR against repository structure...")
        analysis_result = analyze_pr_changes(pr_data, repo_name)
        logger.info(f"🏁 HEPHAI PR Score: {analysis_result.get('score', 'N/A')}/100")
        if analysis_result.get("flagged", False):
            logger.warning(
                "⚠️ PR score is below the acceptable threshold. Review suggested changes before merging."
            )

        report_filename = "pr_review_report.md"

        # Generate markdown report
        report = generate_markdown_report(analysis_result, is_pr_mode=True)
        with open(report_filename, "w") as f:
            f.write(report)

        logger.info(f"📄 Report Generated: {report_filename}")

    elif mode == "github":
        logger.info(
            "🔍 Running in GitHub Actions Mode: Analyzing repository and PR data."
        )
        pr_data = fetch_pr_data()

        analysis_result = analyze_pr_changes(pr_data, repo_name)
        logger.info(f"🏁 HEPHAI PR Score: {analysis_result.get('score', 'N/A')}/100")
        if analysis_result.get("flagged", False):
            logger.warning(
                "⚠️ PR score is below the acceptable threshold. Review suggested changes before merging."
            )
    else:
        logger.error(
            "Invalid mode selected. Please select 'standalone', 'development', or 'github'."
        )


if __name__ == "__main__":
    main()
