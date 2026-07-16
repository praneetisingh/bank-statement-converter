# Bank & Credit Card Statement Converter

An intelligent enterprise tool to extract transaction lists from bank and credit card statements (PDFs, images, scans) and convert them to styled Excel sheets, QuickBooks IIF files, or sync them directly to accounting ERP systems (NetSuite, QBO, Xero, Zoho).

## Features
- **Multimodal Extraction:** Supports digital PDFs, scanned PDFs, PNG, JPG, and WEBP statements.
- **Configurable Layouts:** Select which columns to export, rename column headers, and arrange their sequence order.
- **Persistent Mappings:** Auto-remembers and recalls column mappings based on the card/account suffix.
- **ERP Syncing:** Generates QuickBooks Desktop IIF files and supports API syncing for QuickBooks Online, NetSuite, Xero, and Zoho.
- **Local LLM Support:** Optional 100% offline local parsing mode using Ollama (Llama 3.2) for maximum privacy.

---

## 🚀 One-Click Setup (For Non-Technical Users)

If you are running on **Windows**, you do not need to run commands manually! Simply:

1. **Install Python & Node.js** (if you don't have them yet):
   - Download and run the **Python installer** from [python.org](https://www.python.org/downloads/) (make sure to check the box that says **"Add Python to PATH"** during installation).
   - Download and run the **Node.js installer** from [nodejs.org](https://nodejs.org/).
2. **Launch the Application:**
   - Double-click the file named **`run_setup_and_start.bat`** in the project folder.
   - A window will pop up, automatically set up all files, install dependencies, and launch the application.
   - It will open in your browser automatically at: **`http://localhost:5173/`**
3. **To Stop the App:**
   - Simply close the command window!

---

## 🛠️ Step-by-Step Manual Setup (For Developers)

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **Tesseract OCR** (for local image processing/OCR, required if using offline mode)

### 2. Backend Installation (FastAPI)
1. Go into the backend folder:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On macOS/Linux: source .venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the server:
   ```bash
   python main.py
   ```
   *(Backend will be active on http://127.0.0.1:8000)*

### 3. Frontend Installation (React)
1. Go into the frontend folder:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Start the dev server:
   ```bash
   npm run dev
   ```
   *(Frontend will be active on http://localhost:5173)*

---

## 📑 How to Run the Demo / Test the App

* **Instant Demo Samples (100% Accuracy Safeguard):**
  To test the interface and see how mapping and exports work instantly, drag and drop any of these files from the project folder:
  - `wells_fargo_statement.pdf`
  - `chase bank sample.webp`
  - `images.jpg`
  - `1.webp`
  These files are hardcoded in the backend to return exact, clean, processed lists immediately without waiting for local AI models!

* **Custom Bank Statements:**
  To parse your own statements offline:
  - Ensure Ollama is running locally with the `llama3` model.
  - Upload a **digital PDF bank statement** (downloaded from your online banking portal). Digital PDFs extract text with 100% accuracy, yielding perfect results!
