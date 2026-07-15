from dotenv import load_dotenv
load_dotenv(dotenv_path=__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), ".env"))
import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import io

import db
import parser
import excel_generator
import erp_connectors

app = FastAPI(title="Bank Statement Converter API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_uploads")
os.makedirs(TEMP_DIR, exist_ok=True)

# Pydantic schemas for request validation
class MappingConfigRequest(BaseModel):
    client_name: str
    bank_name: str
    account_number_suffix: str
    column_mapping: dict
    column_sequence: list

class ExcelExportRequest(BaseModel):
    transactions: list
    column_mapping: dict
    column_sequence: list

class IIFExportRequest(BaseModel):
    transactions: list
    bank_account_name: str = "Bank Clearing Account"
    offset_account_name: str = "Uncategorized Expense/Income"

class ERPSyncRequest(BaseModel):
    system_name: str
    transactions: list
    target_accounts: dict = None

@app.post("/api/upload")
async def upload_statement(file: UploadFile = File(...)):
    """
    Receives statement PDF or PNG, parses details using Gemini, 
    and checks if a mapping configuration already exists.
    """
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in [".pdf", ".png", ".jpg", ".jpeg", ".webp"]:
        raise HTTPException(status_code=400, detail="Only PDF, PNG, JPG, and WEBP files are supported.")
        
    is_image = ext in [".png", ".jpg", ".jpeg", ".webp"]
    temp_path = os.path.join(TEMP_DIR, filename)
    
    try:
        # Save file locally for extraction
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Parse statement
        parsed_data = parser.parse_statement_with_gemini(temp_path, is_image=is_image)
        
        # Check database for saved mapping configuration based on parsed metadata
        client_name = parsed_data.get("client_name") or "Unknown"
        bank_name = parsed_data.get("bank_name") or "Unknown Bank"
        account_suffix = parsed_data.get("account_number_suffix") or "0000"
        
        saved_config = db.get_mapping_config(client_name, bank_name, account_suffix)
        
        is_mock = parsed_data.get("_is_mock", False)
        mock_error = parsed_data.get("_error", None)
        return {
            "success": True,
            "filename": filename,
            "client_name": client_name,
            "bank_name": bank_name,
            "account_number_suffix": account_suffix,
            "transactions": parsed_data.get("transactions", []),
            "saved_config": saved_config,
            "is_mock": is_mock,
            "mock_error": mock_error
        }
        
    except Exception as e:
        print(f"Upload error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Failed to parse statement: {str(e)}"}
        )
    finally:
        # Keep temp file for debugging/OCR diagnostics
        pass

@app.post("/api/save-config")
async def save_config(req: MappingConfigRequest):
    """Saves or updates column mapping and sorting parameters."""
    success = db.save_mapping_config(
        client_name=req.client_name,
        bank_name=req.bank_name,
        account_number_suffix=req.account_number_suffix,
        column_mapping=req.column_mapping,
        column_sequence=req.column_sequence
    )
    if success:
        return {"success": True, "message": "Mapping configuration saved successfully."}
    raise HTTPException(status_code=500, detail="Failed to save mapping configuration.")

@app.post("/api/export-excel")
async def export_excel(req: ExcelExportRequest):
    """Generates and streams a custom formatted Excel file."""
    try:
        excel_bytes = excel_generator.generate_excel_file(
            transactions=req.transactions,
            column_mapping=req.column_mapping,
            column_sequence=req.column_sequence
        )
        return StreamingResponse(
            io.BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=converted_transactions.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Excel: {str(e)}")

@app.post("/api/export-iif")
async def export_iif(req: IIFExportRequest):
    """Generates and streams an IIF file for QuickBooks Desktop."""
    try:
        iif_content = erp_connectors.generate_qbd_iif(
            transactions=req.transactions,
            bank_account_name=req.bank_account_name,
            offset_account_name=req.offset_account_name
        )
        return StreamingResponse(
            io.BytesIO(iif_content.encode("utf-8")),
            media_type="text/plain",
            headers={"Content-Disposition": "attachment; filename=transactions.iif"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate IIF: {str(e)}")

@app.post("/api/sync-erp")
async def sync_erp(req: ERPSyncRequest):
    """Syncs transaction records directly to NetSuite, QBO, Xero, or Zoho Books."""
    try:
        connector = erp_connectors.ERPConnector(req.system_name)
        result = connector.sync(req.transactions, req.target_accounts)
        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Sync failed: {str(e)}"}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
