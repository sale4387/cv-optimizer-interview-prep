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
- optimized web version of the CV when the fit is sufficient
- gap analysis and preparation recommendations
- company background
- interview preparation material
- likely interview questions with two or three suggested answers
- saved structured application result

## V2 — Expanded Input and Export

### Input

- uploaded PDF or Word CV
- pasted job ad text
- company name
- optional company website URL

### Output

- parsed and structured CV
- role fit assessment
- optimized CV
- company background
- interview preparation material
- directly generated PDF version of the CV

## V3 — Job Discovery

V3 may add integration with an available Dutch job-market database or API.

The system would periodically identify suitable vacancies based on actual candidate fit rather than only matching job titles.

The user could receive a list of relevant positions together with application guidance and prepared materials.

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

1. The user finds a job ad they are considering.
2. The user opens the application.
3. The application loads the predefined CV profile.
4. The user selects an existing company from the dropdown.
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
    - company research
    - interview preparation material

11. The validated application result is stored for future reuse.
12. The user reviews the complete result.
13. The user may request a revision of a specific section by adding a comment.
14. The system revises only the selected section.
15. The user saves the CV and preparation material through the browser’s Print / Save as PDF functionality.
16. The user applies for the job and uses the preparation material before the interview.

---

# In Scope

The MVP is expected to support the following capabilities.

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
- general Glassdoor-related themes or publicly available employee sentiment

If reliable information is not available, the system should clearly indicate the limitation instead of inventing details.

## Interview Preparation

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

Each question should include two or three suggested answer directions that the user may select, combine or adapt.

## User Review and Revision

The complete result is shown to the user before export.

The user may select a specific section and enter a comment explaining what should be changed.

A follow-up AI request should revise only the selected section and should not regenerate the complete result.

## Data Storage and Reuse

The MVP stores validated structured data in Firebase Firestore.

Two types of records are stored:

- reusable company research
- complete application results

Company research may be reused when the user applies for another position at the same company.

A complete application result may only be reused when the relevant input and version metadata match, including:

- selected CV profile
- job ad content or hash
- schema version
- prompt version

Each application record may contain:

- fit assessment
- tailored CV JSON
- gap analysis
- company reference
- interview preparation
- creation timestamp
- relevant version metadata

The MVP does not include user accounts or a full history-management dashboard.

## Export

The application displays a print-friendly web version of the CV and interview preparation material.

The user exports the documents using the browser’s built-in Print / Save as PDF option.

## Basic Reliability

The MVP includes:

- validation of required user input
- structured AI output
- validation of AI response structure
- validation of stored data before reuse
- safe failure when output is invalid
- limited retry handling
- basic workflow logging
- safe handling of storage failures

---

# Out of Scope

The following capabilities are intentionally excluded from the MVP:

- uploading PDF or Word CV files
- automatic CV parsing
- entering only a job ad URL
- scraping LinkedIn job ads
- importing a LinkedIn profile
- direct application submission
- direct PDF generation
- user accounts
- user-facing application history dashboard
- automated job alerts
- scheduled job discovery
- local AI model fallback
- multiple CV templates
- recruiter or enterprise features

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

The MVP should use a simple and modular web architecture.

The architecture should support:

- a clear separation between frontend and backend responsibilities
- structured CV data
- structured AI output
- validation before rendering
- reuse of existing data when applicable
- safe failure handling
- future use of the backend as an independent API service
- extension without redesigning the complete system

The MVP should remain simple enough to develop, test and demonstrate reliably.

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

If the AI workflow fails repeatedly, processing stops and the user receives a clear error message.

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
- company research is generated or clearly marked as limited
- stored company research can be reused for another application to the same company
- a complete application result is reused only for an exact compatible input and version match
- validated application results and tailored CV JSON versions are stored
- interview questions and suggested answers are generated
- the user can request revision of a specific section
- only the selected section is revised
- AI output is validated before rendering
- stored data is validated before reuse
- invalid output fails safely
- the CV can be saved as PDF through the browser
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
- job ad URL processing
- direct PDF generation
- user accounts
- user-facing application history dashboard
- side-by-side CV version comparison
- job board API integration
- scheduled fit-based job discovery
- email notifications
- optional local model or privacy mode
- multiple CV templates

---

# Guiding Principle

> Every added layer of complexity must be justified by either meaningful product value or meaningful learning value.
