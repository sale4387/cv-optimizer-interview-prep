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

## DECISION-003 — Structured Company Identifier Without Company URL

### Status

Accepted

### Context

The application needs to identify the target company reliably in order to:

- retrieve reusable company research
- distinguish companies with similar names
- connect application records with the correct company
- support consistent Firestore keys

Relying only on company extraction from the job ad could produce incorrect matches.

A company website URL was previously considered as optional supporting input, but it would introduce an additional field without being required for the main MVP workflow.

### Options Considered

1. **Extract the company automatically from the job ad**

   Pros:
   - fewer required user actions
   - smoother input flow

   Cons:
   - the company may be extracted incorrectly
   - some job ads hide or omit the company name
   - the result still requires user confirmation
   - unreliable identification would affect Firestore reuse

2. **Require company name and optionally accept a company website URL**

   Pros:
   - the URL may help distinguish companies
   - additional research context may be available

   Cons:
   - adds another input field
   - the user may provide the wrong website
   - the website may not provide useful information
   - the URL is not required for Firestore identification

3. **Use a structured company label containing company name and country code**

   Pros:
   - simple user input
   - reduces ambiguity
   - supports consistent database keys
   - works without requiring a website URL
   - allows existing companies to be selected from stored records

   Cons:
   - requires the user to provide the correct country code
   - company names still require normalization
   - different legal entities may still need future disambiguation

### Decision

The MVP will use one required company field in this format:

```text
Company Name - ISO2 Country Code
```

Example:

```text
Bird - NL
```

The frontend will:

- show existing companies in a dropdown
- provide an `Add new company` option
- allow the user to enter a new structured company label

The backend will validate the format and generate a normalized company key, for example:

```text
bird-nl
```

A company website URL will not be part of the MVP input.

### Reasoning

The structured company label provides enough information to:

- identify the company consistently
- reduce ambiguity
- support Firestore lookup
- create reusable company research records
- keep the frontend input simple

Removing the optional website URL avoids a field that does not provide enough MVP value to justify additional validation and workflow complexity.

### Tradeoffs

The user must provide the correct ISO2 country code.

Companies operating through multiple legal entities may require more precise identification in the future.

The system cannot rely on a website URL for disambiguation.

### Consequences

The frontend requires:

- an existing-company dropdown
- an `Add new company` option
- one structured company input field

The backend requires:

- format validation
- ISO2 country-code validation
- company-name normalization
- normalized company-key generation
- Firestore lookup by company key

The research workflow uses the validated company identifier rather than a user-provided website URL.

### Review Later

Review this decision if:

- different legal entities require stronger identification
- automatic company extraction becomes reliable
- a company website becomes necessary for research quality
- external users require a more flexible company search experience

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

Replaced by DECISION-014

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

This decision was reviewed after browser Print / Save as PDF produced inconsistent Streamlit layout and page-break behavior.

It was replaced by DECISION-014 — Direct PDF Generation for Accepted CVs.

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

The main programming patterns required for this MVP are already familiar from previous projects.

Repeating the same implementation-heavy workflow would provide less learning value than practicing stronger ownership of:

- product definition
- task planning
- AI workflow design
- acceptance criteria
- testing
- technical review

The project is therefore intentionally used to practice AI Product Engineer and Technical PM responsibilities.

### Options Considered

1. **Manually write nearly all implementation code**

   Pros:
   - maximum direct coding practice
   - detailed familiarity with every implementation step

   Cons:
   - repeats patterns already practiced
   - provides less new product and delivery experience
   - increases delivery time

2. **Allow AI to generate most of the project without strong owner involvement**

   Pros:
   - fastest implementation
   - limited manual effort

   Cons:
   - weak product ownership
   - limited understanding of technical decisions
   - higher risk of unreviewed or inconsistent implementation
   - low portfolio credibility

3. **Lead the project as product owner and technical reviewer while using AI for implementation support**

   Pros:
   - stronger product and delivery practice
   - clear ownership of scope and quality
   - efficient use of existing technical knowledge
   - realistic AI-assisted development workflow

   Cons:
   - less manual coding than in earlier projects
   - requires disciplined review and testing
   - poor task quality would directly affect implementation quality

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
- technical subtasks
- implementation details
- refactoring
- debugging support

The project owner remains responsible for:

- product scope
- architecture direction
- major technical decisions
- AI workflow design
- task goals
- dependencies
- acceptance criteria
- measurements
- test expectations
- understanding the purpose and behavior of each implemented component
- final approval

AI assistance is responsible for:

- proposing technical subtasks
- defining implementation details
- generating code when requested
- identifying technical edge cases
- helping diagnose implementation failures

### Reasoning

The project should demonstrate that an AI product can be:

- defined
- scoped
- structured
- implemented
- validated
- tested
- delivered

Previous projects already covered many required implementation patterns.

The higher-value learning goal is to practice guiding AI-assisted development without transferring product responsibility to the AI.

### Tradeoffs

The project owner will manually write less implementation code than in earlier projects.

This is accepted because the project focuses more heavily on:

- product thinking
- technical specification
- AI workflow design
- validation strategy
- quality assurance
- human-in-the-loop UX
- structured documentation
- final product acceptance

The approach only remains credible if generated implementation is reviewed, understood and tested.

### Consequences

Documentation and task quality become central project outputs.

Each task must clearly define:

- why the task exists
- what must be true when it is complete
- how completion will be tested

AI-generated code must be:

- reviewed
- understood
- tested
- integrated intentionally

The project owner remains accountable for the final product.

### Review Later

Review this decision if the project introduces a technical area that provides meaningful new hands-on development value or if AI-generated implementation cannot be reviewed reliably.

---
## DECISION-010 — Separate Company Research, Main Application and Targeted Revision Workflows

### Status

Accepted

### Context

The application needs to produce several connected outputs:

- role fit assessment
- optimized CV
- gap analysis
- company research
- interview preparation

Company research can be reused across multiple applications to the same company, while the remaining outputs depend on the specific:

- CV profile
- job ad
- role
- application context

A single large AI call would repeat company research and increase response size, cost and validation risk.

The workflow also needs section-level revisions without regenerating accepted content.

### Options Considered

1. **Use one AI call for the entire workflow**

   Pros:
   - one request
   - one initial response
   - shared context

   Cons:
   - large and complex output
   - company research is repeated unnecessarily
   - failure affects every output
   - difficult to cache or reuse company data

2. **Use a separate AI call for every output section**

   Pros:
   - smaller prompts and schemas
   - failures affect fewer sections
   - easier section-specific testing

   Cons:
   - repeated context
   - higher API usage
   - longer processing time
   - possible inconsistency between outputs

3. **Use a conditional company research workflow, one main application workflow and targeted revision calls**

   Pros:
   - company research can be reused
   - the main result remains internally consistent
   - API calls are avoided when stored data is available
   - revisions only affect the selected section
   - response contracts remain manageable

   Cons:
   - multiple workflow types must be implemented
   - stored research must be validated
   - orchestration becomes more complex
   - several response models are required

### Decision

The MVP will use three AI workflows:

1. **Conditional Company Research Workflow**
   - checks Firestore first
   - calls Gemini search grounding only when valid reusable research is unavailable
   - validates and stores company research

2. **Main Fit, CV and Interview Workflow**
   - uses the CV profile, job ad and prepared company research
   - generates fit assessment, tailored CV, gap analysis and interview preparation
   - stops CV tailoring when fit is poor

3. **Targeted Revision Workflow**
   - runs only when the user requests a change
   - revises only the selected section

### Reasoning

This structure separates reusable company knowledge from application-specific output.

It:

- reduces unnecessary AI calls
- supports Firestore persistence
- limits the size of the main response
- improves validation clarity
- preserves consistency between fit, CV and interview preparation
- supports section-level user control

### Tradeoffs

The backend must orchestrate three workflow types.

The project requires:

- multiple Pydantic response models
- separate prompts
- separate validation rules
- Firestore lookup logic
- version compatibility checks
- more detailed failure handling

The additional complexity is accepted because it creates meaningful reuse and reliability value.

### Consequences

The system requires:

- a company research request and result model
- a main application request and result model
- revision request and result models
- separate validation functions
- company-research cache-hit and cache-miss handling
- main workflow integration with stored research
- targeted section replacement logic

Company research is no longer generated inside every main application call.

### Review Later

Review this decision if:

- company research is too unreliable to reuse
- the main application response remains too large
- interview preparation requires a separate model or workflow
- splitting the main workflow improves quality without excessive inconsistency
- provider capabilities make a different orchestration pattern more reliable

---
## DECISION-011 — User Review and Section-Level Control

### Status

Accepted

### Review Note

This decision remains accepted, but will be expanded by DECISION-015 toward a CV-first interface with inline review of AI-suggested changes.

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

## DECISION-012 — Complete the CV Optimization Workflow Before Adding Supporting Features

### Status

Accepted

### Context

The planned main AI workflow includes several outputs:

- role fit assessment
- optimized CV
- company research
- interview preparation
- direct PDF export for accepted CVs

Developing and testing all outputs at the same time would make it harder to identify problems and validate whether the core product value works.

CV optimization is the central product feature. Company research and interview preparation provide additional value but are not required to prove that the main CV workflow works.

Direct PDF export is now part of the MVP, but visual PDF polish should not block development of the remaining product features.

### Options Considered

1. **Develop the complete AI workflow and all outputs at the same time**

   Pros:
   - final workflow is built immediately
   - fewer temporary models and intermediate versions

   Cons:
   - larger and more difficult initial implementation
   - harder debugging
   - unclear which component caused a failure
   - core product value is tested later

2. **Complete CV optimization first, including fully polished PDF export**

   Pros:
   - the complete CV feature is finalized before expansion
   - export quality is resolved early

   Cons:
   - browser-specific formatting issues may delay unrelated features
   - excessive time may be spent polishing output before validating the complete product

3. **Complete the main CV optimization workflow first, then add supporting features without allowing PDF visual polish to block progress**

   Pros:
   - validates the core product early
   - creates a clear implementation sequence
   - simplifies testing and debugging
   - allows company research and interview preparation to be added incrementally
   - prevents non-critical PDF styling problems from blocking development

   Cons:
   - intermediate versions will not contain the complete product
   - some models and prompts may need to be expanded later
   - PDF quality may remain temporarily below the desired standard

### Decision

Development will first complete the core CV optimization flow:

- stored CV profile
- job and company input
- role fit assessment
- CV optimization
- validation
- result rendering
- section-level revision

Company research and interview preparation will be added after the core CV workflow is functional and tested.

Direct PDF generation will be implemented as part of the CV workflow, but imperfect visual styling will not block development of later features if:

- the document can be downloaded successfully
- the content is complete
- the output remains readable and usable

PDF styling may be improved later after the main workflow and review flow are stable.

### Reasoning

This approach validates the main product value as early as possible.

It allows the team to:

- test CV optimization independently
- identify prompt and validation problems earlier
- reduce the size of the first AI response
- establish stable data contracts before expanding them
- add company research and interview preparation to an already functioning system

Treating PDF polish as non-blocking prevents a secondary presentation issue from delaying higher-value functionality.

### Tradeoffs

The first working version will not contain all planned MVP features.

The main AI contract may need to be expanded after the CV workflow is already functional.

Generated PDF output may temporarily have:

- imperfect page breaks
- minor layout problems
- less polished formatting than the final desired design

These limitations are accepted as long as the document remains readable and usable.

### Consequences

The project task order will be changed so that:

1. the CV data model and input flow are completed
2. the main fit and CV optimization workflow is implemented
3. CV results and section revisions are tested
4. company research is added
5. interview preparation is added
6. the full AI response model is integrated and retested

PDF export will have two quality levels:

- **minimum acceptable:** the complete CV can be saved and remains readable
- **desired quality:** professional A4 layout with reliable page breaks and formatting

Failure to reach the desired quality will create a follow-up improvement task but will not automatically block the next product feature.

### Review Later

Review this decision when:

- the core CV workflow is stable
- browser export produces consistently poor results
- PDF formatting significantly reduces real usability
- the generated PDF remains visually below the desired level
- all supporting MVP features are integrated and final product polish begins

## DECISION-013 — Firestore Persistence for Company Research and Application Results

### Status

Accepted

### Context

The system produces structured outputs that have value beyond a single session.

Without persistent storage:

- company research would be generated repeatedly
- validated application results could not be reopened
- tailored CV JSON versions would be lost
- future direct PDF generation would require rerunning the AI workflow
- repeated calls would increase cost and validation risk

The MVP does not include user accounts, but it supports a limited number of predefined CV profiles.

A persistent storage approach was required that provides meaningful reuse without introducing a complete account and permissions system.

### Options Considered

1. **Do not store workflow results**

   Pros:
   - simplest architecture
   - no external database dependency
   - no database schema or credentials

   Cons:
   - every workflow must run again
   - company research is repeatedly generated
   - previous tailored CV versions are lost
   - no foundation for later PDF rendering or history features

2. **Use temporary in-memory or local caching**

   Pros:
   - simpler than an external database
   - can reduce repeated calls during one runtime session

   Cons:
   - data is lost when the application restarts
   - difficult to share between frontend, backend and deployments
   - unreliable as permanent storage
   - limited portfolio and product value

3. **Use Firebase Firestore as persistent storage**

   Pros:
   - persistent structured storage
   - suitable for JSON-like documents
   - supports reuse across sessions
   - already familiar from previous projects
   - available at low or no cost for MVP usage

   Cons:
   - introduces an external service
   - requires credentials and access control
   - requires document models and versioning
   - adds read/write failure cases

### Decision

The MVP will use Firebase Firestore as permanent storage for two collections:

### `companies`

Stores reusable company research and related metadata.

### `applications`

Stores one structured result per processed application, including:

- profile ID
- company key
- job title
- job ad text or hash
- fit assessment
- tailored CV JSON
- gap analysis
- interview preparation
- creation timestamp
- base CV version
- schema version
- prompt version
- model version where useful

A complete application result may only be reused when the relevant inputs and version metadata are compatible.

Firestore access will only occur through the FastAPI backend.

The Streamlit frontend will not access Firestore directly.

The MVP will not include:

- user accounts
- a permissions system
- a full history-management dashboard

### Reasoning

Firestore provides meaningful product value by enabling:

- reuse of company research
- fewer unnecessary grounded-search calls
- storage of tailored CV JSON versions
- reopening validated application results
- future direct PDF rendering from stored data
- future history and comparison features

The database also provides learning value through:

- persistence design
- document validation
- version compatibility
- retrieval logic
- safe failure handling

The additional complexity is justified because the stored data is a reusable product asset rather than a temporary cache.

### Tradeoffs

The system becomes dependent on another external service.

The project requires additional work for:

- credentials
- document schemas
- versioning
- read and write operations
- storage validation
- failure handling
- exact-match logic

Without user accounts, stored records are not separated through a general multi-user permission model.

This limitation is accepted for the controlled MVP.

### Consequences

The architecture requires:

- a Firestore client in the backend
- `companies` and `applications` collections
- normalized company keys
- application matching logic
- job ad hashing or equivalent comparison
- schema and prompt version metadata
- validation of stored documents before reuse
- logging of storage hits, misses and failures

The frontend requires:

- a dropdown of existing companies
- an `Add new company` option

The AI workflow changes so that:

- company research runs only when reusable data is unavailable
- the main application result is stored after validation
- stored tailored CV JSON may later be rendered without another AI call

### Review Later

Review this decision if:

- free-tier limits become restrictive
- storage costs become material
- user accounts are introduced
- stronger multi-user permissions are required
- another database better supports future query patterns
- saved application history becomes a major product feature

---



## DECISION-014 — Direct PDF Generation for Accepted CVs

### Status

Accepted

### Context

The MVP originally planned to use the browser’s Print / Save as PDF functionality.

During implementation, browser-based export produced inconsistent results with Streamlit layout, page breaks and print styling.

The application already stores validated structured CV data, which makes direct PDF generation possible without relying on the rendered Streamlit page.

### Options Considered

1. **Continue using browser Print / Save as PDF**

   Pros:
   - no additional PDF logic
   - uses the existing preview page
   - simpler original plan

   Cons:
   - inconsistent layout
   - less control over page breaks
   - manual user action required
   - weaker user experience

2. **Generate PDF directly from the accepted structured CV data**

   Pros:
   - one-click download
   - more predictable output
   - independent from Streamlit browser layout
   - easier to connect export to accepted CV status
   - better MVP user experience

   Cons:
   - requires PDF rendering code
   - requires layout and font handling
   - visual polish may need later improvement

3. **Use an external PDF generation service**

   Pros:
   - potentially stronger layout capabilities
   - could support advanced templates later

   Cons:
   - additional service dependency
   - possible cost
   - unnecessary for the controlled MVP

### Decision

The MVP will generate a downloadable PDF directly from the accepted structured CV data.

PDF download is enabled only after the user accepts the CV.

Draft CVs may be previewed and revised, but should not be exported as final PDFs.

### Reasoning

Direct PDF generation provides a better and more controlled export flow than browser printing.

It also supports the product rule that only accepted CVs become final exportable documents.

The current PDF output is considered usable for V1 if:

- the content is complete
- Serbian characters are supported
- the document opens successfully
- the document stays within the required page limit
- minor visual imperfections do not prevent use

### Tradeoffs

The PDF generator adds implementation and maintenance complexity.

The first generated PDF may still require cosmetic improvements.

Styling and template polish are intentionally separated from the core workflow.

### Consequences

The application requires:

- PDF generation logic
- PDF export controls
- accepted/draft status enforcement
- PDF error handling
- tests for valid PDF creation

Browser Print / Save as PDF is no longer the primary export method.

Future UI and PDF polish tasks should improve visual quality without changing the core export decision.

### Review Later

Review this decision if:

- generated PDF quality remains below acceptable professional standards
- multiple templates are required
- Word export becomes necessary
- a more robust PDF rendering approach becomes justified

---

## DECISION-015 — CV-First Interface and Inline Change Review Direction

### Status

Accepted

### Context

The current implemented workflow separates optimization input, result preview and review actions.

The user experience can be improved by making the CV itself the primary page and showing AI-suggested changes directly against the current CV content.

This would make it easier for the user to understand what changed before accepting the final CV or requesting revisions.

### Options Considered

1. **Keep the current separate optimize page and ready modal**

   Pros:
   - already implemented
   - simple flow
   - lower short-term development effort

   Cons:
   - the user does not immediately see what changed
   - the result feels more like a black box
   - review is less connected to the original CV

2. **Use a CV-first interface with inline suggested changes**

   Pros:
   - the current CV is always visible
   - AI changes are transparent
   - review is easier and more trustworthy
   - request-change actions can be attached to specific editable content

   Cons:
   - requires UI redesign
   - requires more detailed review state
   - requires finer mapping between original CV content and AI suggestions

### Decision

The product direction is to move toward a CV-first interface.

The main page should show the current CV as the primary view.

The side menu should contain:

- optimization input
- company and country fields
- job title
- job ad text
- My Applications navigation

After optimization, the application should not rely on a `Your CV is ready` modal as the main transition.

Instead, AI-suggested changes should be shown inline against the current CV content where possible.

Editable content should support review and revision actions at a more granular level, including:

- professional summary
- responsibility bullets
- key achievement bullets
- skills or highlights where supported

The existing accept and request-change concepts remain valid, but should be adapted to the inline review experience.

### Reasoning

A CV-first interface better supports user trust and human review.

The user can compare the existing text with AI-suggested changes before deciding whether to accept, keep or revise content.

This matches the product principle that AI should assist the user, not silently replace the user’s judgment.

### Tradeoffs

This is not a small cosmetic change.

It affects:

- navigation
- page layout
- preview rendering
- revision controls
- state handling
- how `cv_patch` is displayed

The change should be handled as a separate UI task rather than mixed into the existing backend workflow.

### Consequences

A new task should be added for the CV-first homepage and inline review UI.

Existing backend workflow and validation logic remain useful because they already produce a structured `cv_patch`.

The frontend will need to display that patch more transparently instead of only rendering the final tailored CV.

### Review Later

Review this decision after the first inline review version is implemented and tested with real generated CV results.

---


# Rejected Decisions

No standalone rejected decisions are currently recorded.

Rejected alternatives are documented inside each accepted decision.

---

# Replaced Decisions

DECISION-005 was replaced by DECISION-014 after browser Print / Save as PDF produced inconsistent Streamlit layout and page-break results.

DECISION-003 and DECISION-010 were updated before implementation to reflect the final MVP input, persistence and AI workflow design.

---

# Decision Log

| ID           | Title                                                                       | Status   | Date | Notes                |
| ------------ | --------------------------------------------------------------------------- | -------- | ---- | -------------------- |
| DECISION-001 | Static Stored CV Profile for MVP                                            | Accepted |      | MVP constraint       |
| DECISION-002 | Pasted Job Ad Text Instead of Job Ad URL                                    | Accepted |      | MVP constraint       |
| DECISION-003 | Structured Company Identifier Without Company URL                           | Accepted |      | Input design         |
| DECISION-004 | FastAPI Backend Instead of Streamlit-Only Application                       | Accepted |      | Architecture         |
| DECISION-005 | Browser Print/Save as PDF Instead of Direct PDF Generation                  | Replaced |      | Replaced by DECISION-014 |
| DECISION-006 | No AI Provider Fallback in MVP                                              | Accepted |      | Gemini only          |
| DECISION-007 | AI Output Must Be JSON Validated Before Rendering                           | Accepted |      | Reliability          |
| DECISION-008 | Poor Fit Stops the Tailoring Workflow                                       | Accepted |      | No MVP override      |
| DECISION-009 | AI-Assisted Development Workflow and Product Ownership Focus                | Accepted |      | Portfolio strategy   |
| DECISION-010 | Separate Company Research, Main Application and Targeted Revision Workflows  | Accepted |      | AI workflow          |
| DECISION-011 | User Review and Section-Level Control                                       | Accepted |      | Human-in-the-loop UX |
| DECISION-012 | Complete the CV Optimization Workflow Before Adding Supporting Features     | Accepted |      | Delivery sequence    |
| DECISION-013 | Firestore Persistence for Company Research and Application Results           | Accepted |      | Persistence          |
| DECISION-014 | Direct PDF Generation for Accepted CVs                                      | Accepted |      | Export               |
| DECISION-015 | CV-First Interface and Inline Change Review Direction                       | Accepted |      | UX direction         |
