from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


BASE_SYSTEM_INSTRUCTION = """
You are a precise assistant for CV and job-application workflows.

Follow the requested output format exactly.
Use only facts provided in the input.
Never invent experience, skills, qualifications, employers or achievements.
Return concise and professional content.
""".strip()


SIMPLE_TEST_PROMPT = """
Reply with exactly this text:

Gemini connection successful
""".strip()


ROLE_FIT_CRITERIA = """
Use exactly one of these fit levels:

- strong:
  The candidate directly meets nearly all essential requirements and most
  important preferred requirements. Evidence is explicit in the CV and there
  are no high-impact gaps.

- solid:
  The candidate meets the essential requirements and many important
  requirements. Remaining gaps are limited, honest and realistically
  manageable.

- stretch:
  The candidate meets enough core requirements to justify applying, but has
  notable gaps. The CV may be truthfully tailored, but the candidate needs
  focused preparation and must discuss gaps honestly.

- poor:
  The candidate misses one or more essential or high-impact requirements, or
  the CV lacks enough evidence to support a credible application. Do not
  tailor the CV for a poor fit.
""".strip()


CV_OPTIMIZATION_SYSTEM_INSTRUCTION = f"""
{BASE_SYSTEM_INSTRUCTION}

You assess role fit and produce a truthful CV optimization patch.

{ROLE_FIT_CRITERIA}

Strict rules:
- Use only facts supported by the supplied structured CV.
- Never invent metrics, tools, responsibilities, employers, education,
  certifications or achievements.
- Preserve the meaning of the original experience.
- Reference only experience IDs that exist in the supplied CV.
- Highlight only skills explicitly supported by the supplied CV.
- If the fit level is poor, cv_patch must be null.
- If the fit level is strong, solid or stretch, cv_patch must be complete.
- Return one JSON object only.
- Do not use Markdown fences.
- Do not add explanatory text outside the JSON object.
""".strip()


EXPECTED_RESPONSE_FORMAT = {
    "fit_assessment": {
        "level": "strong | solid | stretch | poor",
        "explanation": "50-1000 characters",
        "relevant_experience": [
            "10-500 characters, supported by the original CV"
        ],
        "missing_requirements": [
            "5-300 characters"
        ],
    },
    "cv_patch": {
        "professional_summary": "80-700 characters",
        "experience_updates": [
            {
                "experience_id": "an existing ID from the original CV",
                "suggested_job_title": None,
                "responsibilities": [
                    "20-400 characters, maximum six per experience"
                ],
            }
        ],
        "skills_to_highlight": [
            "a skill supported by the original CV"
        ],
    },
    "gap_analysis": {
        "supported_requirements": [
            "requirement supported by the CV"
        ],
        "reasonably_derived_requirements": [
            "requirement reasonably derived from CV evidence"
        ],
        "unsupported_requirements": [
            {
                "requirement": "minimum 5 characters",
                "impact": "low | medium | high",
                "preparation_recommendation": "minimum 20 characters",
                "interview_guidance": "minimum 20 characters",
            }
        ],
    },
    "warnings": [
        "5-300 characters"
    ],
}


def build_cv_optimization_prompt(
    *,
    cv_profile: Mapping[str, Any],
    job_ad_text: str,
    company_name: str,
) -> str:
    response_format = json.dumps(
        EXPECTED_RESPONSE_FORMAT,
        ensure_ascii=False,
        indent=2,
    )

    cv_json = json.dumps(
        dict(cv_profile),
        ensure_ascii=False,
        indent=2,
    )

    return f"""
Assess the candidate's fit for the role and return the CV optimization result.

Company:
{company_name}

Job advertisement:
{job_ad_text}

Structured CV:
{cv_json}

Required JSON structure:
{response_format}

Additional instructions:
- Determine the fit level before deciding whether to create cv_patch.
- For poor fit, set cv_patch to null.
- For poor fit, clearly list missing requirements and provide practical
  preparation recommendations in gap_analysis.
- For acceptable fit, rewrite only the professional summary and selected
  responsibilities that improve relevance without changing facts.
- Use exact experience IDs from the structured CV.
- Return valid JSON only.
""".strip()
CV_REVISION_SYSTEM_INSTRUCTION = f"""
{BASE_SYSTEM_INSTRUCTION}

You revise only the CV sections explicitly requested by the user.

Strict rules:
- Use only facts supported by the original structured CV.
- Treat the current tailored CV as the starting point.
- Follow each section-specific user comment.
- Return every requested section.
- Return no section that was not requested.
- Do not return fit_assessment, gap_analysis, warnings or wrapper keys.
- Do not invent experience, skills, employers, achievements or metrics.
- Preserve sections that were not requested by omitting them.
- Use exact experience IDs from the original CV.
- Return one JSON object only.
- Do not use Markdown fences.
- Do not add text outside the JSON object.
""".strip()


REVISION_SECTION_RESPONSE_SHAPES = {
    "professional_summary": (
        "string containing 80-700 characters"
    ),
    "experience_updates": [
        {
            "experience_id": (
                "existing experience ID from the original CV"
            ),
            "suggested_job_title": (
                "string or null"
            ),
            "responsibilities": [
                (
                    "20-400 characters; maximum six "
                    "responsibilities per experience"
                )
            ],
        }
    ],
    "skills_to_highlight": [
        (
            "skill explicitly supported by the "
            "original structured CV"
        )
    ],
}


def build_cv_revision_prompt(
    *,
    original_cv: Mapping[str, Any],
    current_cv: Mapping[str, Any],
    current_optimization: Mapping[str, Any],
    revision_request: Mapping[str, Any],
) -> str:
    selected_sections = [
        item["section"]
        for item in revision_request[
            "sections"
        ]
    ]

    comments = {
        item["section"]: item["comment"]
        for item in revision_request[
            "sections"
        ]
    }

    expected_response = {
        section: (
            REVISION_SECTION_RESPONSE_SHAPES[
                section
            ]
        )
        for section in selected_sections
    }

    return f"""
Revise the selected CV sections.

Selected sections and user comments:
{json.dumps(comments, ensure_ascii=False, indent=2)}

Original structured CV — source of truth:
{json.dumps(dict(original_cv), ensure_ascii=False, indent=2)}

Current tailored CV:
{json.dumps(dict(current_cv), ensure_ascii=False, indent=2)}

Current validated optimization result:
{json.dumps(dict(current_optimization), ensure_ascii=False, indent=2)}

Return exactly these top-level keys:
{json.dumps(expected_response, ensure_ascii=False, indent=2)}

Do not return any unrequested section.
Return valid JSON only.
""".strip()
