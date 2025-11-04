from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Resume
from app.schemas import ResumeCreate, ResumeResponse

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("/", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def create_resume(
    resume: ResumeCreate,
    set_active: bool = True,
    db: Session = Depends(get_db)
):
    """Create a new resume from text content"""
    # If setting as active, deactivate all other resumes
    if set_active:
        db.query(Resume).update({"is_active": 0})
    
    db_resume = Resume(
        content=resume.content,
        filename=resume.filename,
        is_active=1 if set_active else 0
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    set_active: bool = Form(True),
    db: Session = Depends(get_db)
):
    """Upload a resume file"""
    # Read file content
    content = await file.read()
    content_str = content.decode('utf-8')
    
    # If setting as active, deactivate all other resumes
    if set_active:
        db.query(Resume).update({"is_active": 0})
    
    db_resume = Resume(
        content=content_str,
        filename=file.filename,
        is_active=1 if set_active else 0
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume


@router.get("/", response_model=List[ResumeResponse])
async def list_resumes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all resumes"""
    resumes = db.query(Resume).offset(skip).limit(limit).all()
    return resumes


@router.get("/active", response_model=ResumeResponse)
async def get_active_resume(db: Session = Depends(get_db)):
    """Get the currently active resume"""
    resume = db.query(Resume).filter(Resume.is_active == 1).first()
    if not resume:
        raise HTTPException(status_code=404, detail="No active resume found")
    return resume


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific resume by ID"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.put("/{resume_id}/activate", response_model=ResumeResponse)
async def activate_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """Set a resume as the active one"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Deactivate all other resumes
    db.query(Resume).update({"is_active": 0})
    resume.is_active = 1
    db.commit()
    db.refresh(resume)
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """Delete a resume"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    db.delete(resume)
    db.commit()
    return None
