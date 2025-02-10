# HEPHAI-PR-Doctor

**HEPHAI-PR-Doctor** is an AI-powered GitHub Action for **automated PR review, test generation, and code quality analysis**. It leverages **OpenAI models** to evaluate pull requests, suggest improvements, and generate test cases.

## Features

- **Automated PR Analysis** – Assigns a quality score based on file changes, complexity, and AI-inferred file importance.  
- **AI-Powered Test Suggestions** – Generates test cases for changed files to improve coverage.  
- **Repository Structure Analysis** – Evaluates file types (e.g., security-sensitive, config, tests) to weight their impact.  
- **GitHub Actions & Local Testing** – Works as a GitHub Action or can be executed locally for testing.  
- **Automated PR Comments** – Posts a structured review summary with test suggestions directly on GitHub PRs.  


## Configuration

HEPHAI-PR-doctor requires:

- **`GITHUB_TOKEN`** (Automatically available in GitHub Actions)
- **`OPENAI_API_KEY`** (Set as a repository secret to use OpenAI for PR reviews and test generation)

## How It Works

1. Fetches Repository Structure – Retrieves the list of files in the repo (GitHub API or local scan).
2. Analyzes File Weights with AI – Assigns weights to files based on importance (security, tests, config).
3. Fetches PR Data – Reads PR details, including changed files, additions, deletions, and linting issues.
4. Scores the PR – Calculates a PR quality score (0-100) using file importance, size, and complexity.
5. Generates Test Cases – Uses AI to suggest unit and integration tests for modified files.
6. Saves a Test Report – Outputs a structured JSON report with the analysis results.
7. Posts a PR Comment – (If in GitHub Actions) Posts a review summary with test recommendations.
