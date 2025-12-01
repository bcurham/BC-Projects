"""
Requirements Quality Checker
Analyzes URS requirements for quality issues using AI
"""

import json


class QualityChecker:
    def __init__(self, anthropic_client):
        self.client = anthropic_client

    def analyze_requirements(self, urs_text):
        """
        Analyze URS requirements for quality issues

        Args:
            urs_text: Extracted URS text

        Returns:
            quality_report: Dictionary containing quality analysis
        """
        if not self.client:
            return {
                'error': 'Anthropic API client not available',
                'success': False
            }

        prompt = self._build_quality_check_prompt(urs_text)

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            response_text = message.content[0].text

            # Parse JSON response
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            quality_report = json.loads(response_text)
            quality_report['success'] = True

            return quality_report

        except Exception as e:
            return {
                'error': f'Quality check failed: {str(e)}',
                'success': False
            }

    def _build_quality_check_prompt(self, urs_text):
        """Build prompt for quality checking"""
        prompt = """You are a validation expert analyzing User Requirements Specifications (URS) for quality issues.

Analyze the following URS text and identify:

1. **Ambiguous Requirements**: Requirements with unclear or vague language
2. **Non-Testable Requirements**: Requirements that cannot be objectively tested
3. **Missing Acceptance Criteria**: Requirements without clear success criteria
4. **Conflicting Requirements**: Requirements that contradict each other
5. **Incomplete Requirements**: Requirements missing essential details

For each issue found, provide:
- Requirement ID (if available) or excerpt
- Issue category
- Description of the problem
- Severity (High/Medium/Low)
- Suggested improvement

Output MUST be valid JSON only, no markdown or commentary.

Output format:
{
  "overall_quality_score": "Good|Fair|Poor",
  "total_requirements": <number>,
  "issues_found": <number>,
  "issues": [
    {
      "requirement_excerpt": "excerpt or ID",
      "category": "Ambiguous|Non-Testable|Missing Acceptance|Conflicting|Incomplete",
      "description": "what's wrong",
      "severity": "High|Medium|Low",
      "suggestion": "how to improve"
    }
  ],
  "strengths": ["list of good aspects"],
  "recommendations": ["list of overall recommendations"]
}

URS Text:
""" + urs_text[:8000]  # Limit to first 8000 chars to fit token limits

        prompt += "\n\nGenerate the JSON quality report now:"

        return prompt
