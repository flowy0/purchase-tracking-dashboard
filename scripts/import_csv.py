#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.services.data_import import DataImporter
from app.database import db

def main():
    if len(sys.argv) != 2:
        print("Usage: python import_csv.py <csv_file_path>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    if not Path(csv_path).exists():
        print(f"Error: File {csv_path} does not exist")
        sys.exit(1)
    
    try:
        importer = DataImporter()
        count = importer.import_csv(csv_path)
        print(f"Import completed. {count} records imported successfully.")
        
    except Exception as e:
        print(f"Import failed: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()