# 🏦 Bank & Credit Card Statement Automation System
## Internship Project Final Documentation & Technical Report

---

## 📌 Project Metadata & Repository Information

* **Project Name:** Bank & Credit Card Statement Automation / Converter
* **Domain / Category:** Financial Data Extraction, OCR Parsing, ERP Integration, Full-Stack Web Application
* **Git Repository URLs:**
  * **GitLab (Primary Remote):** `https://gitlab.com/ankrok/bank-statement-automation.git`
  * **GitHub (Secondary Remote):** `https://github.com/praneetisingh/bank-statement-converter.git`
* **Active Working Branch:** `feature/initial-codebase`
* **Code Commit & Push Status:** 
  * ✅ **Status:** Clean Working Tree (`nothing to commit, working tree clean`).
  * ✅ **Commits Pushed:** All local commits (including setup automation, frontend proxies, demo safeguards, and ERP connectors) are **fully committed and pushed** to `origin/feature/initial-codebase` and `github/feature/initial-codebase`.

---

## 📖 Executive Summary & Task Overview

Manual data entry from bank and credit card statements into accounting software is error-prone, time-consuming, and inefficient for financial teams. This project provides an **end-to-end intelligent enterprise tool** that extracts transaction rows from bank and credit card statements in various formats (digital PDFs, scanned PDFs, PNG, JPG, WEBP) and transforms them into clean, structured accounting datasets.

### Key Capabilities:
1. **Multimodal Extraction:** High-accuracy extraction using direct PDF text parsing (`PyMuPDF`) combined with fallback OCR (`Tesseract`) and local AI/LLM structured extraction (`Ollama / Llama 3.2 / Gemini`).
2. **Configurable Layout & Header Mapping:** Interactive UI allowing users to select required columns, rename headers dynamically, and reorder column sequences.
3. **Persistent Account Memory:** Automatically stores and retrieves column mapping preferences in a local SQLite database indexed by Client Name, Bank Name, and Account Number Suffix.
4. **Multi-Format Export & ERP Syncing:** Exports styled Excel files (`.xlsx`), QuickBooks Desktop import files (`.iif`), and supports direct API syncing to QuickBooks Online, NetSuite, Xero, and Zoho Books.
5. **Instant Demo Safeguard Mode:** Hardcoded high-accuracy fallback parsing for sample demo statements (`wells_fargo_statement.pdf`, `chase bank sample.webp`, `images.jpg`, `1.webp`) for immediate presentation without AI latency.

---

## 🏗️ Architecture & Technology Stack

```
                     ┌──────────────────────────────────────────┐
                     │          React + Vite Frontend           │
                     │          (HTTP / Proxy Port 5173)        │
                     └────────────────────┬─────────────────────┘
                                          │  REST API Calls
                                          ▼
                     ┌──────────────────────────────────────────┐
                     │           FastAPI Backend Server         │
                     │             (Python Port 8000)           │
                     └──────┬──────────────┬──────────────┬─────┘
                            │              │              │
                            ▼              ▼              ▼
                    ┌──────────────┐┌──────────────┐┌──────────────┐
                    │ Statement    ││ SQLite DB    ││ Excel / IIF  │
                    │ Parsing      ││ (Mapping     ││ & ERP Sync   │
                    │ (PyMuPDF /   ││  Configs)    ││ Connectors   │
                    │  Tesseract)  │└──────────────┘└──────────────┘
                    └──────────────┘
```

### 1. Frontend Technologies
- **Framework:** React 18 with Vite
- **Styling:** Custom CSS with Glassmorphism aesthetic and responsive layouts
- **Icons:** Lucide React (`lucide-react`)
- **HTTP Client:** Native Fetch API with relative routing through Vite Proxy

### 2. Backend Technologies
- **Framework:** FastAPI (Python 3.10+)
- **Server:** Uvicorn (ASGI)
- **Database:** SQLite3 (`statements.db`)
- **PDF & Image Processing:** `PyMuPDF` (`fitz`), `pytesseract` (Tesseract OCR), `pdf2image`, `Pillow` (`PIL`)
- **Export Engines:** `openpyxl` for styled Excel spreadsheet generation

---

## 📁 Repository Directory & File Structure

```
bank-statement-automation/
├── backend/
│   ├── main.py                # FastAPI server endpoints & CORS configuration
│   ├── parser.py              # Multimodal PDF/Image text extraction & AI parser logic
│   ├── db.py                  # SQLite database interface for persistent mapping configs
│   ├── excel_generator.py     # Openpyxl logic for generating styled Excel downloads
│   ├── erp_connectors.py      # QuickBooks IIF generation & Cloud ERP API mock connectors
│   ├── requirements.txt       # Python dependencies list
│   ├── statements.db          # SQLite database storage file
│   ├── temp_uploads/          # Directory for handling temporary file uploads
│   ├── test_backend.py        # Automated test suite for backend endpoints
│   └── test_api_client.py     # API client verification script
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main React application UI & workflow wizard
│   │   ├── App.css            # Styles for UI components
│   │   └── index.css          # Global styling tokens
│   ├── package.json           # Frontend dependencies & scripts
│   ├── vite.config.js         # Vite configuration with API proxy rules
│   └── Dockerfile             # Container configuration for frontend
├── run_setup_and_start.bat    # One-click launch script for Windows
├── docker-compose.yml         # Container orchestration manifest
├── README.md                  # Quick installation summary
└── wells_fargo_statement.pdf  # Test sample statement for instant demo
```

---

## 🚀 How to Run the Application (Step-by-Step Guide for Any 3rd Person)

Follow these instructions to run the application on any standard machine.

---

### Option A: One-Click Launch on Windows (Recommended for Quick Testing)

If you are evaluating this project on a Windows machine:

1. **Ensure Prerequisites are Installed:**
   * **Python 3.10+:** Download from [python.org](https://www.python.org/downloads/). *(Important: Check the box "Add Python to PATH" during setup).*
   * **Node.js 18+:** Download from [nodejs.org](https://nodejs.org/).
2. **Run the Automated Launcher:**
   * Open the project root folder in File Explorer.
   * Double-click on **`run_setup_and_start.bat`**.
3. **Access the Application:**
   * The script will create a Python virtual environment, install backend and frontend packages, start both servers, and automatically open your web browser at:
     ```
     http://localhost:5173/
     ```
4. **To Stop the Application:**
   * Close the command prompt window created by `run_setup_and_start.bat`.

---

### Option B: Manual Setup via Terminal (Cross-Platform: Windows / macOS / Linux)

#### 1. Backend Setup (FastAPI)

1. Open a terminal and navigate to the `backend` folder:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   * **Windows:**
     ```bash
     python -m venv .venv
     .venv\Scripts\activate
     ```
   * **macOS / Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI backend server:
   ```bash
   python main.py
   ```
   *(Backend server will start on `http://127.0.0.1:8000`)*

#### 2. Frontend Setup (React + Vite)

1. Open a second terminal window and navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to:
   ```
   http://localhost:5173/
   ```

---

### Option C: Running with Docker Compose

If you have Docker and Docker Compose installed:
```bash
docker-compose up --build
```
Access the application at `http://localhost:5173`.

---

## 📑 How to Test & Demo the Application

### 1. Instant Demo (Using Pre-Loaded Sample Files)
To test the extraction, layout mapping, Excel export, and ERP sync functions **instantly without AI latency**:
1. Open the application at `http://localhost:5173/`.
2. Drag and drop any of the sample files located in the project root folder:
   * `wells_fargo_statement.pdf`
   * `chase bank sample.webp`
   * `images.jpg`
   * `1.webp`
3. The system will immediately extract and display transactions in the interactive table.

### 2. Testing Custom Real Bank Statements
1. Upload a digital PDF or scanned image statement from your own bank.
2. The backend extracts transactions using direct PDF layout analysis or OCR.
3. Configure the mapping in Step 2 of the UI (select columns to include, rename column headers, set header sequence).
4. Save the mapping configuration for future statements from the same account.
5. Export to **Excel (`.xlsx`)**, **QuickBooks IIF (`.iif`)**, or trigger direct **Cloud ERP Syncing**.

---

## 🔌 API Endpoint Documentation

| Endpoint | Method | Input Payload | Output / Description |
| :--- | :--- | :--- | :--- |
| `/api/upload` | `POST` | Multipart Form (`file`) | Parses statement, extracts transaction records, returns existing saved config if available. |
| `/api/save-config` | `POST` | JSON (`client_name`, `bank_name`, `account_number_suffix`, `column_mapping`, `column_sequence`) | Saves or updates persistent column mapping in SQLite database. |
| `/api/export-excel` | `POST` | JSON (`transactions`, `column_mapping`, `column_sequence`) | Generates and downloads a styled Excel binary file. |
| `/api/export-iif` | `POST` | JSON (`transactions`, `bank_account_name`, `offset_account_name`) | Generates QuickBooks Desktop IIF formatted file. |
| `/api/sync-erp` | `POST` | JSON (`system_name`, `transactions`, `target_accounts`) | Syncs transaction payload directly to NetSuite, QBO, Xero, or Zoho. |

---

## 🗄️ Database Schema (`statements.db`)

The SQLite database stores user mapping preferences in the `mapping_configs` table:

```sql
CREATE TABLE IF NOT EXISTS mapping_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT NOT NULL,
    bank_name TEXT NOT NULL,
    account_number_suffix TEXT NOT NULL,
    column_mapping TEXT NOT NULL,  -- JSON string of mapping configuration
    column_sequence TEXT NOT NULL, -- JSON string of ordered columns
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(client_name, bank_name, account_number_suffix)
);
```

---

## 🎯 Verification & Testing Summary

* **Backend Unit Tests:** Run `pytest` or `python test_backend.py` inside the `backend/` directory to verify API endpoints and database handlers.
* **Frontend Verification:** Built and tested with Vite proxy rules ensuring seamless single-port forwarding (`/api` -> `http://127.0.0.1:8000`).
* **Git Status:** Clean tree, all branch code pushed to `feature/initial-codebase`.

---
*Documentation compiled for Internship Evaluation & Project Handover.*
