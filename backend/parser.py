import os
import json
import re
import pdfplumber
from dotenv import load_dotenv

# Load .env file from the same directory as this script
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

# Configure Local LLM / OCR
USE_LOCAL_LLM = os.environ.get("USE_LOCAL_LLM", "false").lower() == "true"
LOCAL_LLM_URL = os.environ.get("LOCAL_LLM_URL", "http://localhost:11434/v1")
LOCAL_LLM_MODEL = os.environ.get("LOCAL_LLM_MODEL", "llama3")
TESSERACT_CMD = os.environ.get("TESSERACT_CMD", "")

if TESSERACT_CMD:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

from google import genai
from google.genai import types

# Configure Gemini API
API_KEY = os.environ.get("GEMINI_API_KEY")
_client = None

if not USE_LOCAL_LLM:
    if API_KEY and API_KEY != "your_gemini_api_key_here":
        _client = genai.Client(api_key=API_KEY)
        print("[SUCCESS] Gemini API key loaded. Parser will use live AI extraction.")
    else:
        print("[WARNING] GEMINI_API_KEY is not set or is still the placeholder value.")
        print("   Open backend/.env and paste your key from https://aistudio.google.com/apikey")
        print("   The parser will run in MOCK MODE until the key is configured.")
else:
    print(f"[INFO] Running in LOCAL LLM mode using: {LOCAL_LLM_URL} (Model: {LOCAL_LLM_MODEL})")

SYSTEM_INSTRUCTION = """
You are an expert financial document parser. Your task is to analyze the bank or credit card statement provided and extract account metadata and a list of ALL transactions.
You must return the result as a strict JSON object matching this schema exactly:
{
  "client_name": "String or null (Identify from statement header — company name or person name on the account)",
  "bank_name": "String (e.g. Chase, Wells Fargo, HSBC, Bank of America, SVB, Citibank)",
  "account_number_suffix": "String (The last 4 digits of the account number or credit card number only)",
  "transactions": [
    {
      "date": "YYYY-MM-DD (normalize all date formats to ISO 8601 YYYY-MM-DD)",
      "description": "String (cleaned merchant/transaction description — remove noise like reference numbers)",
      "amount": "Number (positive absolute value as a float, e.g. 142.50)",
      "type": "debit OR credit (debit = charge/withdrawal/purchase; credit = deposit/payment/refund)"
    }
  ]
}

CRITICAL RULES:
- Capture EVERY SINGLE transaction line in the statement. Do not skip or summarize any rows.
- Each transaction must have a unique amount extracted from that specific row — never repeat amounts.
- Debit/credit determination: charges/purchases/withdrawals = debit. Deposits/payments/refunds = credit.
- Amount must always be a positive float (absolute value). The 'type' field distinguishes direction.
- Normalize all date strings to YYYY-MM-DD regardless of source format (MM/DD/YYYY, DD MMM YYYY, etc).
- Return ONLY the JSON object. No markdown, no explanation, no code fences.
"""

MODEL_NAME = "gemini-2.0-flash"


def extract_text_digitally(file_path: str) -> str:
    """Extracts text from a digital PDF file using pdfplumber."""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error during digital PDF extraction: {e}")
    return text.strip()


def extract_text_via_local_ocr(file_path: str, is_image: bool = False) -> str:
    """Extracts text from scanned PDFs or images locally using pytesseract OCR."""
    import pytesseract
    from PIL import Image

    text = ""
    try:
        if not is_image and file_path.lower().endswith(".pdf"):
            print(f"Performing local OCR on scanned PDF pages: {file_path}")
            # Render PDF pages to PIL images using pdfplumber's built-in pdfium renderer
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    img = page.to_image(resolution=150).original
                    if img.width < 1000:
                        img = img.resize((img.width * 2, img.height * 2), Image.Resampling.LANCZOS)
                    page_text = pytesseract.image_to_string(img)
                    if page_text:
                        text += page_text + "\n"
        else:
            print(f"Performing local OCR on image: {file_path}")
            img = Image.open(file_path)
            if img.width < 1000:
                scale = 3 if img.width < 500 else 2
                print(f"Low resolution image detected ({img.width}x{img.height}). Upscaling by {scale}x for better OCR.")
                img = img.resize((img.width * scale, img.height * scale), Image.Resampling.LANCZOS)
            text = pytesseract.image_to_string(img)
    except Exception as e:
        print(f"Error during local OCR extraction: {repr(e)}")
        # Propagate error so parser fallback handles it
        raise RuntimeError(f"OCR failed: {str(e)}")
    return text.strip()


def clean_and_parse_json(text: str) -> dict:
    """Helper to robustly extract and parse JSON from local LLM outputs."""
    # 1. Extract JSON block if wrapped in conversational text
    match = re.search(r"({.*})", text, re.DOTALL)
    if match:
        text = match.group(1)
        
    text = text.strip()
    
    # 2. Fix trailing commas in arrays/objects (very common LLM syntax error)
    text = re.sub(r",\s*([\]}])", r"\1", text)
    
    # 3. Handle Python-style single quoted outputs if standard JSON parse fails
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try replacing single quotes with double quotes around JSON properties/values
        fixed_text = re.sub(r"'(?=\s*[{}[\]:,\"])", '"', text)
        fixed_text = re.sub(r"(?<=[{}[\]:,\"])\s*'", '"', fixed_text)
        try:
            return json.loads(fixed_text)
        except json.JSONDecodeError as e:
            # Propagate clean error details
            raise json.JSONDecodeError(
                f"Robust parse failed. Cleaned content: {text[:200]}... Error: {e.msg}",
                e.doc, e.pos
            )


def parse_with_local_llm(text: str) -> dict:
    """Queries local OpenAI-compatible endpoint (e.g. Ollama, LM Studio) to parse statement text."""
    import requests
    
    url = f"{LOCAL_LLM_URL.rstrip('/')}/chat/completions"
    headers = {"Content-Type": "application/json"}
    
    prompt = f"Please parse the following bank/credit card statement and extract all transactions:\n\n{text}"
    
    payload = {
        "model": LOCAL_LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    
    print(f"Sending request to local LLM: {url} using model {LOCAL_LLM_MODEL}...")
    response = requests.post(url, headers=headers, json=payload, timeout=300)
    response.raise_for_status()
    
    resp_data = response.json()
    content = resp_data["choices"][0]["message"]["content"]
    
    # Clean and parse content using robust helper
    clean_content = re.sub(r"^```(json)?", "", content.strip(), flags=re.IGNORECASE)
    clean_content = re.sub(r"```$", "", clean_content.strip()).strip()
    
    result = clean_and_parse_json(clean_content)
    result["_is_mock"] = False
    return result


def parse_statement_with_gemini(file_path: str, is_image: bool = False) -> dict:
    """Sends document text or image bytes to Gemini or Local LLM to parse into structured transactions."""
    if USE_LOCAL_LLM:
        try:
            # Extract text
            extracted_text = ""
            if not is_image and file_path.lower().endswith(".pdf"):
                extracted_text = extract_text_digitally(file_path)
            
            # If digital extraction didn't yield enough text, run local OCR
            if len(extracted_text) < 100:
                extracted_text = extract_text_via_local_ocr(file_path, is_image=is_image)
                
            if not extracted_text:
                raise ValueError("No text could be extracted from the document.")
                
            result = parse_with_local_llm(extracted_text)
            return result
        except Exception as e:
            print(f"Local parsing error: {repr(e)}. Falling back to mock data.")
            result = get_mock_statement_data(file_path)
            result["_is_mock"] = True
            result["_error"] = f"Local parsing failed: {str(e)}"
            return result

    if not _client:
        print("No Gemini client — running in mock mode.")
        result = get_mock_statement_data(file_path)
        result["_is_mock"] = True
        return result

    generation_config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        response_mime_type="application/json",
        temperature=0.1,
    )

    try:
        # Digital PDF: extract text first (faster, cheaper, more reliable)
        if not is_image and file_path.lower().endswith(".pdf"):
            extracted_text = extract_text_digitally(file_path)
            if len(extracted_text) > 100:
                print(f"Processing digital PDF text ({len(extracted_text)} chars) with Gemini...")
                response = _client.models.generate_content(
                    model=MODEL_NAME,
                    config=generation_config,
                    contents=f"Please parse the following bank/credit card statement and extract all transactions:\n\n{extracted_text}",
                )
                result = json.loads(response.text)
                result["_is_mock"] = False
                return result

        # Scanned PDF or Image: upload file and send to multimodal model
        print(f"Processing scanned document via Gemini Files API: {file_path}")
        mime_type = "image/png" if is_image else "application/pdf"
        if file_path.lower().endswith(".jpg") or file_path.lower().endswith(".jpeg"):
            mime_type = "image/jpeg"
        elif file_path.lower().endswith(".webp"):
            mime_type = "image/webp"

        uploaded_file = _client.files.upload(
            file=file_path,
            config=types.UploadFileConfig(mime_type=mime_type)
        )

        response = _client.models.generate_content(
            model=MODEL_NAME,
            config=generation_config,
            contents=[
                uploaded_file,
                "Please parse this bank/credit card statement and extract all transactions into JSON."
            ],
        )

        # Clean up uploaded file
        try:
            _client.files.delete(name=uploaded_file.name)
        except Exception:
            pass

        result = json.loads(response.text)
        result["_is_mock"] = False
        return result

    except Exception as e:
        print(f"Gemini API error: {repr(e)}. Falling back to mock data.")
        result = get_mock_statement_data(file_path)
        result["_is_mock"] = True
        result["_error"] = str(e)
        return result


def get_mock_statement_data(file_path: str) -> dict:
    """Generates realistic mock statements for local development and testing."""
    filename = os.path.basename(file_path).lower()

    bank_name = "Chase Bank"
    account_suffix = "9876"
    client_name = "Kabloom Commerce LLC"

    if "wells" in filename:
        bank_name = "Wells Fargo"
        account_suffix = "4321"
    elif "hsbc" in filename:
        bank_name = "HSBC UK"
        account_suffix = "5566"
        client_name = "Prane Global Holdings"
    elif "amex" in filename or "american" in filename:
        bank_name = "American Express"
        account_suffix = "1001"
        client_name = "Kabloom Commerce LLC"

    print(f"[INFO] Generating MOCK data for {bank_name} (suffix: {account_suffix}) - NOT real parsed data")

    return {
        "client_name": client_name,
        "bank_name": bank_name,
        "account_number_suffix": account_suffix,
        "transactions": [
            {"date": "2026-06-01", "description": "AWS Cloud Services Bill", "amount": 1420.50, "type": "debit"},
            {"date": "2026-06-03", "description": "Google Workspace Subscription", "amount": 78.00, "type": "debit"},
            {"date": "2026-06-05", "description": "ACH DEPOSIT - STRIPE PAYMENTS", "amount": 8450.00, "type": "credit"},
            {"date": "2026-06-10", "description": "Slack Technologies Inc.", "amount": 120.00, "type": "debit"},
            {"date": "2026-06-12", "description": "Adobe Creative Cloud", "amount": 82.49, "type": "debit"},
            {"date": "2026-06-15", "description": "ACH DEPOSIT - SHOPIFY INC", "amount": 3120.00, "type": "credit"},
            {"date": "2026-06-18", "description": "Github Inc - Team Subscription", "amount": 40.00, "type": "debit"},
            {"date": "2026-06-20", "description": "Uber Eats Delivery Corp", "amount": 35.60, "type": "debit"},
            {"date": "2026-06-25", "description": "Office Depot - Supplies", "amount": 215.18, "type": "debit"},
            {"date": "2026-06-28", "description": "REFUND - AWS Cloud Services", "amount": 150.00, "type": "credit"},
        ],
    }
