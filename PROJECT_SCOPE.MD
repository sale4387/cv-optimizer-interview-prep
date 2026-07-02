mkdir cv-optimizer-interview-prep
cd cv-optimizer-interview-prep

git init

cat > PROJECT_SCOPE.md <<'EOF'

# Project Scope

Initial project scope draft.

This document defines:

- what the project is
- who it is for
- what belongs to MVP
- what is out of scope
- how AI should behave
- what success means

The detailed scope will be written and refined during the planning phase.
EOF

git add PROJECT_SCOPE.md
git commit -m "Add initial project scope"

git branch -M main
git remote add origin https://github.com/sale4387/cv-optimizer-interview-prep.git
git push -u origin main
