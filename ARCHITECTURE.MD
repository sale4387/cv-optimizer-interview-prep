# Architecture

This document answers one question:

> **How does the system work?**

It describes the technical architecture, component responsibilities, AI workflow, validation strategy, error handling and deployment direction.

---

# Architecture Overview

This project is a web-based AI application that helps a user tailor an existing CV to a specific job ad and prepare for a potential interview.

The MVP uses a predefined structured CV profile already stored in the application. The user does not upload a CV in V1. The user provides job-related input through the frontend, and the system uses AI to generate a structured output containing:

- role fit assessment
- optimized CV suggestions
- gap analysis
- company research summary
- interview preparation material

The application follows a validation-first workflow. AI output is not trusted automatically. It must be cleaned, parsed and validated before being shown to the user.

---

# High-Level Architecture

The main components are:

- **Frontend**
- **Backend**
- **AI Layer**
- **Research Layer**
- **Validation Layer**
- **Logger**
- **External APIs**
- **Scheduler** _(future component)_

## Frontend

The frontend is built with Streamlit.

It is responsible for:

- displaying the current CV profile
- collecting job ad input
- collecting company name
- collecting optional company website URL
- showing role fit results
- showing optimized CV preview
- showing company research and interview prep
- allowing the user to print/save the final CV as PDF from the browser

## Backend

The backend is built with FastAPI.

It is responsible for:

- receiving validated frontend input
- orchestrating the AI workflow
- preparing prompts
- calling the AI layer
- cleaning AI responses
- validating structured JSON
- handling retries
- returning validated output to the frontend
- logging workflow events

FastAPI is used intentionally even though Streamlit could technically call the AI workflow directly. The reason is to keep the system modular and easier to extend later as an API-based service.

## AI Layer

The AI layer is responsible for generating structured AI output based on:

- stored CV profile
- job ad text
- company name
- optional company website URL
- system instructions
- expected JSON schema

The AI layer must not freely rewrite the entire CV. It should only suggest changes to allowed CV sections and must not invent experience, employers, dates, education or certifications.

## Research Layer

The research layer is responsible for collecting or generating company-related preparation material.

In the MVP, the primary source is the company name provided by the user. The optional company website URL can be used as additional context if available.

If online research or search grounding is available, the system may use it to generate:

- company overview
- products and services
- industry context
- competitors
- recent relevant news
- Glassdoor-style summary based on available public information

If enough information cannot be found, the app must clearly mark the section as limited instead of pretending that the data is complete.

## Validation Layer

The validation layer is responsible for ensuring that AI output is usable by the application.

It checks:

- whether a response exists
- whether JSON can be parsed
- whether required keys exist
- whether values have correct types
- whether fields are non-empty where required
- whether CV changes only touch allowed sections
- whether forbidden fields remain unchanged

## Logger

The logger records important workflow events, failures and retries.

It is used for debugging and development visibility, not for complex reporting.

## External APIs

The MVP depends on:

- Gemini API for AI generation
- optional search/grounding capability for company research if available

Future versions may add:

- job board APIs
- CV parsing APIs
- PDF generation services
- email notification services

## Scheduler

The scheduler is not part of the MVP.

It may be introduced in V3 to run periodic job searches and notify the user about suitable roles.

---

# Project Structure

Expected project structure:

```text
project/
├── .env
├── .env.example
├── .gitignore
├── README.md
├── PROJECT_SCOPE.md
├── ARCHITECTURE.md
├── PROJECT_BOARD.md
├── DECISIONS.md
├── requirements.txt
├── api.py
├── config.py
├── logger.py
├── streamlit/
│   ├── app.py
│   ├── cv_preview.py
│   ├── interview_prep_view.py
│   └── components.py
├── cv_data/
│   ├── cv_sale.json
│   └── cv_svetlana.json
├── ai/
│   ├── models.py
│   ├── ai_client.py
│   ├── prompts.py
│   ├── workflow.py
│   ├── cleaner.py
│   └── validation.py
└── tests/
    └── manual_test_cases.md
```

## Notes

- `.env` is used only locally and must not be committed.
- `.env.example` is committed to show required environment variables.
- CV data is stored as structured JSON for the MVP.
- AI models and validation logic are separated from Streamlit UI logic.
- FastAPI acts as the backend orchestration layer.

---

# Main Components

## Frontend

Responsibility:

- collect user input
- show processing state
- display validated AI output
- render CV preview
- render interview preparation material

Inputs:

- selected stored CV profile
- job ad text
- company name
- optional company website URL

Outputs:

- user request sent to backend
- rendered CV preview
- rendered interview prep page

## Backend

Responsibility:

- receive request from frontend
- validate basic input
- build AI prompt
- call AI workflow
- clean AI response
- validate AI response
- return structured result

Inputs:

- frontend request
- stored CV profile
- configuration
- prompt instructions

Outputs:

- validated workflow result
- error response if workflow fails

## AI Layer

Responsibility:

- estimate role fit
- generate CV optimization suggestions
- generate gap analysis
- generate company research summary
- generate interview questions and answer suggestions

Inputs:

- CV profile
- job ad text
- company name
- optional website URL
- prompt instructions
- expected output schema

Outputs:

- structured JSON response

## Validation Layer

Responsibility:

- reject invalid AI output
- prevent unsafe or unsupported CV changes
- ensure output can be rendered by the frontend

Inputs:

- raw or cleaned AI response
- expected schema
- original CV profile

Outputs:

- validated AI result
- validation error

## Logger

Responsibility:

- record workflow start and completion
- record AI call failures
- record cleaner failures
- record validation failures
- record retry attempts

## External APIs

Responsibility:

- provide AI generation
- optionally provide company research through search/grounding
- support future integrations

---

# Data Flow

1. User opens the Streamlit application.
2. User selects or uses a predefined CV profile.
3. User pastes the job ad text.
4. User enters the company name.
5. User optionally enters the company website URL.
6. Frontend sends the request to the FastAPI backend.
7. Backend validates basic input.
8. Backend loads the stored CV profile.
9. Backend builds the AI prompt using:
   - CV profile
   - job ad text
   - company name
   - optional company website URL
   - system rules
   - expected JSON structure

10. AI layer sends the request to Gemini.
11. AI returns raw output.
12. Cleaner extracts usable JSON.
13. Validation layer checks structure, types, required fields and forbidden CV changes.
14. If validation passes, backend returns structured output to frontend.
15. Streamlit renders:

- fit assessment
- CV preview
- gap analysis
- company research
- interview prep

16. User reviews the result.
17. User can print/save the CV as PDF from the browser.
18. If the user wants a specific section changed, a follow-up AI call can be triggered for that section only.

---

# AI Workflow

The system has two AI workflows.

## 1. Main AI Workflow

Purpose:

- assess role fit
- generate CV optimization suggestions
- generate gap analysis
- generate company research
- generate interview preparation material

Input sent to AI:

- stored CV profile
- job ad text
- company name
- optional company website URL
- instructions about allowed and forbidden CV changes
- required JSON output structure

Expected output:

- role fit assessment
- user-facing fit explanation
- CV patch or CV suggestions
- gap analysis
- company research summary
- interview questions
- suggested answers
- warnings or limitations

Behavior:

- If fit is strong or solid, AI generates CV suggestions normally.
- If fit is stretch, AI generates suggestions but clearly warns about missing requirements.
- If fit is poor, AI should recommend stopping. The user may still choose to generate anyway, but this is not the default path.

## 2. Follow-Up Revision Workflow

Purpose:

- revise one specific section based on user feedback

Input sent to AI:

- original CV profile
- current AI output
- selected section
- user comment
- original job ad context

Expected output:

- revised version of the selected section only
- short explanation of what changed

Behavior:

- AI must not regenerate the entire CV.
- AI must only modify the section selected by the user.
- The same validation rules still apply.

---

# Data Models

Detailed schemas will be defined during implementation.

Expected main models:

- `CVProfile`
- `JobInput`
- `FitAssessment`
- `CVPatch`
- `GapAnalysis`
- `CompanyResearch`
- `InterviewQuestion`
- `InterviewPrep`
- `AIWorkflowResult`
- `RevisionRequest`
- `RevisionResult`

These models will be validated with Pydantic.

---

# Validation Strategy

## Input Validation

Before processing starts, the backend validates:

- stored CV profile exists
- job ad text is provided
- company name is provided
- company website URL is valid if provided

Company website URL is optional.

Job ad URL parsing is out of scope for the MVP.

## AI Response Validation

After AI responds, the backend validates:

- response exists
- JSON can be extracted
- JSON can be parsed
- required keys exist
- values have correct data types
- required strings are not empty
- lists contain minimum expected items
- allowed enum values are used
- CV patch only touches allowed fields
- forbidden CV fields remain unchanged

Forbidden CV fields include:

- name
- contact details
- employers
- employment dates
- education
- certifications
- factual achievements not present in the original CV

## Retry Strategy

The workflow can be attempted up to 3 times.

Retry can be triggered by:

- AI API failure
- response cleaner failure
- JSON parsing failure
- validation failure

If all 3 attempts fail, the workflow stops safely and the user receives an error message.

---

# Error Handling

Expected failure cases:

- AI API request fails
- AI returns empty response
- AI returns invalid JSON
- cleaner cannot extract JSON
- validation fails
- research data is incomplete
- required user input is missing

Handling strategy:

- log the failure
- retry up to 3 times where appropriate
- stop safely after repeated failure
- show a clear high-level error to the user
- do not display unvalidated AI output as final result

The user should not see raw technical errors.

---

# Security

Secrets are stored using:

- local `.env` file
- deployment environment variables

Secrets must not be committed to Git.

The repository should include:

- `.env.example`
- `.gitignore`

API access is protected with an API key passed in the request header.

Rate limiting can be applied through SlowAPI.

Security principles:

- do not expose API keys
- do not commit private CV data unless intentionally using demo data
- validate all user input
- validate all AI output
- prevent AI from modifying forbidden CV fields
- log failures without exposing sensitive data unnecessarily

---

# Deployment

Initial development runs locally.

Possible deployment options:

- local machine
- home server laptop
- Render
- Streamlit Community Cloud

For portfolio presentation, a live demo may be deployed, but this will be decided later.

Deployment direction:

- local development first
- GitHub as source control
- environment variables for secrets
- simple deployment before advanced infrastructure

---

# Scalability

The main bottleneck is the AI workflow because the application depends on AI response quality and availability.

The MVP is not designed for high traffic.

Future scalability improvements may include:

- better caching
- background processing
- queue-based execution
- separate frontend and backend deployment
- database persistence
- user accounts
- scheduled job search workflows

The current architecture is intentionally simple but modular enough to support future extension.

---

# Architectural Tradeoffs

The following compromises were accepted for the MVP:

## Static CV profile instead of CV upload

Reason:

- faster implementation
- cleaner validation
- easier demo flow
- fewer parsing problems

Tradeoff:

- less flexible for multiple users

## Pasted job ad text instead of job ad URL

Reason:

- avoids scraping issues
- avoids LinkedIn access problems
- gives the AI clean input

Tradeoff:

- user must copy and paste the job ad manually

## Browser print/save as PDF instead of direct PDF generation

Reason:

- avoids PDF rendering complexity
- easier MVP delivery
- reliable enough for demo use

Tradeoff:

- less polished than built-in PDF export

## FastAPI backend instead of Streamlit-only app

Reason:

- cleaner separation of frontend and backend
- easier future API usage
- better place for validation, logging and rate limiting

Tradeoff:

- more project complexity than a pure Streamlit app

## No local model fallback in MVP

Reason:

- CV and interview preparation require high-quality language output
- local model setup would add complexity
- fallback quality may be inconsistent

Tradeoff:

- app depends on external AI API availability

---

# Future Improvements

Potential future improvements:

1. Upload CV as PDF or Word document.
2. Parse LinkedIn profile if technically and legally possible.
3. Accept job ad URL instead of pasted job ad text.
4. Generate PDF directly inside the application.
5. Add user accounts and saved CV versions.
6. Add job board API integration.
7. Schedule weekly job search based on real fit instead of job title alerts.
8. Add email notifications.
9. Add optional local model / privacy mode.
10. Add multiple CV templates.

---

# Architecture Principles

- Simplicity is preferred over unnecessary features.
- Reliability is preferred over speed and quantity.
- User control is preferred over complete automation.
- AI should assist, not replace the user.
- Every component should have clear responsibility.
- AI output must be validated before it is trusted.
- MVP should stay simple, but not structurally messy.
