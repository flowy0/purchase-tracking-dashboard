from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, date
from app.database import db
from app.models.purchase import PurchaseSchema
from app.services.data_import import DataImporter

router = APIRouter()

@router.get("/")
async def get_purchases(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None
):
    """Get all purchases with optional search and pagination."""
    try:
        if search:
            query = f"SELECT * FROM purchases WHERE item_name ILIKE '%{search}%' ORDER BY date DESC LIMIT {limit} OFFSET {offset}"
        else:
            query = f"SELECT * FROM purchases ORDER BY date DESC LIMIT {limit} OFFSET {offset}"
        
        purchases = db.fetchall(query)
        return {"purchases": purchases, "count": len(purchases)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{purchase_id}")
async def get_purchase(purchase_id: int):
    """Get a specific purchase by ID."""
    try:
        purchase = db.fetchone(PurchaseSchema.SELECT_BY_ID, [purchase_id])
        if not purchase:
            raise HTTPException(status_code=404, detail="Purchase not found")
        return purchase
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/summary")
async def get_summary_stats():
    """Get summary statistics for all purchases."""
    try:
        stats = db.fetchone(PurchaseSchema.GET_SUMMARY_STATS)
        return stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import-csv")
async def import_csv_data(csv_path: str):
    """Import data from CSV file."""
    try:
        importer = DataImporter()
        count = importer.import_csv(csv_path)
        return {"message": f"Successfully imported {count} purchases", "count": count}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))