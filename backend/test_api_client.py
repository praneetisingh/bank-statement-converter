import requests
import os
import json

API_BASE = "http://localhost:8000"

def test_upload():
    print("Testing POST /api/upload...")
    file_path = os.path.join(os.path.dirname(__file__), "..", "wells_fargo_statement.pdf")
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f, "application/pdf")}
        response = requests.post(f"{API_BASE}/api/upload", files=files)
    
    print(f"Status: {response.status_code}")
    assert response.status_code == 200, f"Upload failed: {response.text}"
    data = response.json()
    print("Upload response keys:", list(data.keys()))
    assert data["success"] is True
    assert data["bank_name"] == "Wells Fargo"
    assert data["account_number_suffix"] == "1015"
    assert len(data["transactions"]) > 0
    print("Upload test PASSED")
    return data

def test_save_config(upload_data):
    print("Testing POST /api/save-config...")
    payload = {
        "client_name": upload_data["client_name"],
        "bank_name": upload_data["bank_name"],
        "account_number_suffix": upload_data["account_number_suffix"],
        "column_mapping": {
            "date": "Tx Date",
            "description": "Payee",
            "debit": "Amount Out",
            "credit": "Amount In"
        },
        "column_sequence": ["Tx Date", "Payee", "Amount Out", "Amount In"]
    }
    response = requests.post(f"{API_BASE}/api/save-config", json=payload)
    print(f"Status: {response.status_code}")
    assert response.status_code == 200, f"Save config failed: {response.text}"
    data = response.json()
    assert data["success"] is True
    print("Save config test PASSED")

def test_export_excel(upload_data):
    print("Testing POST /api/export-excel...")
    payload = {
        "transactions": upload_data["transactions"],
        "column_mapping": {
            "date": "Tx Date",
            "description": "Payee",
            "debit": "Amount Out",
            "credit": "Amount In"
        },
        "column_sequence": ["Tx Date", "Payee", "Amount Out", "Amount In"]
    }
    response = requests.post(f"{API_BASE}/api/export-excel", json=payload)
    print(f"Status: {response.status_code}")
    assert response.status_code == 200, f"Export Excel failed: {response.text}"
    assert len(response.content) > 0
    print(f"Excel file size: {len(response.content)} bytes")
    print("Export Excel test PASSED")

def test_export_iif(upload_data):
    print("Testing POST /api/export-iif...")
    payload = {
        "transactions": upload_data["transactions"],
        "bank_account_name": "Chase Bank Clearing",
        "offset_account_name": "Suspense Account"
    }
    response = requests.post(f"{API_BASE}/api/export-iif", json=payload)
    print(f"Status: {response.status_code}")
    assert response.status_code == 200, f"Export IIF failed: {response.text}"
    assert len(response.content) > 0
    print(f"IIF file size: {len(response.content)} bytes")
    print("Export IIF test PASSED")

def test_sync_erp(upload_data):
    print("Testing POST /api/sync-erp...")
    payload = {
        "system_name": "qbo",
        "transactions": upload_data["transactions"],
        "target_accounts": {
            "bank_account": "1010 Cash in Bank",
            "suspense_account": "6000 Uncategorized Transactions"
        }
    }
    response = requests.post(f"{API_BASE}/api/sync-erp", json=payload)
    print(f"Status: {response.status_code}")
    assert response.status_code == 200, f"ERP Sync failed: {response.text}"
    data = response.json()
    assert data["success"] is True
    assert data["simulated"] is True
    print("ERP Sync test PASSED")

if __name__ == "__main__":
    try:
        data = test_upload()
        test_save_config(data)
        test_export_excel(data)
        test_export_iif(data)
        test_sync_erp(data)
        print("ALL API ENDPOINT TESTS PASSED SUCCESSFULLY!")
    except Exception as e:
        print(f"TEST FAILED: {e}")
