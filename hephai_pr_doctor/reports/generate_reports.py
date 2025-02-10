from hephai_pr_doctor.debug.custom_logger import get_logger

logger = get_logger("hephai_action_logger")


def generate_pr_report(analysis_result: dict) -> str:
    """
    Generates a markdown report summarizing PR analysis.

    Args:
        analysis_result (dict): PR analysis results.

    Returns:
        str: Markdown formatted PR report.
    """
    return f"""
# 🏆 Scoreboard

- **Total PR Score:** {analysis_result['score']}/100
- **Best Practices Score:** {analysis_result.get('best_practices_score', 'N/A')}/10
- **Security Score:** {analysis_result.get('security_score', 'N/A')}/10
- **Performance Score:** {analysis_result.get('performance_score', 'N/A')}/10
- **Privacy Score:** {analysis_result.get('privacy_score', 'N/A')}/10

## 🚀 PR Summary

### What PR Tries to Achieve
{analysis_result.get('pr_summary', 'No summary available.')}

## 💡 Impact on the Project
{analysis_result.get('impact', 'No impact analysis available.')}

## 🔍 Issues Found
{analysis_result.get('issues_found', 'No issues detected.')}

## 🧪 Suggested Test Cases
{analysis_result.get('test_suggestions', 'No test cases suggested.')}

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
"""
