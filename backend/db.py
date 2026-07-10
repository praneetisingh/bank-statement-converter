import sqlite3
import os
import json

DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "statements.db"))

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize SQLite database schemas."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Table for storing mapping configurations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mapping_configurations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            bank_name TEXT,
            account_number_suffix TEXT NOT NULL,
            column_mapping TEXT NOT NULL,       -- JSON string of mapping rules
            column_sequence TEXT NOT NULL,      -- JSON array of column order
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(client_name, bank_name, account_number_suffix)
        )
    """)
    
    # Table for storing ERP credentials
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS erp_credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            system_name TEXT UNIQUE NOT NULL,    -- 'netsuite', 'qbo', 'xero', 'zoho'
            credentials_json TEXT NOT NULL,       -- JSON config/tokens
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def save_mapping_config(client_name, bank_name, account_number_suffix, column_mapping, column_sequence):
    """Saves or updates a mapping configuration."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    mapping_str = json.dumps(column_mapping)
    sequence_str = json.dumps(column_sequence)
    
    try:
        cursor.execute("""
            INSERT INTO mapping_configurations (client_name, bank_name, account_number_suffix, column_mapping, column_sequence, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(client_name, bank_name, account_number_suffix) DO UPDATE SET
                column_mapping = excluded.column_mapping,
                column_sequence = excluded.column_sequence,
                updated_at = CURRENT_TIMESTAMP
        """, (client_name, bank_name, account_number_suffix, mapping_str, sequence_str))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving mapping config: {e}")
        return False
    finally:
        conn.close()

def get_mapping_config(client_name, bank_name, account_number_suffix):
    """Retrieves mapping config. Fallback checks are applied if certain fields are missing."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Exact match first
    cursor.execute("""
        SELECT * FROM mapping_configurations 
        WHERE client_name = ? AND bank_name = ? AND account_number_suffix = ?
    """, (client_name, bank_name, account_number_suffix))
    row = cursor.fetchone()
    
    # Fallback 1: Match by bank + account suffix (accounts can be shared across client profiles)
    if not row:
        cursor.execute("""
            SELECT * FROM mapping_configurations 
            WHERE bank_name = ? AND account_number_suffix = ?
        """, (bank_name, account_number_suffix))
        row = cursor.fetchone()
        
    # Fallback 2: Match by account suffix only
    if not row:
        cursor.execute("""
            SELECT * FROM mapping_configurations 
            WHERE account_number_suffix = ?
        """, (account_number_suffix,))
        row = cursor.fetchone()

    conn.close()
    
    if row:
        return {
            "id": row["id"],
            "client_name": row["client_name"],
            "bank_name": row["bank_name"],
            "account_number_suffix": row["account_number_suffix"],
            "column_mapping": json.loads(row["column_mapping"]),
            "column_sequence": json.loads(row["column_sequence"])
        }
    return None

def save_erp_credentials(system_name, credentials):
    """Saves or updates credentials for an ERP system."""
    conn = get_db_connection()
    cursor = conn.cursor()
    credentials_str = json.dumps(credentials)
    
    try:
        cursor.execute("""
            INSERT INTO erp_credentials (system_name, credentials_json, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(system_name) DO UPDATE SET
                credentials_json = excluded.credentials_json,
                updated_at = CURRENT_TIMESTAMP
        """, (system_name, credentials_str))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving ERP credentials: {e}")
        return False
    finally:
        conn.close()

def get_erp_credentials(system_name):
    """Gets credentials for an ERP system."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT credentials_json FROM erp_credentials WHERE system_name = ?", (system_name,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return json.loads(row["credentials_json"])
    return None

# Initialize on import
init_db()
