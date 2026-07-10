import os
import unittest
import json
import openpyxl

import db
import excel_generator
import erp_connectors
import parser

class TestStatementConverter(unittest.TestCase):
    
    def setUp(self):
        # Ensure clean state for DB mapping
        self.client = "Test Corp LLC"
        self.bank = "Wells Fargo"
        self.suffix = "1234"
        
        self.transactions = [
            {"date": "2026-06-01", "description": "AWS Cloud Services Bill", "amount": 100.50, "type": "debit"},
            {"date": "2026-06-03", "description": "ACH DEPOSIT - STRIPE PAYMENTS", "amount": 500.00, "type": "credit"} 
        ]
        
        self.mapping = {
            "date": "Tx Date",
            "description": "Payee",
            "debit": "Amount Out",
            "credit": "Amount In"
        }
        
        self.sequence = ["Tx Date", "Payee", "Amount Out", "Amount In"]

    def test_database_mapping_persistence(self):
        """Test that mapping configurations are saved and loaded correctly from SQLite."""
        # Save config
        success = db.save_mapping_config(
            client_name=self.client,
            bank_name=self.bank,
            account_number_suffix=self.suffix,
            column_mapping=self.mapping,
            column_sequence=self.sequence
        )
        self.assertTrue(success)
        
        # Load config
        config = db.get_mapping_config(self.client, self.bank, self.suffix)
        self.assertIsNotNone(config)
        self.assertEqual(config["client_name"], self.client)
        self.assertEqual(config["column_mapping"]["date"], "Tx Date")
        self.assertEqual(config["column_sequence"], self.sequence)

    def test_excel_generator_structure(self):
        """Test that Excel generator outputs custom columns in the correct sequence."""
        excel_bytes = excel_generator.generate_excel_file(
            self.transactions, self.mapping, self.sequence
        )
        self.assertIsInstance(excel_bytes, bytes)
        
        # Read the generated Excel bytes using openpyxl
        import io
        wb = openpyxl.load_workbook(io.BytesIO(excel_bytes))
        ws = wb.active
        
        # Verify Headers sequence
        headers = [cell.value for cell in ws[1]]
        self.assertEqual(headers, self.sequence)
        
        # Verify Data rows count
        self.assertEqual(ws.max_row, 3) # 1 header row + 2 data rows
        
        # Verify values in row 2 (debit transaction)
        # Row 2 should represent AWS bill
        row2 = [cell.value for cell in ws[2]]
        self.assertEqual(row2[0], "2026-06-01")
        self.assertEqual(row2[1], "AWS Cloud Services Bill")
        self.assertEqual(row2[2], 100.50) # Debit
        self.assertIsNone(row2[3]) # Credit field should be empty (converted to empty/none)

    def test_quickbooks_iif_format(self):
        """Test that QBD IIF output formats double-entry ledger listings correctly."""
        iif_text = erp_connectors.generate_qbd_iif(
            self.transactions, "Chase Bank Clearing", "Suspense Account"
        )
        
        self.assertIn("!TRNS", iif_text)
        self.assertIn("!SPL", iif_text)
        self.assertIn("ENDTRNS", iif_text)
        
        # Check transaction 1: debit of 100.50
        # Bank clearance line should be credit (-100.50)
        # Expense offset line should be debit (100.50)
        self.assertIn("Chase Bank Clearing\t-100.50", iif_text)
        self.assertIn("Suspense Account\t100.50", iif_text)

    def test_gemini_parser_mock_fallback(self):
        """Test that statement parser falls back to mock logic if no API key is specified."""
        # Force running in mock state by requesting parsing (which detects key or falls back)
        data = parser.parse_statement_with_gemini("wells_fargo_statement.pdf", is_image=False)
        self.assertEqual(data["bank_name"], "Wells Fargo")
        self.assertEqual(data["account_number_suffix"], "4321")
        self.assertTrue(len(data["transactions"]) > 0)

if __name__ == "__main__":
    unittest.main()
