from hephai_pr_doctor.debug.custom_logger import get_logger

logger = get_logger("hephai_action_logger")


def generate_markdown_report(analysis_result: dict, is_pr_mode: bool) -> str:
    """
    Generates a markdown report summarizing repository or PR analysis.

    Args:
        analysis_result (dict): Analysis results (repository or PR).
        is_pr_mode (bool): Whether the report is for a PR or standalone repo analysis.

    Returns:
        str: Markdown formatted report.
    """
    title = "# 🏆 Scoreboard\n"
    if is_pr_mode:
        title += "\n- **Total PR Score:** {analysis_result.get('score', 'N/A')}/100"

    file_weights_section = ""
    if not is_pr_mode:
        file_weights = analysis_result.get("file_weights", {})
        file_weights_section = "\n## 📂 File Weights & Importance\n"
        for file, weight in file_weights.items():
            file_weights_section += f"- `{file}`: Weight {weight}\n"

    return f"""
{title}

- **Best Practices Score:** {analysis_result.get('best_practices_score', 'N/A')}/10
- **Security Score:** {analysis_result.get('security_score', 'N/A')}/10
- **Performance Score:** {analysis_result.get('performance_score', 'N/A')}/10
- **Privacy Score:** {analysis_result.get('privacy_score', 'N/A')}/10

## 🚀 {"PR Summary" if is_pr_mode else "Repository Overview"}

### {"What PR Tries to Achieve" if is_pr_mode else "Repository Purpose"}
{analysis_result.get('pr_summary' if is_pr_mode else 'purpose', 'No summary available.')}

## 💡 {"Impact on the Project" if is_pr_mode else "Key Components"}
{analysis_result.get('impact' if is_pr_mode else 'key_components', 'No impact analysis available.')}

## 🔍 Issues Found
{analysis_result.get('issues_found', 'No issues detected.')}

## 📝 General Suggestions
{analysis_result.get('suggestions', 'No suggestions provided.')}

## 🔹 Strengths
{analysis_result.get('strengths', 'No strengths identified.')}

## 🔻 Weaknesses
{analysis_result.get('weaknesses', 'No weaknesses identified.')}

## 👏 Applause
{analysis_result.get('applause', 'No specific praises given.')}

## 📈 Areas to Improve
{analysis_result.get('areas_to_improve', 'No improvement areas identified.')}
{file_weights_section}
"""
