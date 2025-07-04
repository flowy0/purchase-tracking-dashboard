from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from decimal import Decimal

@dataclass
class Purchase:
    sn: int
    date: datetime
    tracking_number: str
    company_name: str
    item_name: str
    quantity: int
    item_price: Decimal
    item_price_sgd: Decimal
    export_status: str
    order_id: str
    id: Optional[int] = None

class PurchaseSchema:
    CREATE_TABLE = """
    CREATE SEQUENCE IF NOT EXISTS purchase_id_seq;
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY DEFAULT nextval('purchase_id_seq'),
        sn INTEGER NOT NULL,
        date DATE NOT NULL,
        tracking_number VARCHAR,
        company_name VARCHAR,
        item_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        item_price DECIMAL(10,2) NOT NULL,
        item_price_sgd DECIMAL(10,2) NOT NULL,
        cny_to_sgd_rate DECIMAL(10,4) DEFAULT 0.1962,
        export_status VARCHAR,
        order_id VARCHAR NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    INSERT_PURCHASE = """
    INSERT INTO purchases (sn, date, tracking_number, company_name, item_name, quantity, item_price, item_price_sgd, cny_to_sgd_rate, export_status, order_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    SELECT_ALL = "SELECT * FROM purchases ORDER BY date DESC"
    
    SELECT_BY_ID = "SELECT * FROM purchases WHERE id = ?"
    
    SELECT_BY_DATE_RANGE = """
    SELECT * FROM purchases 
    WHERE date >= ? AND date <= ?
    ORDER BY date DESC
    """
    
    SEARCH_BY_ITEM = """
    SELECT * FROM purchases 
    WHERE item_name ILIKE ?
    ORDER BY date DESC
    """
    
    GET_SUMMARY_STATS = """
    SELECT 
        COUNT(*) as total_purchases,
        SUM(item_price * quantity) as total_amount,
        AVG(item_price) as avg_price,
        MIN(date) as earliest_date,
        MAX(date) as latest_date
    FROM purchases
    """