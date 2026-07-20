# CV Optimizer & Interview Prep Assistant

A web-based AI tool that helps users tailor an existing CV to a specific job opportunity and prepare for a potential interview.

---

# Overview

One CV cannot effectively represent a candidate for every possible job opportunity.

Adjusting the presentation of previous experience for each job ad is time-consuming and adds additional stress to an already demanding job-search process.

The CV Optimizer & Interview Prep Assistant provides a tailored CV, company research and interview preparation while keeping the original CV as the factual source of truth.

The V1 workflow uses predefined structured CV profiles and pasted job-ad text. AI may improve wording and emphasis, but it must not invent experience, skills, achievements or qualifications.

---

# V1 Features

- predefined structured CV profiles
- pasted job-ad text
- role fit assessment
- poor-fit workflow stop with a clear explanation
- CV optimization based only on existing experience
- fit and gap analysis
- company research with Firestore reuse
- on-demand interview preparation
- likely interviewer questions and candidate questions
- inline review with accept, keep-original and targeted-revision decisions
- direct PDF generation after CV acceptance
- Firestore persistence for applications and company research
- controlled retries, validation and failure handling
- Docker Compose deployment for a repeatable portfolio demo
- bookmarkable candidate routes:
  - `/sale`
  - `/svetlana`

Company Research and Interview Prep are separate supporting workflows. A failure in either workflow does not remove an already valid CV result.

---

# Screenshots / Demo

The application can be demonstrated locally or from the home-server deployment.

Local-network demo routes:

```text
http://SERVER_IP:8502/sale
http://SERVER_IP:8502/svetlana
```

Screenshots can be added later without changing the MVP scope.

---

# Technology Stack

- Python
- Streamlit
- FastAPI
- Pydantic
- Gemini API
- Firebase / Firestore
- ReportLab
- Docker
- Docker Compose
- Nginx

FastAPI remains available in the repository, but the final Streamlit V1 flow calls the service layer directly and does not require a separate FastAPI container.

---

# Project Structure

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
├── config.py
├── firebase.py
├── observability.py
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

---

# Quick Start

## Local development

Create a local `.env` file from `.env.example` and provide the required values.

Run Streamlit:

```bash
streamlit run streamlit/app.py
```

FastAPI can still be started separately for development or API testing:

```bash
uvicorn api:app --reload
```

## Docker Compose

Create `.env` from `.env.example`.

Create the local credentials path:

```text
secrets/firebase-service-account.json
```

The Firebase service-account JSON must remain outside Git.

Build and start the application:

```bash
docker compose up -d --build
```

Check container status:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
```

Stop the application:

```bash
docker compose down
```

The default Docker demo port is controlled by:

```text
CV_APP_PORT=8502
```

---

# Environment Variables

Required or supported configuration:

```text
BACKEND_API_KEY=
RATE_LIMIT=
FIREBASE_CREDENTIALS_PATH=
GEMINI_API_KEY=
GEMINI_MODEL=
GEMINI_MAX_OUTPUT_TOKENS=
GEMINI_TIMEOUT_SECONDS=
GEMINI_MAX_ATTEMPTS=
CV_APP_PORT=
```

Exact defaults and validation rules are defined in `config.py`.

Do not commit:

- `.env`
- Firebase service-account JSON
- API keys
- access tokens
- private credentials

---

# Main Workflow

1. Select a predefined candidate profile.
2. Enter the company, role and pasted job-ad text.
3. Run CV Optimization.
4. Review fit, gaps and the proposed tailored CV.
5. Accept suggestions, keep original content or request targeted revisions.
6. Save all review decisions.
7. Accept the final CV.
8. Generate and download the PDF.
9. Run Interview Prep on demand.
10. Reopen saved applications from Firestore.

Company Research is reused when a valid fresh company record already exists.

---

# Validation and Safety

The project uses several controls around AI output:

- the original CV is the factual source of truth
- prompts define allowed and forbidden changes
- raw model responses are cleaned into structured JSON
- Pydantic and business validation reject incomplete or invalid results
- poor-fit roles can stop CV tailoring
- targeted revisions are limited to selected content
- PDF export is available only after the CV is accepted
- supporting workflow failures do not overwrite valid application data
- secrets are excluded from logs and Git

---

# Current Project Status

V1 is complete and deployed through Docker Compose on a home-server laptop for portfolio demonstration.

Completed work includes:

- main CV optimization workflow
- company research
- interview preparation
- inline human review
- direct PDF generation
- Firestore persistence
- validation and controlled failures
- automated and manual testing
- architecture and cleanup review
- Docker and Nginx deployment
- `/sale` and `/svetlana` access routes

---

# Known Limitations

- V1 supports predefined structured CV profiles rather than arbitrary CV uploads.
- Job ads are pasted manually.
- Company Research does not yet have a manual retry button after a failed attempt.
- The Docker deployment is intended primarily for a local-network portfolio demo.
- Public hosting, domain configuration and HTTPS are not part of V1.
- AI output still requires human review before use.

---

# Roadmap

## V1 — Controlled MVP

- predefined structured CV profiles
- pasted job-ad text
- role fit assessment
- CV tailoring
- fit and gap analysis
- company research
- interview preparation
- inline review and targeted revisions
- direct PDF generation
- Firestore persistence
- Docker Compose portfolio deployment

## V2 — Expanded Input

- PDF and Word CV upload
- automatic CV parsing
- job-ad URL processing
- pasted job-ad fallback
- manual Company Research retry
- broader user-managed profile support

## V3 — Agentic Job Discovery

- scheduled job discovery
- job-alert email processing
- role-fit evaluation
- application preparation workflow
- candidate notifications
- stronger observability and agent-quality checks

---

# Documentation

- [Project Scope](PROJECT_SCOPE.md)
- [Architecture](ARCHITECTURE.md)
- [Project Board](PROJECT_BOARD.md)
- [Decisions](DECISIONS.md)

---

# License

This project is currently intended for personal portfolio use.

No software license has been selected yet.
