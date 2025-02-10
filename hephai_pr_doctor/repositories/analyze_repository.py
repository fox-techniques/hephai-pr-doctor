"""
analyze_repository.py

Handles repository structure analysis for HEPHAI-PR-Doctor.

- Fetches repository structure (local or via GitHub API)
- Analyzes repository files using OpenAI API
- Extracts repository purpose and functionality

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import os
import json
import openai
import requests
from hephai_pr_doctor.config.config import CONFIG
from hephai_pr_doctor.debug.custom_logger import get_logger

logger = get_logger("hephai_action_logger")

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def fetch_repo_structure(repo_name: str, local: bool = False) -> list[str]:
    """
    Fetches the repository file structure.

    Args:
        repo_name (str): Name of the repository.
        local (bool): If True, reads the local repository directory.

    Returns:
        list[str]: List of file paths in the repository.
    """
    logger.info(f"Fetching repository structure for {repo_name}, local mode: {local}.")

    if local:
        return fetch_local_repo_structure()

    url = f"https://api.github.com/repos/{repo_name}/git/trees/main?recursive=1"
    headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logger.error(f"Failed to fetch repo structure: {response.text}")
        return fetch_local_repo_structure()  # Fallback to local

    repo_tree = response.json().get("tree", [])
    return [file["path"] for file in repo_tree if file["type"] == "blob"]


def fetch_local_repo_structure() -> list[str]:
    """
    Reads the repository structure from the local filesystem, excluding:
    - Files & directories listed in .gitignore
    - The .git directory and its contents
    - The __pycache__ directory and its contents

    Returns:
        list[str]: List of relevant file paths in the local repository.
    """
    logger.info("Fetching repository structure from local directory.")

    repo_root = os.getcwd()
    file_list = []
    ignored_patterns = set()
    gitignore_path = os.path.join(repo_root, ".gitignore")

    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            ignored_patterns.update(
                line.strip() for line in f if line.strip() and not line.startswith("#")
            )

    ignored_patterns.update([".git", "__pycache__"])

    def is_ignored(file_path: str) -> bool:
        return any(pattern in file_path for pattern in ignored_patterns)

    for root, _, files in os.walk(repo_root):
        if any(pattern in root for pattern in ignored_patterns):
            continue
        for file in files:
            relative_path = os.path.relpath(os.path.join(root, file), repo_root)
            if not is_ignored(relative_path):
                file_list.append(relative_path)

    return file_list


def analyze_repo_with_ai(repo_name: str, local: bool = False) -> dict[str, int]:
    """
    Sends the repository structure to OpenAI for analysis and receives file weights.

    Args:
        file_list (list[str]): List of repository file paths.

    Returns:
        dict[str, int]: Dictionary mapping filenames to importance weights.
    """
    logger.info(f"Analyzing repository: {repo_name} files with AI.")

    file_list = fetch_repo_structure(repo_name, local)

    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OpenAI API key is missing. Using default file weights.")
        return {}

    prompt = f"""
    You are an expert software engineer analyzing a GitHub repository. 
    Your goal is to determine the **purpose**, **technology stack**, and **file importance** based on its structure.

    ### **Analysis Requirements:**
    1. **Repository Purpose:**  
    - Summarize the repository's primary functionality in **3-5 sentences**.
    - Identify whether it is a web application, API, CLI tool, data processing system, etc.

    2. **Technology Stack:**  
    - Detect the programming languages, frameworks, and libraries used.
    - Consider take a look at dependencies from package files (`requirements.txt`, `pyproject.toml`, `package.json`).
    - Include any relevant database technologies (SQL, NoSQL).

    3. **File Importance Weights:**  
    - Assign a **numeric weight (1-10) to each file** based on its role:
        - **10 (Critical):** Security-sensitive files (authentication, database access, API keys).
        - **8-9 (High):** Core business logic (service handlers, data processing, transaction management).
        - **6-7 (Medium):** Supporting modules (helper utilities, middleware, logging).
        - **3-5 (Low):** Non-critical functionality (frontend templates, scripts, configurations).
        - **1-2 (Very Low):** Documentation, test files, CI/CD workflows.
    - Assign **higher weights to files handling user input** (e.g., API endpoints, form validators).
    - **Error handling and monitoring files** should have medium priority.
    - **Unit tests should have minimal weight** unless they contain business-critical validation.

    ---

    ### **Repository Structure:**
    {json.dumps(file_list, indent=2)}

    ---

    ### **Expected JSON Output:**
    Return a **JSON object** with the following format:

    ```json
    {{
        "repo_name": "{repo_name}",
        "purpose": "<Summarized repository purpose in 3-5 sentences>",
        "tech_stack": ["<Detected Technologies>"],
        "file_weights": {{
            "path/to/file_1.py": 9,
            "path/to/file_2.py": 6,
            "tests/test_auth.py": 2
        }}
    }}

    DO NOT include markdown formatting. Return only the JSON object.

    Ensure **no markdown formatting** in your response. Only return raw JSON.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert software engineer analyzing a repository.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        return {}
