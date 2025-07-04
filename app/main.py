from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.purchases import router as purchases_router
from app.database import db

app = FastAPI(
    title="Purchase Tracker API",
    description="API for tracking and managing purchase data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(purchases_router, prefix="/api/purchases", tags=["purchases"])

@app.get("/")
async def root():
    return {"message": "Welcome to Purchase Tracker API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    from app.models.purchase import PurchaseSchema
    db.execute(PurchaseSchema.CREATE_TABLE)

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    db.close()