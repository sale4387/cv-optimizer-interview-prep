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
TASK-012:
TASK-013:
TASK-014:
TASK-019:
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
Status:
Actual result:
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
Status:
Actual first page:
Candidate switch visible: yes/no
Default candidate:
Stored CV visible before optimization: yes/no
Job form placement:
Optimized CV review placement:
Issues:
Screenshots:
```

---

# Scenario 1 — Sale, acceptable-fit application

Goal:

Confirm normal workflow works for Aleksandar/Sale profile.

Inputs:

```text
Candidate profile: Aleksandar Markovic
Company:
Country:
Job title:
Job ad:
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

Result:

```text
Status:
Actual result:
Application ID:
Company key:
Issues:
Screenshots:
```

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
```

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
Status:
Actual result:
Application ID:
Issues:
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
Status:
Actual result:
Application ID:
Issues:
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

Result:

```text
Status:
Actual result:
Company keys:
Issues:
Screenshots:
```

---

# Scenario 5 — Interview preparation quality

Goal:

Confirm interview prep is application-specific and useful.

Steps:

1. Open an acceptable-fit application.
2. Find interview prep from the application preview.
3. Count questions.
4. Check whether questions are likely interviewer questions.
5. Check whether candidate questions to ask are separate.
6. Check whether questions reference job ad, tailored CV or company.
7. Check whether older/smaller experience has prep warnings.
8. Check whether it avoids invented claims.

Expected:

```text
- 10–15 likely interviewer questions.
- Not generic.
- Not only questions candidate should ask.
- Tied to application, position and tailored CV.
- Candidate questions to ask are a separate section.
- No invented facts.
```

Result:

```text
Status:
Question count:
Actual result:
Issues:
Screenshots:
```

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

```text
Status:
Actual result:
Changed item:
Unrelated content changed: yes/no
Issues:
Screenshots:
```

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
Status:
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
Status:
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
Status:
Actual result:
Application ID:
Issues:
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

```text
Overall result:
Can demo full workflow: yes/no
Blockers:
High-priority fixes:
Medium-priority fixes:
Cosmetic issues:
Accepted limitations:
Ready for TASK-011 refactor: yes/no
```
