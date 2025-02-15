"""
main.py

Entry point for running PR analysis locally or in GitHub Actions.

- Fetches repository structure and analyzes it with AI.
- Retrieves PR metadata and scores the PR.
- Extracts exact PR changes and compares them to repository analysis.
- Provides inline comments and centralized review summary.
- Flags PRs that fall below the configured threshold.
- Generates a detailed markdown report.
- Can analyze the repository alone or compare a PR against it.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import os
import json
from hephai_pr_doctor.repositories.analyze_repository import (
    fetch_repo_structure,
    analyze_repo_with_ai,
)
from hephai_pr_doctor.reviews.pull_request import (
    fetch_pr_data,
    analyze_pr_changes,
)
from hephai_pr_doctor.reports.generate_reports import generate_markdown_report
from hephai_pr_doctor.debug.custom_logger import get_logger
from hephai_pr_doctor.config.config import CONFIG

logger = get_logger("hephai_action_logger")


def main():
    """
    Executes the PR analysis workflow.
    """
    logger.info("🚀 Starting HEPHAI-PR-Doctor Diagnosis...")

    local_mode = os.getenv("LOCAL_MODE", "false").lower() == "true"
    repo_name = "fox-techniques/hephai-pr-doctor"

    # Fetch repository structure
    repo_structure = fetch_repo_structure(repo_name, local=local_mode)
    pr_data = None if local_mode else fetch_pr_data()
    repo_analysis = analyze_repo_with_ai(repo_structure, repo_name, pr_data)

    is_pr_mode = pr_data is not None

    if is_pr_mode:
        logger.info("🔍 Comparing PR against repository structure...")
        analysis_result = analyze_pr_changes(pr_data, repo_name)
        logger.info(f"🏁 HEPHAI PR Score: {analysis_result.get('score', 'N/A')}/100")
    else:
        logger.info("📊 Performing standalone repository analysis...")
        analysis_result = repo_analysis

    # Generate markdown report
    report = generate_markdown_report(analysis_result, is_pr_mode)
    with open(
        "pr_review_report.md" if is_pr_mode else "repo_analysis_report.md", "w"
    ) as f:
        f.write(report)

    if is_pr_mode and analysis_result.get("flagged", False):
        logger.warning(
            "⚠️ PR score is below the acceptable threshold. Review suggested changes before merging."
        )

    logger.info(
        "📄 Report Generated: "
        + ("pr_review_report.md" if is_pr_mode else "repo_analysis_report.md")
    )


if __name__ == "__main__":
    main()
