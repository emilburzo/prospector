from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import JobLead, JobApplication, Resume
from app.schemas import (
    JobLeadCreate,
    JobLeadResponse,
    JobLeadPromoteRequest,
    JobApplicationResponse,
)
from app.services import OpenRouterService

router = APIRouter(prefix="/leads", tags=["Job Leads"])


@router.post("/", response_model=JobLeadResponse, status_code=status.HTTP_201_CREATED)
async def create_job_lead(
    lead: JobLeadCreate,
    rank_immediately: bool = True,
    db: Session = Depends(get_db)
):
    """Create a new job lead and optionally rank it immediately"""
    db_lead = JobLead(**lead.model_dump())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    
    # Rank immediately if requested and there's an active resume
    if rank_immediately:
        resume = db.query(Resume).filter(Resume.is_active == 1).first()
        if resume:
            try:
                ai_service = OpenRouterService()
                match_result = await ai_service.calculate_job_match(
                    db_lead.job_posting,
                    resume.content
                )
                db_lead.match_percentage = match_result["match_percentage"]
                db_lead.match_reasoning = match_result["reasoning"]
                db.commit()
                db.refresh(db_lead)
            except Exception as e:
                # Don't fail the creation if ranking fails
                print(f"Failed to rank job lead: {e}")
    
    return db_lead


@router.get("/", response_model=List[JobLeadResponse])
async def list_job_leads(
    skip: int = 0,
    limit: int = 100,
    sort_by_match: bool = True,
    db: Session = Depends(get_db)
):
    """List all job leads, optionally sorted by match percentage"""
    query = db.query(JobLead)
    if sort_by_match:
        query = query.order_by(JobLead.match_percentage.desc().nullslast())
    else:
        query = query.order_by(JobLead.created_at.desc())
    leads = query.offset(skip).limit(limit).all()
    return leads


@router.get("/{lead_id}", response_model=JobLeadResponse)
async def get_job_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific job lead by ID"""
    lead = db.query(JobLead).filter(JobLead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Job lead not found")
    return lead


@router.post("/{lead_id}/rank", response_model=JobLeadResponse)
async def rank_job_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Rank a job lead using AI"""
    lead = db.query(JobLead).filter(JobLead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Job lead not found")
    
    resume = db.query(Resume).filter(Resume.is_active == 1).first()
    if not resume:
        raise HTTPException(status_code=400, detail="No active resume found. Please upload a resume first.")
    
    ai_service = OpenRouterService()
    try:
        match_result = await ai_service.calculate_job_match(
            lead.job_posting,
            resume.content
        )
        lead.match_percentage = match_result["match_percentage"]
        lead.match_reasoning = match_result["reasoning"]
        db.commit()
        db.refresh(lead)
    except Exception as e:
        # Log the actual error for debugging but don't expose to user
        import logging
        logging.error(f"Failed to rank job lead {lead_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to rank job lead. Please try again later.")
    
    return lead


@router.post("/rank-batch")
async def rank_job_leads_batch(
    lead_ids: List[int],
    db: Session = Depends(get_db)
):
    """Rank multiple job leads using AI"""
    resume = db.query(Resume).filter(Resume.is_active == 1).first()
    if not resume:
        raise HTTPException(status_code=400, detail="No active resume found. Please upload a resume first.")
    
    ai_service = OpenRouterService()
    results = []
    
    for lead_id in lead_ids:
        lead = db.query(JobLead).filter(JobLead.id == lead_id).first()
        if not lead:
            results.append({"lead_id": lead_id, "status": "not_found"})
            continue
        
        try:
            match_result = await ai_service.calculate_job_match(
                lead.job_posting,
                resume.content
            )
            lead.match_percentage = match_result["match_percentage"]
            lead.match_reasoning = match_result["reasoning"]
            db.commit()
            results.append({
                "lead_id": lead_id,
                "status": "success",
                "match_percentage": match_result["match_percentage"]
            })
        except Exception as e:
            # Log the actual error for debugging but don't expose to user
            import logging
            logging.error(f"Failed to rank job lead {lead_id}: {str(e)}")
            results.append({
                "lead_id": lead_id,
                "status": "error",
                "error": "Failed to rank this lead"
            })
    
    return {"results": results}


@router.post("/{lead_id}/promote", response_model=JobApplicationResponse)
async def promote_job_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Promote a job lead to a job application"""
    lead = db.query(JobLead).filter(JobLead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Job lead not found")
    
    # Use AI to extract fields
    ai_service = OpenRouterService()
    try:
        extracted = await ai_service.extract_job_fields(lead.job_posting)
    except Exception as e:
        # Fallback to basic extraction if AI fails
        extracted = {
            "company_name": lead.company_name,
            "role_name": lead.role_name,
            "job_ad": lead.job_posting,
            "additional_info": {}
        }
    
    # Create job application
    db_application = JobApplication(
        company_name=extracted.get("company_name", lead.company_name),
        role_name=extracted.get("role_name", lead.role_name),
        job_ad=extracted.get("job_ad", lead.job_posting),
        additional_info=extracted.get("additional_info", {}),
        stage="not_started",
        stage_date=datetime.utcnow(),
        job_match_percentage=lead.match_percentage,
        history=[],
        notes=f"Promoted from job lead #{lead.id}\nMatch reasoning: {lead.match_reasoning}"
    )
    
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    
    return db_application


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Delete a job lead"""
    lead = db.query(JobLead).filter(JobLead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Job lead not found")
    
    db.delete(lead)
    db.commit()
    return None
