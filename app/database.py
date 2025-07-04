import duckdb
from pathlib import Path
from typing import Optional

class Database:
    def __init__(self, db_path: str = "db/purchase_tracker.db"):
        self.db_path = Path(db_path)
        self.connection: Optional[duckdb.DuckDBPyConnection] = None
        
    def connect(self) -> duckdb.DuckDBPyConnection:
        if self.connection is None:
            self.connection = duckdb.connect(str(self.db_path))
        return self.connection
    
    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute(self, query: str, parameters=None):
        conn = self.connect()
        if parameters:
            return conn.execute(query, parameters)
        return conn.execute(query)
    
    def fetchall(self, query: str, parameters=None):
        return self.execute(query, parameters).fetchall()
    
    def fetchone(self, query: str, parameters=None):
        return self.execute(query, parameters).fetchone()

db = Database()