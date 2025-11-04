from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import job_applications, job_leads, resumes

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Prospector API",
    description="AI-powered job application management system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resumes.router)
app.include_router(job_applications.router)
app.include_router(job_leads.router)


@app.get("/")
def read_root():
    return {
        "message": "Prospector API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
