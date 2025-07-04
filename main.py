import sys
from pathlib import Path

def main():
    """Main entry point for the purchase tracker application."""
    
    if len(sys.argv) < 2:
        print("Purchase Tracker Application")
        print("Usage:")
        print("  python main.py init          - Initialize database")
        print("  python main.py import <csv>  - Import CSV data")
        print("  python main.py api           - Start API server")
        print("  python main.py dashboard     - Start dashboard")
        return
    
    command = sys.argv[1]
    
    if command == "init":
        from scripts.init_db import init_database
        init_database()
        
    elif command == "import":
        if len(sys.argv) < 3:
            print("Usage: python main.py import <csv_file>")
            return
        csv_file = sys.argv[2]
        from scripts.import_csv import main as import_main
        sys.argv = ["import_csv.py", csv_file]
        import_main()
        
    elif command == "api":
        import uvicorn
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
        
    elif command == "dashboard":
        import subprocess
        subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])
        
    else:
        print(f"Unknown command: {command}")
        print("Use 'python main.py' for help")


if __name__ == "__main__":
    main()
