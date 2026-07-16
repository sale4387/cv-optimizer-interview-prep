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
- Keep responsibilities and achievements strictly separate.
- Responsibilities describe recurring scope, ownership, processes and duties.
- Achievements describe quantified outcomes, one-off wins, promotions,
  acquisitions, awards and measurable commercial impact.
- Never copy, paraphrase or move an existing achievement into responsibilities.
- Metrics already present in achievements must remain only in achievements.
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
                    "20-400 characters; maximum six; recurring scope only; exclude achievements and duplicated metrics"
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
- Preserve the original achievements section unchanged.
- Do not repeat, paraphrase or move achievement bullets into responsibilities.
- Remove outcome-heavy responsibility bullets when the same result or metric
  already exists in achievements for that experience.
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
- Keep responsibilities and achievements strictly separate.
- Responsibilities describe recurring scope, ownership, processes and duties.
- Never repeat or paraphrase an existing achievement inside responsibilities.
- Metrics already present in achievements must remain only in achievements.
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

For experience_updates, keep recurring responsibilities separate from
existing achievements. Do not repeat achievement metrics or outcomes inside
responsibilities.
Do not return any unrequested section.
Return valid JSON only.
""".strip()
COMPANY_RESEARCH_SYSTEM_INSTRUCTION = f"""
{BASE_SYSTEM_INSTRUCTION}

You produce search-grounded company intelligence.

Strict rules:
- Use current public web information.
- Do not invent company facts, customers, competitors, news, stock information or employee sentiment.
- Separate verified information from limitations and uncertainty.
- Prefer official company sources for what the company does.
- Use reputable news or financial sources for recent developments when available.
- Treat employee sentiment as a public signal only, not a definitive rating.
- If reliable information is unavailable, mark the report as limited.
- Return every required top-level field exactly once.
- Keep primary_industry, secondary_industries and business_model nested inside industry.
- Company research must not generate interviewer questions or candidate questions.
- interview_intelligence contains only talking_points and risks_to_prepare_for.
- Return one JSON object only.
- Do not use Markdown fences.
- Do not add explanatory text outside the JSON object.
""".strip()


COMPANY_RESEARCH_RESPONSE_FORMAT = {
    "research_status": "complete | limited",
    "confidence_level": "high | medium | low",
    "short_description": "Short factual company description.",
    "industry": {
        "primary_industry": "Main industry.",
        "secondary_industries": [
            "Additional relevant industry."
        ],
        "business_model": "How the company appears to make money.",
    },
    "products_and_services": [
        {
            "name": "Product, service or platform name.",
            "type": "product | service | platform | solution | unknown",
            "description": "Short factual description.",
            "why_it_matters_for_interview": "Interview relevance.",
        }
    ],
    "customers_and_market": {
        "known_public_customers": [
            {
                "name": "Customer name.",
                "context": "Why this customer is relevant.",
            }
        ],
        "customer_types": [
            "Customer segment or type."
        ],
        "target_markets": [
            "Market, region or segment."
        ],
        "limitations": "Customer data limitation if needed.",
    },
    "competitors": [
        {
            "name": "Competitor name.",
            "reason": "Why this company is a competitor.",
            "comparison_note": "How the target company appears different.",
        }
    ],
    "recent_developments": [
        {
            "date": "YYYY-MM-DD or YYYY-MM if available",
            "type": "news | acquisition | merger | funding | product | partnership | leadership | financial | other",
            "title": "Development title.",
            "summary": "Short factual summary.",
            "interview_relevance": "Why this may matter for interview preparation.",
        }
    ],
    "public_company_information": {
        "is_public_company": False,
        "ticker": None,
        "exchange": None,
        "summary": "Short summary or null.",
        "limitations": "Limitation if not public or unavailable.",
    },
    "employee_sentiment": {
        "signal": "positive | mixed | negative | insufficient_public_data",
        "summary": "Publicly available employee sentiment themes.",
        "positive_themes": [
            "Positive theme."
        ],
        "negative_themes": [
            "Negative theme."
        ],
        "interview_caution": "How to treat this information carefully.",
        "limitations": "Source limitations.",
    },
    "interview_intelligence": {
        "talking_points": [
            {
                "topic": "Useful company-specific topic.",
                "why_it_matters": "Why this is useful.",
                "how_to_use": "How the candidate may mention it.",
            }
        ],
        "risks_to_prepare_for": [
            {
                "risk": "Potential concern or uncertainty.",
                "preparation_note": "How to prepare.",
            }
        ],
    },
    "sources": [
        {
            "title": "Source title.",
            "url": "Source URL.",
            "publisher": "Publisher or website name.",
            "source_type": "official | news | financial | review | other",
            "supports": [
                "What this source supports."
            ],
            "accessed_at": "YYYY-MM-DD",
        }
    ],
    "limitations": [
        "Important limitation, missing data or uncertainty."
    ],
}


COMPANY_RESEARCH_REQUIRED_TOP_LEVEL_KEYS = (
    "research_status",
    "confidence_level",
    "short_description",
    "industry",
    "products_and_services",
    "customers_and_market",
    "competitors",
    "recent_developments",
    "public_company_information",
    "employee_sentiment",
    "interview_intelligence",
    "sources",
    "limitations",
)


def build_company_research_prompt(
    *,
    company_label: str,
    company_key: str,
    country_code: str,
    generated_at: str,
    valid_until: str,
) -> str:
    response_format = json.dumps(
        COMPANY_RESEARCH_RESPONSE_FORMAT,
        ensure_ascii=False,
        indent=2,
    )

    required_keys = json.dumps(
        COMPANY_RESEARCH_REQUIRED_TOP_LEVEL_KEYS,
        ensure_ascii=False,
        indent=2,
    )

    return f"""
Create a search-grounded company intelligence report.

Company:
{company_label}

Company key:
{company_key}

Country code:
{country_code}

Generated at:
{generated_at}

Valid until:
{valid_until}

Required top-level keys:
{required_keys}

Required JSON structure:
{response_format}

Additional instructions:
- Return all required top-level keys, even when some information is limited.
- Do not add any other top-level keys.
- industry must be one nested object.
- primary_industry, secondary_industries and business_model are forbidden at the top level.
- interview_intelligence must contain only talking_points and risks_to_prepare_for.
- Do not generate likely interviewer questions or candidate questions in company research.
- Do current public web research.
- Include official sources where possible.
- Include source URLs for factual claims.
- If named customers are not public, use customer types and explain limitations.
- If employee sentiment is not reliable or public enough, use insufficient_public_data.
- If the company is private, set is_public_company to false and do not invent ticker data.
- Do not include generic filler.
- Return valid JSON only.
""".strip()


def build_company_research_retry_prompt(
    *,
    company_label: str,
    company_key: str,
    country_code: str,
    generated_at: str,
    valid_until: str,
    invalid_response: Mapping[str, Any] | str,
    validation_reasons: list[str],
) -> str:
    response_format = json.dumps(
        COMPANY_RESEARCH_RESPONSE_FORMAT,
        ensure_ascii=False,
        indent=2,
    )

    required_keys = json.dumps(
        COMPANY_RESEARCH_REQUIRED_TOP_LEVEL_KEYS,
        ensure_ascii=False,
        indent=2,
    )

    if isinstance(invalid_response, Mapping):
        invalid_text = json.dumps(
            dict(invalid_response),
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    else:
        invalid_text = str(
            invalid_response
        )

    invalid_text = invalid_text[:12000]

    reasons_text = json.dumps(
        validation_reasons,
        ensure_ascii=False,
        indent=2,
    )

    return f"""
The previous company research JSON was invalid. Correct it completely.

Company:
{company_label}

Company key:
{company_key}

Country code:
{country_code}

Generated at:
{generated_at}

Valid until:
{valid_until}

Validation failures:
{reasons_text}

Invalid previous response:
{invalid_text}

Required top-level keys:
{required_keys}

Required JSON structure:
{response_format}

Repair rules:
- Return a completely new JSON object, not a partial patch.
- Return every required top-level key exactly once.
- Do not add extra top-level keys.
- Nest primary_industry, secondary_industries and business_model inside industry.
- Do not return those three industry fields at the top level.
- interview_intelligence contains only talking_points and risks_to_prepare_for.
- Do not generate interviewer questions or candidate questions in company research.
- Preserve only claims that can be supported by public sources.
- Use limitations instead of guessing.
- Return valid JSON only, without Markdown or explanation.
""".strip()


INTERVIEW_PREP_SYSTEM_INSTRUCTION = f"""
{BASE_SYSTEM_INSTRUCTION}

You generate application-specific interview preparation from:
- the exact job advertisement
- the original CV
- the tailored CV
- fit and gap evidence
- company research

Strict rules:
- Generate 10 to 15 likely questions the interviewer may ask.
- Candidate questions to ask must remain a separate section.
- Every interviewer question must be tied to at least one concrete anchor:
  company, role requirement, named CV employer, named project, documented
  responsibility, documented achievement, fit evidence or identified gap.
- Do not use generic coaching templates.
- Do not write phrases such as "use one concrete example", "open with your
  strongest experience", "use only examples already present", or
  "this tests whether the candidate can connect their background".
- evidence_to_use must name the actual CV evidence to use. Prefer employer,
  project, responsibility, achievement, metric or documented skill.
- Each suggested_answer_direction must be usable, not abstract.
- angle must state a specific response strategy for this exact question.
- key_points must contain factual points from the supplied data.
- example_focus must be a 3-to-5 sentence candidate-ready draft answer using
  only supplied facts. It must not be a generic instruction.
- Suggested answers may use first person, but may not invent facts.
- Highlight older, smaller or less recent experience that should be refreshed.
- Explicitly warn where the candidate must avoid overstating a gap.
- Tell-me-about-yourself guidance belongs in positioning_guidance.
- Return one JSON object only.
- Do not use Markdown fences.
- Do not add text outside the JSON object.
""".strip()


INTERVIEW_PREP_RESPONSE_FORMAT = {
    "interview_prep_id": "application-id",
    "prep_status": "complete | limited",
    "positioning_guidance": {
        "summary": (
            "Specific positioning for this company and role."
        ),
        "focus_points": [
            (
                "Concrete CV experience, employer, project, "
                "achievement or skill to emphasize."
            )
        ],
        "avoid_overstating": [
            (
                "Specific gap or risk that must be discussed "
                "carefully."
            )
        ],
    },
    "questions": [
        {
            "question_id": "q001",
            "category": (
                "cv_experience | job_requirement | "
                "company_context | gap_or_risk | behavioral | "
                "technical_or_domain | motivation"
            ),
            "question": (
                "Likely interviewer question specific to the "
                "application."
            ),
            "why_this_matters": (
                "Concrete reason based on the role, company, "
                "fit or gap."
            ),
            "evidence_to_use": [
                (
                    "Named CV employer, project, responsibility, "
                    "achievement, metric or documented skill."
                )
            ],
            "suggested_answer_directions": [
                {
                    "angle": (
                        "Specific response strategy for this "
                        "question."
                    ),
                    "key_points": [
                        (
                            "Factual point copied or faithfully "
                            "paraphrased from supplied data."
                        )
                    ],
                    "example_focus": (
                        "A 3-to-5 sentence candidate-ready draft "
                        "answer using supplied facts only."
                    ),
                }
            ],
            "preparation_note": (
                "Specific item to verify or refresh before the "
                "interview."
            ),
            "risk_level": "low | medium | high",
        }
    ],
    "experience_checkpoints": [
        {
            "emphasized_area": (
                "Experience emphasized for this role."
            ),
            "supporting_cv_evidence": (
                "Exact CV evidence supporting it."
            ),
            "likely_follow_up_questions": [
                "Specific likely follow-up question."
            ],
            "preparation_needed": (
                "Specific detail the candidate should refresh."
            ),
        }
    ],
    "company_specific_talking_points": [
        {
            "topic": "Verified company-specific topic.",
            "why_relevant": (
                "Why it matters for this role."
            ),
            "how_to_use": (
                "How to mention it naturally."
            ),
        }
    ],
    "candidate_questions_to_ask": [
        {
            "question": (
                "Question the candidate can ask."
            ),
            "reason": (
                "Why this question is useful for this "
                "specific application."
            ),
        }
    ],
    "limitations": [
        "Missing context or uncertainty."
    ],
}


def build_interview_prep_prompt(
    *,
    application_id: str,
    original_cv: dict,
    tailored_cv: dict,
    job_ad: str,
    company_research: dict | None,
    generated_at: str,
) -> str:
    response_format = json.dumps(
        INTERVIEW_PREP_RESPONSE_FORMAT,
        ensure_ascii=False,
        indent=2,
    )

    return f"""
Generate deeply personalized interview preparation for one application.

Application ID:
{application_id}

Generated at:
{generated_at}

Exact job advertisement:
{job_ad}

Original CV - factual source of truth:
{json.dumps(original_cv, ensure_ascii=False, indent=2, default=str)}

Tailored CV:
{json.dumps(tailored_cv, ensure_ascii=False, indent=2, default=str)}

Company research:
{json.dumps(company_research, ensure_ascii=False, indent=2, default=str)}

Required JSON structure:
{response_format}

Quality requirements:
- Produce 10 to 15 likely interviewer questions.
- At least 8 questions must mention or clearly depend on a concrete company,
  role, requirement, employer, project, achievement, metric, skill or gap.
- Every evidence_to_use item must identify the real evidence, not tell the
  candidate to find an example later.
- Every question needs at least one candidate-ready answer draft in
  example_focus.
- Use different evidence across questions where possible.
- Separate likely interviewer questions from candidate questions to ask.
- Do not invent facts.
- Return valid JSON only.
""".strip()

