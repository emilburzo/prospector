from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.post("/", response_model=schemas.JobApplication)
def create_application(application: schemas.JobApplicationCreate, db: Session = Depends(get_db)):
    """Create a new job application"""
    db_application = models.JobApplication(**application.model_dump())
    db.add(db_application)
    db.commit()
    db.refresh(db_application)

    # Create initial stage history entry
    history_entry = models.StageHistory(
        job_application_id=db_application.id,
        previous_stage=None,
        new_stage=db_application.stage,
        changed_at=db_application.created_at
    )
    db.add(history_entry)
    db.commit()
    db.refresh(db_application)

    return db_application


@router.get("/", response_model=List[schemas.JobApplication])
def list_applications(
    skip: int = 0,
    limit: int = 100,
    stage: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all job applications with optional filters"""
    query = db.query(models.JobApplication)

    if stage:
        query = query.filter(models.JobApplication.stage == stage)
    if company:
        query = query.filter(models.JobApplication.company_name.ilike(f"%{company}%"))

    applications = query.offset(skip).limit(limit).all()
    return applications


@router.get("/{application_id}", response_model=schemas.JobApplication)
def get_application(application_id: int, db: Session = Depends(get_db)):
    """Get a specific job application"""
    application = db.query(models.JobApplication).filter(
        models.JobApplication.id == application_id
    ).first()
    if not application:
        raise HTTPException(status_code=404, detail="Job application not found")
    return application


@router.put("/{application_id}", response_model=schemas.JobApplication)
def update_application(
    application_id: int,
    application: schemas.JobApplicationUpdate,
    db: Session = Depends(get_db)
):
    """Update a job application"""
    db_application = db.query(models.JobApplication).filter(
        models.JobApplication.id == application_id
    ).first()
    if not db_application:
        raise HTTPException(status_code=404, detail="Job application not found")

    update_data = application.model_dump(exclude_unset=True)
    old_stage = db_application.stage

    for field, value in update_data.items():
        setattr(db_application, field, value)

    # If stage changed, update stage_date and create history entry
    if "stage" in update_data and update_data["stage"] != old_stage:
        db_application.stage_date = datetime.utcnow()
        history_entry = models.StageHistory(
            job_application_id=application_id,
            previous_stage=old_stage,
            new_stage=update_data["stage"],
            changed_at=datetime.utcnow()
        )
        db.add(history_entry)

    db.commit()
    db.refresh(db_application)
    return db_application


@router.delete("/{application_id}")
def delete_application(application_id: int, db: Session = Depends(get_db)):
    """Delete a job application"""
    db_application = db.query(models.JobApplication).filter(
        models.JobApplication.id == application_id
    ).first()
    if not db_application:
        raise HTTPException(status_code=404, detail="Job application not found")

    db.delete(db_application)
    db.commit()
    return {"message": "Job application deleted successfully"}


@router.get("/{application_id}/history", response_model=List[schemas.StageHistory])
def get_application_history(application_id: int, db: Session = Depends(get_db)):
    """Get stage change history for a job application"""
    application = db.query(models.JobApplication).filter(
        models.JobApplication.id == application_id
    ).first()
    if not application:
        raise HTTPException(status_code=404, detail="Job application not found")

    return application.stage_history
