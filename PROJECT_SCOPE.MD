# Project Scope

This document answers one question:

> **What are we building, why are we building it, and what is intentionally outside the scope of this project?**

---

# Project Name

## CV Optimizer & Interview Prep Assistant

A tool that helps users tailor their CV to a specific job opportunity and prepare for a potential interview.

---

# Problem

One CV cannot effectively represent a candidate for every possible job opportunity.

Adjusting the presentation of previous experience for each job ad is time-consuming and adds additional stress to an already demanding job-search process.

General AI chat tools can help, but they usually require significant back-and-forth communication before they understand:

- the candidate’s experience
- the target position
- what may or may not be changed
- the expected output format
- the required interview preparation

This solution aims to complete the same process in a few structured actions instead of several hours of manual work.

---

# Goal

The primary objective is to reduce the time and effort required to:

- assess whether a job opportunity is suitable
- tailor an existing CV
- research the target company
- prepare for a potential interview

The user should receive the necessary CV and interview preparation materials approximately ten minutes after finding a relevant job ad.

---

# Product Vision

The product should become a practical everyday tool for job seekers.

## V1 — Controlled MVP

### Input

- predefined structured CV profile already stored in the application
- pasted job ad text
- selected existing company or a new company entered in the required format

### Output

- role fit assessment
- explanation of the fit assessment
- optimized CV when the fit is sufficient
- gap analysis and preparation recommendations
- company background
- on-demand interview preparation material
- likely interview questions with answer directions
- saved structured application result
- directly generated PDF version of the accepted CV

V1 also includes:

- inline human review of AI-suggested CV changes
- Firestore persistence
- controlled validation and failure handling
- Docker Compose deployment for a local-network portfolio demo
- bookmarkable `/sale` and `/svetlana` routes

## V2 — Expanded Input

### Input

- uploaded PDF or Word CV
- automatic CV parsing
- job ad URL processing
- pasted job ad fallback
- company name
- optional company website URL

### Output

- parsed and structured CV
- role fit assessment
- optimized CV
- company background
- interview preparation material
- additional export options or CV templates

V2 may also add manual Company Research retry and broader user-managed profile support.

## V3 — Agentic Job Discovery

V3 may add an agentic workflow that periodically identifies suitable vacancies based on actual candidate fit rather than only matching job titles.

Possible inputs may include:

- job-board APIs
- job-alert emails
- scheduled search criteria

The user could receive relevant positions together with fit analysis, application guidance and prepared materials.

---

# Primary User

The primary user is a person who:

- wants to change jobs
- is actively looking for a new position
- has recently lost a job
- wants to reduce the effort required for each application
- has limited technical knowledge

The user’s goal is to present existing experience in the most relevant and accurate way for a specific position and improve the chances of standing out among other applicants.

---

# Potential Future Users

No additional user groups are currently planned for the MVP.

---

# User Journey

1. The user opens the application.
2. The application loads and displays the selected predefined CV profile as the primary view.
3. The user opens the optimization form.
4. The user selects an existing company from stored records.
5. If the company does not exist, the user enters a new company in the format `Company Name - ISO2 Country Code`.
6. The user pastes the full job ad text.
7. The user starts the workflow.
8. The system evaluates the candidate’s fit for the role.
9. If the fit is poor, the workflow stops and returns:
   - an explanation
   - the main missing requirements
   - recommendations for improving future eligibility

10. If the fit is sufficient, the system generates:
    - an optimized CV
    - a fit explanation
    - gap analysis

11. Company Research is generated or reused as a separate supporting workflow.
12. The validated application result is stored in Firestore as a draft.
13. The user reviews AI-suggested CV changes inline.
14. For each supported item, the user may:
    - accept the AI suggestion
    - keep the original content
    - request a targeted revision

15. The system revises only the selected content.
16. The user saves all review decisions.
17. The user accepts the final CV.
18. After acceptance, the user downloads a directly generated PDF version of the CV.
19. Interview Prep can be generated on demand using the job ad, CV and available company context.
20. The user may reopen saved applications from Firestore.

Company Research or Interview Prep failure must not delete or invalidate an already valid CV result.

---

# In Scope

The MVP supports the following capabilities.

## Data Input

- predefined structured CV profile
- pasted job ad text
- selection of an existing company from stored records
- entry of a new company in the format `Company Name - ISO2 Country Code`

Example:

```text
Bird - NL
```

The user does not upload a CV in V1.

The user does not provide a job ad URL in V1.

## Role Fit Assessment

The system evaluates whether the candidate has sufficiently relevant experience and qualifications for the advertised role.

The fit result should explain:

- why the candidate is considered a strong, solid, stretch or poor fit
- which experience is relevant
- which requirements are missing
- which gaps may be reduced through preparation or learning

If the role is classified as poor fit, CV tailoring stops.

The user may still independently decide to apply, but the MVP will not generate a tailored CV for that application.

## CV Optimization

When the fit is sufficient, the AI may improve:

- professional summary
- job title wording where appropriate
- responsibility descriptions
- skill presentation
- ordering and emphasis of relevant information

The AI may highlight responsibilities or skills that were a smaller part of a previous role when they are particularly relevant to the target position.

The original CV remains the factual source of truth.

The AI must not invent:

- employers
- employment dates
- education
- certifications
- experience
- achievements
- tools or skills unsupported by the available CV information

## Gap Analysis and Preparation

The system classifies relevant job requirements as:

- clearly supported by the CV
- reasonably derived from existing experience
- currently unsupported

For unsupported requirements, the system should explain:

- why the requirement matters
- how strongly it affects the candidate’s fit
- what the user could learn or review before applying
- how the user may discuss the gap honestly during an interview

Unsupported skills must not be silently added as confirmed skills.

## Company Research

The system produces a concise company profile using available public information.

The report should cover, where information is available:

- company overview
- products and services
- industry
- customers or customer types
- competitors
- important recent news
- general employee-sentiment themes where reliable public information is available

If reliable information is not available, the system should clearly indicate the limitation instead of inventing details.

Company Research is stored separately from applications and may be reused when a valid fresh record already exists for the same company.

V1 does not include a manual Company Research retry button after a failed attempt.

## Interview Preparation

Interview Prep is generated on demand after the CV has been accepted.

The system generates approximately 10–15 likely interview questions.

Questions should cover a range of topics, including:

- previous experience
- role-specific knowledge
- candidate strengths
- weaknesses or CV gaps
- motivation
- company knowledge
- situational and behavioral questions
- topics the candidate should review before the interview

Each question should include answer directions, relevant evidence from the candidate’s background and preparation guidance.

The workflow also generates questions the candidate may ask the interviewer.

Interview Prep may still run without Company Research, but the result may be less company-specific.

## User Review and Revision

The result is shown to the user before export.

The user sees the current CV and AI-suggested changes inline before accepting the final result.

The user may:

- accept the suggestion
- keep the original content
- request a targeted revision

A follow-up AI request revises only the selected content and does not regenerate the complete result.

The CV cannot be accepted until all review decisions are resolved and saved.

## Data Storage and Reuse

The MVP stores validated structured data in Firebase Firestore.

Two main record types are stored:

- reusable company research in the `companies` collection
- application results in the `applications` collection

Company research may be reused when the user applies for another position at the same company and the existing record is still valid.

Each application record may contain:

- application ID
- profile ID
- company key
- fit assessment
- tailored CV JSON
- gap analysis
- company reference or embedded summary
- interview preparation
- application status
- supporting workflow statuses
- creation and update timestamps
- relevant version metadata

The application status moves from `draft` to `accepted` after the review is completed.

The MVP does not include user accounts or a full history-management dashboard.

## Export

The application generates a downloadable PDF version of the accepted CV from the stored structured CV data.

PDF export is unavailable while the application remains in draft status.

The current PDF is considered usable for V1, while final visual polish and template improvements may be handled later.

## Deployment

V1 includes a Docker Compose deployment for a repeatable portfolio demo.

The deployment uses:

- a Streamlit application container
- an Nginx reverse-proxy container
- mounted Firebase credentials
- environment-based configuration
- health checks and visible container logs

The first deployment target is a user-owned home-server laptop accessible from the local network.

Public cloud hosting, domain configuration and HTTPS are not part of V1.

## Basic Reliability

The MVP includes:

- validation of required user input
- structured AI output
- cleaning of raw AI responses
- Pydantic and business validation
- validation of stored data before reuse
- safe failure when output is invalid
- limited retry handling
- workflow logging and timing
- safe handling of storage failures
- preservation of valid CV data when supporting workflows fail

---

# Out of Scope

The following capabilities are intentionally excluded from the MVP:

- uploading PDF or Word CV files
- automatic CV parsing
- entering only a job ad URL
- scraping LinkedIn job ads
- importing a LinkedIn profile
- direct application submission
- manual Company Research retry
- advanced PDF styling and additional templates
- user accounts
- user-facing application history dashboard
- automated job alerts
- scheduled job discovery
- local AI model fallback
- multiple CV templates
- recruiter or enterprise features
- public internet deployment
- domain and HTTPS configuration
- Kubernetes or complex cloud infrastructure

---

# Constraints

The project operates with a budget close to zero.

Development and hosting should rely on:

- free or low-cost services
- user-owned hardware where appropriate
- limited external API usage
- simple deployment
- one-person product ownership

The product should avoid unnecessary infrastructure and enterprise-level complexity.

---

# Core Product Philosophy

## Accuracy Over Appeal

The AI should improve how real experience and skills are presented, but must not invent qualifications or achievements.

## Minimalism Over Visual Complexity

The CV should be readable, professional and suitable for common recruitment and ATS workflows.

It should not resemble a heavily designed invitation or marketing document.

## Simplicity Over Unjustified Complexity

The system should only introduce complexity when it produces meaningful product value or learning value.

The AI should focus on sections where tailoring is useful.

Stable factual information such as contact details, employers and employment dates should remain unchanged.

## Quality and Personalization Over Speed

The product aims to reduce preparation time, but should not sacrifice output quality.

Company research and interview preparation should be specific to the company and role rather than generic or copied from public pages without interpretation.

## User Control Over Full Automation

The user reviews the complete result before export and may request targeted revisions.

The AI assists the user but does not make the final decision about whether the user should apply.

A poor-fit result only prevents the application from generating a tailored CV; it does not prevent the user from applying independently.

---

# Architecture Direction

The MVP uses a simple and modular web architecture.

The architecture includes:

- Streamlit as the user interface
- a service layer for workflow orchestration and business rules
- separate AI workflows
- structured CV and AI models
- validation before rendering and persistence
- Firebase Firestore persistence
- direct PDF generation
- Docker Compose deployment with Nginx
- FastAPI retained as an optional API entry point, but not required by the final Streamlit flow

The architecture should remain simple enough to develop, test and demonstrate reliably.

---

# AI Philosophy

The AI is responsible for:

- assessing role fit
- improving the presentation of existing experience
- identifying gaps
- researching the target company
- generating interview preparation material
- revising specific sections based on user feedback

The AI must not:

- invent factual experience
- invent achievements
- change protected CV information
- hide important gaps
- present unsupported information as confirmed fact
- produce a tailored CV when the fit is classified as poor

AI output must be structured and validated before it is shown as a final result or stored for reuse.

If an AI workflow fails repeatedly, that workflow stops and the user receives a controlled error message.

A supporting-workflow failure must not delete an already valid CV result.

---

# Success Criteria

The MVP is considered complete when:

- the application successfully loads a predefined structured CV profile
- the user can select an existing company or add a new company in the required format
- the user can submit pasted job ad text
- the system produces a clear role fit assessment
- a poor-fit result correctly stops CV tailoring
- a poor-fit result still provides useful gap and preparation recommendations
- a suitable role produces an optimized CV based only on available facts
- protected CV fields remain unchanged
- company research is generated, reused or clearly marked as limited
- validated application results and tailored CV data are stored
- the user can review suggestions inline
- the user can accept suggestions, keep original content or request targeted revisions
- only the selected content is revised
- the application cannot be accepted until review decisions are resolved
- interview preparation can be generated on demand
- AI output is validated before rendering
- stored data is validated before reuse
- invalid output fails safely
- supporting-workflow failure does not remove a valid CV
- the accepted CV can be downloaded as a directly generated PDF
- Docker Compose starts the portfolio demo
- `/sale` and `/svetlana` open the correct candidate profiles
- Firestore data remains available after container restart
- the complete main workflow can be demonstrated without editing the code

---

# Non-Goals

The product is not intended to:

- replace the user’s personal communication and interview skills
- guarantee employment
- mislead recruiters
- fabricate experience or qualifications
- automatically apply for jobs
- create the most visually decorative CV
- make every candidate appear suitable for every position

The goal is to present real experience accurately, clearly and strategically.

---

# Future Expansion

Potential future expansion includes:

- PDF and Word CV upload
- automatic CV parsing
- LinkedIn profile import if technically and legally possible
- job ad URL processing with pasted-text fallback
- manual Company Research retry
- user accounts
- user-facing application history dashboard
- side-by-side CV version comparison
- job-board API integration
- scheduled fit-based job discovery
- job-alert email processing
- candidate notifications
- optional local model or privacy mode
- multiple CV templates
- public hosting with domain and HTTPS
- stronger agent observability and quality checks

---

# Guiding Principle

> Every added layer of complexity must be justified by either meaningful product value or meaningful learning value.
