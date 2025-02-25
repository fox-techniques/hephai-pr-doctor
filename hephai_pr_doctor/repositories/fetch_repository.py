"""
fetch_repository.py

Handles repository structure for analysis.

- Fetches repository structure (local or via GitHub API)

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import os
import requests
from dotenv import load_dotenv

from hephai_pr_doctor.debug.custom_logger import get_logger

logger = get_logger("hephai_action_logger")

# Load environment variables from .env file
load_dotenv()

# Fetch environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_EVENT_PATH = os.getenv("GITHUB_EVENT_PATH")


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
        return _fetch_local_repo_structure()

    url = f"https://api.github.com/repos/{repo_name}/git/trees/main?recursive=1"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logger.error(f"Failed to fetch repo structure: {response.text}")
        return _fetch_local_repo_structure()  # Fallback to local

    repo_tree = response.json().get("tree", [])
    return [file["path"] for file in repo_tree if file["type"] == "blob"]


def _fetch_local_repo_structure():
    """
    Reads the repository structure from the local filesystem, excluding:
    - Files & directories listed in .gitignore
    - The .git directory and its contents
    - The __pycache__ directory and its contents
    """
    logger.info("Fetching repository structure for local repository.")

    repo_root = os.getcwd()
    file_list = []
    gitignore_path = os.path.join(repo_root, ".gitignore")

    # Read .gitignore file if it exists
    ignored_patterns = set()
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):  # Ignore empty lines and comments
                    ignored_patterns.add(line)

    # Always exclude .git and __pycache__ directories
    ignored_patterns.update([".git", "__pycache__"])

    def is_ignored(file_path):
        """Check if a file path matches any .gitignore pattern."""
        for pattern in ignored_patterns:
            if file_path.startswith(pattern) or file_path.endswith(pattern):
                return True
        return False

    # Walk through the repository structure
    for root, dirs, files in os.walk(repo_root):
        # Skip ignored directories
        if any(ignored in root for ignored in ignored_patterns):
            continue

        for file in files:
            relative_path = os.path.relpath(os.path.join(root, file), repo_root)
            if not is_ignored(relative_path):  # Skip ignored files
                file_list.append(relative_path)

    return file_list
