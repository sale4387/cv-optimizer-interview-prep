# TASK-010 Manual UI Checks

Run:

```powershell
streamlit run streamlit/app.py
```

## Review controls

1. Open a draft application.
2. Confirm that `Request changes` and `Accept CV` are visible.
3. Confirm that PDF download is not available while status is `draft`.

## Revision comments

1. Click `Request changes`.
2. Select one editable section.
3. Add a comment.
4. Edit the comment.
5. Clear the comment or unselect the section to remove it.
6. Select another section and add a comment.

## Cancel

1. Click `Cancel`.
2. Confirm that the revision form closes.
3. Confirm that the CV remains unchanged and in `draft` status.

## Make changes

1. Add at least one selected section and comment.
2. Click `Make changes`.
3. Confirm that the updated preview opens.
4. Confirm that only requested sections changed.
5. Confirm that status remains `draft`.

## Accept and PDF

1. Click `Accept CV`.
2. Confirm that status becomes `accepted`.
3. Confirm that revision controls disappear.
4. Confirm that `Download CV as PDF` becomes available.
5. Download and open the PDF.
