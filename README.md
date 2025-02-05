# hephai-pr-doctor

# HEPHAI-PR-doctor

## Overview
**HEPHAI-PR-doctor** is a GitHub Action that provides **AI-powered PR reviews** and **automated test generation** for **Python & JavaScript**. It leverages OpenAI to analyze pull requests, generate unit tests, and provide actionable feedback on code quality.

## Features
- AI-generated PR review comments on **code quality & best practices**  
- Automated **test case generation** for changed Python/JavaScript functions  
- Runs tests and posts **pass/fail results** on the PR  
- Works with **Poetry for dependency management**  
- Seamlessly integrates into GitHub CI/CD pipelines  

## Installation
To use **HEPHAI-PR-doctor**, add the following workflow file to your repo:

```yaml
name: HEPHAI-PR-doctor

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  test-action:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Poetry
        run: pip install poetry

      - name: Install dependencies
        run: poetry install --no-root

      - name: Run HEPHAI-PR-doctor
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: poetry run hephai-pr-doctor
```

## Configuration
HEPHAI-PR-doctor requires:
- **`GITHUB_TOKEN`** (Automatically available in GitHub Actions)
- **`OPENAI_API_KEY`** (Set as a repository secret to use OpenAI for PR reviews and test generation)

## How It Works
1. The action is triggered when a PR is opened or updated.
2. It fetches **changed Python/JavaScript files** in the PR.
3. The AI reviews code for **readability, best practices, and potential issues**.
4. It **generates test cases** for modified functions.
5. Runs tests and **posts results** as a comment on the PR.

## Example Output
Example AI-generated PR comment:
```
### AI-Powered PR Review Feedback
#### File: my_script.py
```
- Code readability is good, but consider adding docstrings for better maintainability.
- Best practices followed. No major issues detected.
- Function `process_data()` lacks unit tests. Suggested test cases:
```python
import pytest
from my_script import process_data

def test_process_data():
    assert process_data("input") == "expected_output"
```
```

## License
This project is licensed under the **Apache-2.0 License**.

## Contributing
Contributions are welcome! Feel free to submit PRs for enhancements or bug fixes.

## Contact
For any questions, open an issue or reach out on GitHub.

---
**Improve your PR workflow with AI-powered reviews & test generation!**
