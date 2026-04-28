import json
import logging
from typing import Optional
from anthropic import Anthropic
from ..core.config import get_settings

logger = logging.getLogger(__name__)


ANALYSIS_PROMPT_TEMPLATE = """You are a senior web development architect analyzing a project idea.

## Project Idea
Title: {title}
Description: {description}
Constraints: {constraints}
Preferences: {preferences}

## Your Task
Evaluate this idea across four dimensions and produce a structured analysis report.

## Constraints for Analysis
- Deployment target: Vercel (primary)
- Database options: NeonDB (PostgreSQL), no external DB required
- AI runtime: Claude Code CLI (available tools: file creation, git, npm, etc.)
- Tech stack flexibility: any modern web stack (React, Vue, Svelte, Next.js, etc.)
- Do NOT assume external APIs beyond standard web APIs

## Output Format
Return a JSON object with this exact structure:
{{
  "scope_score": "small|medium|large|xlarge",
  "complexity_score": "simple|moderate|complex|very_complex",
  "tech_feasibility": {{
    "verdict": "feasible|risky|not_feasible",
    "challenges": ["challenge1", ...],
    "suggestions": ["suggestion1", ...]
  }},
  "estimated_effort_hours": {{
    "min": number,
    "max": number,
    "confidence": "low|medium|high"
  }},
  "recommended_stack": {{
    "frontend": "string",
    "backend": "string|null",
    "database": "string|null",
    "deployment": "string"
  }},
  "feature_breakdown": [
    {{
      "feature": "string",
      "estimated_hours": number,
      "priority": "must|should|could"
    }}
  ],
  "risks": [
    {{
      "description": "string",
      "severity": "low|medium|high",
      "mitigation": "string"
    }}
  ],
  "summary": "string (2-3 sentence executive summary)"
}}

## Guidelines
- Be conservative with effort estimates — add 20% buffer for edge cases
- Flag any features that require external services not supported by Vercel/NeonDB
- If the idea is not feasible, explain why and suggest a minimal viable alternative
- "risky" verdict means achievable with additional care/mitigation
"""


async def analyze_idea(
    title: str,
    description: str,
    constraints: Optional[dict] = None,
    preferences: Optional[dict] = None,
) -> dict:
    settings = get_settings()
    client = Anthropic(api_key=settings.anthropic_api_key)

    constraints_json = json.dumps(constraints or {}, indent=2)
    preferences_json = json.dumps(preferences or {}, indent=2)

    prompt = ANALYSIS_PROMPT_TEMPLATE.format(
        title=title,
        description=description,
        constraints=constraints_json,
        preferences=preferences_json,
    )

    response = client.messages.create(
        model="MiniMax-M2.7",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.content[0].text.strip()

    json_start = raw_text.find("{")
    json_end = raw_text.rfind("}") + 1
    if json_start == -1 or json_end == 0:
        logger.error("Failed to parse analysis JSON from response: %s", raw_text[:500])
        raise ValueError("Analysis response was not valid JSON")

    analysis = json.loads(raw_text[json_start:json_end])
    return analysis