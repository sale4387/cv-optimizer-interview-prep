# Architecture

This document answers one question:

> **How does the system work?**

It describes the final V1 technical architecture, component responsibilities, AI workflows, validation strategy, persistence, observability and Docker deployment.

---

# Architecture Overview

This project is a web-based AI application that helps a user tailor an existing CV to a specific job ad and prepare for a potential interview.

V1 uses predefined structured CV profiles already stored in the application. The user does not upload a CV in V1.

The user provides:

- selected CV profile
- job ad text
- company name in the required format

The system can produce:

- role fit assessment
- optimized CV suggestions
- gap analysis
- company research
- interview preparation material
- accepted CV PDF

The application follows a validation-first workflow.

AI output is not trusted automatically. It must be cleaned, parsed and validated before it is shown to the user or stored in Firestore.

Firestore stores:

- reusable company research
- application records
- tailored CV data
- review decisions
- workflow statuses
- interview preparation material

---

# High-Level Architecture

The final V1 components are:

- **Streamlit UI**
- **Service Layer**
- **AI Workflow Layer**
- **Validation Layer**
- **Storage Layer**
- **PDF Renderer**
- **Observability and Logging**
- **Docker and Nginx Deployment**
- **FastAPI Entry Point** _(available, but not required by the final Streamlit flow)_
- **Scheduler** _(future component)_

---

## Streamlit UI

The frontend is built with Streamlit.

It is responsible for:

- displaying the selected CV profile
- collecting job ad text
- allowing the user to select an existing company
- allowing the user to add a new company
- validating basic input before workflow execution
- showing role fit results
- showing gap analysis
- showing company research
- showing the tailored CV
- showing AI suggestions inline against current CV content
- collecting accept, keep-original and targeted-revision decisions
- preventing CV acceptance until review decisions are resolved
- starting Interview Prep on demand
- allowing the user to download an accepted CV as a directly generated PDF
- reopening saved applications from Firestore

Existing companies are shown in a dropdown.

If the company does not exist, the user enters it in this format:

```text
Company Name - ISO2 Country Code
```

Example:

```text
Bird - NL
```

The final V1 UI is CV-first:

- the selected candidate CV is the primary view
- optimization and saved-application navigation are available from the interface
- suggested changes are shown inline
- the user decides whether to accept the suggestion, keep the original or request a revision
- the accepted application becomes the source for PDF generation and Interview Prep

Bookmarkable portfolio routes are provided through Nginx:

```text
/sale
/svetlana
```

These routes redirect to the correct Streamlit profile query parameters.

---

## Service Layer

The service layer is the main orchestration layer used by the final Streamlit flow.

It is responsible for:

- loading the selected CV profile
- validating workflow prerequisites
- creating and updating application records
- deciding when an AI workflow should run
- deciding when stored company research may be reused
- preserving valid CV data when a supporting workflow fails
- coordinating inline review decisions
- coordinating targeted revisions
- enforcing draft and accepted application rules
- starting Interview Prep on demand
- preparing accepted CV data for PDF generation
- reading and writing Firestore records
- returning controlled results to the UI

Business decisions belong in the service layer rather than in Streamlit, Firestore helpers or AI clients.

Examples include:

- whether a cached company record is fresh and valid
- whether CV tailoring is allowed for the fit category
- whether all review decisions are resolved
- whether the application may move from `draft` to `accepted`
- whether PDF export is allowed
- whether Interview Prep has enough valid input to run

---

## FastAPI Entry Point

FastAPI remains available in the repository as an API entry point.

It supports:

- request models
- authentication
- rate limiting
- structured API errors
- future use by another frontend or integration

However, the final V1 Streamlit application calls the service layer directly.

FastAPI is therefore:

- useful for API testing and future reuse
- not required for the current Streamlit Docker deployment
- not started as a separate Docker Compose service in V1

This avoids unnecessary deployment complexity while preserving the option to expose the workflow as an API later.

---

## AI Workflow Layer

The AI layer is divided into focused workflows rather than one large call.

The final V1 uses four AI workflows:

1. CV Optimization
2. Company Research
3. Interview Prep
4. Targeted Revision

Each workflow has its own:

- prompt
- expected structured output
- cleaner and parsing path
- validation rules
- retry behavior
- controlled failure result

The original CV remains the factual source of truth.

The AI must not invent:

- employers
- employment dates
- education
- certifications
- experience
- achievements
- unsupported tools or skills

---

## 1. CV Optimization Workflow

### Purpose

Assess fit and produce a tailored CV proposal based only on documented candidate facts.

### Input

- original CV profile
- job ad text
- company and role context
- allowed and forbidden CV change rules
- expected output schema

### Expected Output

- fit category
- fit explanation
- tailored CV proposal
- gap analysis
- warnings or limitations

### Behavior

- `strong`, `solid` and `stretch` fit may produce a tailored CV
- `poor` fit stops CV tailoring
- poor fit still returns useful explanation and gap guidance
- the original CV remains unchanged
- the generated application is stored as `draft`
- later review decisions determine the final accepted CV

---

## 2. Company Research Workflow

### Purpose

Generate reusable company research independently from CV Optimization.

### Input

- company name
- country context
- research instructions
- expected company-research schema

### Behavior

1. Normalize the company identity into `company_key`.
2. Check Firestore for an existing company record.
3. Validate the stored record and its freshness.
4. Reuse valid research when available.
5. Call Gemini research only when a valid reusable record is unavailable.
6. Clean and validate the AI response.
7. Store the validated result in the `companies` collection.
8. Attach the relevant company context or reference to the application.

Company research may include:

- company overview
- products and services
- industry context
- customers or customer types
- competitors
- recent relevant news
- publicly available employee-sentiment themes
- sources and limitations where available

Company Research is a supporting workflow.

If it fails:

- the valid CV result remains available
- the application remains usable
- Interview Prep may still run with less company-specific context
- V1 does not provide a manual Company Research retry button

---

## 3. Interview Prep Workflow

### Purpose

Generate interview preparation after the CV has been accepted.

### Input

- original CV
- accepted tailored CV
- job ad
- fit and gap context
- company research when available
- expected Interview Prep schema

### Expected Output

- approximately 10–15 likely interviewer questions
- answer directions
- relevant evidence from the candidate’s background
- preparation guidance
- questions the candidate may ask the interviewer

### Behavior

- the workflow is started on demand
- an accepted CV is required
- the accepted CV defines what the candidate must be prepared to defend
- the original CV remains available as the factual boundary
- company research is used when available
- the workflow may still run without company research
- the validated result is stored inside the application record

Interview Prep failure does not invalidate the accepted CV.

---

## 4. Targeted Revision Workflow

### Purpose

Revise only selected CV content based on user feedback.

### Input

- original CV
- current tailored CV
- selected field or bullet
- user revision comment
- job ad context

### Expected Output

- revised selected content
- validated structured result

### Behavior

- only the selected content may change
- the complete CV must not be regenerated
- protected facts must remain unchanged
- the result must pass revision-scope validation
- the revised value is merged into the current tailored CV
- unresolved review decisions continue to block CV acceptance

---

## Validation Layer

The validation layer ensures that AI and stored data are safe and usable.

It validates:

- user input
- company format and normalized identifiers
- cleaned AI responses
- Pydantic models
- business rules
- stored Firestore documents
- CV changes
- targeted revision scope
- application-state transitions
- PDF prerequisites

It checks:

- whether a response exists
- whether JSON can be extracted
- whether JSON can be parsed
- whether required keys exist
- whether values have correct types
- whether required fields are non-empty
- whether allowed enum values are used
- whether CV changes affect only supported fields
- whether protected CV facts remain unchanged
- whether poor-fit behavior follows the required rule
- whether revision output changes only the selected content
- whether all review decisions are resolved before acceptance
- whether PDF export is requested only for an accepted application

Raw AI text is never treated as a final result.

The normal path is:

```text
prompt → Gemini response → cleaner → JSON parsing → Pydantic validation → business validation
```

---

## Storage Layer

The storage layer uses Firebase Firestore.

The MVP uses two main collections.

### `companies`

Stores reusable company research.

Typical fields include:

- `company_key`
- display name
- normalized company name
- country code
- company research
- sources
- limitations
- generated timestamp
- schema version
- prompt version

A company record is reused only when it is valid and sufficiently fresh.

### `applications`

Stores one record per application workflow.

Typical fields include:

- `application_id`
- `profile_id`
- `company_key`
- job title
- job ad text
- fit assessment
- tailored CV
- gap analysis
- company context or reference
- interview preparation
- inline review decisions
- application status
- workflow statuses
- created and updated timestamps
- schema and prompt metadata

Application status:

```text
draft → accepted
```

Supporting workflow statuses track areas such as:

- CV Optimization
- Company Research
- Interview Prep
- PDF export

The storage layer enables the system to:

- reopen saved applications
- preserve accepted CV data
- reuse company research
- store Interview Prep with the application
- keep supporting-workflow failures isolated
- generate PDF output from accepted structured data

The final Streamlit flow reaches Firestore through service-layer functions.

Firestore access is not required to pass through FastAPI in V1.

---

## Inline Review and Acceptance

The inline review layer supports three decisions:

- `accepted_suggestion`
- `kept_original`
- `revision_requested`

Behavior:

- `accepted_suggestion` applies the AI proposal
- `kept_original` preserves the original content and ordering
- `revision_requested` runs the targeted revision workflow
- an empty AI bullet suggestion is displayed as `Remove this bullet`
- accepting that suggestion removes the bullet

`Save all decisions`:

- validates that all decisions are resolved
- runs required targeted revisions
- merges accepted and kept content into the tailored CV
- stores the completed review state

`Accept CV` remains blocked until the review state is valid.

After acceptance:

- application status becomes `accepted`
- direct PDF generation is enabled
- Interview Prep may be generated on demand

---

## PDF Renderer

The PDF renderer creates a downloadable CV from accepted structured CV data.

It is responsible for:

- validating accepted application input
- rendering supported CV sections
- applying predictable page layout
- handling Unicode text
- returning downloadable PDF bytes
- failing with a controlled user-facing message

The Docker image installs the DejaVu font package required by the PDF renderer.

The PDF is generated only after:

- all inline-review decisions are resolved
- the review result is saved
- the application is accepted

Browser Print / Save as PDF is not the primary V1 export flow.

---

## Observability and Logging

The project records operational information for debugging and workflow analysis.

Examples include:

- workflow start and completion
- workflow duration
- AI call duration
- retry and attempt count
- cleaner failures
- validation failures
- Firestore reads and writes
- company-research cache hits and misses
- error type and controlled error message
- PDF generation start and failure

Logs must not contain:

- Gemini API keys
- Firebase private keys
- access tokens
- `.env` contents
- credential JSON contents

Observability is intended for development, reliability and portfolio explanation, not for advanced analytics.

---

## External Services

V1 depends on:

- Gemini API
- Gemini research/search capabilities
- Firebase Firestore

Future versions may add:

- job-board APIs
- CV parsing services
- job-alert email ingestion
- notification services
- optional alternative AI providers

---

## Scheduler

The scheduler is not part of V1.

It may be introduced in V3 to:

- process job alerts
- run periodic job searches
- evaluate job fit
- prepare application materials
- notify the user about suitable positions

---

# Project Structure

The final structure is organized by responsibility:

```text
project/
├── .env.example
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── README.md
├── PROJECT_SCOPE.md
├── ARCHITECTURE.md
├── PROJECT_BOARD.md
├── DECISIONS.md
├── requirements.txt
├── api.py
├── api_models.py
├── config.py
├── firebase.py
├── logger.py
├── observability.py
├── security.py
├── rate_limit.py
├── error_handlers.py
├── streamlit/
│   └── app.py
├── ui/
├── services/
├── ai/
├── cv_data/
├── nginx/
│   └── default.conf
└── tests/
```

Notes:

- `.env` is local and must not be committed.
- Firebase service-account JSON is mounted at runtime and must not be committed.
- CV data is stored as structured JSON.
- Streamlit UI logic is separated from services and AI workflows.
- Firestore persistence logic is isolated from UI rendering.
- Docker deployment contains one Streamlit application container and one Nginx proxy container.

---

# Final V1 Data Flow

## Application Creation

1. The user opens `/sale`, `/svetlana` or the normal Streamlit route.
2. Nginx redirects the bookmark route to the correct Streamlit profile query.
3. Streamlit loads the selected predefined CV profile.
4. The user selects or enters a company.
5. The user pastes the job ad.
6. Streamlit calls the application service.
7. The service validates input and loads the original CV.
8. The CV Optimization workflow runs.
9. The response is cleaned and validated.
10. The valid application is stored as `draft`.
11. Company Research is loaded from Firestore or generated separately.
12. Company Research status is stored without invalidating the CV result.
13. Streamlit renders fit, gaps, research and inline CV suggestions.

## Review and Acceptance

1. The user reviews each supported change.
2. The user accepts the suggestion, keeps the original or requests a revision.
3. Targeted revisions run only for selected content.
4. `Save all decisions` validates and merges the review result.
5. `Accept CV` becomes available.
6. The accepted application is stored with status `accepted`.

## PDF and Interview Prep

1. The user generates the CV PDF from the accepted application.
2. The PDF renderer validates the accepted state and generates the file.
3. The user may start Interview Prep on demand.
4. Interview Prep uses the original CV, accepted CV, job ad and available company context.
5. The validated Interview Prep result is stored inside the application.

---

# Data Models

The implementation uses structured Pydantic and domain models for concepts such as:

- CV profile
- application input
- fit assessment
- tailored CV and CV patch
- gap analysis
- company research
- company record
- application record
- interview questions
- interview preparation
- inline review decisions
- targeted revision request and result
- workflow statuses

The exact class names are defined in the codebase.

---

# Retry Strategy

Retry behavior is workflow-specific rather than one global rule.

Retries may be triggered by:

- AI API failure
- empty response
- cleaner failure
- JSON parsing failure
- schema-validation failure
- quality-gate failure

Each workflow defines:

- its maximum number of attempts
- which failures are retryable
- what controlled result is returned after final failure

Firestore retry handling is separate from AI retry handling.

A Firestore failure must not automatically trigger another Gemini call.

A supporting-workflow failure must not overwrite valid CV data.

---

# Error Handling

Expected failure cases include:

- missing user input
- invalid company format
- AI API failure
- empty AI response
- invalid JSON
- cleaner failure
- Pydantic validation failure
- business-validation failure
- incomplete company research
- Firestore read or write failure
- malformed stored document
- PDF rendering failure
- missing deployment configuration

Handling strategy:

- log the failure safely
- retry only where appropriate
- stop the affected workflow after final failure
- do not display unvalidated output
- show a clear high-level error to the user
- preserve already valid workflow data
- avoid exposing raw secrets or credential content

---

# Security

Secrets are stored using:

- local `.env`
- deployment environment configuration
- mounted Firebase service-account JSON

Secrets must not be committed to Git or copied into the Docker image.

The repository includes:

- `.env.example`
- `.gitignore`
- `.dockerignore`

FastAPI endpoints can be protected with:

- API-key authentication
- rate limiting
- request validation

The final Streamlit Docker flow is intended for a trusted local-network portfolio demo.

Security principles:

- do not expose API keys
- do not expose Firebase credentials
- do not log secret values
- validate user input
- validate AI output
- validate stored database documents
- prevent AI from modifying protected CV facts
- keep local credentials outside source control
- do not treat the local-network deployment as a public production service

---

# Docker Deployment

The final V1 deployment uses Docker Compose on a user-owned Ubuntu home-server laptop.

Services:

### `cv-app`

- runs the Streamlit application
- listens internally on port `8501`
- loads `.env`
- mounts Firebase credentials read-only
- exposes a Streamlit health endpoint
- writes logs to container output

### `cv-proxy`

- runs Nginx
- exposes the configured host port, normally `8502`
- proxies HTTP and WebSocket traffic to `cv-app`
- provides `/sale` and `/svetlana` bookmark routes
- preserves the original Host header and external port
- waits for the application health check

Request flow:

```text
browser → Nginx proxy → Streamlit application → service layer
```

External dependencies are then reached from the service layer:

```text
service layer → Gemini API
service layer → Firestore
```

The deployment supports:

- repeatable local build
- browser access from the home network
- container restart
- persistent Firestore data
- PDF generation inside Docker
- visible logs
- secret files outside Git

Public hosting, a domain, HTTPS and advanced cloud infrastructure are outside V1.

---

# Scalability

The MVP is designed for personal use and portfolio demonstration, not high traffic.

The main limitations are:

- dependency on Gemini availability and output quality
- synchronous workflow execution
- single-user-oriented UI
- no background queue
- no user-account isolation
- home-server local-network deployment

Firestore reduces unnecessary AI calls by reusing company research.

Future scalability improvements may include:

- background processing
- queue-based execution
- public frontend and API deployment
- authentication and user accounts
- application-history UI
- more advanced caching
- scheduled job-discovery agents
- notification workflows

---

# Architectural Tradeoffs

## Static CV Profiles Instead of CV Upload

### Reason

- faster implementation
- cleaner validation
- fewer parsing problems
- easier testing

### Tradeoff

- less flexible for new users
- CV profiles must be prepared in advance

---

## Pasted Job Ad Instead of URL Processing

### Reason

- avoids scraping and login restrictions
- provides predictable input
- keeps V1 focused

### Tradeoff

- user must copy and paste the job ad manually

Job-ad URL processing with pasted-text fallback is planned for V2.

---

## Separate AI Workflows Instead of One Large Call

### Reason

- clearer responsibilities
- better validation
- independent retries
- failure isolation
- reusable company research
- Interview Prep can run on demand after CV acceptance

### Tradeoff

- more orchestration code
- more workflow statuses
- more validation paths

---

## Direct PDF Generation Instead of Browser Print

### Reason

- predictable downloadable output
- accepted structured data can be rendered consistently
- saved applications can be reopened and exported

### Tradeoff

- PDF layout must be maintained separately
- Unicode fonts must be available in the runtime
- template polish remains limited in V1

---

## Streamlit Calling the Service Layer Directly

### Reason

- simpler Docker deployment
- avoids an unnecessary internal API hop
- keeps the final V1 demo reliable
- preserves modular business logic

### Tradeoff

- Streamlit is coupled to the Python service layer
- FastAPI is not demonstrated in the primary deployed path

FastAPI remains available for future external clients.

---

## Nginx Reverse Proxy

### Reason

- clean `/sale` and `/svetlana` routes
- WebSocket proxy support
- one controlled external port
- easier future addition of domain and HTTPS

### Tradeoff

- a second container is required
- proxy headers and redirects require correct configuration

---

## No AI Provider Fallback in V1

### Reason

- consistent output behavior
- simpler prompts and validation
- easier debugging

### Tradeoff

- Gemini remains a single point of failure

---

## Firestore Persistence

### Reason

- reuse company research
- save applications and review state
- save Interview Prep
- reopen accepted CV versions
- preserve data across container restarts

### Tradeoff

- additional external dependency
- schema validation and versioning are required
- credential management is required

---

# Known Architectural Limitations

- V1 supports only predefined CV profiles.
- Job ads are pasted manually.
- Company Research has no manual retry button after failure.
- Workflows run synchronously.
- The deployment is intended for the local network.
- There are no user accounts or multi-user authorization.
- FastAPI is not part of the primary deployed request path.
- PDF layout options are limited.
- Gemini remains the only AI provider.

---

# Future Improvements

Potential future improvements:

1. Upload and parse PDF or Word CV files.
2. Accept job-ad URLs with pasted-text fallback.
3. Add manual Company Research retry.
4. Add broader profile management.
5. Add user accounts and history UI.
6. Add alternative CV templates.
7. Add public hosting, domain and HTTPS.
8. Add job-board and job-alert ingestion.
9. Add scheduled agentic job discovery.
10. Add candidate notifications.
11. Add background processing and queues where justified.
12. Add optional AI-provider fallback or privacy mode.
13. Expand observability and agent-quality checks.

---

# Architecture Principles

- Simplicity is preferred over unnecessary features.
- Reliability is preferred over speed and quantity.
- User control is preferred over complete automation.
- AI should assist, not replace the user.
- Every component should have a clear responsibility.
- The original CV remains the factual source of truth.
- AI output must be validated before it is trusted.
- Stored data must be validated before it is reused.
- Supporting-workflow failures must not destroy valid results.
- MVP complexity must be justified by meaningful product or learning value.
