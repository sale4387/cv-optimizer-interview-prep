# TASK-015 — Manual Test Plan and Result Log

## Purpose

Use this file while testing the full MVP workflow.

For each scenario:

- run the test
- write what actually happened
- mark status
- add screenshots or app IDs if useful
- send the completed notes back for cleanup/fix planning

---

# Status Legend

- PASS — works as expected
- FAIL — blocks the workflow
- PARTIAL — usable but needs fix
- COSMETIC — visual or wording issue only
- SKIP — not tested yet

---

# Test Header

```text
Date:
Git commit:
Tester:
Environment:
Streamlit command:
FastAPI command:
Notes:
```

---

# Pre-check

## 0.1 Automated task tests

Run available task test scripts.

```powershell
python task_012_test_script_FIXED.py
python task_013_test_script.py
python task_014_test_script.py
python task_019_test_script.py
```

Result:

```text
TASK-012: Passed
TASK-013: Passed
TASK-014: Passed
TASK-019: Passed
Notes:
```

## 0.2 App startup

Steps:

1. Start backend if still used.
2. Start Streamlit.
3. Open app in browser.
4. Confirm sidebar loads.
5. Confirm there are no startup errors.

Result:

```text
Status: Passed
Actual result: 1-5 worked as expected.
Notes:
```

## 0.3 CV-first landing page and candidate switch

Goal:

Confirm the app opens with a stored CV as the primary page, not with the job-ad form as the main screen.

Expected UX:

```text
- App opens on stored CV preview by default.
- Default selected candidate is Aleksandar Markovic.
- User can switch candidate to Svetlana Markovic.
- Switching candidate updates the stored CV preview.
- Sidebar still contains My Applications and Companies.
- Job-ad/application form is secondary, not the default main page.
- Job-ad/application form can be opened from sidebar, button, modal, expander or separate panel.
- After optimization, the same CV-first view shows original/stored CV plus optimized suggestions for review.
```

Steps:

1. Open the app fresh.
2. Confirm what appears as the main page.
3. Confirm whether Aleksandar CV is visible without starting optimization.
4. Switch to Svetlana if candidate switch exists.
5. Confirm Svetlana CV appears.
6. Open job-ad/application form.
7. Run optimization.
8. Confirm optimized version appears next to or inside the CV review flow.
9. Confirm review/comment controls are connected to the optimized suggestions.

Result:

```text
Status: Partial
Actual first page: Aleksandar CV
Candidate switch visible: yes
Default candidate: Aleksandar
Stored CV visible before optimization: yes
Job form placement: separate window
Optimized CV review placement: new page below the comparission of current and optimized parts
Issues:
- Success modal still appears after optimization. This should be removed or de-emphasized.
- Review is not fully inline inside the CV-first page.
- Suggested changes appear below fit/gap as expandable sections.
- Global Request changes button is redundant because each review item already has revision_requested.
Screenshots:

![0.3-1 Success modal still appears](docs/screenshots/task-015/0.3-1.png)

![0.3-2 Review appears below fit-gap, not truly inline](docs/screenshots/task-015/0.3-2.png)

![0.3-3 Per-item decision options](docs/screenshots/task-015/0.3-3.png)

![0.3-4 Global Request changes button is redundant](docs/screenshots/task-015/0.3-4.png)
```

---

# Scenario 1 — Sale, acceptable-fit application

Goal:

Confirm normal workflow works for Aleksandar/Sale profile.

Inputs:

```text
Candidate profile: Aleksandar Markovic
Company: Worldline
Country: NL
Job title:Strategic Account Manager
Job ad:Who we are



Worldline helps businesses of all shapes and sizes to accelerate their growth journey - quickly, simply, and securely. We are the innovators at the heart of the payments technology industry, shaping how the world pays and gets paid. Our technology powers the growth of millions of businesses across 5 continents. And just as we help our customers accelerate their business, we are committed to helping our people accelerate their careers. Together, we shape the evolution.



The opportunity



We are building a dynamic partnership team with a clear mission: empower Enterprise Accounts through unwavering support and innovative payments solutions. The sponsor translates ambitious goals into tangible results by cultivating strategic relationships and delivering cross-functional value across Indirect Sales, Product, Consulting, and Customer Support. This role blends strategic vision with hands-on execution, shaping client needs and guiding high-value deals from concept to outcome with disciplined CRM practices. It offers an international, multinational setting with global travel to meet clients and present transformative solutions. You will develop long-term account plans that drive sustained growth and measurable impact in payments. Join us to lead, inspire, and advance enterprise partnerships on the world stage.



Day-to-day responsibilities



Cultivate and manage relationships with Enterprise accounts, ensuring high levels of customer satisfaction and engagement.
Serve as the primary point of contact for assigned accounts, understanding their business needs and objectives.
Proactively identify and pursue new sales opportunities within existing accounts.
Work closely with the line manager on ongoing opportunities, account status, and sales performance metrics.
Maintain accurate and up-to-date records in the CRM system, documenting opportunities, progress and outcomes.
Work closely with internal teams, including Indirect Sales, Product, Consulting and Customer Support to align on client needs and deliver solutions.
Engage in international travel to meet clients, conduct presentations and attend industry events.


Who are we looking for



We look for big thinkers. People who can drive positive change, step up and show what’s next – people with passion, can-do attitude and a hunger to learn and grow. In practice this means:



Proven Track Record in High-Value Sales



At least 5 years experience in Key Account Management or Business Development
Proven sales experience with technical complex solutions
Capable of building strategic account plans that drive long term objectives
Persuasive communicator, able to articulate a vision that delivers value
Proactive, self-motivated, capable of anticipating customer needs and risks


International mindset



Used to work in multinational companies with matrix organizations
Fluent in English, any other language is a plus


Deep understanding of the Payment Industry


Relationship-focused



Displays customer empathy & relationship mindset
Team oriented & collaborative
Intellectually curious, energetic and innovative.
A “can do” mindset


Perks & Benefits



At Worldline you’ll get the chance to be at the heart of the global payments technology industry and shape how the world pays and gets paid. On top of that, you will also:



Be part of a company guided by a strong purpose to do good and recognized as top 1% of the most sustainable companies in all sectors worldwide.
Work with inspiring colleagues and be empowered to learn, grow and accelerate your career.
Work in an international environment with cutting edge technologies.
Enjoy a wide range of benefits: medical insurance, pension found, tickets restaurant, company bonus, 50% of remote working.


Shape the evolution



We are on an exciting journey towards the next frontiers of payments technology, and we look for big thinkers, people with passion, can-do attitude and a hunger to learn and grow. Here you'll work with ambitious colleagues from around the world, take on unique challenges as a team, and make a real impact on the society. With an empowering culture, strong technology and extensive training opportunities, we help you accelerate your career - wherever you decide to go. Join our global team of 18,000 innovators and shape a tomorrow that is yours to own.



Learn more about life at Worldline at jobs.worldline.com



We are proud to be an Equal Opportunity employer. We do not discriminate based upon race, religion, color, national origin, sex, sexual orientation, gender identity, gender expression, age, status as an individual with a disability, or any applicable legally protected characteristics.
Expected fit: strong / solid / stretch
```

Steps:

1. Select Aleksandar Markovic.
2. Enter company.
3. Enter job title.
4. Paste job ad.
5. Run optimization.
6. Confirm draft application is created.
7. Confirm fit assessment is visible.
8. Confirm gap analysis is visible.
9. Confirm tailored CV is visible.
10. Confirm company research is generated or reused.
11. Confirm interview prep is generated or visible from application preview.
12. Confirm inline review appears.
13. Accept one AI suggestion.
14. Keep one original value.
15. Request one targeted revision if available.
16. Confirm unrelated CV content did not change.
17. Accept CV.
18. Download PDF.
19. Open PDF.
20. Reopen application from My Applications.

Expected:

```text
- Application is saved as draft first.
- Fit/gap are visible.
- Interview prep belongs to this application, not only company page.
- Interview prep has 10–15 likely interviewer questions.
- Candidate questions to ask are separate.
- Inline review works.
- Revision keeps draft status.
- Accept CV changes status to accepted.
- PDF download is available only after acceptance.
- Reopened application keeps accepted state.
```

Status: PARTIAL

Actual result:

- Application was saved as draft.
- Fit assessment is visible.
- Gap analysis is visible.
- Tailored CV is visible.
- Company research exists.
- Interview prep appears under the company page only, not under the application.
- Interview prep is not connected to the application record in DB.
- Interview prep does not generate 10–15 likely interviewer questions.
- Interview prep currently contains talking points and candidate questions to ask.
- Inline review appears and decisions can be saved.
- Application can be accepted.
- PDF download becomes available only after accepting the CV.
- Reopened application keeps accepted state.

Application ID:
CIzgbi98opkYnqJ9NfGk

Issues:

- Interview prep must be stored and displayed under the application, not only under company research.
- Interview prep must generate 10–15 likely interviewer questions.
- Candidate questions to ask must remain a separate section.
- Save decision needs visible UI feedback.
- Consider one Save all decisions button instead of saving each item separately.
- Some AI suggestions show no visible change.
- It is unclear after saving all review decisions whether the user should click Accept CV.
- Company page readability needs improvement; headings and subtitles are too flat.
- Role fit and risk assessment are too visually flat; fit levels should be easier to distinguish.
- PDF download is placed too low after acceptance.
- Accepted applications should not show active revision controls; they should show fit assessment, gap analysis, final CV and download button.

Screenshots:
1-1.png, 1-2.png, 1-3.png, 1-4.png, 1-5.png

````

---

# Scenario 2 — Svetlana, acceptable-fit application

Goal:

Confirm candidate selection works and Svetlana CV is used.

Inputs:

```text
Candidate profile: Svetlana Markovic
Company:
Country:
Job title:
Job ad:
Expected fit: strong / solid / stretch
````

Steps:

1. Select Svetlana Markovic.
2. Run the same flow as Scenario 1.
3. Confirm generated CV content is based on Svetlana, not Sale.
4. Confirm My Applications shows the correct profile.
5. Confirm PDF contains Svetlana’s CV, not Sale’s CV.

Expected:

```text
- profile_id is svetlana.
- Application preview shows Svetlana profile.
- Tailored CV uses Svetlana experience.
- PDF uses Svetlana accepted CV.
```

Result:

```text
Status: Passed
Actual result:
Application ID: w5fXfNZJkwLzEGJRzYR2
Issues: None
Screenshots:
```

---

# Scenario 3 — Poor-fit application

Goal:

Confirm poor fit stops CV tailoring but still gives useful guidance.

Inputs:

```text
Candidate profile:
Company:
Country:
Job title:
Job ad:
Expected fit: poor
```

Steps:

1. Select candidate.
2. Use a clearly unrelated job ad.
3. Run optimization.
4. Confirm fit is poor.
5. Confirm tailored CV is not generated.
6. Confirm Request changes is hidden or blocked safely.
7. Confirm Accept CV is hidden or blocked safely.
8. Confirm PDF download is not available.
9. Confirm gap analysis and preparation guidance are visible.
10. Confirm company research can still exist.

Expected:

```text
- No tailored CV.
- No revision flow.
- No accept/PDF flow.
- Fit/gap guidance still visible.
- No crash.
```

Result:

```text
Status:Passed
Actual result:
Application ID:eA9h7deE0SpdhaPZ9qmW
Issues: None
Screenshots:
```

---

# Scenario 4 — Company research and cache

Goal:

Confirm company research works as reusable company-level data.

Inputs:

```text
Company with enough data:
Company with limited data:
```

Steps:

1. Generate application for a company.
2. Open Companies page.
3. Open the saved company report.
4. Confirm report is readable.
5. Create another application for the same company.
6. Confirm stored company research is reused.
7. Test a company with limited public data.
8. Confirm limited fields are marked honestly.

Expected:

```text
- Saved company report opens from Companies.
- Same company reuses cache when fresh.
- Limited data is marked as limited, not invented.
- Company report is useful but not too long.
```

Status: FAIL / PARTIAL

Actual result:
Company research failed safely because Gemini returned JSON that did not match the required schema. The response appears to have returned industry fields at the top level instead of nesting them under the required `industry` object.

Issue:
Company research prompt/validation needs hardening so AI always returns the full expected schema, or the workflow needs a controlled retry when required top-level fields are missing.

Error:
CompanyResearchValidationError:
Missing required fields: research_status, confidence_level, short_description, industry, products_and_services, customers_and_market, competitors, public_company_information, employee_sentiment, interview_intelligence.
Extra fields: primary_industry, secondary_industries, business_model.

---

# Scenario 5 — Interview preparation quality

Status: FAIL

Question count:
0 valid likely interviewer questions found.

Actual result:

- Interview prep is not displayed as an application-specific section.
- Interview prep appears under the company profile/company research area.
- It is not clearly connected to the selected application, job title, job ad or tailored CV.
- It does not generate 10–15 likely interviewer questions.
- Existing content is mostly talking points and candidate questions to ask.
- Candidate questions to ask are not clearly separated from interviewer questions.
- Questions do not sufficiently reference the job ad, tailored CV or application-specific fit/gap.
- No useful prep warning is shown for weaker, older or smaller experience areas.

Issues:

- Interview prep must be generated and stored per application.
- Interview prep must be visible from the application preview.
- It must generate 10–15 likely questions the interviewer/company may ask the candidate.
- Candidate questions to ask must be a separate section.
- Questions should reference the company, role requirements, tailored CV, fit assessment and gap analysis.
- Prompt must avoid generic coaching output.
- Prompt must avoid inventing candidate experience or claims.
- Interview prep should include warnings for weak areas, gaps or stretch-fit topics.

Screenshots:
1-3.png

---

# Scenario 6 — Inline review and targeted revision

Goal:

Confirm TASK-019 review behavior is usable.

Steps:

1. Open acceptable-fit draft application.
2. Confirm inline review section appears.
3. Accept one suggestion.
4. Keep one original value.
5. Mark one item for targeted revision.
6. Run existing revision flow if available.
7. Confirm only selected content changes.
8. Confirm unrelated content does not change.
9. Confirm draft status remains draft.

Expected:

```text
- Inline differences are visible.
- Decisions can be saved.
- Revision does not change unrelated CV sections.
- Draft remains draft.
```

Result:

Status: PARTIAL

Actual result:

- Inline review section appears.
- Differences are shown as expandable review items.
- Decisions can be selected per item.
- Decisions can be saved.
- Accept / keep / revision_requested options exist.
- It was not easy to clearly compare the original CV against the generated CV in one clean view.
- Targeted revision flow was not fully validated in this round.
- It was not confirmed clearly enough whether only the selected content changed.
- Draft/accepted state behavior was partially checked through Scenario 1.

Changed item:
Not fully validated in this round.

Unrelated content changed:
Not confirmed.

Issues:

- Inline review is technically available, but the comparison UX is not clear enough.
- Original CV and optimized CV should be easier to compare side by side or section by section.
- Targeted revision should be retested after review/PDF design cleanup.
- Need to confirm that targeted revision changes only selected items.
- Need to confirm unrelated CV sections remain unchanged.
- This should be revisited together with CV review design and PDF layout fixes.

Screenshots:
1-1.png, 1-2.png, 1-3.png

---

# Scenario 7 — Accept CV, PDF and reopen

Goal:

Confirm final CV output is stable.

Steps:

1. Accept a draft CV.
2. Confirm status becomes accepted.
3. Confirm PDF download becomes available.
4. Download PDF.
5. Open PDF.
6. Confirm PDF has correct candidate.
7. Confirm PDF matches accepted CV content.
8. Restart app.
9. Reopen application from My Applications.
10. Confirm accepted status remains.

Expected:

```text
- Draft PDF blocked.
- Accepted PDF available.
- PDF opens.
- PDF has correct candidate.
- Saved accepted application reloads correctly.
```

Result:

```text
Status: Passed
Actual result:
PDF filename:
Issues:
Screenshots:
```

---

# Scenario 8 — Invalid input

Goal:

Confirm bad user input fails safely.

Tests:

```text
Empty job title:
Empty job ad:
Too-short job ad:
Invalid company format:
Missing candidate profile:
```

Expected:

```text
- Input is rejected before AI call where possible.
- Error is user-safe.
- No broken Firestore record is created.
```

Result:

```text
Status:Passed
Actual result:
Issues:
Screenshots:
```

---

# Scenario 9 — Old saved records

Goal:

Confirm older records still load or fail safely.

Steps:

1. Open older application from My Applications.
2. Confirm it either loads or shows clear fallback/migration message.
3. Confirm app does not crash.
4. Confirm missing new fields do not break display.

Expected:

```text
- Old records do not crash app.
- Missing candidate/company/interview fields show safe empty states.
```

Result:

```text
Status: partial
Actual result:
Application ID:
Issues: Seems that so far for same position and same job add new applicaiton was made and cv was done again
Screenshots:
```

---

# Scenario 10 — Failure and partial-result behavior

Goal:

Confirm failures do not corrupt valid data.

Manual or simulated tests:

```text
Company research fails:
Interview prep fails:
CV optimization succeeds but supporting feature fails:
Firestore read/write fails:
AI provider fails:
Invalid AI JSON:
Unsupported AI CV claim:
```

Expected:

```text
- Controlled error.
- No unvalidated output displayed.
- Existing valid data preserved.
- Main CV result not corrupted by supporting feature failure.
```

Result:

```text
Status:
Actual result:
How failure was triggered:
Issues:
Screenshots/logs:
```

---

# Known Issues Found During Early UI Review

Use this section if still valid after testing.

```text
- Interview prep placement may be wrong if it appears only under company instead of application.
- Interview prep must generate 10–15 likely interviewer questions.
- Candidate questions to ask must be separate from likely interviewer questions.
- Company research is functionally acceptable; cosmetic cleanup may remain.
- Revision flow must not show "The current CV cannot be prepared for revision" on valid acceptable-fit applications.
- App currently may still open on job-ad form instead of stored CV-first landing page.
```

---

# Final Summary

Overall result: PARTIAL

Can demo full workflow: yes, with limitations

Blockers:

- Interview prep is not application-specific.
- Interview prep does not generate 10–15 likely interviewer questions.
- Candidate questions to ask are not clearly separated.
- Company research can fail when Gemini returns JSON that does not match the required schema.

High-priority fixes:

- Move interview prep to application-level storage and application preview.
- Rewrite interview prep prompt/schema for likely interviewer questions.
- Add controlled retry for company research schema validation failures.
- Clean accepted application view so revision controls are hidden after acceptance.
- Improve CV comparison/review UX before retesting targeted revision.

Medium-priority fixes:

- Add visible feedback after saving review decisions.
- Add one Save all decisions button.
- Improve company page readability.
- Improve role fit/risk visual hierarchy.
- Move PDF download button higher.

Cosmetic issues:

- Remove or de-emphasize success modal after optimization.
- Improve headings/subheadings on company page.
- Make fit/risk labels easier to scan visually.

Accepted limitations:

- Scenario 6 targeted revision was not fully validated.
- Scenario 10 failure simulation was not fully tested.
- PDF/design review will be retested after layout cleanup.

Ready for TASK-011 refactor: no
