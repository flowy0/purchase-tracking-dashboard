import polars as pl
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from app.database import db
from app.models.purchase import Purchase, PurchaseSchema

class DataImporter:
    # Current CNY to SGD exchange rate (as of 2025)
    CNY_TO_SGD_RATE = Decimal('0.1962')  # 1 CNY = 0.1962 SGD
    
    def __init__(self):
        self.db = db
    
    def import_csv(self, csv_path: str) -> int:
        """Import purchases from CSV file using Polars."""
        try:
            print(f"Reading CSV file: {csv_path}")
            
            # Read CSV with Polars
            df = pl.read_csv(
                csv_path,
                separator="|",
                has_header=True,
                infer_schema_length=1000
            )
            
            print(f"Loaded {len(df)} rows from CSV")
            
            # Clean and transform data
            df_cleaned = self._clean_data(df)
            
            # Import to database
            imported_count = self._import_to_database(df_cleaned)
            
            print(f"Successfully imported {imported_count} purchases")
            return imported_count
            
        except Exception as e:
            print(f"Error importing CSV: {e}")
            raise
    
    def _clean_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """Clean and transform the CSV data."""
        # The CSV has a malformed structure - let's parse it manually
        cleaned_rows = []
        
        # Get the raw data as strings
        for row in df.iter_rows():
            try:
                # Skip empty rows
                if not row or all(str(cell).strip() == '' for cell in row):
                    continue
                
                # Convert row to string and split by |
                row_str = '|'.join(str(cell) for cell in row)
                
                # Skip header row
                if 'SN|date|tracking_number' in row_str:
                    continue
                
                # Split by pipe and parse manually
                parts = row_str.split('|')
                
                if len(parts) >= 5:
                    # Parse the specific format from the CSV
                    sn_str = parts[0]
                    if not sn_str.isdigit():
                        continue
                    
                    sn = int(sn_str)
                    
                    # Extract item name and other details from the concatenated string
                    # Format: SN|ItemName,Date,Quantity,PriceInfo|OrderID
                    remaining = '|'.join(parts[1:])
                    
                    # Find the order ID at the end
                    order_id_match = remaining.split('|')[-1]
                    if order_id_match.isdigit():
                        order_id = order_id_match
                        data_part = remaining.rsplit('|', 1)[0]
                    else:
                        order_id = ""
                        data_part = remaining
                    
                    # Parse the data part: ItemName,Date,Quantity,PriceInfo
                    # Split by comma from the right to get reliable parts
                    data_parts = data_part.split(',')
                    
                    if len(data_parts) >= 4:
                        item_name = ','.join(data_parts[:-3])  # Everything except last 3 parts
                        date_str = data_parts[-3]
                        quantity = int(data_parts[-2]) if data_parts[-2].isdigit() else 1
                        price_str = data_parts[-1]
                        
                        price = self._parse_price(price_str)
                        price_sgd = price * self.CNY_TO_SGD_RATE
                        date = self._parse_date(date_str)
                        
                        cleaned_rows.append({
                            'sn': sn,
                            'date': date,
                            'tracking_number': '',
                            'company_name': '',
                            'item_name': item_name,
                            'quantity': quantity,
                            'item_price': price,
                            'item_price_sgd': price_sgd,
                            'cny_to_sgd_rate': self.CNY_TO_SGD_RATE,
                            'export_status': '',
                            'order_id': order_id
                        })
                    
            except Exception as e:
                print(f"Error parsing row {row}: {e}")
                continue
        
        return pl.DataFrame(cleaned_rows)
    
    def _parse_price(self, price_str: str) -> Decimal:
        """Parse price from various formats."""
        try:
            # Handle formats like "173.310.000.0014.31173.31"
            # Use the second "." as the end of the price
            price_str = str(price_str).strip()
            
            # Find the position of the second dot
            first_dot = price_str.find('.')
            if first_dot != -1:
                second_dot = price_str.find('.', first_dot + 1)
                if second_dot != -1:
                    # Extract from start to 2 characters after the second dot
                    price_part = price_str[:second_dot + 3]  # Include 2 decimal places
                    # Extract just the numeric part with one decimal
                    import re
                    match = re.match(r'^(\d+\.\d{2})', price_part)
                    if match:
                        return Decimal(match.group(1))
            
        except (ValueError, Exception):
            pass
        
        return Decimal('0.00')
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date from string."""
        try:
            # Try common date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    return datetime.strptime(str(date_str), fmt)
                except ValueError:
                    continue
        except Exception:
            pass
        
        # Return current date as fallback
        return datetime.now()
    
    def _import_to_database(self, df: pl.DataFrame) -> int:
        """Import cleaned data to DuckDB."""
        conn = self.db.connect()
        imported_count = 0
        
        for row in df.iter_rows(named=True):
            try:
                conn.execute(
                    PurchaseSchema.INSERT_PURCHASE,
                    [
                        row['sn'],
                        row['date'],
                        row['tracking_number'],
                        row['company_name'],
                        row['item_name'],
                        row['quantity'],
                        float(row['item_price']),
                        float(row['item_price_sgd']),
                        float(row['cny_to_sgd_rate']),
                        row['export_status'],
                        row['order_id']
                    ]
                )
                imported_count += 1
            except Exception as e:
                print(f"Error inserting row: {e}")
                continue
        
        return imported_count