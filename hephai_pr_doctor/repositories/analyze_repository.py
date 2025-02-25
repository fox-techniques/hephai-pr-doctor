"""
analyze_repository.py

Handles repository structure analysis for HEPHAI-PR-Doctor.

- Uses AI to determine repository purpose and functionality
- Assigns dynamic file weights to highlight critical components
- Supports PR impact analysis by providing structured insights
- Can analyze repository alone or compare a PR against it

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import os
import json
import openai
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
    
    Here is the list of file paths in the repository: {file_list}

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
        "purpose": "<Brief repository purpose>",
        "file_weights": <example of estimated file weights: {
            "path/to/file1.py": 9,
            "path/to/file2.py": 6,
            "tests/test_auth.py": 2
        }>,
        "best_practices_score": <estimated_best_practice_score>,
        "security_score": <estimated_security_score>,
        "performance_score": <estimated_performance_score>,
        "privacy_score": <estimated_privacy_score>,
        "issues_found": "<Brief description of list of issues found>",
        "suggestions": "<General suggestions to improve quality, functionality, or other aspects>",
        "strengths": "<List of strengths of the current implementation/initiative>",
        "weaknesses": "<List of weaknesses of the current implementation/initiative>",
        "applause": "<Applause the contributor on their skill, way of working, though process, coding style etc.>",
        "areas_to_improve": "<Suggest where they should invest to improve their skills>"
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
