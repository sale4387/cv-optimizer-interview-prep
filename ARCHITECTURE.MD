# Architecture

This document answers one question:

> **How does the system work?**

It describes the technical architecture, component responsibilities, AI workflow, validation strategy, persistence, error handling and deployment direction.

---

# Architecture Overview

This project is a web-based AI application that helps a user tailor an existing CV to a specific job ad and prepare for a potential interview.

The MVP uses a predefined structured CV profile already stored in the application. The user does not upload a CV in V1.

The user provides:

- selected CV profile
- job ad text
- company name in the required format

The system generates structured output containing:

- role fit assessment
- optimized CV suggestions
- gap analysis
- company research
- interview preparation material

The application follows a validation-first workflow.

AI output is not trusted automatically. It must be cleaned, parsed and validated before being shown to the user or stored in the database.

Firestore is used to store:

- reusable company research
- saved application results
- tailored CV JSON versions
- gap analysis
- interview preparation material

---

# High-Level Architecture

The main components are:

- **Frontend**
- **Backend**
- **AI Layer**
- **Research Layer**
- **Validation Layer**
- **Storage Layer**
- **Logger**
- **External Services**
- **Scheduler** _(future component)_

---

## Frontend

The frontend is built with Streamlit.

It is responsible for:

- displaying the current CV profile
- collecting job ad text
- allowing the user to select an existing company
- allowing the user to add a new company
- validating the expected company name format
- showing role fit results
- showing the optimized CV preview
- showing company research
- showing interview preparation material
- allowing section-level revision requests
- allowing the user to download an accepted final CV as a directly generated PDF

Existing companies are shown in a dropdown.

If the company does not exist, the user enters it in this format:

```text
Company Name - ISO2 Country Code
```

Example:

```text
Bird - NL
```


Planned UI direction:

- the default page should show the base CV first
- the optimization form and `My Applications` navigation should live in the sidebar
- after optimization, suggested changes should be shown inline against the existing CV content
- the completion modal should be replaced by the CV preview updating directly
- change requests should later be available on each editable CV element, including summary, responsibility bullets and achievement bullets

---

## Backend

The backend is built with FastAPI.

It is responsible for:

- receiving frontend requests
- validating input
- loading the selected CV profile
- checking Firestore for reusable data
- deciding whether an AI call is required
- preparing prompts
- calling the AI layer
- cleaning AI responses
- validating structured JSON
- handling retries
- storing validated results
- returning validated output to the frontend
- logging workflow events

FastAPI is used intentionally even though Streamlit could technically call the AI workflow directly.

The reason is to:

- separate frontend and backend responsibilities
- create clear API contracts
- allow future use of the workflow by another client
- centralize validation, authentication, rate limiting and logging

---

## AI Layer

The AI layer is responsible for:

- estimating role fit
- generating CV optimization suggestions
- generating gap analysis
- generating company research when required
- generating interview questions
- generating suggested answer directions
- revising selected sections based on user feedback

The AI layer uses:

- stored CV profile
- job ad text
- company name
- existing company research when available
- system instructions
- expected JSON schemas

The AI must not invent:

- employers
- employment dates
- education
- certifications
- experience
- achievements
- unsupported tools or skills

---

## Research Layer

The research layer is responsible for obtaining reusable company information.

It follows this logic:

1. Check whether the company already exists in Firestore.
2. Check whether the stored company research is valid and reusable.
3. If valid research exists, reuse it.
4. If no valid research exists, call Gemini with search grounding.
5. Validate the returned company research.
6. Store the validated result in Firestore.

Company research may include:

- company overview
- products and services
- industry context
- customers or customer types
- competitors
- recent relevant news
- publicly available employee sentiment
- source information where available

If enough reliable information cannot be found, the system must clearly mark the result as limited.

---

## Validation Layer

The validation layer ensures that data is safe and usable.

It validates:

- user input
- company name format
- AI responses
- stored Firestore documents
- CV changes
- revision results

It checks:

- whether a response exists
- whether JSON can be extracted
- whether JSON can be parsed
- whether required keys exist
- whether values have correct types
- whether required fields are non-empty
- whether allowed enum values are used
- whether CV changes only affect allowed fields
- whether forbidden CV fields remain unchanged
- whether revision output only changes the selected section

---

## Storage Layer

The storage layer uses Firebase Firestore.

It is responsible for storing and retrieving structured application data.

The MVP uses two collections:

### `companies`

Stores reusable company research.

Example fields:

- company key
- display name
- normalized company name
- company research
- products and services
- competitors
- recent news
- employee sentiment
- sources
- generated timestamp
- schema version
- prompt version

### `applications`

Stores one record per processed application.

Example fields:

- profile ID
- company key
- job title
- job ad text or hash
- fit assessment
- tailored CV
- gap analysis
- interview preparation
- created timestamp
- base CV version
- schema version
- prompt version
- model version

The storage layer allows the system to:

- reuse company research
- avoid unnecessary search calls
- reopen saved tailored CV versions
- reuse complete application results when the input is an exact match
- support direct PDF rendering from accepted application records

Firestore access must go through the FastAPI backend.

The Streamlit frontend must not access Firestore directly.

---

## Logger

The logger records important workflow events.

It records:

- workflow start and completion
- AI call failures
- cleaner failures
- validation failures
- retry attempts
- Firestore cache hits
- Firestore cache misses
- Firestore read failures
- Firestore write failures
- company research refreshes

The logger is used for debugging and development visibility.

It is not intended for complex analytics or reporting.

---

## External Services

The MVP depends on:

- Gemini API
- Gemini search grounding
- Firebase Firestore

Future versions may add:

- job board APIs
- CV parsing services
- PDF styling or template services
- email notification services

---

## Scheduler

The scheduler is not part of the MVP.

It may be introduced in V3 to:

- run periodic job searches
- evaluate job fit
- generate application preparation
- notify the user about suitable positions

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
├── db.py
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
- CV data is stored as structured JSON.
- AI models and validation logic are separated from Streamlit UI logic.
- FastAPI acts as the backend orchestration layer.
- Firestore stores company research and application results.
- The exact file structure may change during technical grooming.

---

# Main Components

## Frontend

### Responsibilities

- collect user input
- display existing company options
- allow new company input
- show processing state
- display validated AI output
- render CV preview
- render company research
- render interview preparation
- allow section revision requests
- support direct PDF download after CV acceptance

### Inputs

- selected CV profile
- job ad text
- selected or newly entered company name

### Outputs

- request sent to backend
- rendered fit result
- rendered CV preview
- rendered company research
- rendered interview preparation

---

## Backend

### Responsibilities

- receive frontend request
- validate input
- load stored CV profile
- check Firestore for existing company research
- check Firestore for exact application match
- return reusable stored data when appropriate
- build AI prompts
- call AI workflows
- clean AI responses
- validate AI responses
- store validated results
- return structured output

### Inputs

- frontend request
- stored CV profile
- configuration
- prompt instructions
- Firestore data

### Outputs

- validated workflow result
- stored application result
- structured error response

---

## AI Layer

### Responsibilities

- estimate role fit
- optimize the CV
- generate gap analysis
- generate company research when required
- generate interview preparation
- revise selected sections

### Inputs

- CV profile
- job ad text
- company research
- company name
- prompt instructions
- expected output schema

### Outputs

- structured JSON responses

---

## Validation Layer

### Responsibilities

- reject invalid AI output
- validate Firestore documents
- prevent unsupported CV changes
- ensure output can be rendered
- ensure revisions only affect selected sections

### Inputs

- raw or cleaned AI response
- expected schema
- original CV profile
- stored data

### Outputs

- validated result
- validation error

---

## Storage Layer

### Responsibilities

- store company research
- retrieve company research
- store application records
- retrieve exact matching application records
- return hit, miss or invalid status

### Inputs

- company key
- profile ID
- job ad hash
- application data
- company research data

### Outputs

- company research record
- application record
- storage status

---

## Logger

### Responsibilities

- record workflow events
- record AI failures
- record cleaner failures
- record validation failures
- record retry attempts
- record Firestore operations

---

# Data Flow

1. The user opens the Streamlit application.
2. The user selects a predefined CV profile.
3. The user pastes the job ad text.
4. The user selects an existing company from the dropdown.
5. If the company does not exist, the user adds it using the required format.
6. Streamlit sends the request to the FastAPI backend.
7. The backend validates the input.
8. The backend loads the selected CV profile.
9. The backend checks Firestore for an exact matching application result.
10. An exact match requires compatible:
    - profile ID
    - job ad hash
    - schema version
    - prompt version

11. If an exact application match exists, the backend returns it.
12. If no exact application match exists, the backend checks the `companies` collection.
13. If valid company research exists, it is reused.
14. If company research does not exist or is not reusable:
    - Gemini search grounding is called
    - the response is cleaned
    - the response is validated
    - validated company research is stored in Firestore

15. The backend builds the main AI prompt using:
    - CV profile
    - job ad text
    - company name
    - company research
    - system rules
    - expected JSON structure

16. Gemini generates the main workflow response.
17. The response cleaner extracts usable JSON.
18. The validation layer checks:
    - structure
    - types
    - required fields
    - fit behavior
    - forbidden CV changes

19. If validation passes, the backend stores the application result in Firestore.
20. The backend returns the validated result to Streamlit.
21. Streamlit renders:
    - fit assessment
    - CV preview
    - gap analysis
    - company research
    - interview preparation

22. The user reviews the result.
23. The user may request a revision of one section.
24. The backend runs the targeted revision workflow.
25. Only the selected section is replaced.
26. After acceptance, the user can download the CV as a directly generated PDF.

---

# AI Workflows

The system has three AI workflows.

## 1. Conditional Company Research Workflow

### Purpose

Generate reusable company research only when it is not already available.

### Input

- company name
- research instructions
- expected company research schema

### Behavior

- check Firestore first
- reuse valid stored research
- call Gemini search grounding only on cache miss
- validate company research
- store validated result

### Expected Output

- company overview
- products and services
- industry context
- competitors
- recent news
- public employee sentiment
- sources where available
- warnings or limitations

---

## 2. Main Fit, CV and Interview Workflow

### Purpose

Generate the main application result.

### Input

- stored CV profile
- job ad text
- company name
- company research
- allowed and forbidden CV change rules
- required JSON schema

### Expected Output

- role fit assessment
- user-facing fit explanation
- tailored CV
- gap analysis
- interview questions
- suggested answer directions
- warnings or limitations

### Behavior

- strong fit: generate the complete result
- solid fit: generate the complete result and explain key improvements
- stretch fit: generate the result with clear warnings and preparation advice
- poor fit:
  - stop CV tailoring
  - do not generate a tailored CV
  - return missing requirements
  - return preparation recommendations
  - do not provide an override in the MVP

---

## 3. Targeted Revision Workflow

### Purpose

Revise one selected section based on user feedback.

### Input

- original CV profile
- current application result
- selected section
- user comment
- original job ad context

### Expected Output

- revised selected section
- short explanation of the change

### Behavior

- only the selected section may change
- the complete CV must not be regenerated
- the same validation and safety rules apply
- the updated application result may be stored as a new version

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
- `CompanyRecord`
- `ApplicationRecord`
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
- company name follows the required format
- country code contains two valid ISO2 letters
- request payload size is acceptable

Job ad URL parsing is out of scope for the MVP.

---

## Stored Data Validation

Before reusing Firestore data, the backend validates:

- required document fields exist
- stored data matches the expected schema
- schema version is supported
- prompt version is compatible
- company key matches the request
- application hash matches the current input

Invalid stored data must not be reused.

---

## AI Response Validation

After AI responds, the backend validates:

- response exists
- JSON can be extracted
- JSON can be parsed
- required keys exist
- values have correct data types
- required strings are not empty
- lists contain the minimum expected number of items
- allowed enum values are used
- CV changes only affect allowed fields
- forbidden CV fields remain unchanged
- poor-fit behavior follows the required rule
- revision output only modifies the selected section

Forbidden CV fields include:

- name
- contact details
- employers
- employment dates
- education
- certifications
- factual achievements unsupported by the original CV

---

## Retry Strategy

The AI workflow can be attempted up to three times.

Retry may be triggered by:

- AI API failure
- empty response
- cleaner failure
- JSON parsing failure
- validation failure

If all three attempts fail:

- processing stops
- the failure is logged
- the user receives a clear error message

Firestore retry handling is separate from AI retry handling.

A Firestore failure must not automatically trigger another Gemini call.

---

# Error Handling

Expected failure cases include:

- missing user input
- invalid company name format
- AI API failure
- empty AI response
- invalid JSON
- cleaner failure
- validation failure
- incomplete research
- Firestore read failure
- Firestore write failure
- malformed stored document
- incompatible stored schema version

Handling strategy:

- log the failure
- retry only where appropriate
- stop safely after repeated failure
- do not display unvalidated output
- show a clear high-level error to the user
- avoid showing raw technical errors

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

Firestore credentials must only exist in the backend environment.

The frontend must not access Firestore directly.

Security principles:

- do not expose API keys
- do not expose Firestore credentials
- do not commit private CV data unless intentionally using demo data
- use anonymized or demo data for public deployments
- validate all user input
- validate all AI output
- validate stored database documents
- prevent AI from modifying forbidden CV fields
- avoid logging sensitive data unnecessarily

---

# Deployment

Initial development runs locally.

Possible deployment options include:

- local machine
- home server laptop
- Render
- Streamlit Community Cloud

For portfolio presentation, a live demo may be deployed later.

Deployment direction:

- local development first
- GitHub as source control
- environment variables for secrets
- simple deployment before advanced infrastructure
- Firestore accessed only through the backend

---

# Scalability

The main bottleneck is the AI workflow because the application depends on AI response quality and availability.

The MVP is not designed for high traffic.

Firestore reduces unnecessary AI calls by reusing:

- company research
- exact matching application results

Future scalability improvements may include:

- improved caching rules
- background processing
- queue-based execution
- separate frontend and backend deployment
- user accounts
- user-facing history dashboard
- scheduled job search workflows

The current architecture is intentionally simple but modular enough to support future extension.

---

# Architectural Tradeoffs

The following compromises were accepted for the MVP.

## Static CV Profile Instead of CV Upload

### Reason

- faster implementation
- cleaner validation
- fewer parsing problems
- easier testing

### Tradeoff

- less flexible for new users
- CV profiles must be prepared in advance

---

## Pasted Job Ad Text Instead of Job Ad URL

### Reason

- avoids scraping issues
- avoids login restrictions
- provides clean input

### Tradeoff

- user must copy and paste the job ad manually

---

## Direct PDF Generation Instead of Browser Print/Save as PDF

### Reason

- browser printing produced inconsistent page breaks and layout results in Streamlit
- direct PDF generation creates a predictable downloadable output
- the PDF can be generated from the validated and accepted structured CV data
- the result is easier to reopen and export from saved application records

### Tradeoff

- more implementation complexity
- PDF styling must be maintained separately from the Streamlit preview
- final visual polish may require a dedicated later task

---

## FastAPI Backend Instead of Streamlit-Only Application

### Reason

- clearer separation of responsibilities
- reusable API contracts
- centralized validation, authentication and logging
- easier future integration

### Tradeoff

- additional service
- more deployment complexity
- more potential failure points

---

## No AI Provider Fallback in MVP

### Reason

- consistent output behavior
- simpler architecture
- easier debugging and validation
- avoids provider-specific differences

### Tradeoff

- Gemini remains a single point of failure

---

## Firestore Persistence

### Reason

- reuse company research
- reduce unnecessary AI calls
- save tailored CV versions
- save application results
- support direct PDF rendering from accepted application records

### Tradeoff

- additional service dependency
- database schema and versioning are required
- Firestore errors must be handled
- more backend complexity

---

# Future Improvements

Potential future improvements:

1. Upload CV as PDF or Word document.
2. Parse a LinkedIn profile if technically and legally possible.
3. Accept a job ad URL instead of pasted text.
4. Improve PDF styling and templates.
5. Add user accounts.
6. Add a user-facing application history dashboard.
7. Add side-by-side CV version comparison.
8. Add job board API integration.
9. Schedule weekly job searches based on role fit.
10. Add email notifications.
11. Add optional local model or privacy mode.
12. Add multiple CV templates.

---

# Architecture Principles

- Simplicity is preferred over unnecessary features.
- Reliability is preferred over speed and quantity.
- User control is preferred over complete automation.
- AI should assist, not replace the user.
- Every component should have a clear responsibility.
- AI output must be validated before it is trusted.
- Stored data must be validated before it is reused.
- MVP complexity must be justified by meaningful product or learning value.
- The MVP should remain simple, but not structurally messy.
