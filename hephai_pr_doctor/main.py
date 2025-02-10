"""
main.py

Entry point for running PR analysis locally or in GitHub Actions.

- Fetches repository structure and analyzes it with AI.
- Retrieves PR metadata and scores the PR.
- Extracts exact PR changes and compares them to repository analysis.
- Provides inline comments and centralized review summary.
- Flags PRs that fall below the configured threshold.
- Generates a detailed markdown report.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import os
from hephai_pr_doctor.repositories.analyze_repository import analyze_repo_with_ai

from hephai_pr_doctor.reviews.pull_request import (
    fetch_pr_data,
    analyze_pr_changes,
)

from hephai_pr_doctor.reports.generate_reports import generate_pr_report

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

    # Run analysis on the repository
    repo_analysis = analyze_repo_with_ai(repo_name, local=local_mode)

    print(repo_analysis)

    pr_data = (
        fetch_pr_data()
        if not local_mode
        else {
            "changed_files": 2,
            "additions": 30,
            "deletions": 5,
            "files": [
                {
                    "filename": "src/auth.py",
                    "diff": "+ def new_login_function():\n    pass",
                },
                {
                    "filename": "tests/test_auth.py",
                    "diff": "+ def test_new_login_function():\n    assert True",
                },
            ],
            "diffs": [
                {
                    "filename": "src/auth.py",
                    "changes": "+ def new_login_function():\n    pass",
                },
                {
                    "filename": "tests/test_auth.py",
                    "changes": "+ def test_new_login_function():\n    assert True",
                },
            ],
        }
    )

    # Analyze PR changes in context of repository
    analysis_result = analyze_pr_changes(pr_data, repo_name, repo_analysis)
    print(analysis_result)

    # Generate markdown report
    report = generate_pr_report(analysis_result)
    with open("pr_review_report.md", "w") as f:
        f.write(report)

    logger.info(f"🏁 HEPHAI PR Score: {analysis_result['score']}/100")
    if analysis_result["flagged"]:
        logger.warning(
            "⚠️ PR score is below the acceptable threshold. Review suggested changes before merging."
        )

    logger.info("📄 PR Review Report Generated: pr_review_report.md")


if __name__ == "__main__":
    main()
