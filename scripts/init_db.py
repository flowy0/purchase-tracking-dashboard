#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database import db
from app.models.purchase import PurchaseSchema

def init_database():
    """Initialize the DuckDB database with the purchases table."""
    try:
        print("Initializing DuckDB database...")
        
        conn = db.connect()
        conn.execute(PurchaseSchema.CREATE_TABLE)
        
        print(f"Database initialized successfully at {db.db_path}")
        print("Purchases table created.")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    init_database()