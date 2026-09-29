# LegalEase — AI-Powered Legal Document Generator

A complete FastAPI + Streamlit + Google Gemini application for creating editable legal-document drafts and exporting TXT, DOCX, and PDF.

> LegalEase is a drafting aid, not legal advice. AI output can contain errors and may not satisfy jurisdiction-specific requirements. Review with a qualified legal professional before signing or relying on a document.

## Project structure

```text
LegalEase/
├── backend/
│   ├── main.py
│   ├── routes.py
│   ├── schemas.py
│   ├── config.py
│   ├── ai_core/gemini_generator.py
│   └── services/{document_service.py,exporters.py}
├── frontend/app.py
├── tests/test_api.py
├── assets/
├── requirements.txt
├── .env.example
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
└── README.md
```

## Local VS Code setup

1. Open this folder in VS Code.
2. Install Python 3.10+.
3. Create a virtual environment.

Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

4. Install dependencies:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

5. Copy `.env.example` to `.env` and set:
```env
GEMINI_API_KEY=your_real_key
GEMINI_MODEL=gemini-2.5-flash
BACKEND_URL=http://127.0.0.1:8000
FRONTEND_URL=http://localhost:8501
```

6. Start FastAPI in terminal 1:
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

7. Start Streamlit in terminal 2:
```bash
streamlit run frontend/app.py
```

Open the Streamlit URL shown in the terminal, normally http://localhost:8501.

## Test

The automated tests mock Gemini, so a real API key is not required:
```bash
pytest -q
```

## API checks

- `GET /` — service status
- `GET /health` — health/configuration status
- `POST /generate` — Gemini document generation
- `POST /export/txt` — TXT export
- `POST /export/docx` — DOCX export
- `POST /export/pdf` — PDF export
- `/docs` — FastAPI Swagger UI

## Docker

Create `.env`, then:
```bash
docker compose up --build
```

Frontend: http://localhost:8501
Backend: http://localhost:8000

## Example input

Document type: `Freelance Work Contract`

Parties:
`Jane Doe (Service Provider), TechNova Inc. (Client)`

Terms:
`Payment within 30 days; Confidentiality must be maintained; Either party may terminate with 15 days notice`

Effective date:
`2026-04-15`

The UI supports editing the generated text and exporting the edited version with an optional logo.

## Design decisions based on the supplied specification

The supplied document defines Streamlit as the frontend, FastAPI as the backend, Gemini as the AI core, and DOCX/PDF/TXT export. It also specifies inputs for document type, parties, terms and dates, editable previews, and branded exports.

The source specifies Gemini 1.5 Pro. The implementation instead makes the model configurable through `GEMINI_MODEL`, with `gemini-2.5-flash` as the default, so a currently available model can be selected without code changes.

Terms are still accepted as semicolon-separated clauses, and the export service creates a key-terms table in DOCX and branding/footer elements in DOCX/PDF.

## Security and reliability

- API key stays on the backend.
- `.env` is ignored by Git.
- Pydantic validates incoming fields.
- Export endpoints do not call Gemini.
- Gemini calls have controlled generation settings.
- Automated tests cover health, generation flow, and all three export formats.
