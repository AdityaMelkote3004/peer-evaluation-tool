# Peer Evaluation — Run & Cleanup Instructions

Copy-paste this entire block into `README.md` (single markdown cell). These instructions cover running the project locally (Windows / PowerShell) and finishing secure cleanup of the accidentally committed `.env`.

---

## Repository layout
- Frontend: `services/frontend` (React + Vite + Tailwind)
- Backend: `services/backend` (FastAPI)
- Example env: `services/backend/.env.example` (placeholders only — DO NOT commit secrets)

> IMPORTANT: A real `services/backend/.env` containing secrets was present in the repo history. That file has been removed from tracking and an `.env.example` added. Rotate any exposed secrets immediately (Supabase keys, DB password). See the "Secrets & Git history" section below.

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



5. Start the backend (development):
    
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




- Add a `SECURITY.md` snippet documenting the rotation and notification steps.

---

Paste this entire block into `README.md` — it is a single uninterrupted markdown cell ready for GitHub.
