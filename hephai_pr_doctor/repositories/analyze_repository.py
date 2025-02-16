"""
analyze_repository.py

Handles repository structure analysis for HEPHAI-PR-Doctor.

- Fetches repository structure (local or via GitHub API)
- Uses AI to determine repository purpose and functionality
- Assigns dynamic file weights to highlight critical components
- Supports PR impact analysis by providing structured insights
- Can analyze repository alone or compare a PR against it

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import os
import json
import openai
import requests
from dotenv import load_dotenv

from hephai_pr_doctor.debug.custom_logger import get_logger

logger = get_logger("hephai_action_logger")

# Load environment variables from .env file
load_dotenv()

# Fetch environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_EVENT_PATH = os.getenv("GITHUB_EVENT_PATH")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    logger.error(
        "OpenAI API key is missing. Ensure it is set in the environment variables or .env file."
    )
    raise EnvironmentError(
        "Missing OpenAI API key. Set the OPENAI_API_KEY environment variable in .env."
    )

# Initialize OpenAI client using the API key
client = openai.OpenAI(api_key=OPENAI_API_KEY)


def fetch_repo_structure(repo_name, local=False):
    """
    Fetches the repository file structure.

    - If `local=True`, it reads the local repository directory.
    - Otherwise, it fetches the structure from the GitHub API.
    """
    logger.info(
        f"Fetching repository structure for {repo_name} repository with local mode set to {local}."
    )

    if local:
        return fetch_local_repo_structure()

    url = f"https://api.github.com/repos/{repo_name}/git/trees/main?recursive=1"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logger.error(f"Failed to fetch repo structure: {response.text}")
        return fetch_local_repo_structure()  # Fallback to local

    repo_tree = response.json().get("tree", [])
    return [file["path"] for file in repo_tree if file["type"] == "blob"]


def fetch_local_repo_structure():
    """
    Reads the repository structure from the local filesystem, excluding:
    - Files & directories listed in .gitignore
    - The .git directory and its contents
    """
    logger.info(f"Fetching repository structure for local repository.")

    repo_root = os.getcwd()
    file_list = []
    gitignore_path = os.path.join(repo_root, ".gitignore")

    ignored_patterns = set()
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignored_patterns.add(line)

    ignored_patterns.add(".git")

    def is_ignored(file_path):
        """Check if a file path matches any .gitignore pattern."""
        return any(
            file_path.startswith(pattern) or file_path.endswith(pattern)
            for pattern in ignored_patterns
        )

    for root, _, files in os.walk(repo_root):
        if ".git" in root.split(os.sep):
            continue
        for file in files:
            relative_path = os.path.relpath(os.path.join(root, file), repo_root)
            if not is_ignored(relative_path):
                file_list.append(relative_path)

    return file_list


def analyze_repo_with_ai(file_list, repo_name, pr_data=None):
    """
    Uses AI to determine the primary purpose and functionality of the repository.
    Also assigns weight scores for each file type.
    If a PR is provided, it compares the PR changes against the repository.

    Args:
        file_list (list[str]): List of repository file paths.
        repo_name (str): Name of the repository.
        pr_data (dict, optional): PR data if PR comparison is needed.

    Returns:
        dict: Repository analysis including purpose, file weights, best practices, security, performance, and privacy scores.
    """
    logger.info(f"Analyzing repository '{repo_name}' with AI.")

    prompt = f"""
    You are analyzing the repository '{repo_name}'.
    Based on the following structure, determine:
    - The primary purpose and functionality of the repository (3-5 sentences).
    - Assign weight scores (1-10) for each file based on its importance.
    - Security-sensitive files (e.g., authentication, database access) should have higher weights.
    - Test files should have lower weights.
    - Utility/helper scripts should be neutral.
    
    """

    if pr_data:
        prompt += f"""
        Additionally, compare the following PR changes against the repository:
        {json.dumps(pr_data, indent=2)}
        
        - Determine how the PR modifies existing functionality.
        - Highlight potential security, performance, and privacy risks.
        - Suggest improvements based on best practices.
        """

    prompt += """
    Respond in JSON format:
    {
        "purpose": "<Brief repo purpose>",
        "file_weights": {
            "path/to/file1.py": 9,
            "path/to/file2.py": 6,
            "tests/test_auth.py": 2
        },
        "best_practices_score": 8,
        "security_score": 7,
        "performance_score": 9,
        "privacy_score": 6,
        "issues_found": "No critical issues detected.",
        "suggestions": "Consider adding more unit tests for authentication logic.",
        "strengths": "Modular structure, clear logging.",
        "weaknesses": "Lack of input validation in API endpoints.",
        "applause": "Great job on implementing repository-aware PR scoring!",
        "areas_to_improve": "Improve security awareness in API handling."
    }
    
    Ensure no markdown formatting. Return only raw JSON.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert software architect analyzing a repository.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        return {
            "purpose": "Unknown",
            "file_weights": {},
            "best_practices_score": "N/A",
            "security_score": "N/A",
            "performance_score": "N/A",
            "privacy_score": "N/A",
            "issues_found": "Analysis failed.",
            "suggestions": "No suggestions available.",
            "strengths": "No strengths detected.",
            "weaknesses": "No weaknesses detected.",
            "applause": "No commendations.",
            "areas_to_improve": "No improvement areas detected.",
        }
