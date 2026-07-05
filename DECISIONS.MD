# Decisions

This document answers one question:

> **Why did we choose this approach instead of another one?**

It records important product, architecture, technical and development workflow decisions made during the project.

---

# Purpose

This document records decisions that materially affect:

- product scope
- user experience
- technical architecture
- AI workflow
- validation and reliability
- development approach
- future expansion

Each decision explains:

- the context in which the decision was required
- the alternatives that were considered
- the selected direction
- the reasoning behind it
- the accepted tradeoffs
- the consequences for the project
- the conditions under which the decision should be reviewed

---

# Decision Template

Use this template for every important future decision.

## DECISION-XXX — Decision Title

### Status

Proposed / Accepted / Rejected / Replaced

### Context

Explain:

- what problem or situation required a decision
- which constraints existed
- why the decision was needed

### Options Considered

List the realistic alternatives and their main advantages and disadvantages.

### Decision

State:

- which option was selected
- what exactly was decided
- whether the decision applies only to the MVP or represents a long-term direction

### Reasoning

Explain:

- why the selected option is appropriate for this project
- how it supports the product scope
- how it improves reliability, simplicity, usability or learning value

### Tradeoffs

Explain:

- what is lost by choosing this option
- which risks are introduced
- which limitations are accepted

### Consequences

Explain:

- which parts of the system are affected
- what future tasks must take into account
- what becomes easier or more difficult

### Review Later

Explain:

- when the decision should be reviewed
- what evidence would justify changing it
- whether it is likely to change in a future version

---

# Accepted Decisions

## DECISION-001 — Static Stored CV Profile for MVP

### Status

Accepted

### Context

The application needs a reliable representation of the user’s current CV before the AI can compare it with a job ad and generate tailored suggestions.

Allowing users to upload PDF or Word files would require document parsing, layout interpretation, normalization and additional validation.

The purpose of the MVP is to validate the core AI workflow before introducing document ingestion complexity.

### Options Considered

1. **Upload PDF or Word CV**

   Pros:
   - familiar input format for users
   - supports self-service use
   - allows different users to upload their own CV

   Cons:
   - requires document parsing
   - CV layouts, tables and columns may be interpreted incorrectly
   - requires additional normalization and validation
   - increases development and testing complexity

2. **Import data from LinkedIn**

   Pros:
   - potentially convenient for users
   - reduces the need to maintain a separate CV file

   Cons:
   - access and scraping limitations
   - privacy and legal concerns
   - profiles may be incomplete or outdated
   - additional integration complexity

3. **Use a predefined structured CV profile**

   Pros:
   - stable and predictable input
   - easy to validate
   - easy to render as a web CV
   - avoids document parsing problems

   Cons:
   - users cannot upload their own CV in the MVP
   - profiles must be prepared manually

### Decision

The MVP will use predefined structured CV profiles stored as JSON.

Streamlit will render the stored profile as a web-based CV.

CV upload and automatic document parsing are postponed to a later version.

### Reasoning

A structured CV profile provides:

- stable input for the AI workflow
- easier validation of AI changes
- no parsing errors
- faster MVP delivery
- a reusable CV representation for the portfolio website

This allows the project to focus on its main value:

- role fit assessment
- CV tailoring
- gap analysis
- company research
- interview preparation

### Tradeoffs

The MVP is limited to CV profiles prepared in advance.

New users cannot independently upload their CV.

Updating a profile requires changing the structured source data.

The reduced flexibility is accepted in exchange for a more reliable and testable MVP.

### Consequences

The system does not require:

- PDF parsing
- Word parsing
- layout interpretation
- CV normalization

The frontend renders structured CV data.

The backend and AI workflow operate on a known JSON structure.

### Review Later

Review this decision when:

- V2 development begins
- self-service CV upload is required
- external users need to use the product
- reliable document parsing becomes a product priority

---

## DECISION-002 — Pasted Job Ad Text Instead of Job Ad URL

### Status

Accepted

### Context

The application needs the full content of a job ad.

Direct access through a URL may fail because:

- the AI model may not have access to the page
- the website may require login
- LinkedIn and similar platforms may restrict scraping
- the content may be loaded dynamically
- the page structure may change

A reliable MVP input method was required.

### Options Considered

1. **Allow the AI or a search tool to access the job ad URL**

   Pros:
   - convenient user experience
   - no manual copying required

   Cons:
   - access is not guaranteed
   - some pages require authentication
   - results depend on provider capabilities

2. **Scrape the job ad through the backend**

   Pros:
   - keeps data collection under application control
   - potentially supports many job websites

   Cons:
   - scraping logic must be developed and maintained
   - different websites require different handling
   - legal and access restrictions may apply
   - dynamic pages may be difficult to process

3. **Require the user to paste the job ad text**

   Pros:
   - reliable and simple
   - no scraping required
   - provides the complete text directly to the workflow
   - works regardless of the job platform

   Cons:
   - requires an additional action from the user
   - the user may accidentally omit part of the job ad
   - some formatting may be lost

### Decision

The MVP will require the user to copy and paste the job ad text.

Job ad URL ingestion is postponed to a later version.

### Reasoning

Pasted text is the most reliable MVP option because it:

- does not depend on website access
- does not require scraping
- avoids login and dynamic page problems
- gives the AI direct access to the relevant content
- keeps the workflow simple and predictable

### Tradeoffs

The user must manually copy and paste the job ad.

The user may omit part of the text or copy unnecessary content.

The workflow is slightly less elegant than URL-based input.

### Consequences

The frontend provides a job ad text field.

The backend validates and processes the provided text.

The MVP does not require:

- URL fetching
- scraping
- website-specific parsers
- page content extraction

### Review Later

Review this decision when a reliable, legal and sufficiently simple job ad URL ingestion method is available.

---

## DECISION-003 — Company Name Required, Company URL Optional

### Status

Accepted

### Context

The application needs to identify the target company in order to generate:

- company background
- products and services
- competitors
- recent news
- interview preparation material

Although the company name may already exist inside the job ad, relying only on AI extraction could lead to incorrect identification.

A separate input structure was required.

### Options Considered

1. **Extract the company name automatically from the job ad**

   Pros:
   - fewer fields for the user
   - smoother input flow

   Cons:
   - the company may be identified incorrectly
   - job ads may hide or omit the company name
   - additional extraction and validation are required

2. **Require both company name and company URL**

   Pros:
   - provides more precise research context
   - reduces ambiguity between companies with similar names

   Cons:
   - the user may not know the correct website
   - the URL may not provide useful information
   - an unnecessary field may block the workflow

3. **Require company name and keep company URL optional**

   Pros:
   - provides stable company identification
   - improves prompt quality and validation
   - allows additional disambiguation when the URL is available
   - keeps the required input simple

   Cons:
   - adds one required user action
   - users may still enter incorrect information

### Decision

The company name will be a required input.

The company website URL will be optional.

### Reasoning

A separate company name field provides:

- more reliable input
- easier validation
- better company research
- less dependence on AI extraction
- cleaner prompt construction

The optional URL may improve research quality or help distinguish between companies with similar names.

### Tradeoffs

The user must enter information that may already appear in the job ad.

Incorrect company information may produce incorrect research results.

Company information may still be limited even when the correct name is provided.

### Consequences

The frontend requires:

- company name
- optional company website URL
- job ad text

The backend validates the company name separately from the job ad.

The research workflow can use the optional website URL as supporting context.

### Review Later

Review this decision if company extraction from job ads becomes reliable enough to automatically populate the field for user confirmation.

---

## DECISION-004 — FastAPI Backend Instead of Streamlit-Only Application

### Status

Accepted

### Context

The application could be built entirely inside Streamlit, with the UI directly calling the AI workflow.

A decision was required whether to keep the architecture minimal or introduce a separate FastAPI backend.

### Options Considered

1. **Streamlit-only application**

   Pros:
   - simplest architecture
   - easier local development
   - fewer services
   - simpler deployment

   Cons:
   - UI and backend logic become more tightly coupled
   - harder to reuse the workflow from another client
   - validation, authentication and rate limiting remain inside the UI application

2. **Streamlit frontend with FastAPI backend**

   Pros:
   - clear separation of frontend and backend responsibilities
   - defined API request and response models
   - easier reuse by another frontend, scheduler or service
   - better location for validation, logging, authentication and rate limiting
   - stronger architecture demonstration in the portfolio

   Cons:
   - additional service and configuration
   - more complex deployment
   - more possible failure points
   - HTTP communication must be handled between frontend and backend

### Decision

The application will use:

- Streamlit as the frontend
- FastAPI as the backend and AI workflow entry point

Streamlit will not call the AI provider directly.

### Reasoning

FastAPI provides:

- separation of concerns
- reusable API contracts
- centralized validation
- centralized logging
- easier future integration
- a clear path toward using the workflow as an independent service

Portfolio value is an additional benefit, but the main reason is architectural separation and future reuse.

### Tradeoffs

The architecture becomes more complex than a Streamlit-only application.

The project requires:

- two application layers
- HTTP communication
- additional configuration
- separate error handling
- more deployment work

This complexity is accepted because the backend has a clear independent responsibility.

### Consequences

FastAPI becomes the main entry point for the AI workflow.

The backend is responsible for:

- request validation
- prompt construction
- AI calls
- response cleaning
- output validation
- retries
- logging
- rate limiting
- structured error responses

Streamlit remains responsible for:

- user input
- loading state
- displaying validated results
- revision controls
- CV rendering

### Review Later

Review this decision if the separate backend creates significant deployment complexity without providing meaningful separation or reuse.

---

## DECISION-005 — Browser Print/Save as PDF Instead of Direct PDF Generation

### Status

Accepted

### Context

The final tailored CV should be available as a PDF document.

A decision was required whether the application should generate the PDF directly or rely on the browser’s built-in print functionality.

### Options Considered

1. **Generate PDF directly from structured data or rendered HTML**

   Pros:
   - one-click download
   - consistent file naming
   - greater control over output
   - more polished user experience

   Cons:
   - requires an additional rendering engine
   - requires handling fonts, page breaks and layout differences
   - increases development and testing complexity

2. **Use browser Print / Save as PDF**

   Pros:
   - no PDF generation service required
   - uses the already rendered CV page
   - reliable enough for the MVP
   - significantly reduces implementation time

   Cons:
   - requires a manual user action
   - output may differ between browsers
   - less control over filenames and rendering
   - print-specific styling is still required

### Decision

The MVP will use the browser’s built-in Print / Save as PDF functionality.

Direct PDF generation is postponed to a later version.

### Reasoning

This option:

- keeps focus on the AI workflow
- avoids PDF rendering complexity
- still produces a usable document
- reduces time to MVP
- allows the final CV layout to be tested before adding a PDF engine

### Tradeoffs

The application has less control over:

- page breaks
- browser-specific rendering
- file naming
- the export process

The user must manually select Print / Save as PDF.

### Consequences

The backend does not generate PDF files.

The frontend must provide:

- clean CV preview
- print-friendly layout
- A4-compatible styling
- hidden navigation and controls during printing

### Review Later

Review this decision when:

- the main workflow is stable
- one-click export becomes important
- browser output proves inconsistent
- V2 development begins

---

## DECISION-006 — No AI Provider Fallback in MVP

### Status

Accepted

### Context

The AI workflow depends on an external model provider.

A fallback could reduce downtime, but introducing multiple providers would require:

- provider switching logic
- different API clients
- prompt and schema compatibility testing
- output quality comparison
- additional error handling

### Options Considered

1. **Use a local model as fallback**

   Pros:
   - reduced dependence on external providers
   - potential privacy and cost benefits
   - offline experimentation

   Cons:
   - inconsistent output quality
   - additional infrastructure
   - hardware requirements
   - more validation risk

2. **Use a secondary hosted provider as fallback**

   Pros:
   - improved availability
   - opportunity to compare models

   Cons:
   - additional cost
   - different output behavior
   - additional provider integration and testing
   - more complex retry and failure logic

3. **Use Gemini only in the MVP**

   Pros:
   - simplest architecture
   - consistent output behavior
   - one API contract
   - easier testing and debugging

   Cons:
   - Gemini becomes a single point of failure
   - the workflow cannot continue during provider outages

### Decision

The MVP will use Gemini as the only AI provider.

There will be no local or hosted provider fallback.

The workflow will retry Gemini up to three times and stop safely if all attempts fail.

### Reasoning

The project should first validate:

- prompt quality
- structured output
- business logic
- validation
- user experience

Adding a second provider before the main workflow is stable would increase complexity without proving core product value.

Failing clearly is preferable to silently switching to a provider with lower or inconsistent output quality.

### Tradeoffs

Gemini remains a single point of failure.

The user may not receive a result during provider outages or repeated invalid responses.

The simpler architecture and consistent behavior are accepted in exchange.

### Consequences

The backend does not require provider-switching logic.

The workflow:

1. calls Gemini
2. cleans and validates the response
3. retries when appropriate
4. stops after the third failed attempt
5. logs the failure
6. returns a clear error message to the user

Claude or another provider may be evaluated later through a separate test task, but not as an MVP fallback.

### Review Later

Review this decision if:

- Gemini availability becomes a recurring problem
- another provider reliably supports the same output contract
- a privacy or offline mode is introduced
- model comparison becomes a formal project goal

---

## DECISION-007 — AI Output Must Be JSON Validated Before Rendering

### Status

Accepted

### Context

AI responses may fail in two different ways:

- the content may be inaccurate or incomplete
- the format may be unusable by the application

The frontend needs a predictable structure for:

- fit assessment
- CV changes
- gap analysis
- company research
- interview questions
- suggested answers

Unvalidated free text cannot reliably support this workflow.

### Options Considered

1. **Accept AI output as free text**

   Pros:
   - simplest implementation
   - no schema or validation required
   - fewer rejected responses

   Cons:
   - sections cannot be rendered predictably
   - required information may be missing
   - forbidden CV changes are harder to detect
   - follow-up revisions cannot target reliable fields

2. **Require and validate structured JSON**

   Pros:
   - predictable frontend rendering
   - clear data models
   - required fields can be enforced
   - forbidden changes can be detected
   - follow-up revision workflows are easier

   Cons:
   - additional backend development
   - some otherwise useful responses may fail validation
   - retries may increase API usage

### Decision

AI output must be returned as structured JSON and validated before it is used by the application.

Unvalidated AI output will never be shown as a final result.

### Reasoning

A CV and its supporting material naturally form a hierarchical structure containing:

- key-value fields
- nested objects
- lists of experience
- lists of responsibilities
- lists of skills
- questions and answers

Structured output allows the system to:

- identify each section reliably
- compare AI changes with the original CV
- protect forbidden fields
- validate required content
- render the result consistently

### Tradeoffs

The project intentionally accepts a lower percentage of successful workflow results in exchange for higher-quality accepted results.

An API call may technically succeed while the workflow correctly rejects the response because it does not meet the required contract.

This may increase:

- retries
- response time
- API usage

### Consequences

The backend requires:

- response cleaner
- JSON parser
- Pydantic models
- structural validation
- semantic validation
- CV change validation
- retry logic

The frontend only receives validated structured data.

### Review Later

The validation principle should remain permanent.

Future reviews may change:

- the JSON schema
- validation rules
- structured output features
- provider-specific implementation

---

## DECISION-008 — Poor Fit Stops the Tailoring Workflow

### Status

Accepted

### Context

The application should improve how relevant experience is presented, but it should not create the impression that wording alone can compensate for missing essential qualifications.

A poor role fit may lead to:

- wasted application effort
- unrealistic expectations
- overly aggressive CV rewriting
- pressure to invent or exaggerate experience

### Options Considered

1. **Always generate a tailored CV**

   Pros:
   - every AI call produces a document
   - the user always receives a result
   - no application opportunity is blocked

   Cons:
   - may create false confidence
   - may encourage excessive stretching of experience
   - wastes time on clearly unsuitable roles
   - conflicts with the product’s honesty principle

2. **Stop CV tailoring when fit is below the accepted threshold**

   Pros:
   - provides an honest assessment
   - prevents misleading CV optimization
   - saves time
   - allows the tool to focus on actionable gaps

   Cons:
   - the AI may incorrectly reject a potentially suitable role
   - users cannot override the decision in the MVP
   - some API calls will not produce a tailored CV

### Decision

If the role is classified as poor fit:

- the tailored CV will not be generated
- the workflow will return an explanation
- the main missing requirements will be listed
- the user will receive preparation or learning recommendations
- the user will not be able to override the result in the MVP

### Reasoning

The product must distinguish between:

- presenting real experience more effectively
- creating qualifications that do not exist

A polished CV cannot replace essential missing requirements.

The tool should provide an honest signal instead of producing a document that suggests the user is more suitable than the available evidence supports.

### Tradeoffs

The fit assessment may produce false negatives.

A candidate may still want to apply for strategic reasons.

The user loses some control because poor fit cannot be overridden inside the MVP.

The quality of the fit classification and threshold becomes critical.

### Consequences

The system must define:

- available fit levels
- the threshold for continuing
- the threshold for stopping
- the output required for poor-fit results

The prompt, schema, business logic, frontend and tests must all support the stop condition.

### Review Later

Review this decision when:

- real test results are available
- poor-fit classifications show too many false negatives
- users request an override option
- the threshold proves too strict or too permissive

---

## DECISION-009 — AI-Assisted Development Workflow and Product Ownership Focus

### Status

Accepted

### Context

This is the third personal AI portfolio project after earlier projects that focused more heavily on:

- hands-on implementation
- backend logic
- API integration
- validation
- deployment
- debugging

The core programming patterns required for this MVP are already familiar from previous projects.

Repeating the same implementation-heavy workflow would provide less additional learning value than focusing on a different professional skill set.

The project is therefore intentionally used to practice AI Product Engineer and Technical PM ownership.

### Options Considered

1. Build the project primarily by manually writing all code again.
2. Let AI generate most of the code without strong product ownership.
3. Lead the project as product owner, technical PM, tester and reviewer while using AI assistance for implementation.

### Decision

The project owner will lead the project as:

- product designer
- product owner
- technical PM
- AI workflow designer
- tester
- reviewer

AI assistance may be used for:

- code generation
- refactoring
- implementation support
- debugging support

The project owner remains responsible for:

- product scope
- architecture direction
- AI workflow design
- documentation
- task definition
- acceptance criteria
- testing
- final approval

### Reasoning

The project is intended to demonstrate not only that a working application can be built, but that an AI product can be:

- defined
- scoped
- structured
- validated
- tested
- delivered

Previous projects already covered many required implementation patterns.

The higher-value learning goal in this project is to practice guiding AI-assisted development effectively.

### Tradeoffs

The project owner will write less implementation code manually than in earlier projects.

The tradeoff is accepted because this project focuses on:

- product thinking
- technical specification
- AI workflow design
- validation strategy
- QA
- human-in-the-loop UX
- structured documentation
- final product acceptance

### Consequences

Documentation and task quality become central project outputs.

AI-generated code must still be:

- reviewed
- understood
- tested
- integrated intentionally

The owner remains accountable for the final product even when code is generated with AI assistance.

### Review Later

No review is currently required.

The decision may be reconsidered if the project introduces a technical area that provides meaningful new hands-on development value.

---

## DECISION-010 — One Main AI Call with Targeted Follow-Up Revisions

### Status

Accepted

### Context

The application needs to generate several connected outputs:

- role fit assessment
- optimized CV
- gap analysis
- company research
- interview preparation

These outputs use the same:

- CV profile
- job ad
- company information
- product rules

A decision was required whether to generate them through separate AI calls or one combined workflow.

### Options Considered

1. **Use a separate AI call for every output**

   Pros:
   - smaller response models
   - simpler prompts per section
   - failures may affect only one section

   Cons:
   - repeated context
   - higher API usage
   - increased processing time
   - possible inconsistency between outputs

2. **Use one main AI call for all outputs**

   Pros:
   - consistent context
   - lower API usage
   - simpler initial user flow

   Cons:
   - large and complex response
   - higher validation risk
   - failure affects the complete workflow

3. **Use one main AI call and targeted follow-up calls**

   Pros:
   - consistent initial result
   - lower repeated API usage
   - allows focused user corrections
   - accepted sections do not need regeneration

   Cons:
   - requires both complete and partial response models
   - revision logic must be section-specific

### Decision

The application will use one main AI call to produce the initial complete result.

A follow-up AI call will only be made when the user requests a revision of a specific section.

The follow-up call must return only the revised section and must not regenerate the complete result.

### Reasoning

This approach:

- avoids repeating the same context across multiple calls
- reduces API usage
- reduces processing time
- keeps the initial output internally consistent
- allows targeted improvements
- avoids regenerating accepted content

### Tradeoffs

The main AI response requires a large and complex JSON structure.

This increases the risk of:

- incomplete output
- invalid JSON
- validation failure
- longer response time

The risks are accepted and managed through validation and retry logic.

### Consequences

The system requires:

- one complete workflow result model
- section-specific revision request models
- section-specific revision response models
- validation for complete and partial results
- frontend controls for selecting a section
- user comment input
- replacement of only the revised section

### Review Later

Review this decision if:

- the main response becomes too large or unreliable
- different sections require different models
- different sections require substantially different prompts
- splitting the workflow improves quality without excessive cost or inconsistency

---

## DECISION-011 — User Review and Section-Level Control

### Status

Accepted

### Context

AI-generated CV changes and interview preparation material may be structurally valid but still fail to match:

- the user’s preferred wording
- the user’s tone
- the user’s interpretation of their experience
- the level of emphasis the user considers accurate

The user must remain responsible for deciding which version is used.

### Options Considered

1. **Automatically apply and export all AI-generated changes**

   Pros:
   - fastest workflow
   - minimal user effort

   Cons:
   - user may not notice inaccurate wording
   - removes meaningful human control
   - increases the risk of misleading content

2. **Require approval for every individual field**

   Pros:
   - maximum user control
   - detailed review

   Cons:
   - slow and complicated UX
   - excessive user effort
   - too many actions for minor changes

3. **Show the complete result and allow section-level revisions**

   Pros:
   - balanced human control
   - simpler review process
   - accepted content remains unchanged
   - specific problems can be corrected

   Cons:
   - user must still review the complete result
   - multiple revision calls may be required

### Decision

The application will show the complete validated result before export.

The user may request a revision of a specific section by:

- selecting the section
- entering a comment
- submitting a follow-up request

The AI must only revise the selected section.

The application will not silently modify the final CV after it has been shown to the user.

### Reasoning

This approach keeps the user in control without creating an unnecessarily complicated approval workflow.

It allows the user to:

- verify accuracy
- correct misleading wording
- change tone
- adjust emphasis
- improve interview questions or answers
- keep sections that are already satisfactory

### Tradeoffs

The user must invest time in reviewing the output.

Some users may approve content without reading it carefully.

Other users may require several revision calls.

The application cannot guarantee that every user-approved statement is accurate.

### Consequences

The frontend requires:

- clearly separated result sections
- revision controls
- comment input
- section replacement logic
- distinction between the original and latest version

The backend requires:

- revision request validation
- section-specific prompts
- section-specific output validation
- protection against changes outside the selected section

### Review Later

Review this decision if:

- users require accept/reject controls for individual changes
- revision history becomes necessary
- users need side-by-side version comparison
- automatic approval becomes useful for low-risk cosmetic changes

---

# Rejected Decisions

No standalone rejected decisions are currently recorded.

Rejected alternatives are documented inside each accepted decision.

---

# Replaced Decisions

No decisions have been replaced.

---

# Decision Log

| ID           | Title                                                        | Status   | Date | Notes                |
| ------------ | ------------------------------------------------------------ | -------- | ---- | -------------------- |
| DECISION-001 | Static Stored CV Profile for MVP                             | Accepted |      | MVP constraint       |
| DECISION-002 | Pasted Job Ad Text Instead of Job Ad URL                     | Accepted |      | MVP constraint       |
| DECISION-003 | Company Name Required, Company URL Optional                  | Accepted |      | Input design         |
| DECISION-004 | FastAPI Backend Instead of Streamlit-Only Application        | Accepted |      | Architecture         |
| DECISION-005 | Browser Print/Save as PDF Instead of Direct PDF Generation   | Accepted |      | MVP export           |
| DECISION-006 | No AI Provider Fallback in MVP                               | Accepted |      | Gemini only          |
| DECISION-007 | AI Output Must Be JSON Validated Before Rendering            | Accepted |      | Reliability          |
| DECISION-008 | Poor Fit Stops the Tailoring Workflow                        | Accepted |      | No MVP override      |
| DECISION-009 | AI-Assisted Development Workflow and Product Ownership Focus | Accepted |      | Portfolio strategy   |
| DECISION-010 | One Main AI Call with Targeted Follow-Up Revisions           | Accepted |      | AI workflow          |
| DECISION-011 | User Review and Section-Level Control                        | Accepted |      | Human-in-the-loop UX |
