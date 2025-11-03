# Peer Evaluation — Run instructions

Quick copy-paste guide to run this project locally on Windows (PowerShell).

## Prerequisites
- Node.js (v16+)
- npm (or yarn/pnpm)
- Python 3.10+
- A database (Postgres / MySQL / SQLite) — configure via env

## Repository layout
- Frontend: services/frontend
- Backend: services/backend

---

## Backend (FastAPI)

1. Open PowerShell, create & activate a venv:
```powershell
cd "c:\Users\Lenovo\Documents\5th sem\se lab\mini-project\peer-eval\services\backend"
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install Python deps:
```powershell
pip install -r requirements.txt
```

3. Create `.env` in the backend folder (example keys):
```env
# services/backend/.env
DATABASE_URL=postgresql://user:pass@localhost:5432/peer_eval_db
SECRET_KEY=your_secret_here
```

4. (Optional) Run DB migrations (if applicable):
```powershell
# adjust to your migrations tool (alembic/example)
alembic upgrade head
```

5. Start backend (development):
```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Open API docs: http://127.0.0.1:8000/docs

---

## Frontend (React + Vite)

1. Install dependencies:
```powershell
cd "c:\Users\Lenovo\Documents\5th sem\se lab\mini-project\peer-eval\services\frontend"
npm install
```

2. Start dev server:
```powershell
npm run dev
```
Open UI: http://localhost:3000

Notes:
- If you changed fonts via CSS imports and see a Vite/Tailwind error: ensure any `@import` statements are placed at the very top of `services/frontend/src/index.css` (before other rules) OR add the font `<link>` in `services/frontend/index.html` head.
- If fonts don't appear, hard refresh (Ctrl+Shift+R) or clear cache.

---

## Run both (recommended)
Open two PowerShell windows/tabs and run backend and frontend commands in each.

Optional small PowerShell helper (create `start-all.ps1` in repo root):
```powershell
# filepath: c:\Users\Lenovo\Documents\5th sem\se lab\mini-project\start-all.ps1
Start-Process powershell -ArgumentList "-NoExit","-Command","cd `\"c:\Users\Lenovo\Documents\5th sem\se lab\mini-project\peer-eval\services\backend`\"; .venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
Start-Process powershell -ArgumentList "-NoExit","-Command","cd `\"c:\Users\Lenovo\Documents\5th sem\se lab\mini-project\peer-eval\services\frontend`\"; npm run dev"
```

Run it from PowerShell:
```powershell
.\start-all.ps1
```

---

## Production (brief)
- Frontend: `npm run build` in services/frontend -> `dist/`
- Backend: run uvicorn/gunicorn behind a reverse proxy (NGINX) on 0.0.0.0

---

## Troubleshooting
- Backend 500 errors: check backend terminal logs; verify `DATABASE_URL`, migrations, and `.env`.
- Tailwind/Vite CSS error: "[@import must precede all other statements]" — move font `@import` to top of `src/index.css` or add the `<link>` to `index.html`.
- Font not updating: hard refresh (Ctrl+Shift+R), clear cache, or verify font link is present in `services/frontend/index.html`.

If you want, I can add a `.env.example`, a startup script for Windows, or fix the font import in your frontend files.
```// filepath: c:\Users\Lenovo\Documents\5th sem\se lab\mini-project\README.md
# Peer Evaluation — Run instructions

Quick copy-paste guide to run this project locally on Windows (PowerShell).

## Prerequisites
- Node.js (v16+)
- npm (or yarn/pnpm)
- Python 3.10+
- A database (Postgres / MySQL / SQLite) — configure via env

## Repository layout
- Frontend: services/frontend
- Backend: services/backend

---

## Backend (FastAPI)

1. Open PowerShell, create & activate a venv:
```powershell
cd "c:\Users\Lenovo\Documents\5th sem\se lab\mini-project\peer-eval\services\backend"
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install Python deps:
```powershell
pip install -r requirements.txt
```

3. Create `.env` in the backend folder (example keys):
```env
# services/backend/.env
DATABASE_URL=postgresql://user:pass@localhost:5432/peer_eval_db
SECRET_KEY=your_secret_here
```

4. (Optional) Run DB migrations (if applicable):
```powershell
# adjust to your migrations tool (alembic/example)
alembic upgrade head
```

5. Start backend (development):
```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Open API docs: http://127.0.0.1:8000/docs

---

## Frontend (React + Vite)

1. Install dependencies:
```powershell
cd "c:\Users\Lenovo\Documents\5th sem\se lab\mini-project\peer-eval\services\frontend"
npm install
```

2. Start dev server:
```powershell
npm run dev
```
Open UI: http://localhost:3000

Notes:
- If you changed fonts via CSS imports and see a Vite/Tailwind error: ensure any `@import` statements are placed at the very top of `services/frontend/src/index.css` (before other rules) OR add the font `<link>` in `services/frontend/index.html` head.
- If fonts don't appear, hard refresh (Ctrl+Shift+R) or clear cache.

---

## Run both (recommended)
Open two PowerShell windows/tabs and run backend and frontend commands in each.

Optional small PowerShell helper (create `start-all.ps1` in repo root):
```powershell
# filepath: c:\Users\Lenovo\Documents\5th sem\se lab\mini-project\start-all.ps1
Start-Process powershell -ArgumentList "-NoExit","-Command","cd `\"c:\Users\Lenovo\Documents\5th sem\se lab\mini-project\peer-eval\services\backend`\"; .venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
Start-Process powershell -ArgumentList "-NoExit","-Command","cd `\"c:\Users\Lenovo\Documents\5th sem\se lab\mini-project\peer-eval\services\frontend`\"; npm run dev"
```

Run it from PowerShell:
```powershell
.\start-all.ps1
```

---

## Production (brief)
- Frontend: `npm run build` in services/frontend -> `dist/`
- Backend: run uvicorn/gunicorn behind a reverse proxy (NGINX) on 0.0.0.0

---

## Troubleshooting
- Backend 500 errors: check backend terminal logs; verify `DATABASE_URL`, migrations, and `.env`.
- Tailwind/Vite CSS error: "[@import must precede all other statements]" — move font `@import` to top of `src/index.css` or add the `<link>` to `index.html`.
- Font not updating: hard refresh (Ctrl+Shift+R), clear cache, or verify font link is present in `services/frontend/index.html`.

If you want, I can add a `.env.example`, a startup script for Windows, or fix the font import in your frontend files.
