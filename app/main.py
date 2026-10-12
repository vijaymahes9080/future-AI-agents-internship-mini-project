import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db, SessionLocal
from app.crud import seed_sample_students_if_empty
from app.routers import students, stats, ai

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    init_db()
    # Seed initial fictional data if empty
    db = SessionLocal()
    try:
        seed_sample_students_if_empty(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="A complete, professional, fully functional Student Record Management System for EWB Edu Tech Pvt. Ltd.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware for development flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(students.router)
app.include_router(stats.router)
app.include_router(ai.router)

# Mount static directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", include_in_schema=False)
async def serve_dashboard():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Welcome to EWB Student Record Management System API", "docs": "/docs"}

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "database": "sqlite_connected"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please contact the administrator."}
    )
