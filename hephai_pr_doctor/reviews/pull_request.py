"""
pull_request.py

Handles PR analysis, scoring, and test case suggestions for HEPHAI-PR-Doctor.

- Fetches PR metadata from GitHub event payload.
- Extracts exact PR changes (diffs) and compares them against repository analysis.
- Analyzes PR complexity and assigns an AI-powered dynamic quality score.
- Uses OpenAI to suggest test cases for changed files.
- Provides inline comments on code changes.
- Flags PRs below a configurable threshold.
- Generates a detailed review report based on PR modifications.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import os
import openai
import json
from hephai_pr_doctor.repositories.analyze_repository import fetch_repo_structure

from hephai_pr_doctor.debug.custom_logger import get_logger
from hephai_pr_doctor.config.config import CONFIG
import requests

logger = get_logger("hephai_action_logger")
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def fetch_pr_data() -> dict:
    """
    Loads PR data including exact file diffs from the GitHub event payload.

    Returns:
        dict: PR metadata extracted from the GitHub event file, including changed files and diff details.
    """
    logger.info("Fetching PR data from GitHub event payload.")
    try:
        with open(os.getenv("GITHUB_EVENT_PATH"), "r") as f:
            event_data = json.load(f)
        pr_data = event_data.get("pull_request", {})

        # Fetch file diffs
        diff_url = pr_data.get("url", "") + "/files"
        headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}
        response = requests.get(diff_url, headers=headers)

        if response.status_code == 200:
            pr_data["diffs"] = response.json()
        else:
            logger.error("Failed to fetch PR file diffs.")
            pr_data["diffs"] = []

        return pr_data
    except Exception as e:
        logger.error(f"Failed to load PR data: {e}")
        return {}


def analyze_pr_changes(pr_data: dict, repo_name: str, repo_analysis: dict) -> dict:
    """
    Analyzes PR changes, evaluates file complexity, and assigns an AI-driven score.

    Args:
        pr_data (dict): PR metadata, including exact diffs.
        repo_name (str): Repository name.
        repo_analysis (dict): Repository analysis output including purpose, tech stack, and file weights.

    Returns:
        dict: Analysis results including dynamic AI-powered score and inline comments.
    """
    logger.info(f"Analyzing PR changes for {repo_name}.")
    changed_files = pr_data.get("changed_files", 0)
    additions = pr_data.get("additions", 0)
    deletions = pr_data.get("deletions", 0)
    diffs = pr_data.get("diffs", [])

    # Base scoring system
    score = CONFIG.BASE_SCORE
    score -= changed_files * CONFIG.CHANGE_FILE_WEIGHT
    score -= additions * CONFIG.ADDITION_WEIGHT
    score -= deletions * CONFIG.DELETION_WEIGHT

    # Security, Performance, and Best Practices Analysis
    ai_quality_prompt = f"""
    You are reviewing a pull request for the repository '{repo_name}'.
    The repository is described as follows:
    Purpose: {repo_analysis.get("purpose", "Unknown")}
    Tech Stack: {repo_analysis.get("tech_stack", [])}
    File Weights: {repo_analysis.get("file_weights", {})}

    Here are the exact changes made in this PR:
    {json.dumps(diffs, indent=2)}
    
    ```json
    {{
        "pr_summary": "<Summarized PR purpose in 3-5 sentences>",
        "impact": "<Impact on the repository>",
        "issues_found": "<Number and brief details of Issues Found: Best Practices, Security, Performance etc.>",
        "test_suggestions": "<Suggested test cases for the PR>",
        "strengths": "<List the strength of the PR in various aspects>",
        "weaknesses": "<List the weaknesses of the PR in various aspects>",
        "suggestions": "<General suggestions for the PR>",
        "applause": "<Applaud the contributor for the positive aspects of their skills>",
        "areas_to_improve": "<Skills to improve/explore>"
    }}
    
    DO NOT include markdown formatting. Return only the JSON object.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert software engineer reviewing a pull request.",
                },
                {"role": "user", "content": ai_quality_prompt},
            ],
        )
        ai_analysis = json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        ai_analysis = {}

    return {
        "score": max(0, min(100, score)),
        "flagged": score < CONFIG.PR_SCORE_THRESHOLD,
        **ai_analysis,  # Merging AI-generated structured review with existing analysis
    }
