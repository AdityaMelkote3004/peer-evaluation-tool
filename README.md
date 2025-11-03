# Peer Evaluation — Run & Cleanup Instructions

Copy-paste this entire block into `README.md` (single markdown cell). These instructions cover running the project locally (Windows / PowerShell) and finishing secure cleanup of the accidentally committed `.env`.

---

## Repository layout
- Frontend: `services/frontend` (React + Vite + Tailwind)
- Backend: `services/backend` (FastAPI)
- Example env: `services/backend/.env.example` (placeholders only — DO NOT commit secrets)

> IMPORTANT: A real `services/backend/.env` containing secrets was present in the repo history. That file has been removed from tracking and an `.env.example` added. Rotate any exposed secrets immediately (Supabase keys, DB password). See the "Secrets & Git history" section below.

---

## Prerequisites
- Node.js (v16+)
- npm
- Python 3.10+
- Git
- A database (Postgres / Supabase / SQLite)

---

## 1) Backend — Local development (PowerShell)

1. Change to the backend folder:
    
    cd "c:\Users\Lenovo\Documents\5th sem\se lab\mini-project\peer-eval\services\backend"

2. Create & activate a Python virtual environment:
    
    python -m venv .venv
    # Activate in PowerShell
    .venv\Scripts\Activate.ps1

3. Install Python dependencies:
    
    pip install -r requirements.txt

4. Create a local `.env` from the example and edit it (DO NOT commit):
    
    Copy-Item .env.example .env
    notepad .env   # add real values and save

   Populate:
   - `DATABASE_URL`, `ASYNC_DATABASE_URL`
   - `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
   - `SECRET_KEY`, etc.

5. (Optional) Run migrations (if applicable):
    
    # Example if Alembic is configured
    alembic upgrade head

6. Start the backend (development):
    
    python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

Open API docs: http://127.0.0.1:8000/docs

---

## 2) Frontend — Local development (PowerShell)

1. Change to the frontend folder:
    
    cd "c:\Users\Lenovo\Documents\5th sem\se lab\mini-project\peer-eval\services\frontend"

2. Install dependencies:
    
    npm install

3. Start the dev server:
    
    npm run dev

Open the UI: http://localhost:3000

Notes:
- If you see a Vite/Tailwind CSS error: `@import must precede all other statements`, move any `@import` font lines to the very top of `services/frontend/src/index.css` OR add the font `<link>` in `services/frontend/index.html` head.
- If fonts/CSS don't update, do a hard refresh (Ctrl+Shift+R) or use an incognito window.

---

## 3) Run both simultaneously (optional)

Create `start-all.ps1` in the repo root containing:

    Start-Process powershell -ArgumentList "-NoExit","-Command","cd `\"c:\Users\Lenovo\Documents\5th sem\se lab\mini-project\peer-eval\services\backend`\"; .venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
    Start-Process powershell -ArgumentList "-NoExit","-Command","cd `\"c:\Users\Lenovo\Documents\5th sem\se lab\mini-project\peer-eval\services\frontend`\"; npm run dev"

Run it:

    .\start-all.ps1

---

## 4) Production build (brief)

Frontend:

    cd services/frontend
    npm run build
    # deploy contents of services/frontend/dist

Backend (example):

    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    # run behind a reverse proxy (NGINX) in production

---

## 5) Verify `.env` is NOT tracked locally

From repo root:

    git ls-files | Select-String "\.env" -AllMatches | ForEach-Object { $_.ToString() }

You should only see `peer-eval/services/backend/.env.example` (and other non-sensitive entries); `peer-eval/services/backend/.env` should NOT appear.

---

## 6) Secrets — Rotate immediately (essential)

If secrets were pushed, rotate them now (do this before or immediately after history purge):

- Supabase:
  - Dashboard → Project → Settings → API
  - Revoke old ANON and SERVICE_ROLE keys; generate new keys
  - Update local `services/backend/.env` (do NOT commit)

- Database:
  - Change DB password or create a new DB user
  - Update `DATABASE_URL` / `ASYNC_DATABASE_URL` in local `.env` and deployment settings

- CI / hosting:
  - Update environment variables with the new secrets

---

## 7) Purge `.env` from git history (optional, advanced)

To remove secrets from all commits (rewrites history). **Do this from a mirror clone; rewriting history forces all collaborators to re-clone.**

Recommended: `git-filter-repo`

1. Install (if needed):

    pip install git-filter-repo

2. Create a mirror clone:

    git clone --mirror https://github.com/AdityaMelkote3004/peer-evaluation-tool.git
    Set-Location .\peer-evaluation-tool.git

3. Remove the file from history:

    git filter-repo --path peer-eval/services/backend/.env --invert-paths

4. Force-push cleaned history:

    git push --force --all
    git push --force --tags

Alternative: BFG Repo-Cleaner (similar effect). After rewrite: inform collaborators to re-clone:

    git clone https://github.com/AdityaMelkote3004/peer-evaluation-tool.git

---

## 8) Helpful git commands (quick)

Stop tracking `.env` (if needed):

    git rm --cached peer-eval/services/backend/.env
    git add .gitignore
    git commit -m "Stop tracking .env and add to .gitignore"
    git push origin main

Search history for `.env` occurrences (quick heuristic):

    git log --all --pretty=format:%H --name-only | Select-String "peer-eval/services/backend/.env" -SimpleMatch

---

## 9) Troubleshooting

- Vite/Tailwind CSS `@import` error: ensure any `@import` is at the top of `src/index.css` or use `<link>` in `index.html`.
- Backend 500 errors: check logs, verify `DATABASE_URL`, run migrations.
- After history rewrite: do not `git pull`; re-clone the repo.
- Fonts not showing: hard-refresh cache (Ctrl+Shift+R) or test in incognito mode.

---

## 10) Next steps I can help with

If you want, I can:
- Generate a PowerShell script to perform the history purge (ready-to-run).
- Perform the purge and force-push (I will not proceed without your confirmation).
- Provide step-by-step rotation instructions for Supabase keys.
- Add a `SECURITY.md` snippet documenting the rotation and notification steps.

---

Paste this entire block into `README.md` — it is a single uninterrupted markdown cell ready for GitHub.
