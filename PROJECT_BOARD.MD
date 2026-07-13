# Project Board

This document answers one question:

> **What needs to be built, what is being built now, and how do we know when each task is finished?**

It tracks development work, task status, acceptance criteria, test cases and delivery progress.

---

# Board Structure

Questions to answer:

- How is work organized?
- Which statuses are used?
- What does each status mean?

Statuses:

- Backlog
- This Sprint
- In Progress
- Review
- Blocked
- On Hold
- Done

---

# Backlog

Tasks that are planned but not currently being worked on.

Questions to answer:

- Which features are not started yet?
- Which tasks are required for the MVP?
- Which tasks are optional or future improvements?

## TASK-012 — Implement Company Research and Search Grounding

### Status

Backlog

### Goal

Generate reusable company intelligence that helps the user understand the target company and prepare for a stronger interview.

### Description

This task implements the company research pillar of the product.

Based on the company name and ISO2 country code, the system should generate a structured company intelligence report using search-grounded AI.

The report should not be a generic company profile.

It should help the user prepare for a specific job application by explaining:

- what the company does
- which products, services or platforms matter
- who the company serves
- who the company competes with
- what recent events may matter for an interview
- what public employee sentiment suggests, when available
- what risks, limitations or uncertainties should be considered
- which talking points and questions the candidate can use during interview preparation

The report must be reusable.

When the same company is used again, the system should first check Firestore. If a valid company report exists and is less than 3 months old, the stored report should be reused. If no valid report exists, or if the report is older than 3 months, the system should run a new search-grounded company research workflow.

The report must clearly separate verified information from limited, uncertain or unavailable information.

The AI must not invent company facts, customers, financial information, employee sentiment, news or competitors.

### Dependencies

- TASK-010 must be completed.
- Firestore persistence must be available.
- Gemini client must be available.
- Search grounding must be available.
- AI response cleaner and validation flow must be available.
- Company key normalization must be available.

### Subtasks

- [ ] Define company research response model.
- [ ] Define company research validation rules.
- [ ] Add company research prompt with search-grounding instructions.
- [ ] Add strict rules against invented company facts.
- [ ] Add source and limitation requirements to the prompt.
- [ ] Add freshness rule for stored company reports.
- [ ] Implement Firestore lookup by normalized company key.
- [ ] Reuse stored company report when it is valid and less than 3 months old.
- [ ] Regenerate company report when no report exists or when the stored report is older than 3 months.
- [ ] Validate AI output before storing.
- [ ] Store validated company research in the `companies` collection.
- [ ] Store generated timestamp and valid-until timestamp.
- [ ] Add `Companies` section to the left side menu.
- [ ] List saved company reports from newest to oldest.
- [ ] Allow opening a saved company report as a preview.
- [ ] Display company report in a readable interview-preparation format.
- [ ] Connect company research to the main application workflow.
- [ ] Ensure the main workflow can use stored company research without a new grounded AI call.
- [ ] Log cache hits, cache misses, refreshes, validation failures, AI failures and Firestore failures.

### Expected JSON Format

```json
{
  "company_key": "company-name-iso2",
  "display_name": "Company Name - ISO2",
  "country_code": "ISO2",
  "research_status": "complete | limited",
  "confidence_level": "high | medium | low",
  "short_description": "Short factual description of the company.",
  "industry": {
    "primary_industry": "Main industry.",
    "secondary_industries": ["Additional relevant industry."],
    "business_model": "Short factual description of how the company appears to make money."
  },
  "products_and_services": [
    {
      "name": "Product, service or platform name.",
      "type": "product | service | platform | solution | unknown",
      "description": "Short factual description.",
      "why_it_matters_for_interview": "Why this may matter when preparing for the interview."
    }
  ],
  "customers_and_market": {
    "known_public_customers": [
      {
        "name": "Customer name.",
        "context": "Why this customer is relevant."
      }
    ],
    "customer_types": ["Customer segment or type."],
    "target_markets": ["Market, region or segment."],
    "limitations": "Explain if named customers or markets are not public or only partly available."
  },
  "competitors": [
    {
      "name": "Competitor name.",
      "reason": "Why this company is a relevant competitor.",
      "comparison_note": "Short note on how the target company appears different."
    }
  ],
  "recent_developments": [
    {
      "date": "YYYY-MM-DD or YYYY-MM if available",
      "type": "news | acquisition | merger | funding | product | partnership | leadership | financial | other",
      "title": "Development title.",
      "summary": "Short factual summary.",
      "interview_relevance": "Why this may matter for interview preparation."
    }
  ],
  "public_company_information": {
    "is_public_company": true,
    "ticker": "Ticker if available.",
    "exchange": "Exchange if available.",
    "summary": "Short factual summary or limitation.",
    "limitations": "Explain if stock or financial information is not applicable or not available."
  },
  "employee_sentiment": {
    "signal": "positive | mixed | negative | insufficient_public_data",
    "summary": "Short summary of publicly available employee sentiment themes.",
    "positive_themes": ["Publicly reported positive theme."],
    "negative_themes": ["Publicly reported negative theme."],
    "interview_caution": "How the candidate should treat this information carefully.",
    "limitations": "Explain source limitations."
  },
  "interview_intelligence": {
    "talking_points": [
      {
        "topic": "Useful company-specific topic.",
        "why_it_matters": "Why this topic may be useful.",
        "how_to_use": "How the candidate may mention it in an interview."
      }
    ],
    "questions_to_ask": [
      {
        "question": "Question the candidate may ask the interviewer.",
        "reason": "Why this is a useful question."
      }
    ],
    "risks_to_prepare_for": [
      {
        "risk": "Potential concern, uncertainty or business risk.",
        "preparation_note": "How the candidate should prepare for this topic."
      }
    ]
  },
  "sources": [
    {
      "title": "Source title.",
      "url": "Source URL.",
      "publisher": "Publisher or website name.",
      "source_type": "official | news | financial | review | other",
      "supports": ["Which parts of the report this source supports."],
      "accessed_at": "YYYY-MM-DD"
    }
  ],
  "limitations": ["Important limitation, missing data or uncertainty."],
  "generated_at": "ISO datetime",
  "valid_until": "ISO datetime"
}
```

### Acceptance Criteria

- [ ] The system can generate a company research report from a valid company name and ISO2 country code.
- [ ] The system checks Firestore before calling the AI research workflow.
- [ ] A stored report is reused when it is valid and less than 3 months old.
- [ ] A new report is generated when no valid report exists or when the stored report is older than 3 months.
- [ ] The generated report is stored only after validation passes.
- [ ] The report contains at minimum:
  - company key
  - display name
  - country code
  - research status
  - confidence level
  - short description
  - industry
  - products and services
  - customer types or known public customers
  - competitors
  - interview talking points
  - sources
  - generated timestamp
  - valid-until timestamp
- [ ] The report clearly marks unavailable, uncertain or limited information.
- [ ] The report does not invent customers, competitors, employee sentiment, stock information, recent news or company facts.
- [ ] Each important factual section is supported by at least one source or marked as limited.
- [ ] Employee sentiment is treated as a public signal, not as a definitive rating.
- [ ] Employee sentiment is skipped or marked as insufficient when reliable public information is not available.
- [ ] Public-company fields are filled only when the company is actually public.
- [ ] The report includes interview-useful talking points.
- [ ] The report includes useful questions the candidate may ask the interviewer.
- [ ] The report includes risks or uncertainty notes where relevant.
- [ ] Saved company reports are visible from a `Companies` section in the left side menu.
- [ ] Saved company reports can be opened as previews.
- [ ] The main application workflow can use stored company research without making a new grounded AI call.
- [ ] AI failures, invalid output, Firestore failures and limited research results are handled safely.

### Measurements

Success is measured by:

- User can access a company report that is not older than 3 months.
- Stored company research is reused for the same company key.
- Report contains the minimum required company intelligence fields.
- Report is useful for interview preparation, not only general company reading.
- Report includes talking points and questions to ask.
- Report clearly marks limited or unavailable fields.
- Key factual claims can be traced to listed sources or verified through a manual search.
- The system avoids repeated grounded AI calls when a valid stored report exists.
- The user can open saved company reports from the UI.

### Test Cases

- [ ] Normal flow: company is not in Firestore; system generates, validates, stores and displays the report.
- [ ] Cache hit: company exists in Firestore and report is less than 3 months old; system reuses stored report.
- [ ] Refresh flow: company exists in Firestore but report is older than 3 months; system generates a fresh report.
- [ ] Invalid company input is rejected before research starts.
- [ ] AI response with invalid JSON is rejected.
- [ ] AI response with missing required fields is rejected.
- [ ] AI response without sources is rejected unless the report is explicitly marked as limited.
- [ ] AI response with unsupported named customers is rejected where validation can detect it.
- [ ] AI response with public-company information for a private company is rejected where validation can detect it.
- [ ] Employee sentiment is marked as insufficient when reliable public information is unavailable.
- [ ] Company with limited public data produces a limited report instead of fake data.
- [ ] Search grounding failure returns a controlled error.
- [ ] Firestore read failure returns a controlled error.
- [ ] Firestore write failure returns a controlled error.
- [ ] Saved company report can be opened from the `Companies` page.
- [ ] Main application workflow receives stored company research without a new research call.

### Notes

- The report should be short enough to use before an interview.
- The report should not become a long business dossier.
- Customers may not always be public; customer types are acceptable when named customers cannot be verified.
- Competitors should be relevant, not a random list.
- Recent developments should be included only when they are relevant or notable.
- Employee sentiment should be handled carefully because review platforms may be incomplete, biased, outdated or partially inaccessible.
- Direct quotes from sources should be avoided unless short and necessary.
- This task should not include interview-question generation; that belongs to TASK-013.

## TASK-013 — Implement Interview Preparation Generation

### Status

Backlog

### Goal

Generate personalized interview preparation that helps the user defend and explain the tailored CV in the context of the target company and job ad.

### Description

This task implements the third pillar of the product: interview preparation.

Based on the user’s original CV, tailored CV, company research and job advertisement, the AI should generate a practical interview preparation report.

The report should not be a generic list of interview questions.

It should help the user prepare for the specific situation created by the application workflow:

- what the company is likely to care about
- what the job ad emphasizes
- what the tailored CV now highlights
- which parts of the user’s experience can support those claims
- which older, smaller or less recent experience areas need refresh before the interview
- where the user should be careful not to overstate experience

Generic interview themes are allowed only when personalized.

For example, instead of returning a generic “Tell me about yourself” question, the system should provide positioning guidance explaining how the candidate should present their background for this specific role, company and tailored CV.

The interview preparation should also help verify whether the candidate can genuinely support the experience emphasized in the tailored CV.

This is especially important when the CV optimization made older or smaller parts of past experience more visible because they are relevant to the target role.

### Dependencies

- TASK-010 must be completed.
- TASK-012 should be completed first.
- Tailored CV JSON must be available.
- Company research must be available or clearly marked as limited.
- Firestore application records must support the `interview_prep` field.

### Subtasks

- [ ] Define interview preparation response model.
- [ ] Define interview preparation validation rules.
- [ ] Add interview preparation prompt.
- [ ] Include original CV, tailored CV, job ad and company research in the prompt.
- [ ] Add rules that prevent invented experience, achievements, metrics or tools.
- [ ] Add rules that connect questions to evidence from the CV, company research or job ad.
- [ ] Generate 10–15 personalized interview questions.
- [ ] Generate 1–3 suggested answer directions per question.
- [ ] Add candidate positioning guidance for “tell me about yourself” style opening questions.
- [ ] Add preparation notes for emphasized but older, smaller or less recent experience areas.
- [ ] Add warnings where the candidate should avoid overstating experience.
- [ ] Store validated interview preparation in the `interview_prep` field of the application record.
- [ ] Display interview preparation in the application preview.
- [ ] Allow reopening saved interview preparation from `My Applications`.
- [ ] Log AI failures, validation failures and Firestore save failures.

### Expected JSON Format

```json
{
  "interview_prep_id": "application-id-or-generated-id",
  "application_id": "application-id",
  "prep_status": "complete | limited",
  "positioning_guidance": {
    "summary": "How the candidate should position themselves for this specific role.",
    "focus_points": ["Main experience or strength to emphasize."],
    "avoid_overstating": [
      "Area where the candidate should be careful or precise."
    ]
  },
  "questions": [
    {
      "question_id": "q001",
      "category": "cv_experience | job_requirement | company_context | gap_or_risk | behavioral | technical_or_domain | motivation",
      "question": "Personalized interview question.",
      "why_this_matters": "Why this question is likely or useful for this role.",
      "evidence_to_use": [
        "Relevant CV, tailored CV, company research or job-ad evidence."
      ],
      "suggested_answer_directions": [
        {
          "angle": "Possible answer angle.",
          "key_points": ["Point the candidate can mention."],
          "example_focus": "Short guidance for how to frame the answer without inventing facts."
        }
      ],
      "preparation_note": "What the candidate should review before the interview.",
      "risk_level": "low | medium | high"
    }
  ],
  "experience_checkpoints": [
    {
      "emphasized_area": "Skill or experience emphasized in the tailored CV.",
      "supporting_cv_evidence": "Where this is supported in the CV.",
      "likely_follow_up_questions": ["Possible follow-up question."],
      "preparation_needed": "What the candidate should refresh or prepare."
    }
  ],
  "company_specific_talking_points": [
    {
      "topic": "Company-specific topic.",
      "why_relevant": "Why it may matter in the interview.",
      "how_to_use": "How the candidate may mention it."
    }
  ],
  "candidate_questions_to_ask": [
    {
      "question": "Question the candidate can ask the interviewer.",
      "reason": "Why this is useful."
    }
  ],
  "limitations": ["Important limitation, missing data or uncertainty."],
  "generated_at": "ISO datetime"
}
```

### Acceptance Criteria

- [ ] The system generates 10–15 interview questions.
- [ ] Questions are personalized to the CV, tailored CV, job ad and company research.
- [ ] Questions are not duplicated.
- [ ] Generic questions are not returned as generic questions.
- [ ] “Tell me about yourself” is handled as personalized positioning guidance, not as a generic question.
- [ ] Each question includes 1–3 suggested answer directions.
- [ ] Suggested answer directions use only facts supported by the original CV, tailored CV, company research or job ad.
- [ ] The report includes preparation notes for experience that was emphasized in the tailored CV but may be older, smaller or less recent.
- [ ] The report includes warnings where the candidate should avoid overstating experience.
- [ ] The report includes questions that test whether the candidate can genuinely support the tailored CV.
- [ ] The report includes company-specific talking points when company research is available.
- [ ] If company research is limited, the report still works but clearly marks the limitation.
- [ ] The result is stored in Firebase under the application’s `interview_prep` field.
- [ ] Saved interview preparation can be reopened from the application preview.
- [ ] Invalid AI output is rejected before being stored or displayed.

### Measurements

Success is measured by:

- Each report contains 10–15 questions.
- At least one part of the report gives personalized positioning guidance.
- At least one section checks whether the candidate can defend emphasized tailored-CV experience.
- No question is a generic copy-paste interview question without connection to the job, company or CV.
- Each question has clear relevance to at least one of:
  - original CV
  - tailored CV
  - job requirements
  - company research
- Each suggested answer direction avoids invented facts.
- Interview preparation is saved and can be reopened with the application record.

### Test Cases

- [ ] Normal flow: valid application with tailored CV and company research generates, validates, stores and displays interview preparation.
- [ ] Valid application with limited company research still generates interview preparation with limitations marked.
- [ ] Poor-fit application does not generate full tailored interview preparation unless explicitly allowed by later scope.
- [ ] AI response with fewer than 10 questions is rejected.
- [ ] AI response with more than 15 questions is rejected.
- [ ] AI response with duplicated questions is rejected.
- [ ] AI response with generic questions and no personalization is rejected.
- [ ] AI response with invented experience, unsupported tools or unsupported achievements is rejected where validation can detect it.
- [ ] AI response missing suggested answer directions is rejected.
- [ ] AI response missing positioning guidance is rejected.
- [ ] Firestore save failure returns a controlled error.
- [ ] Application preview shows saved interview preparation after reload.
- [ ] Existing application without interview preparation displays a clear empty state or generation option.

### Notes

- Suggested answers should be answer directions, not fake scripts.
- The system must help the user prepare honestly, not memorize invented claims.
- The interview preparation should make the tailored CV safer by exposing areas the user needs to refresh.
- Company-specific content depends on TASK-012 quality.
- This task should not include a full interview simulator or live chat practice.

## TASK-014 — Extend Main Application Contract and Integrate Supporting Features

### Status

Backlog

### Goal

Create one validated application package that connects CV optimization, fit assessment, gap analysis, company research and interview preparation into a single saved workflow result and application preview.

### Description

This task extends the current validated CV optimization contract into a complete application package contract.

The current core workflow already produces:

- role fit assessment
- CV patch
- gap analysis
- warnings

TASK-012 adds reusable company research.

TASK-013 adds personalized interview preparation.

This task connects those outputs without turning the system into one large AI call.

The goal is to keep the workflows modular, but make the saved application result feel complete and consistent to the user.

The application package should answer:

- what role was analyzed
- which company was used
- whether the fit is strong, solid, stretch or poor
- why the candidate received that fit assessment
- which CV version was generated
- which requirements are supported by the CV
- which requirements are reasonably derived from existing experience
- which requirements remain unsupported
- what preparation or interview guidance follows from those gaps
- what company research was used
- what interview preparation was generated
- which parts are complete, limited, missing or failed
- which schema, prompt and model versions produced the result

This task is an extension of the earlier response-model and validation work.

It should update the application-level models, validation rules, storage format and UI integration so that all core and supporting outputs are part of the same saved application record instead of disconnected outputs.

The task must preserve the existing product rules:

- poor fit stops CV tailoring
- draft CV can be revised
- accepted CV enables PDF download
- fit assessment is always shown
- gap analysis is shown for both poor-fit and acceptable-fit applications
- company research and interview preparation must be validated before display or storage

### Dependencies

- TASK-006 must be completed.
- TASK-010 must be completed.
- TASK-012 should be completed first.
- TASK-013 should be completed first.
- Firestore application persistence must be available.
- Existing CV optimization validation must remain active.

### Subtasks

- [ ] Review the current CV optimization response model.
- [ ] Review the current saved application model.
- [ ] Define the complete application package model.
- [ ] Add company research reference or snapshot fields to the application record.
- [ ] Add interview preparation fields to the application record.
- [ ] Add supporting-feature status fields.
- [ ] Add prompt-version metadata for each workflow.
- [ ] Add model-version metadata for each workflow.
- [ ] Add generated-at timestamps for each supporting feature.
- [ ] Update application validation rules.
- [ ] Keep backward compatibility for older saved application records where possible.
- [ ] Update Firestore save and update logic.
- [ ] Update Firestore load and list logic.
- [ ] Update the main application orchestration flow.
- [ ] Ensure company research can be reused from Firestore.
- [ ] Ensure interview preparation uses the validated CV, job ad and company research.
- [ ] Ensure poor-fit applications do not generate a misleading tailored interview preparation package.
- [ ] Add fit assessment panel to the application preview.
- [ ] Add gap analysis panel to the application preview.
- [ ] Show supported requirements from gap analysis.
- [ ] Show reasonably derived requirements from gap analysis.
- [ ] Show unsupported requirements from gap analysis.
- [ ] Show preparation recommendations for unsupported requirements.
- [ ] Show interview guidance for unsupported requirements.
- [ ] Reuse the same fit and gap display components for poor-fit and acceptable-fit applications where possible.
- [ ] Update the application preview UI to show company research and interview preparation when available.
- [ ] Add clear empty, limited or failed states for supporting features.
- [ ] Ensure accepted CV PDF generation remains unchanged.
- [ ] Add automated tests for the complete application package contract.
- [ ] Add tests for fit assessment and gap analysis rendering.
- [ ] Add tests for old records, partial records and invalid supporting-feature output.
- [ ] Log integration failures, validation failures and partial-result states.

### Expected JSON Format

```json
{
  "application_id": "application-id",
  "profile_id": "profile-id",
  "company_key": "company-name-iso2",
  "job_title": "Target job title",
  "job_ad_hash": "hash-of-job-ad",
  "status": "draft | accepted",
  "fit_assessment": {
    "level": "strong | solid | stretch | poor",
    "explanation": "Fit explanation.",
    "relevant_experience": ["Relevant experience supported by the CV."],
    "missing_requirements": ["Missing requirement."]
  },
  "tailored_cv": {
    "profile_id": "profile-id",
    "cv_version": "cv-version",
    "personal_info": {},
    "professional_summary": "Tailored summary.",
    "core_skills": [],
    "professional_experience": [],
    "projects": [],
    "education": [],
    "languages": [],
    "tools_and_technologies": []
  },
  "gap_analysis": {
    "supported_requirements": ["Supported requirement."],
    "reasonably_derived_requirements": ["Reasonably derived requirement."],
    "unsupported_requirements": [
      {
        "requirement": "Unsupported requirement.",
        "impact": "low | medium | high",
        "preparation_recommendation": "Preparation recommendation.",
        "interview_guidance": "Interview guidance."
      }
    ]
  },
  "company_research": {
    "status": "not_started | complete | limited | failed",
    "company_key": "company-name-iso2",
    "research_snapshot": "CompanyResearchReport or null",
    "generated_at": "ISO datetime or null",
    "valid_until": "ISO datetime or null",
    "prompt_version": "company-research-prompt-version or null",
    "model_version": "model version or null",
    "error_message": "User-safe error message or null"
  },
  "interview_prep": {
    "status": "not_started | complete | limited | failed | skipped",
    "prep_snapshot": "InterviewPreparationReport or null",
    "generated_at": "ISO datetime or null",
    "prompt_version": "interview-prep-prompt-version or null",
    "model_version": "model version or null",
    "error_message": "User-safe error message or null"
  },
  "workflow_status": {
    "cv_optimization": "complete | failed",
    "fit_assessment": "complete | failed",
    "gap_analysis": "complete | failed",
    "company_research": "not_started | complete | limited | failed",
    "interview_prep": "not_started | complete | limited | failed | skipped",
    "pdf_export": "blocked | available"
  },
  "metadata": {
    "base_cv_version": "cv-version",
    "schema_version": "application-schema-version",
    "cv_prompt_version": "cv-optimization-prompt-version",
    "revision_prompt_version": "revision-prompt-version or null",
    "created_at": "ISO datetime",
    "updated_at": "ISO datetime",
    "accepted_at": "ISO datetime or null"
  }
}
```

### UI Preview Requirements

The application preview should show the saved application as one coherent package.

For acceptable-fit applications, the preview should include:

- fit assessment
- gap analysis
- review controls
- tailored CV preview
- company research when available
- interview preparation when available
- PDF download after CV acceptance

For poor-fit applications, the preview should include:

- fit assessment
- missing requirements
- gap analysis
- preparation recommendations
- interview guidance for gaps
- company research when available
- no tailored CV preview
- no CV acceptance flow
- no final CV PDF download

Fit assessment should show:

- fit level
- explanation
- relevant experience
- missing requirements

Gap analysis should show:

- supported requirements
- reasonably derived requirements
- unsupported requirements
- impact level for unsupported requirements
- preparation recommendation
- interview guidance

Company research and interview preparation should show clear states:

- not started
- complete
- limited
- failed
- skipped

### Acceptance Criteria

- [ ] A complete application package model exists.
- [ ] The model includes CV optimization, fit assessment, gap analysis, company research and interview preparation.
- [ ] The model preserves the existing poor-fit rule.
- [ ] Poor-fit applications must not contain a tailored CV.
- [ ] Acceptable-fit applications must contain a tailored CV.
- [ ] Fit assessment is visible in the application preview.
- [ ] Gap analysis is visible in the application preview.
- [ ] Fit assessment display includes level, explanation, relevant experience and missing requirements.
- [ ] Gap analysis display includes supported requirements, reasonably derived requirements and unsupported requirements.
- [ ] Unsupported requirements display impact, preparation recommendation and interview guidance.
- [ ] Poor-fit display behavior remains valid but should reuse fit and gap display components where possible.
- [ ] Company research can be attached as a validated snapshot or validated reference.
- [ ] Interview preparation can be attached as a validated snapshot.
- [ ] Supporting features have clear statuses: `not_started`, `complete`, `limited`, `failed` or `skipped`.
- [ ] Invalid company research is not stored inside the application package.
- [ ] Invalid interview preparation is not stored inside the application package.
- [ ] Existing draft and accepted CV behavior remains unchanged.
- [ ] Draft applications still allow revisions.
- [ ] Accepted applications still allow direct PDF download.
- [ ] The application preview shows CV, fit assessment, gap analysis, company research and interview preparation when available.
- [ ] The application preview clearly shows when a supporting feature is limited, missing, failed or skipped.
- [ ] Firestore records include prompt and model version metadata for each workflow.
- [ ] Old saved application records without company research or interview preparation can still load, or fail safely with a clear migration note.
- [ ] The main application workflow can produce a complete package without merging all AI work into one prompt.
- [ ] No unvalidated AI output is displayed or stored.

### Measurements

Success is measured by:

- A saved application can be reopened and shows all available validated outputs.
- Fit assessment is visible without needing to inspect Firestore or logs.
- Gap analysis is visible without needing to inspect Firestore or logs.
- CV optimization still works exactly as before.
- Company research can be reused through the application package.
- Interview preparation is connected to the correct application.
- Supporting feature status is visible and understandable.
- Failed or limited supporting features do not corrupt the main CV result.
- Existing PDF export behavior still works after the contract extension.
- Stored records contain enough metadata to understand which prompt and model generated each part.

### Test Cases

- [ ] Existing acceptable-fit application with only CV optimization still loads.
- [ ] Existing poor-fit application still loads and does not contain a tailored CV.
- [ ] New application package with CV optimization only validates.
- [ ] New application package with CV optimization and company research validates.
- [ ] New application package with CV optimization, company research and interview preparation validates.
- [ ] Poor-fit application with tailored CV is rejected.
- [ ] Acceptable-fit application without tailored CV is rejected.
- [ ] Application with missing fit assessment is rejected.
- [ ] Application with missing gap analysis is rejected.
- [ ] Application with invalid company research snapshot is rejected.
- [ ] Application with invalid interview preparation snapshot is rejected.
- [ ] Application with failed company research status and no snapshot validates.
- [ ] Application with limited company research status and valid limitation notes validates.
- [ ] Application with skipped interview preparation for poor fit validates.
- [ ] Fit assessment panel renders for acceptable-fit application.
- [ ] Fit assessment panel renders for poor-fit application.
- [ ] Gap analysis panel renders supported requirements.
- [ ] Gap analysis panel renders reasonably derived requirements.
- [ ] Gap analysis panel renders unsupported requirements.
- [ ] Gap analysis panel renders preparation recommendations and interview guidance.
- [ ] Firestore save failure returns a controlled error.
- [ ] Firestore load failure returns a controlled error.
- [ ] Application preview displays available supporting features.
- [ ] Application preview displays empty state when supporting features are not started.
- [ ] Accepted CV PDF download still works after the model changes.
- [ ] Draft CV PDF download is still blocked after the model changes.

### Notes

- This task should not combine all AI workflows into one large prompt.
- The purpose is integration, contract consistency and preview completeness, not prompt consolidation.
- Fit assessment and gap analysis are already core outputs and must be displayed before adding more supporting features.
- Company research remains reusable company-level data.
- Interview preparation remains application-specific data.
- The application record may store a company research snapshot to preserve what was used at the time of preparation.
- If storage size becomes a concern, the snapshot/reference decision can be reviewed later.
- This task should be implemented carefully because it touches models, Firestore records, UI preview and workflow orchestration.

## TASK-015 — Test Complete Workflow, Edge Cases and Failure Handling

### Status

Backlog

### Goal

What should this task achieve and why is it needed?

### Description

What is included in this task?

What is explicitly not included?

### Dependencies

Which tasks or decisions must be completed first?

### Subtasks

- [ ] Subtask 1
- [ ] Subtask 2
- [ ] Subtask 3

### Acceptance Criteria

- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

### Measurements

How will success be measured?

- Metric 1
- Metric 2

### Test Cases

- [ ] Normal flow
- [ ] Invalid input
- [ ] Expected failure
- [ ] Relevant edge case

### Notes

Only include risks, open questions or important implementation constraints.

## TASK-016 — Prepare Docker and Production Deployment

### Status

Backlog

### Goal

What should this task achieve and why is it needed?

### Description

What is included in this task?

What is explicitly not included?

### Dependencies

Which tasks or decisions must be completed first?

### Subtasks

- [ ] Subtask 1
- [ ] Subtask 2
- [ ] Subtask 3

### Acceptance Criteria

- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

### Measurements

How will success be measured?

- Metric 1
- Metric 2

### Test Cases

- [ ] Normal flow
- [ ] Invalid input
- [ ] Expected failure
- [ ] Relevant edge case

### Notes

Only include risks, open questions or important implementation constraints.

## TASK-017 — Finalize Documentation and Conduct Project Review

### Status

Backlog

### Goal

What should this task achieve and why is it needed?

### Description

What is included in this task?

What is explicitly not included?

### Dependencies

Which tasks or decisions must be completed first?

### Subtasks

- [ ] Subtask 1
- [ ] Subtask 2
- [ ] Subtask 3

### Acceptance Criteria

- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

### Measurements

How will success be measured?

- Metric 1
- Metric 2

### Test Cases

- [ ] Normal flow
- [ ] Invalid input
- [ ] Expected failure
- [ ] Relevant edge case

### Notes

Only include risks, open questions or important implementation constraints.

## TASK-019 — Implement CV-First Inline Review and Granular Change Requests

### Status

Backlog

### Goal

Redesign the review experience so the CV is the primary screen and AI-suggested changes can be reviewed, accepted, kept or revised inline before final acceptance.

### Description

This task improves the human-in-the-loop review flow.

The current workflow allows the user to request changes at broad section level after a tailored CV has already been generated.

That is functional for the MVP, but it is not the ideal review experience.

The user should not experience the AI result as a black box.

The application should show the current CV as the primary page and display AI-suggested changes directly next to the relevant original CV content.

The user should be able to understand:

- what the original CV said
- what the AI changed
- why the change may be useful
- whether the change is safe and accurate
- whether to accept the suggestion
- whether to keep the original text
- whether to request a targeted revision

The broad `Professional experience` revision box should be replaced by a more granular review flow.

Instead of one large comment box for the full experience section, the user should be able to review and comment on smaller editable elements, such as:

- professional summary
- core skills
- individual responsibility bullets
- key achievement bullets
- AI & Technical Projects
- Tools and Technologies

The goal is not to make the UI visually complex.

The goal is to make AI changes transparent, reviewable and safer before the user accepts the final CV.

This task should preserve the existing draft/accepted flow:

- generated CV starts as draft
- draft CV can be revised
- accepted CV enables PDF download
- final PDF export remains available only after acceptance

### Dependencies

- TASK-010 must be completed.
- TASK-014 should be completed first.
- Existing CV preview must be available.
- Existing revision workflow must be available.
- Existing draft and accepted application statuses must remain active.
- Existing direct PDF export must remain active.

### Subtasks

- [ ] Make the CV view the default landing page.
- [ ] Move optimization input into the side menu or a clearly separated side panel.
- [ ] Keep `My Applications` accessible from the left side menu.
- [ ] Keep `Companies` accessible from the left side menu if TASK-012 has been implemented.
- [ ] Remove or de-emphasize the `Your CV is ready` modal as the main transition.
- [ ] After optimization, route the user directly to the CV review view.
- [ ] Display original CV content and AI-suggested content inline where possible.
- [ ] Add inline review UI for professional summary.
- [ ] Add inline review UI for core skills.
- [ ] Add inline review UI for responsibility bullets.
- [ ] Add inline review UI for key achievement bullets.
- [ ] Add inline review UI for AI & Technical Projects.
- [ ] Add inline review UI for Tools and Technologies.
- [ ] Add per-element actions: accept suggestion, keep original, request change.
- [ ] Add comment input only for the selected element being revised.
- [ ] Avoid one large textbox for the full professional experience section.
- [ ] Store review choices in session state or draft review state.
- [ ] Apply accepted suggestions into the current draft CV.
- [ ] Preserve original content when the user chooses to keep original text.
- [ ] Send targeted revision requests only for selected editable elements.
- [ ] Extend revision request models if current section-level model is not granular enough.
- [ ] Extend validation so revised output can only change the selected editable element or allowed related patch field.
- [ ] Ensure unreviewed or rejected AI suggestions are not silently included in the accepted CV.
- [ ] Keep `Accept CV` disabled or clearly risky until required review choices are resolved.
- [ ] Preserve existing PDF download behavior after acceptance.
- [ ] Add empty states for fields that do not have AI suggestions.
- [ ] Add visual distinction between original content, AI suggestion and accepted content.
- [ ] Add logging for review decisions and targeted revision failures.
- [ ] Add automated tests for review state and merge behavior where possible.
- [ ] Add manual UI test checklist for inline review interactions.

### Expected Review State Format

```json
{
  "application_id": "application-id",
  "review_status": "not_started | in_progress | ready_to_accept | accepted",
  "items": [
    {
      "item_id": "summary",
      "item_type": "professional_summary",
      "source_section": "professional_summary",
      "source_reference": "summary",
      "original_value": "Original CV text.",
      "suggested_value": "AI-suggested text.",
      "current_value": "Currently selected text.",
      "decision": "pending | accepted_suggestion | kept_original | revised",
      "user_comment": "Optional user comment for targeted revision.",
      "revision_status": "not_requested | pending | complete | failed",
      "last_updated_at": "ISO datetime or null"
    },
    {
      "item_id": "experience_001_responsibility_001",
      "item_type": "responsibility_bullet",
      "source_section": "professional_experience",
      "source_reference": "experience_001",
      "original_value": "Original responsibility bullet.",
      "suggested_value": "AI-suggested responsibility bullet.",
      "current_value": "Currently selected bullet.",
      "decision": "pending | accepted_suggestion | kept_original | revised",
      "user_comment": "Optional user comment for targeted revision.",
      "revision_status": "not_requested | pending | complete | failed",
      "last_updated_at": "ISO datetime or null"
    }
  ],
  "accepted_cv_snapshot": "CVProfile or null",
  "created_at": "ISO datetime",
  "updated_at": "ISO datetime"
}
```

### UI Requirements

The main screen should prioritize the CV.

The side menu should contain:

- optimize CV input
- My Applications
- Companies, if available
- navigation to saved results

The review view should show:

- current CV content
- AI suggestions inline
- review state per editable item
- request-change controls only where they are relevant
- fit assessment and gap analysis if TASK-014 has been completed
- company research and interview preparation if available

For each editable item, the UI should support:

- viewing original content
- viewing AI suggestion
- accepting AI suggestion
- keeping original content
- requesting a revision with a targeted comment
- showing revision success or failure

### Acceptance Criteria

- [ ] The app can open with the CV as the primary view.
- [ ] Optimization input is available from the side menu or side panel.
- [ ] The user can start optimization without leaving the CV-first flow.
- [ ] After optimization, the user is taken to the CV review view without relying on a success modal.
- [ ] The user can see original CV content and AI-suggested content together.
- [ ] Professional summary suggestions can be reviewed inline.
- [ ] Core skills suggestions can be reviewed inline.
- [ ] Responsibility bullet suggestions can be reviewed inline.
- [ ] Key achievement bullet suggestions can be reviewed inline.
- [ ] AI & Technical Projects can be reviewed or commented on inline.
- [ ] Tools and Technologies can be reviewed or commented on inline.
- [ ] The broad full-section `Professional experience` comment box is removed or replaced by granular controls.
- [ ] The user can accept a suggestion for an individual editable item.
- [ ] The user can keep the original value for an individual editable item.
- [ ] The user can request a targeted revision for an individual editable item.
- [ ] Targeted revision does not change unrelated CV content.
- [ ] Review choices are preserved during the draft review session.
- [ ] Accepted CV is built only from accepted suggestions, kept originals and completed revisions.
- [ ] Draft CV remains editable until the user accepts it.
- [ ] Accepted CV still enables direct PDF download.
- [ ] Draft CV still blocks PDF download.
- [ ] My Applications still works after the UI redesign.
- [ ] Existing saved applications can still be opened.
- [ ] Fit assessment and gap analysis remain visible if TASK-014 has been implemented.
- [ ] The UI remains simple and readable.

### Measurements

Success is measured by:

- User can understand what AI changed without comparing raw JSON or separate pages.
- User can review individual CV changes instead of commenting on broad sections.
- User can keep original content where AI suggestion is not preferred.
- User can request changes to specific bullets or fields.
- Final accepted CV does not include unreviewed or rejected suggestions.
- Existing draft/accepted/PDF behavior remains intact.
- The review flow feels transparent rather than black-box.

### Test Cases

- [ ] App opens with CV-first view.
- [ ] User opens optimization form from side menu.
- [ ] User completes optimization and is routed to inline review view.
- [ ] Professional summary suggestion appears next to original summary.
- [ ] User accepts professional summary suggestion.
- [ ] User keeps original professional summary.
- [ ] User requests revision for professional summary.
- [ ] Responsibility bullet suggestion appears next to original bullet.
- [ ] User accepts one responsibility bullet and keeps another original bullet.
- [ ] User requests revision for one responsibility bullet; unrelated bullets remain unchanged.
- [ ] Key achievement bullet can be reviewed or commented on.
- [ ] AI & Technical Projects section can be reviewed or commented on.
- [ ] Tools and Technologies section can be reviewed or commented on.
- [ ] Unrequested AI changes are rejected by validation.
- [ ] Review state survives rerun during the same draft session.
- [ ] Accepted CV contains only selected final values.
- [ ] Draft PDF download remains blocked.
- [ ] Accepted PDF download remains available.
- [ ] Saved application opens correctly from My Applications.
- [ ] Existing application without review-state data opens safely.
- [ ] Revision failure shows a clear error and does not corrupt the draft CV.

### Notes

- This is a UX and review-safety task, not a visual redesign task.
- The UI should remain simple.
- The task may require extending the current revision model beyond broad sections.
- The task should not weaken factual validation.
- The task should not allow AI to invent new experience, tools, metrics or achievements.
- This task should not include company research or interview preparation generation.
- Company research and interview preparation may be displayed if already available, but they are not generated by this task.
- If the task becomes too large, it may be split into:
  - CV-first layout
  - inline comparison display
  - granular review decisions
  - granular targeted revisions

# This Sprint

# In Progress

Tasks currently being implemented.

Questions to answer:

- What is actively being built?
- Who or what is blocking progress?
- What still needs to be tested?

# Review

Tasks that are implemented but not yet accepted.

Questions to answer:

- Does the feature work as expected?
- Are acceptance criteria met?
- Were edge cases tested?
- Is documentation updated?

---

# Blocked

Tasks that cannot continue until something is resolved.

Questions to answer:

- What is blocking the task?
- Who needs to resolve it?
- What decision or dependency is missing?

---

# On Hold

Tasks intentionally paused or postponed.

Questions to answer:

- Why is this task paused?
- What needs to happen before it continues?
- Is this still part of the MVP?

## TASK-011 — Perform Project Refactoring and Architecture Review

### Status

On Hold

### Goal

What should this task achieve and why is it needed?

### Description

What is included in this task?

What is explicitly not included?

### Dependencies

Which tasks or decisions must be completed first?

### Subtasks

- [ ] Subtask 1
- [ ] Subtask 2
- [ ] Subtask 3

### Acceptance Criteria

- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

### Measurements

How will success be measured?

- Metric 1
- Metric 2

### Test Cases

- [ ] Normal flow
- [ ] Invalid input
- [ ] Expected failure
- [ ] Relevant edge case

### Notes

Only include risks, open questions or important implementation constraints.

---

# Done

Completed and accepted tasks.

Questions to answer:

- What was delivered?
- What was tested?
- Are there any follow-up tasks?

## TASK-001 — Initialize Project Structure and Development Environment

### Status

Done

### Goal

Create a stable, clean and repeatable development environment for the project.

The project should be ready for feature development without repository, interpreter, dependency or configuration issues.

### Description

This task includes:

- creating and configuring the Git repository
- creating the local project folder
- adding the initial project documentation
- creating the planned folder and file structure
- creating and activating a Python virtual environment
- adding the initial required dependencies
- preparing environment variable handling
- configuring `.gitignore`
- verifying the Python interpreter and installed packages
- completing the initial commit and push

This task does not include any product feature development.

### Dependencies

None — this is the first implementation task.

### Subtasks

- [x] Create the GitHub repository.
- [x] Create the local project folder.
- [x] Initialize Git and connect the local repository to GitHub.
- [x] Create `.gitignore`.
- [x] Ensure `.venv`, `.env`, cache files and local IDE files are excluded from Git.
- [x] Add the initial project documentation:
  - [x] `README.md`
  - [x] `PROJECT_SCOPE.md`
  - [x] `ARCHITECTURE.md`
  - [x] `PROJECT_BOARD.md`
  - [x] `DECISIONS.md`

- [x] Create the initial planned folder structure.
- [x] Create the Python virtual environment.
- [x] Activate the virtual environment.
- [x] Configure the correct Python interpreter.
- [x] Create `requirements.txt`.
- [x] Add only the initial dependencies currently required.
- [x] Install dependencies from `requirements.txt`.
- [x] Create `.env.example`.
- [?] Create a local `.env` file if environment variables are already required.
- [x] Verify that installed packages can be imported.
- [x] Commit and push the initial project setup.

### Acceptance Criteria

- The GitHub repository exists and is connected to the local repository.
- The initial project folder structure exists.
- The Python virtual environment can be created and activated.
- The correct Python interpreter is selected.
- `pip install -r requirements.txt` completes without errors.
- Initial package imports complete without errors.
- The following documents exist:
  - [ ] `README.md`
  - [ ] `PROJECT_SCOPE.md`
  - [ ] `ARCHITECTURE.md`
  - [ ] `PROJECT_BOARD.md`
  - [ ] `DECISIONS.md`

- `.gitignore` excludes `.venv`, `.env`, cache files and local IDE files.
- `.env.example` exists.
- No secrets or local environment files are tracked by Git.
- The initial commit and push complete successfully.
- No product feature has been implemented as part of this task.

### Measurements

- `pip install -r requirements.txt` succeeds with zero errors.
- Initial package imports succeed with zero errors.
- `git status` does not show `.venv`, `.env` or other excluded local files.
- Initial commit and push complete without errors.
- All required initial documentation files are present.
- The development environment can be restarted without manual repair.

### Test Cases

- [x] Activate the virtual environment from a new terminal session.
- [x] Run `pip install -r requirements.txt`.
- [x] Import the initial installed packages.
- [x] Run `git status` and verify that excluded files are not tracked.
- [x] Verify that `.env.example` is committed and `.env` is not committed.
- [x] Commit a small documentation change and push it successfully.
- [x] Close and reopen the project and verify that the correct interpreter can be selected again.

### Notes

Dependencies should be added gradually as they become necessary.

The project should not install speculative packages that are not yet used.

## TASK-002 — Define CV Data Model and Build Initial Streamlit Input Flow

### Status

Done

### Goal

This task produces the main CV input for the application.

### Description

The user’s CV will be examined and a decision will be made about which parts should be kept.

The most appropriate CV format will be selected, the approved data will be stored as structured JSON, and the final output of the task will be an initial Streamlit CV page.

### Dependencies

TASK-001 must be completed first.

### Subtasks

- [x] Review the current CV and agree on which sections and information will be kept.
- [x] Select an ATS-friendly CV format.
- [x] Define the structured JSON model for the CV.
- [x] Create and populate `cv_data/cv_sale.json`.
- [x] Create a validation model for the CV data.
- [x] Create the initial Streamlit page.
- [x] Load the CV data from the JSON file.
- [x] Render the agreed CV sections on the page.
- [x] Add basic screen and print styling.
- [x] Handle a missing or invalid CV data file.
- [x] Confirm that CV content is not hardcoded inside the Streamlit page.

### Acceptance Criteria

- [ ] CV format selected.
- [ ] User’s CV examined and data selected.
- [ ] CV data stored as structured JSON.
- [ ] Static Streamlit page created.
- [ ] Streamlit page loads the CV from the JSON file.

### Measurements

- Streamlit page exists.
- Page can be launched via terminal.
- Web version of the CV contains the agreed data.
- When saved as PDF, the CV is a maximum of two pages long.

### Test Cases

- [x] Normal flow — user runs the command via terminal and the webpage loads the complete CV from the JSON file.

### Notes

- This task includes only the first CV profile.
- Svetlana’s CV and profile selection are not included.
- Final PDF styling can be improved in a later task if the document is already readable and usable.

## TASK-003 — Implement FastAPI Backend Foundation, Configuration and Logging

### Status

Done

### Goal

This task should produce the necessary technical foundation for the rest of the project.

### Description

The following will be implemented:

- FastAPI backend foundation
- `config.py` containing the main application configuration
- basic logging logic
- root endpoint for confirming that the backend is running

### Dependencies

TASK-002 must be completed first.

### Subtasks

- [x] **3.1** Add FastAPI and Uvicorn to `requirements.txt` and install them.
- [x] **3.2** Create `config.py` with the initial application settings.
- [x] **3.3** Create `logger.py` and configure basic application logging.
- [x] **3.4** Initialize the FastAPI application in `api.py`.
- [x] **3.5** Create the root endpoint.
- [x] **3.6** Add logging to application startup and the root endpoint.
- [x] **3.7** Confirm that `config.py` and `logger.py` can be imported successfully.
- [x] **3.8** Run the backend and complete the defined test cases.

### Acceptance Criteria

- [ ] `api.py` is created and the FastAPI application is initialized.
- [ ] Root endpoint is created.
- [ ] `config.py` is created and imported successfully.
- [ ] `logger.py` is created and imported successfully.
- [ ] Application startup is logged.
- [ ] Requests to the root endpoint are logged.
- [ ] The backend starts without import or runtime errors.
- [ ] Undefined endpoints return `404 Not Found`.

### Measurements

- Application starts without import or runtime errors.
- Root endpoint returns the expected response.
- Request to the root endpoint creates the expected log entry.
- Application startup creates the expected log entry.
- Invalid endpoint returns `404 Not Found`.

### Test Cases

- [x] Normal flow — user starts the FastAPI application from the terminal and the root endpoint returns the expected response.
- [x] Normal flow — application startup and root request are logged.
- [x] Invalid endpoint — request to an undefined endpoint returns `404 Not Found`.
- [x] Import test — `config.py`, `logger.py` and `api.py` import without errors.

### Notes

- API authentication, request contracts and rate limiting belong to TASK-004.
- Advanced logging configuration and external monitoring are outside this task.

## TASK-004 — Define API Request Contracts and Protect Backend Endpoints

### Status

Done

### Goal

Ensure the stability and security of the application by standardizing API requests and applying a protective layer.

### Description

With this task, we will define the request contract for each planned protected endpoint.

Furthermore, we will use an API key to protect access to the backend and apply rate limiting to prevent request flooding.

### Dependencies

TASK-003 must be completed first.

### Subtasks

- [x] Define Pydantic request models for the planned protected endpoints.
- [x] Add request validation to reject missing or invalid fields.
- [x] Add API key configuration through environment variables.
- [x] Create reusable API key authentication logic.
- [x] Apply API key protection to protected endpoints.
- [x] Add rate-limiting configuration.
- [x] Apply rate limiting to protected endpoints.
- [x] Return structured error responses for authentication, validation and rate-limit failures.
- [x] Add logging for rejected authentication and rate-limit requests.
- [x] Confirm that secrets are not hardcoded or committed to Git.

### Acceptance Criteria

- [ ] Each planned protected endpoint has a defined request contract.
- [ ] Requests with an invalid contract are rejected.
- [ ] Protected endpoints require a valid API key.
- [ ] The API key is stored securely through environment variables.
- [ ] The API key is not hardcoded or committed to Git.
- [ ] Rate limiting is applied to protected endpoints.
- [ ] Missing or invalid API keys return an access-denied response.
- [ ] Exceeding the rate limit returns a clear rate-limit response.

### Measurements

- Valid requests are accepted.
- Invalid request payloads are rejected with a validation error.
- Missing or invalid API keys are rejected.
- A valid API key allows access.
- Requests exceeding the configured limit are rejected.
- API secrets do not exist in tracked repository files.

### Test Cases

- [ ] Normal flow — a request with a valid payload and valid API key is accepted.
- [ ] Invalid payload — a request that does not match the request contract is rejected.
- [ ] Missing API key — access is denied.
- [ ] Invalid API key — access is denied.
- [ ] Rate limit exceeded — additional requests are rejected with a rate-limit error.

### Notes

- Root or health-check endpoints may remain unprotected if required for deployment monitoring.
- Exact rate limits will be agreed during technical implementation.

## TASK-018 — Implement Firebase Persistence for Job Applications and Company Research

### Status

Done

### Goal

This task will allow us to save and read polished CV results and company information in Firebase.

### Description

In this task, we will define the logic for saving and reading CV application results and company information in Firebase, making them accessible later and avoiding additional workflow runs when reusable data already exists.

### Dependencies

TASK-004 must be completed first.

### Subtasks

- [x] Create and configure a Firebase project with Firestore enabled.
- [x] Configure Firebase Admin SDK credentials for backend access.
- [x] Store credentials in the repository which is not commited and load their location through environment configuration.
- [x] Create `firebase.py`.
- [x] Initialize the Firestore client.
- [x] Create `firebase.py`.
- [x] Create storage logic for the `companies` collection.
- [x] Create storage logic for the `applications` collection.
- [x] Add functions for saving and reading company records.
- [x] Add functions for saving and reading application records.
- [x] Use the normalized company key as the company document ID.
- [x] Generate a unique ID for each application record.
- [x] Add creation and update timestamps.
- [x] Use `Europe/Amsterdam` when displaying stored timestamps.
- [x] Validate records before saving and after reading.
- [x] Implement timeout handling.
- [x] Implement a maximum of three total attempts for retryable failures.
- [x] Log important read, write, retry and failure events.
- [x] Confirm that Firebase credentials are not committed to Git.

### Acceptance Criteria

- [ ] A Firebase project with Firestore is created.
- [ ] `firebase.py` is created.
- [ ] Backend credentials are configured securely and are not stored in the repository.
- [ ] Firestore contains the `companies` and `applications` collections.
- [ ] Company information can be saved and read using a normalized company key.
- [ ] Application results can be saved and read using a unique application ID.
- [ ] Existing company records are reused instead of creating duplicates.
- [ ] Records contain creation and update timestamps.
- [ ] Stored timestamps can be displayed using the `Europe/Amsterdam` timezone.
- [ ] Invalid records are rejected.
- [ ] Stored records are validated before reuse.
- [ ] Timeout errors are handled.
- [ ] Retryable failures allow a maximum of three total attempts.
- [ ] Important operations and failures are logged.

### Measurements

- Firebase credentials are configured securely and are not committed.
- A company record can be saved and read successfully.
- An application record can be saved and read successfully.
- Each application record has a unique ID.
- Existing companies are not duplicated.
- Timeout and retry errors are handled and logged.
- Stored timestamps are displayed in the Amsterdam timezone.

### Test Cases

- [x] Normal flow — a company record is saved and successfully read using its company key.
- [x] Normal flow — an application record is saved with a unique ID and successfully read.
- [x] Invalid input — a record missing mandatory fields is rejected.
- [x] Expected failure — missing or invalid Firebase credentials produce a controlled and logged error.
- [x] Expected failure — a timeout or retryable connection failure stops after three total attempts and is logged.
- [x] Expected failure — reading a nonexistent document returns a controlled not-found result.
- [x] Relevant edge case — an existing company record is reused instead of creating a duplicate.
- [x] Relevant edge case — malformed stored data is rejected before reuse.

### Notes

- Firestore access must only go through the FastAPI backend.
- The Streamlit frontend must not access Firestore directly.
- The MVP does not include user accounts.
- Credentials must not be stored in a committed `secrets` folder.

## TASK-005 — Integrate Gemini Client, Prompt Configuration and Retry Logic

### Status

Done

### Goal

Integrate Gemini as the AI provider and create a reusable client foundation for future AI workflows.

### Description

The following will be implemented:

- Gemini API client configuration
- model configuration
- prompt instructions
- maximum output token configuration
- request timeout
- retry logic with a maximum of three total attempts
- logging and controlled failure handling

This task only establishes and tests the Gemini integration. CV optimization will be implemented in a later task.

### Dependencies

TASK-018 must be completed first.

### Subtasks

- [x] Install and configure the current Google GenAI Python SDK.
- [x] Create `ai/ai_client.py`.
- [x] Create `ai/prompts.py`.
- [x] Add the Gemini API key to environment configuration.
- [x] Add the selected model name to `config.py`.
- [x] Add maximum output token, timeout and retry settings to `config.py`.
- [x] Create a reusable function for sending requests to Gemini.
- [x] Implement retry logic with a maximum of three total attempts.
- [x] Add handling for API failures, timeouts and empty responses.
- [x] Log each failed attempt and the final workflow failure.
- [x] Add a simple test prompt to confirm that the client returns a text response.
- [x] Confirm that the API key is not hardcoded or committed to Git.

### Acceptance Criteria

- [ ] A suitable Gemini model is selected.
- [ ] `ai/ai_client.py` is created.
- [ ] `ai/prompts.py` is created.
- [ ] Gemini API key is securely stored through environment variables.
- [ ] Model name is configurable.
- [ ] Maximum output tokens are configured.
- [ ] Request timeout is configured.
- [ ] Retry logic allows a maximum of three total attempts.
- [ ] API failures, timeouts and empty responses are handled and logged.
- [ ] Final failure after the third unsuccessful attempt is logged.
- [ ] A successful test request returns a non-empty string.
- [ ] No Gemini secrets are hardcoded or committed to Git.

### Measurements

- The Gemini client runs without import or runtime errors.
- A valid test request returns a non-empty text response.
- A failed request stops after three total attempts.
- Every failed attempt is logged.
- Final failure is returned in a controlled form.
- Gemini credentials do not exist in tracked repository files.

### Test Cases

- [x] Normal flow — a valid test prompt returns a non-empty string.
- [x] Timeout — the request times out, retries where appropriate and logs the failure.
- [x] API failure — Gemini returns an error and the attempt is logged.
- [x] Empty response — an empty response is treated as a failed attempt.
- [x] Maximum attempts reached — processing stops after three total unsuccessful attempts and logs the final failure.

### Notes

- Prompt instructions belong in `ai/prompts.py`; technical settings belong in `config.py`.
- This task does not yet generate or validate an optimized CV.
- Model selection should be based on output quality, structured-output support, availability and expected cost.

## TASK-006 — Define Core CV Optimization Response Models, Cleaner and Validation Rules

### Status

Done

### Goal

Define the minimum set of response models and validation rules required to ensure the integrity of the generated CV result.

### Description

With this task, we will define the expected JSON response format returned by the AI.

Furthermore, we will define cleaner rules that remove Markdown code fences and surrounding text from the AI response.

Finally, we will define validation rules that check:

- required JSON keys
- data types
- allowed values
- minimum and maximum lengths
- consistency between the fit result and CV output

Company research and interview preparation are not included in this task.

### Dependencies

TASK-005 must be completed first.

### Expected JSON Format

```json
{
  "fit_assessment": {
    "level": "strong",
    "explanation": "Explanation of the candidate's fit.",
    "relevant_experience": [
      "Relevant experience supported by the original CV."
    ],
    "missing_requirements": []
  },
  "cv_patch": {
    "professional_summary": "Optimized professional summary.",
    "experience_updates": [
      {
        "experience_id": "experience_001",
        "suggested_job_title": null,
        "responsibilities": [
          "Optimized responsibility based on existing CV information."
        ]
      }
    ],
    "skills_to_highlight": ["Stakeholder management"]
  },
  "gap_analysis": {
    "supported_requirements": ["Requirement supported by the CV."],
    "reasonably_derived_requirements": [],
    "unsupported_requirements": [
      {
        "requirement": "Unsupported requirement.",
        "impact": "medium",
        "preparation_recommendation": "Recommended preparation.",
        "interview_guidance": "How to discuss the gap honestly."
      }
    ]
  },
  "warnings": []
}
```

For a `poor` fit, `cv_patch` must be `null`.

### Subtasks

- [x] Define Pydantic models for the core CV optimization response.
- [x] Define nested models for fit assessment, CV patch and gap analysis.
- [x] Configure models to reject unexpected fields.
- [x] Create `ai/cleaner.py`.
- [x] Remove Markdown JSON fences from AI responses.
- [x] Extract the JSON object from surrounding AI text.
- [x] Reject responses that do not contain valid JSON.
- [x] Create `ai/validation.py`.
- [x] Validate required keys, data types, enums and field lengths.
- [x] Validate that referenced experience IDs exist in the original CV.
- [x] Validate that highlighted skills are supported by the original CV.
- [x] Enforce the poor-fit rule.
- [x] Return all validation failure reasons.
- [x] Log cleaner failures.
- [x] Log validation failures with the complete list of reasons.

### Acceptance Criteria

- [ ] The JSON response format is defined and locked.
- [ ] `ai/cleaner.py` is created.
- [ ] `ai/validation.py` is created.
- [ ] Cleaner returns pure parsed JSON without Markdown or surrounding text.
- [ ] Cleaner does not invent or repair missing response content.
- [ ] Cleaner failures are logged.
- [ ] Validation failures are logged with all detected reasons.
- [ ] Missing mandatory keys are rejected.
- [ ] Incorrect data types are rejected.
- [ ] Invalid field lengths are rejected.
- [ ] Unsupported enum values are rejected.
- [ ] Unexpected JSON fields are rejected.
- [ ] A `poor` fit requires `cv_patch` to be `null`.
- [ ] A `strong`, `solid` or `stretch` fit requires a valid `cv_patch`.

### Validation Rules

#### `fit_assessment`

- `level`
  - required string
  - allowed values: `strong`, `solid`, `stretch`, `poor`
- `explanation`
  - required string
  - 50–1,000 characters
- `relevant_experience`
  - required list of strings
  - minimum one item
  - each item: 10–500 characters
- `missing_requirements`
  - required list of strings
  - may be empty
  - each item: 5–300 characters

#### `cv_patch`

- required for `strong`, `solid` and `stretch`
- must be `null` for `poor`
- allowed keys:
  - `professional_summary`
  - `experience_updates`
  - `skills_to_highlight`

#### `professional_summary`

- required string
- 80–700 characters

#### `experience_updates`

- required list
- minimum one item
- each item must contain:
  - valid `experience_id`
  - optional `suggested_job_title`
  - `responsibilities`
- each responsibility:
  - 20–400 characters
- maximum six responsibilities per experience entry

#### `skills_to_highlight`

- required list of strings
- minimum one item
- maximum 30 items
- each skill must be supported by the original CV

#### `gap_analysis`

Required keys:

- `supported_requirements`
- `reasonably_derived_requirements`
- `unsupported_requirements`

Each unsupported requirement must contain:

- `requirement`
  - required string
  - minimum 5 characters
- `impact`
  - allowed values: `low`, `medium`, `high`
- `preparation_recommendation`
  - required string
  - minimum 20 characters
- `interview_guidance`
  - required string
  - minimum 20 characters

#### `warnings`

- required list of strings
- may be empty
- each warning: 5–300 characters

### Measurements

- Cleaner returns pure parsed JSON.
- Valid responses pass validation.
- Validation fails when any mandatory rule is not met.
- Validation returns all detected failure reasons.
- Cleaner and validation errors are logged.

### Test Cases

- [x] Normal flow — a valid raw AI response is cleaned, parsed and validated successfully.
- [x] Markdown wrapper — valid JSON inside a Markdown code block is extracted successfully.
- [x] Surrounding text — valid JSON surrounded by AI text is extracted successfully.
- [x] Missing keys — validation fails and lists the missing keys.
- [x] Wrong type — validation fails when a field has an incorrect data type.
- [x] Wrong size — validation fails when a field does not meet length or list-size rules.
- [x] Invalid enum — validation fails for an unsupported fit level or impact value.
- [x] Poor-fit violation — validation fails when a poor-fit response contains a CV patch.
- [x] Cleaner failure — a response without valid JSON is rejected and logged.

### Notes

- The cleaner may remove wrappers and surrounding text, but it must not modify the JSON content.
- Protected CV-field validation will compare the response with the original structured CV.
- Company research and interview preparation models will be added in later tasks.

## TASK-007 — Implement Role Fit and CV Optimization Workflow

### Status

Done

### Goal

This task implements the first core pillar of the project by building the role-fit and CV optimization logic.

### Description

In this task, we will build the logic to estimate role fit and produce a polished CV in JSON format by using the models, cleaner and validation rules from TASK-006.

### Dependencies

TASK-006 must be completed first.

### Subtasks

- [x] Define clear prompt instructions for role-fit assessment.
- [x] Define criteria for the four fit levels: `strong`, `solid`, `stretch` and `poor`.
- [x] Create the main CV optimization workflow.
- [x] Load the stored CV profile and job input.
- [x] Send the required context to Gemini.
- [x] Pass the AI response through the cleaner.
- [x] Validate the cleaned response using TASK-006 rules.
- [x] Stop CV tailoring when the fit level is `poor`.
- [x] Return a structured poor-fit result with missing requirements and next-step advice.
- [x] Return a validated CV optimization JSON result when the fit is acceptable.
- [x] Log workflow start, completion, poor-fit stop and failures.

### Acceptance Criteria

- [ ] Criteria for grading whether the candidate is a good fit are clearly defined.
- [ ] Four role-fit levels are defined: `strong`, `solid`, `stretch` and `poor`.
- [ ] The workflow stops CV tailoring when the fit is `poor`.
- [ ] A poor-fit result returns a clear explanation, missing requirements and advice on next actions.
- [ ] If the fit is acceptable, the workflow produces validated JSON that can later be used to render the CV.
- [ ] AI output passes through the cleaner and validation logic from TASK-006.
- [ ] Invalid AI output is rejected and handled safely.
- [ ] Workflow results and failures are logged.

### Measurements

- The workflow stops CV tailoring when the fit is `poor`.
- A poor-fit result returns structured reasons and next-step advice.
- The workflow produces a polished CV in validated JSON format when the fit is acceptable.
- Invalid AI output does not reach the final workflow result.
- Workflow completion and failure events are logged.

### Test Cases

- [x] Normal flow — acceptable fit produces a polished CV in validated JSON format.
- [x] Normal flow — poor fit produces a structured warning and stops CV tailoring.
- [x] Validation failure — invalid AI output is rejected and logged.
- [x] Manual quality review — review whether the assigned fit level is reasonable for the provided CV and job ad.

### Notes

- Displaying results in the frontend belongs to a later task.
- Fit quality must be reviewed manually because a structurally valid AI response may still contain a poor assessment.

## TASK-008 — Build CV Results UI, Preview and Direct PDF Export

### Status

Done

### Goal

Complete the CV optimization flow by saving, displaying and exporting the validated CV result.

### Description

This task delivers the validated CV optimization result to the user.

The application saves the result to Firestore before displaying it, allows the user to reopen saved applications, renders the tailored CV in Streamlit and generates a downloadable PDF directly from the stored structured CV data.

Browser Print / Save as PDF was replaced with direct PDF generation because Streamlit browser printing produced inconsistent page breaks and layout results.

### Dependencies

TASK-007 must be completed first.

### Subtasks

- [x] Save the validated application result to Firestore before displaying it to the user with status `draft`.
- [x] Create the CV results page.
- [x] Load the saved application using its `application_id`.
- [x] Render the CV from the stored structured data.
- [x] Add a success modal with the message `Your CV is ready`.
- [x] Add a `Check it now` button that opens the preview in the same tab.
- [x] Add a `My Applications` page or menu option.
- [x] Sort saved applications from newest to oldest.
- [x] Allow the user to reopen a saved application.
- [x] Create direct PDF generation from the tailored CV data.
- [x] Add a `Download CV as PDF` button.
- [x] Support Unicode characters such as `Marković`.
- [x] Limit the generated PDF to a maximum of two pages.
- [x] Add handling for missing, invalid or unavailable application records.
- [x] Log PDF generation attempts and failures.

### Acceptance Criteria

- [x] The result is saved to Firestore with status `draft` before it is displayed.
- [x] When the CV is prepared, the user sees the `Your CV is ready` modal.
- [x] Clicking `Check it now` opens the correct saved result in the same tab.
- [x] The preview loads the correct application using its `application_id`.
- [x] Previous applications are available through `My Applications`.
- [x] Applications are displayed from newest to oldest.
- [x] A saved application can be reopened.
- [x] The CV can be downloaded as a generated PDF.
- [x] The PDF contains the tailored CV content.
- [x] The PDF supports Serbian characters.
- [x] The generated PDF has a maximum of two pages.
- [x] Missing, invalid and unavailable records are handled safely.

### Measurements

- The draft application can be verified in Firestore.
- The success modal appears after the result is saved.
- `Check it now` opens the correct result.
- `My Applications` lists saved results newest first.
- A saved application can be reopened.
- The PDF downloads and opens successfully.
- The generated PDF contains two pages or fewer.
- Invalid and missing records do not crash the UI.

### Test Cases

- [x] Normal flow — the CV patch is merged into a complete CV.
- [x] Normal flow — the draft application is saved and reloaded before display.
- [x] Normal flow — the preview renders the correct saved CV.
- [x] Normal flow — saved applications are sorted newest first.
- [x] Expected failure — a nonexistent `application_id` returns a controlled not-found result.
- [x] Expected failure — invalid stored application data is rejected.
- [x] Expected failure — Firestore loading failures are handled safely.
- [x] PDF generation — a valid PDF is generated from the tailored CV.
- [x] PDF generation — the PDF contains a maximum of two pages.
- [x] Manual UI test — the success modal appears and `Check it now` opens the preview.
- [x] Manual UI test — the PDF downloads and opens successfully.
- [x] Manual content review — the generated CV content is usable as a first version.

### Notes

- PDF content is generated from the validated and stored structured CV data.
- PDF generation is independent of the Streamlit browser layout.
- The current PDF is considered usable for V1.
- Final visual polish is intentionally deferred until after the revision workflow.

## TASK-009 — Define Section Revision Models and Validation Rules

### Status

Done

### Goal

This task will define the models and validation rules required to revise only the CV sections selected by the user.

### Description

In this task, we will define the request and response formats for section revisions.

The revision response will contain only the selected sections. Each revised section will be validated separately, merged with the existing CV, and the complete merged result will then pass the full validation from TASK-006.

### Dependencies

TASK-008 must be completed first.

### Subtasks

- [x] Define the revision request model.
- [x] Define how selected sections and user comments are represented.
- [x] Define the revision response model.
- [x] Allow the response to contain only requested sections.
- [x] Create section-specific validation rules.
- [x] Reject sections that were not requested.
- [x] Reject unexpected keys.
- [x] Validate each revised section before merging.
- [x] Merge validated revisions with the existing CV.
- [x] Run complete CV validation after the merge.
- [x] Return all revision validation failure reasons.
- [x] Log revision validation and merge failures.

### Acceptance Criteria

- [ ] Revision request and response JSON formats are defined.
- [ ] Each selected section can contain its own user comment.
- [ ] AI response may contain only the requested sections.
- [ ] Additional or unrequested sections are rejected.
- [ ] Each revised section follows its section-specific validation rules.
- [ ] Valid revised sections replace the existing sections.
- [ ] Sections not selected for revision remain unchanged.
- [ ] The complete merged result passes the full TASK-006 validation.
- [ ] Validation failures return and log all detected reasons.

### Measurements

- Only selected sections can be revised.
- Unrequested sections are rejected.
- Invalid revised sections fail validation.
- Unchanged sections remain identical.
- The merged CV passes complete validation.
- All validation errors are logged.

### Test Cases

- [x] Normal flow — selected sections are validated, merged and pass complete validation.
- [x] Missing section — the response does not contain one of the requested sections.
- [x] Additional section — the response contains a section that was not requested.
- [x] Wrong type — a revised section contains an invalid data type.
- [x] Wrong size — revised content does not meet its length rules.
- [x] Merge failure — the merged result fails complete CV validation.

### Notes

- Revision validation is separate from complete CV validation.
- The cleaner may remove wrappers but must not modify revision content.

## TASK-010 — Implement Targeted Revision Workflow and Review UI

### Status

in Progress

### Goal

This task will allow the user to review the generated CV, request changes to selected sections, or accept the CV.

### Description

In this task, a second AI workflow will be developed using separate revision instructions and the user’s comments.

The AI will return only the selected sections. After cleaning and validation, the revised sections will replace the existing sections and the updated CV will remain in draft status until the user accepts it.

### Dependencies

TASK-009 must be completed first.

### Subtasks

- [x] Add separate revision instructions to `ai/prompts.py`.
- [x] Display `Request changes` and `Accept CV` buttons on the preview page.
- [x] Allow comments only on sections that may be revised.
- [x] Allow each comment to be edited or removed.
- [x] Add a button to cancel the revision request.
- [x] Add a `Make changes` button.
- [x] Build the targeted revision AI call.
- [x] Send the existing CV, selected sections and user comments to Gemini.
- [x] Request only the selected sections in the AI response.
- [x] Pass the response through the cleaner and TASK-009 validation.
- [x] Merge validated sections with the current CV.
- [x] Save the revised result as the latest draft version.
- [x] Keep the CV in `draft` status after revisions.
- [x] Change the status to `accepted` only after the user clicks `Accept CV`.
- [x] Enable browser PDF export only for an accepted CV.
- [x] Log revision requests, completions and failures.

### Acceptance Criteria

- [ ] The initial CV result is available with status `draft`.
- [ ] The preview displays `Request changes` and `Accept CV`.
- [ ] Clicking `Request changes` allows the user to comment only on editable sections.
- [ ] Comments can be edited and removed.
- [ ] The user can cancel the revision process.
- [ ] Clicking `Make changes` starts the targeted revision workflow.
- [ ] AI returns only the selected sections.
- [ ] Revised sections are cleaned, validated and merged.
- [ ] Sections that were not selected remain unchanged.
- [ ] A revised CV is saved as the latest draft version.
- [ ] Clicking `Accept CV` changes the status to `accepted`.
- [ ] PDF export is available only after acceptance.

### Measurements

- Review and acceptance buttons are displayed and work.
- Only editable sections can receive revision comments.
- Comments can be added, edited and removed.
- A successful revision updates only the selected sections.
- Revised results remain in draft status.
- Acceptance updates the Firestore status to `accepted`.
- Accepted CVs can be saved through browser Print / Save as PDF.

### Test Cases

- [x] Normal flow — the user accepts the CV and the database status changes to `accepted`.
- [x] Normal flow — the user adds, edits and removes comments on editable sections.
- [x] Normal flow — the user requests changes and receives an updated draft CV.
- [x] Normal flow — the user cancels the revision process without changing the CV.
- [x] Expected failure — AI returns an unrequested section.
- [x] Expected failure — revision response fails validation.
- [x] Expected failure — Firestore cannot save the revised draft.
- [x] Expected failure — PDF export is attempted while the CV is still in draft status.

### Notes

- A revision does not automatically accept the CV.
- The user may repeat the review and revision process before acceptance.
- Full revision history and side-by-side comparison are outside the MVP.

---

---

# Task Template

Use this template for every task.

## TASK-XXX — Title

### Status

Backlog

### Goal

What should this task achieve and why is it needed?

### Description

What is included in this task?

What is explicitly not included?

### Dependencies

Which tasks or decisions must be completed first?

### Subtasks

- [ ] Subtask 1
- [ ] Subtask 2
- [ ] Subtask 3

### Acceptance Criteria

- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

### Measurements

How will success be measured?

- Metric 1
- Metric 2

### Test Cases

- [ ] Normal flow
- [ ] Invalid input
- [ ] Expected failure
- [ ] Relevant edge case

### Notes

Only include risks, open questions or important implementation constraints.

# MVP Task List

Questions to answer:

- Which tasks are required before the MVP is complete?
- Which tasks can be postponed?
- Which tasks are critical for demo quality?

---

# Success Metrics

Questions to answer:

- How do we measure whether the project is good enough?
- What should work reliably?
- What would make the demo convincing?

Example:

- The main user flow works end-to-end.
- AI output is validated before display.
- Invalid AI output fails safely.
- User can complete the main workflow without editing code.
- Project can be explained clearly in the README.

---

# Release Checklist

Questions to answer:

- Is the app runnable from a clean setup?
- Is `.env.example` available?
- Are secrets excluded from Git?
- Are main workflows tested?
- Is documentation updated?
- Are screenshots or demo materials ready?

Checklist:

- [ ] App runs locally
- [ ] Main workflow tested
- [ ] Error cases tested
- [ ] README updated
- [ ] Scope updated
- [ ] Architecture updated
- [ ] Decisions updated
- [ ] No secrets committed
- [ ] Demo ready

# Task Diagram

```mermaid
flowchart TD;
    Task-001-->Task-002;
    Task-002-->Task-003;
    Task-003-->Task-004;
    Task-004-->Task-018;
    Task-018-->Task-005;
    Task-005-->Task-006;
    Task-006-->Task-007;
    Task-007-->Task-008;
    Task-008-->Task-009;
    Task-009-->Task-010;
    Task-010-->Task-012;
    Task-012-->Task-013;
    Task-013-->Task-014;
    Task-014-->Task-019;
    Task-019-->Task-015;
    Task-015-->Task-011;
    Task-011-->Task-016;
    Task-016-->Task-017;

```
