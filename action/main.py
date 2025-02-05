import os
import json
import requests
from github import Github

github_token = os.getenv("GITHUB_TOKEN")
github_event_path = os.getenv("GITHUB_EVENT_PATH")
github_repository = os.getenv("GITHUB_REPOSITORY")
openai_api_key = os.getenv("OPENAI_API_KEY")

g = Github(github_token)
repo = g.get_repo(github_repository)


def get_pr_files():
    """Fetch changed files from PR."""
    with open(github_event_path, "r") as f:
        event_data = json.load(f)

    pr_number = event_data["pull_request"]["number"]
    pr_files_url = (
        f"https://api.github.com/repos/{github_repository}/pulls/{pr_number}/files"
    )
    headers = {"Authorization": f"token {github_token}"}
    response = requests.get(pr_files_url, headers=headers)

    if response.status_code == 200:
        return [
            file["filename"]
            for file in response.json()
            if file["filename"].endswith((".py", ".js"))
        ]
    return []


def generate_review(file_content):
    """Use OpenAI to review PR changes."""
    url = "https://api.openai.com/v1/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json",
    }
    prompt = f"Review the following code for quality, readability, and best practices:\n\n{file_content}\n\nProvide constructive feedback."

    data = {"model": "gpt-4-turbo", "prompt": prompt, "max_tokens": 500}
    response = requests.post(url, headers=headers, json=data)
    return response.json().get("choices", [{}])[0].get("text", "No feedback generated.")


def post_pr_comment(pr_number, comment):
    """Post review feedback as a PR comment."""
    comments_url = (
        f"https://api.github.com/repos/{github_repository}/issues/{pr_number}/comments"
    )
    headers = {"Authorization": f"token {github_token}"}
    data = {"body": comment}
    requests.post(comments_url, headers=headers, json=data)


def main():
    pr_files = get_pr_files()
    if not pr_files:
        print("No relevant files changed in this PR.")
        return

    feedback = "### AI-Powered PR Review Feedback\n"
    for file in pr_files:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()

        review = generate_review(content)
        feedback += f"#### File: {file}\n```\n{review}\n```\n"

    pr_number = json.load(open(github_event_path))["pull_request"]["number"]
    post_pr_comment(pr_number, feedback)


if __name__ == "__main__":
    main()
