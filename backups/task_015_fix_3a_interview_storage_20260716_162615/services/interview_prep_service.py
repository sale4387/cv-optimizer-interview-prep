from __future__ import annotations

from typing import Any


def _to_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        try:
            return value.model_dump()
        except Exception:
            pass
    if hasattr(value, "dict"):
        try:
            return value.dict()
        except Exception:
            pass
    return {}


def _first_text(data: dict[str, Any], keys: list[str], default: str = "") -> str:
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return default


def _flatten_text(value: Any, limit: int = 14000) -> str:
    parts: list[str] = []

    def walk(item: Any) -> None:
        if len(" ".join(parts)) > limit:
            return
        if item is None:
            return
        if isinstance(item, str):
            text = item.strip()
            if text:
                parts.append(text)
            return
        if isinstance(item, (int, float, bool)):
            parts.append(str(item))
            return
        if isinstance(item, dict):
            for nested in item.values():
                walk(nested)
            return
        if isinstance(item, list):
            for nested in item:
                walk(nested)
            return

    walk(value)
    return " ".join(parts)[:limit]


def _contains_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms)


def _extract_application_id(application: dict[str, Any]) -> str | None:
    for key in ("application_id", "id", "doc_id", "document_id", "firestore_id"):
        value = application.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    metadata = application.get("metadata")
    if isinstance(metadata, dict):
        for key in ("application_id", "id", "doc_id", "document_id", "firestore_id"):
            value = metadata.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    return None


def _extract_company_name(application: dict[str, Any]) -> str:
    for key in ("company_name", "company", "company_display_name", "company_key"):
        value = application.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    company = application.get("company")
    if isinstance(company, dict):
        for key in ("name", "company_name", "display_name", "company_key"):
            value = company.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    return "the company"


def _extract_job_title(application: dict[str, Any]) -> str:
    return _first_text(
        application,
        ["job_title", "target_job_title", "role_title", "position_title", "title"],
        default="the role",
    )


def _extract_job_ad(application: dict[str, Any]) -> str:
    for key in ("job_ad", "job_description", "posting_text", "description", "raw_job_ad"):
        value = application.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    inputs = application.get("inputs")
    if isinstance(inputs, dict):
        for key in ("job_ad", "job_description", "posting_text", "description"):
            value = inputs.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    return ""


def _extract_fit_label(application: dict[str, Any]) -> str:
    fit = application.get("fit_assessment") or application.get("fit") or application.get("fit_gap")
    if isinstance(fit, str):
        return fit.strip()
    if isinstance(fit, dict):
        for key in ("fit", "fit_label", "overall_fit", "recommendation", "score_label"):
            value = fit.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return "not explicitly stated"


def is_valid_application_interview_prep(prep: dict[str, Any]) -> bool:
    if not isinstance(prep, dict):
        return False
    questions = prep.get("likely_interviewer_questions")
    candidate_questions = prep.get("candidate_questions_to_ask")
    if not isinstance(questions, list):
        return False
    if not 10 <= len(questions) <= 15:
        return False
    if not isinstance(candidate_questions, list):
        return False
    if len(candidate_questions) < 3:
        return False
    for item in questions:
        if not isinstance(item, dict):
            return False
        if not isinstance(item.get("question"), str) or not item["question"].strip():
            return False
    return True


def _existing_interview_prep(application: dict[str, Any]) -> dict[str, Any] | None:
    for key in ("interview_prep", "interview_preparation", "application_interview_prep"):
        value = application.get(key)
        if isinstance(value, dict) and is_valid_application_interview_prep(value):
            return value
    return None


def _make_question(
    question: str,
    why: str,
    answer_angle: str,
    evidence_to_use: str,
    risk_level: str = "medium",
) -> dict[str, str]:
    return {
        "question": question,
        "why_it_may_be_asked": why,
        "answer_angle": answer_angle,
        "evidence_to_use": evidence_to_use,
        "risk_level": risk_level,
    }


def _build_prep_warnings(job_ad: str, cv_text: str, fit_label: str) -> list[str]:
    warnings: list[str] = []

    if _contains_any(job_ad, ["payment", "payments", "fintech", "merchant acquiring"]) and not _contains_any(
        cv_text, ["payment", "payments", "fintech", "merchant"]
    ):
        warnings.append(
            "Payment industry knowledge may be a weak area. Prepare a concise learning story and avoid claiming direct payments experience unless it is already in the CV."
        )

    if _contains_any(job_ad, ["crm", "salesforce", "hubspot"]) and not _contains_any(
        cv_text, ["crm", "salesforce", "hubspot"]
    ):
        warnings.append(
            "CRM ownership may be tested. Prepare a truthful example about pipeline hygiene, forecasting, notes, or structured follow-up."
        )

    if _contains_any(job_ad, ["matrix", "cross-functional", "product", "consulting", "customer support"]) and not _contains_any(
        cv_text, ["cross-functional", "matrix", "product", "support", "consulting", "stakeholder"]
    ):
        warnings.append(
            "Cross-functional collaboration may need stronger positioning. Prepare a confirmed example involving internal teams and customer outcomes."
        )

    if "stretch" in fit_label.lower() or "gap" in fit_label.lower():
        warnings.append(
            "Treat this as a stretch-fit interview. Prepare clear answers for gaps without exaggerating experience."
        )

    if not warnings:
        warnings.append(
            "No major prep warning detected from available data. Still verify every answer against the original CV before using it."
        )

    return warnings


def build_application_interview_prep(application: Any) -> dict[str, Any]:
    app = _to_dict(application)

    company_name = _extract_company_name(app)
    job_title = _extract_job_title(app)
    job_ad = _extract_job_ad(app)
    fit_label = _extract_fit_label(app)

    tailored_cv = (
        app.get("tailored_cv")
        or app.get("optimized_cv")
        or app.get("accepted_cv")
        or app.get("cv")
        or app.get("candidate_cv")
        or {}
    )
    fit_gap = app.get("fit_gap") or app.get("gap_analysis") or app.get("fit_assessment") or {}
    company_research = app.get("company_research") or app.get("company_profile") or {}

    cv_text = _flatten_text(tailored_cv)
    fit_gap_text = _flatten_text(fit_gap)
    company_text = _flatten_text(company_research)
    all_context = f"{job_ad} {cv_text} {fit_gap_text} {company_text}"

    if not cv_text and not job_ad:
        return {
            "schema_version": "application-interview-prep-v1",
            "scope": "application",
            "status": "skipped",
            "reason": "Missing job ad and CV content.",
            "likely_interviewer_questions": [],
            "candidate_questions_to_ask": [],
            "prep_warnings": ["Interview prep could not be generated because application context is missing."],
        }

    has_payments = _contains_any(job_ad, ["payment", "payments", "merchant", "fintech"])
    has_crm = _contains_any(job_ad, ["crm", "salesforce", "hubspot"])
    has_matrix = _contains_any(job_ad, ["matrix", "cross-functional", "indirect sales", "product", "consulting", "customer support"])
    has_international = _contains_any(job_ad, ["international", "global", "multinational", "travel"])

    evidence_default = "Use only examples already present in the stored or tailored CV. Do not add new claims."

    questions = [
        _make_question(
            f"Walk me through your most relevant experience for the {job_title} role at {company_name}.",
            "This tests whether the candidate can connect their background to this exact role.",
            "Open with the strongest matching experience, then connect it to account ownership, customer outcomes and the company context.",
            evidence_default,
            "low",
        ),
        _make_question(
            "Tell me about a time you managed or developed an important customer/account relationship.",
            "The role requires relationship ownership and customer satisfaction.",
            "Use one concrete account or client example with situation, action and result.",
            "Use confirmed account management, partnership, customer success or stakeholder examples from the CV.",
            "medium",
        ),
        _make_question(
            "How would you build a strategic account plan for an enterprise customer?",
            "The job ad explicitly mentions long-term account plans and sustained growth.",
            "Explain a structured approach: account goals, stakeholders, needs, risks, opportunities, actions and follow-up cadence.",
            evidence_default,
            "medium",
        ),
        _make_question(
            "Describe a complex solution you had to explain or sell to a customer.",
            "The role asks for sales experience with technically complex solutions.",
            "Show how you translated complexity into business value without overclaiming technical depth.",
            "Use product, SaaS, platform, telecom, API, technical or consultative sales examples already in the CV.",
            "medium",
        ),
        _make_question(
            "How do you identify expansion or new sales opportunities inside existing accounts?",
            "The role includes proactively pursuing new opportunities within assigned accounts.",
            "Describe discovery, account signals, stakeholder mapping, pain points and next-step discipline.",
            evidence_default,
            "medium",
        ),
        _make_question(
            "How do you keep CRM records accurate and useful for forecasting?",
            "The job ad highlights disciplined CRM practices.",
            "Give a practical operating rhythm: notes, next steps, opportunity stages, risks, dates and follow-up.",
            "Use confirmed CRM or structured pipeline/process examples. If CRM tool is not named in CV, keep the answer tool-neutral.",
            "medium" if has_crm else "high",
        ),
        _make_question(
            "Tell me about a time you worked with internal teams to solve a customer need.",
            "The role works across Indirect Sales, Product, Consulting and Customer Support.",
            "Use a cross-functional example with the customer problem, internal alignment and outcome.",
            evidence_default,
            "medium" if has_matrix else "high",
        ),
        _make_question(
            "How do you handle a situation where a customer wants something the product or support team cannot immediately deliver?",
            "This tests stakeholder management, expectation-setting and escalation behavior.",
            "Show empathy, clear communication, internal escalation and realistic alternatives.",
            evidence_default,
            "medium",
        ),
        _make_question(
            "Give an example of how you anticipated a customer risk before it became a bigger problem.",
            "The role asks for proactive behavior and anticipation of customer needs and risks.",
            "Use a risk detection story: signal, action, communication and result.",
            evidence_default,
            "medium",
        ),
        _make_question(
            "How do you prepare for a senior client meeting or commercial presentation?",
            "The role includes client meetings, presentations and industry events.",
            "Explain research, agenda, stakeholder goals, value proposition, objections and follow-up.",
            evidence_default,
            "medium",
        ),
        _make_question(
            f"What do you understand about {company_name} and why does this role interest you?",
            "The interviewer will likely test motivation and company understanding.",
            "Connect company mission, role scope and your confirmed experience. Avoid generic praise.",
            "Use company research only if it is available and sourced; otherwise rely on the job ad.",
            "low",
        ),
        _make_question(
            "What would be your learning plan for the first 90 days in this role?",
            "This tests self-awareness, onboarding approach and ability to close domain gaps.",
            "Mention product, customer segments, CRM/pipeline, internal stakeholders, payment industry context and account priorities.",
            evidence_default,
            "medium",
        ),
        _make_question(
            "Tell me about a deal, project or customer situation that did not go as planned.",
            "This tests ownership, resilience and learning mindset.",
            "Use a truthful example focused on what changed in your process afterward.",
            evidence_default,
            "medium",
        ),
        _make_question(
            "How would your previous manager describe your strengths and development areas?",
            "This tests self-awareness and maturity.",
            "Keep it balanced: one strength linked to the role, one development area with mitigation.",
            evidence_default,
            "medium",
        ),
        _make_question(
            "Which part of this role would be the biggest stretch for you?",
            "This directly tests gaps without requiring the interviewer to challenge them indirectly.",
            "Name a real stretch area, then explain how you would close it quickly.",
            "Use fit/gap analysis if available. Do not invent missing experience.",
            "high" if ("stretch" in fit_label.lower() or has_payments) else "medium",
        ),
    ]

    selected_questions = questions[:12]

    if has_payments:
        selected_questions.append(
            _make_question(
                "What is your current understanding of the payments industry and where would you need to learn more?",
                "The job ad asks for deep payment industry understanding.",
                "Be honest about current exposure. Show preparation, learning speed and adjacent experience.",
                "Do not claim deep payments experience unless the CV explicitly supports it.",
                "high",
            )
        )

    if has_international and len(selected_questions) < 15:
        selected_questions.append(
            _make_question(
                "Tell me about your experience working in an international or multinational environment.",
                "The role highlights international mindset and global travel.",
                "Use confirmed experience with international teams, clients, regions, languages or remote collaboration.",
                evidence_default,
                "medium",
            )
        )

    selected_questions = selected_questions[:15]

    candidate_questions = [
        f"What does success look like for the {job_title} role after the first 6 months?",
        "Which account segments or customer types would be the main priority?",
        "How do Sales, Product, Consulting and Customer Support work together on enterprise opportunities?",
        "What are the main risks or growth opportunities in this portfolio today?",
        "Which CRM/process discipline matters most for this team?",
    ]

    return {
        "schema_version": "application-interview-prep-v1",
        "scope": "application",
        "status": "complete",
        "company_name": company_name,
        "job_title": job_title,
        "fit_label": fit_label,
        "question_count": len(selected_questions),
        "likely_interviewer_questions": selected_questions,
        "candidate_questions_to_ask": candidate_questions,
        "prep_warnings": _build_prep_warnings(job_ad, cv_text, fit_label),
        "source_notes": [
            "Generated from application-level context: job title, job ad, tailored CV, fit/gap and company context when available.",
            "Questions are intended as likely interviewer questions, not as final answers.",
            "Candidate must verify all answer examples against the real CV before using them.",
        ],
    }


def _write_prep_to_firestore(application_id: str, prep: dict[str, Any]) -> bool:
    try:
        from firebase_admin import firestore  # type: ignore
    except Exception:
        return False

    try:
        db = firestore.client()
    except Exception:
        return False

    candidate_collections = [
        "applications",
        "cv_applications",
        "job_applications",
        "application_records",
    ]

    for collection_name in candidate_collections:
        try:
            ref = db.collection(collection_name).document(str(application_id))
            snapshot = ref.get()
            if snapshot.exists:
                ref.set(
                    {
                        "interview_prep": prep,
                        "interview_preparation": prep,
                        "application_interview_prep": prep,
                    },
                    merge=True,
                )
                return True
        except Exception:
            continue

    return False


def ensure_application_interview_prep(application: Any) -> dict[str, Any]:
    app = _to_dict(application)

    existing = _existing_interview_prep(app)
    if existing:
        return existing

    prep = build_application_interview_prep(app)

    application_id = _extract_application_id(app)
    if application_id and prep.get("status") == "complete":
        _write_prep_to_firestore(application_id, prep)

    return prep
