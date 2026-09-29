# Bank & Credit Card Statement Converter

A local web application for turning statement PDFs or images into transaction tables and exports. It combines a React/Vite frontend with a FastAPI backend.

## What the demo shows

- Upload and review a statement file.
- Inspect and adjust the extracted transaction columns.
- Export the resulting table as an Excel workbook.
- Try the included `wells_fargo_statement.pdf` sample to see the interface and export flow without external AI credentials.

**Demo mode caveat:** the bundled sample filename uses canned demo transactions. It does not parse the sample PDF, and it does not demonstrate OCR/LLM accuracy. Custom statements require a configured Gemini API key or local LLM endpoint; scanned documents also need OCR support. Review all generated financial data before using it.

## Run locally

Requirements: Python 3.10+, Node.js 18+.

```sh
# Terminal 1: backend
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

```sh
# Terminal 2: frontend
cd frontend
npm ci
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). The Vite development server proxies `/api` to the backend on port 8000. The Docker Compose setup serves the frontend and API through the container configuration.

## Stack

React, Vite, FastAPI, Python, OCR/LLM integrations, and Excel export tooling. See `backend/requirements.txt`, `frontend/package.json`, and the source for implementation details.
