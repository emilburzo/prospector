from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/resumes", tags=["resumes"])


@router.post("/", response_model=schemas.Resume)
def create_resume(resume: schemas.ResumeCreate, db: Session = Depends(get_db)):
    """Create a new resume"""
    # Set all other resumes to inactive
    db.query(models.Resume).update({"is_active": 0})

    db_resume = models.Resume(**resume.model_dump(), is_active=1)
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume


@router.get("/", response_model=List[schemas.Resume])
def list_resumes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all resumes"""
    resumes = db.query(models.Resume).offset(skip).limit(limit).all()
    return resumes


@router.get("/active", response_model=schemas.Resume)
def get_active_resume(db: Session = Depends(get_db)):
    """Get the currently active resume"""
    resume = db.query(models.Resume).filter(models.Resume.is_active == 1).first()
    if not resume:
        raise HTTPException(status_code=404, detail="No active resume found")
    return resume


@router.get("/{resume_id}", response_model=schemas.Resume)
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    """Get a specific resume"""
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.put("/{resume_id}", response_model=schemas.Resume)
def update_resume(resume_id: int, resume: schemas.ResumeUpdate, db: Session = Depends(get_db)):
    """Update a resume"""
    db_resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    if not db_resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    update_data = resume.model_dump(exclude_unset=True)

    # If setting this resume as active, deactivate all others
    if update_data.get("is_active") is True:
        db.query(models.Resume).update({"is_active": 0})

    for field, value in update_data.items():
        setattr(db_resume, field, value)

    db.commit()
    db.refresh(db_resume)
    return db_resume


@router.delete("/{resume_id}")
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    """Delete a resume"""
    db_resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    if not db_resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    db.delete(db_resume)
    db.commit()
    return {"message": "Resume deleted successfully"}
