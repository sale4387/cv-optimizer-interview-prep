# CV Optimizer & Interview Prep Assistant

A web-based AI tool that helps users tailor an existing CV to a specific job opportunity and prepare for a potential interview.

---

# Overview

One CV cannot effectively represent a candidate for every possible job opportunity.

Adjusting the presentation of previous experience for each job ad is time-consuming and adds additional stress to an already demanding job-search process.

The CV Optimizer & Interview Prep Assistant aims to provide a tailored CV and interview preparation materials approximately ten minutes after the user finds a relevant job ad.

---

# Planned Features

Development has not started yet. The following features are planned for the MVP:

- predefined structured CV rendered as a web page
- role fit assessment
- poor-fit workflow stop with clear explanation
- CV optimization based only on existing experience
- gap analysis and preparation recommendations
- company research
- likely interview questions
- two or three suggested answer directions per question
- section-level revisions based on user feedback
- browser Print / Save as PDF export
- Firestore firebase

---

# Screenshots / Demo

Screenshots and a live demo are not yet available because features implementation has not started.

They will be added when the main MVP workflow is functional.

---

# Planned Technology Stack

- Python
- FastAPI
- Streamlit
- Pydantic
- Gemini API
- Docker
- Firebase

---

# Planned Project Structure

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

The structure may be adjusted during task planning and implementation.

---

# Quick Start

Setup and run instructions will be added when MVP implementation begins.

---

# Current Project Status

The project is currently in the planning and documentation phase.

Completed planning work includes:

- project scope
- architecture direction
- core product and technical decisions

Implementation has not started yet.

---

# Roadmap

## V1 — Controlled MVP

- predefined structured CV
- pasted job ad text
- company name input
- role fit assessment
- CV tailoring
- gap analysis
- company research
- interview preparation
- section-level revisions
- browser PDF export
- Firestore Firebase persistance

## V2 — Expanded Input and Export

- PDF and Word CV upload
- automatic CV parsing
- job ad URL processing
- direct PDF generation

## V3 — Job Discovery

- job board API integration
- scheduled role searches
- fit-based job alerts
- application preparation notifications

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
