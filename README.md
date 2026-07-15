# Bank & Credit Card Statement Converter

An intelligent enterprise tool to extract transaction lists from bank and credit card statements (PDFs, images, scans) and convert them to styled Excel sheets, QuickBooks IIF files, or sync them directly to accounting ERP systems (NetSuite, QBO, Xero, Zoho).

## Features
- **Multimodal Extraction:** Supports digital PDFs, scanned PDFs, PNG, JPG, and WEBP statements.
- **Configurable Layouts:** Select which columns to export, rename column headers, and arrange their sequence order.
- **Persistent Mappings:** Auto-remembers and recalls column mappings based on the card/account suffix.
- **ERP Syncing:** Generates QuickBooks Desktop IIF files and supports API syncing for QuickBooks Online, NetSuite, Xero, and Zoho.
- **Local LLM Support:** Optional 100% offline local parsing mode using Ollama (Llama 3.2) for maximum privacy.

---

## Getting Started

### Prerequisites
- Docker & Docker Compose
- *For Local LLM (Optional):* Ollama installed on the host machine.

### Environment Setup
Create a `.env` file inside the `backend/` directory:
```ini
# backend/.env
GEMINI_API_KEY=your_gemini_api_key

# Set to true to run parsing locally via Ollama
USE_LOCAL_LLM=true
LOCAL_LLM_URL=http://localhost:11434/v1
LOCAL_LLM_MODEL=llama3.2:latest
```

---

## How to Run

### Option 1: Docker Compose (Recommended)
Build and run the entire stack (Frontend on port `80`, Backend on port `8000`) in detached mode:
```bash
docker-compose up --build -d
```

### Option 2: Local Development Setup

#### Backend (FastAPI)
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the API server:
   ```bash
   python main.py
   ```

#### Frontend (React + Vite)
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173` in your browser.
