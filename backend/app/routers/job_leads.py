from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app import models, schemas
from app.services.openrouter import OpenRouterService

router = APIRouter(prefix="/api/leads", tags=["leads"])


@router.post("/", response_model=schemas.JobLead)
def create_lead(lead: schemas.JobLeadCreate, db: Session = Depends(get_db)):
    """Create a new job lead"""
    db_lead = models.JobLead(**lead.model_dump())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead


@router.get("/", response_model=List[schemas.JobLead])
def list_leads(
    skip: int = 0,
    limit: int = 100,
    sort_by_match: bool = Query(False, description="Sort by match percentage descending"),
    company: Optional[str] = Query(None),
    promoted: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """List all job leads with optional filters and sorting"""
    query = db.query(models.JobLead)

    if company:
        query = query.filter(models.JobLead.company_name.ilike(f"%{company}%"))
    if promoted is not None:
        query = query.filter(models.JobLead.is_promoted == promoted)

    if sort_by_match:
        # Sort by match_percentage descending, nulls last
        query = query.order_by(models.JobLead.match_percentage.desc().nullslast())
    else:
        query = query.order_by(models.JobLead.created_at.desc())

    leads = query.offset(skip).limit(limit).all()
    return leads


@router.get("/{lead_id}", response_model=schemas.JobLead)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    """Get a specific job lead"""
    lead = db.query(models.JobLead).filter(models.JobLead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Job lead not found")
    return lead


@router.put("/{lead_id}", response_model=schemas.JobLead)
def update_lead(lead_id: int, lead: schemas.JobLeadUpdate, db: Session = Depends(get_db)):
    """Update a job lead"""
    db_lead = db.query(models.JobLead).filter(models.JobLead.id == lead_id).first()
    if not db_lead:
        raise HTTPException(status_code=404, detail="Job lead not found")

    update_data = lead.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_lead, field, value)

    db.commit()
    db.refresh(db_lead)
    return db_lead


@router.delete("/{lead_id}")
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    """Delete a job lead"""
    db_lead = db.query(models.JobLead).filter(models.JobLead.id == lead_id).first()
    if not db_lead:
        raise HTTPException(status_code=404, detail="Job lead not found")

    db.delete(db_lead)
    db.commit()
    return {"message": "Job lead deleted successfully"}


@router.post("/{lead_id}/analyze", response_model=schemas.JobMatchResponse)
async def analyze_lead(
    lead_id: int,
    resume_id: Optional[int] = Query(None, description="Resume ID to use, or active resume if not specified"),
    db: Session = Depends(get_db)
):
    """Analyze how well a job lead matches a resume using AI"""
    # Get the job lead
    lead = db.query(models.JobLead).filter(models.JobLead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Job lead not found")

    # Get the resume
    if resume_id:
        resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
    else:
        resume = db.query(models.Resume).filter(models.Resume.is_active == True).first()
        if not resume:
            raise HTTPException(status_code=404, detail="No active resume found")

    # Analyze the match using OpenRouter
    openrouter = OpenRouterService()
    try:
        result = await openrouter.analyze_job_match(lead.job_ad_content, resume.content)

        # Update the lead with the analysis
        lead.match_percentage = result["match_percentage"]
        lead.match_reasoning = result["reasoning"]
        db.commit()

        return schemas.JobMatchResponse(
            match_percentage=result["match_percentage"],
            reasoning=result["reasoning"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing job match: {str(e)}")


@router.post("/{lead_id}/promote", response_model=schemas.PromoteLeadResponse)
async def promote_lead(lead_id: int, db: Session = Depends(get_db)):
    """Promote a job lead to a job application using AI to extract fields"""
    # Get the job lead
    lead = db.query(models.JobLead).filter(models.JobLead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Job lead not found")

    # Extract fields using OpenRouter
    openrouter = OpenRouterService()
    try:
        extracted = await openrouter.extract_job_application_fields(lead.job_ad_content)

        # Handle extracted_content - convert to string if it's a dict
        extracted_content = extracted.get("extracted_content", lead.job_ad_content)
        if isinstance(extracted_content, dict):
            import json
            extracted_content = json.dumps(extracted_content, indent=2)

        # Create the job application
        # Use extracted company name only if it's valid (not "Unknown" or empty)
        extracted_company = extracted.get("company_name", "")
        # Determine company_name with clear logic
        if lead.company_name:
            if not extracted_company or extracted_company == "Unknown":
                company_name = lead.company_name
            else:
                company_name = extracted_company
        elif extracted_company and extracted_company != "Unknown":
            company_name = extracted_company
        else:
            company_name = "Unknown"

        # Use extracted role name only if it's valid
        extracted_role = extracted.get("role_name", "")
        role_name = lead.role_name if lead.role_name and (not extracted_role or extracted_role == "Unknown") else extracted_role or "Unknown"

        application_data = {
            "company_name": company_name,
            "role_name": role_name,
            "stage": models.JobStage.NOT_STARTED,
            "job_ad_content": lead.job_ad_content,
            "match_percentage": lead.match_percentage,
            "match_reasoning": lead.match_reasoning,
        }

        db_application = models.JobApplication(**application_data)
        db.add(db_application)
        db.commit()
        db.refresh(db_application)

        # Create initial stage history
        history_entry = models.StageHistory(
            job_application_id=db_application.id,
            previous_stage=None,
            new_stage=models.JobStage.NOT_STARTED,
            changed_at=datetime.utcnow()
        )
        db.add(history_entry)
        db.commit()

        # Delete the lead after successful promotion
        db.delete(lead)
        db.commit()

        db.refresh(db_application)

        return schemas.PromoteLeadResponse(
            job_application=db_application,
            message="Job lead successfully promoted to application"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error promoting lead: {str(e)}")
