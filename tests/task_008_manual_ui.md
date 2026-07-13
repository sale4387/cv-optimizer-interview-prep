# TASK-008 Manual UI and PDF Checks

Run:

```powershell
streamlit run streamlit/app.py
```

## Test 1 — Success modal and preview

1. Enter a job title.
2. Enter the company as `Company Name - NL`.
3. Paste a job advertisement of at least 100 characters.
4. Click `Optimize CV`.
5. Confirm that the modal says `Your CV is ready`.
6. Click `Check it now`.
7. Confirm that the preview opens in the same browser tab.

## Test 2 — My Applications

1. Create another application or close the success modal.
2. Open `My Applications`.
3. Confirm that the newest application appears first.
4. Click `Open`.
5. Confirm that the correct saved CV opens.

## Test 3 — Browser PDF

1. Open a CV preview.
2. Click `Print / Save as PDF`, or press `Ctrl+P`.
3. Choose `Save as PDF`.
4. Confirm that the CV is readable.
5. Confirm that the target length is no more than two pages.

## Test 4 — Missing application

Open this path with a fake ID:

```text
?page=preview&application_id=does-not-exist
```

Confirm that the app shows a controlled not-found message.
