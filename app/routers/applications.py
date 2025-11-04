from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import JobApplication
from app.schemas import (
    JobApplicationCreate,
    JobApplicationUpdate,
    JobApplicationResponse,
)

router = APIRouter(prefix="/applications", tags=["Job Applications"])


@router.post("/", response_model=JobApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_job_application(
    application: JobApplicationCreate,
    db: Session = Depends(get_db)
):
    """Create a new job application"""
    db_application = JobApplication(
        **application.model_dump(),
        history=[],
        stage_date=datetime.utcnow()
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


@router.get("/", response_model=List[JobApplicationResponse])
async def list_job_applications(
    skip: int = 0,
    limit: int = 100,
    stage: str = None,
    db: Session = Depends(get_db)
):
    """List all job applications with optional filtering by stage"""
    query = db.query(JobApplication)
    if stage:
        query = query.filter(JobApplication.stage == stage)
    applications = query.offset(skip).limit(limit).all()
    return applications


@router.get("/{application_id}", response_model=JobApplicationResponse)
async def get_job_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific job application by ID"""
    application = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Job application not found")
    return application


@router.put("/{application_id}", response_model=JobApplicationResponse)
async def update_job_application(
    application_id: int,
    application_update: JobApplicationUpdate,
    db: Session = Depends(get_db)
):
    """Update a job application"""
    db_application = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if not db_application:
        raise HTTPException(status_code=404, detail="Job application not found")
    
    update_data = application_update.model_dump(exclude_unset=True)
    
    # Track stage changes in history
    if "stage" in update_data and update_data["stage"] != db_application.stage:
        history = db_application.history or []
        history.append({
            "date": datetime.utcnow().isoformat(),
            "before_stage": db_application.stage,
            "after_stage": update_data["stage"]
        })
        update_data["history"] = history
        update_data["stage_date"] = datetime.utcnow()
    
    for key, value in update_data.items():
        setattr(db_application, key, value)
    
    db.commit()
    db.refresh(db_application)
    return db_application


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    """Delete a job application"""
    db_application = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if not db_application:
        raise HTTPException(status_code=404, detail="Job application not found")
    
    db.delete(db_application)
    db.commit()
    return None
