from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models import JobStage


# Resume Schemas
class ResumeBase(BaseModel):
    content: str
    file_name: Optional[str] = None


class ResumeCreate(ResumeBase):
    pass


class ResumeUpdate(BaseModel):
    content: Optional[str] = None
    file_name: Optional[str] = None
    is_active: Optional[bool] = None


class Resume(ResumeBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Stage History Schemas
class StageHistoryBase(BaseModel):
    previous_stage: Optional[JobStage] = None
    new_stage: JobStage
    changed_at: datetime


class StageHistory(StageHistoryBase):
    id: int
    job_application_id: int

    class Config:
        from_attributes = True


# Job Application Schemas
class JobApplicationBase(BaseModel):
    company_name: str
    role_name: str
    stage: JobStage = JobStage.NOT_STARTED
    job_ad_content: Optional[str] = None
    cover_letter: Optional[str] = None
    application_notes: Optional[str] = None
    notes: Optional[str] = None
    match_percentage: Optional[float] = None
    match_reasoning: Optional[str] = None


class JobApplicationCreate(JobApplicationBase):
    pass


class JobApplicationUpdate(BaseModel):
    company_name: Optional[str] = None
    role_name: Optional[str] = None
    stage: Optional[JobStage] = None
    job_ad_content: Optional[str] = None
    cover_letter: Optional[str] = None
    application_notes: Optional[str] = None
    notes: Optional[str] = None
    match_percentage: Optional[float] = None
    match_reasoning: Optional[str] = None


class JobApplication(JobApplicationBase):
    id: int
    stage_date: datetime
    created_at: datetime
    updated_at: datetime
    stage_history: List[StageHistory] = []

    class Config:
        from_attributes = True


# Job Lead Schemas
class JobLeadBase(BaseModel):
    company_name: Optional[str] = None
    role_name: Optional[str] = None
    job_ad_content: str
    job_url: Optional[str] = None


class JobLeadCreate(JobLeadBase):
    pass


class JobLeadUpdate(BaseModel):
    company_name: Optional[str] = None
    role_name: Optional[str] = None
    job_ad_content: Optional[str] = None
    job_url: Optional[str] = None
    match_percentage: Optional[float] = None
    match_reasoning: Optional[str] = None


class JobLead(JobLeadBase):
    id: int
    match_percentage: Optional[float] = None
    match_reasoning: Optional[str] = None
    is_promoted: bool
    promoted_to_application_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# AI Analysis Schemas
class JobMatchRequest(BaseModel):
    job_lead_id: int
    resume_id: Optional[int] = None


class JobMatchResponse(BaseModel):
    match_percentage: float
    reasoning: str


class PromoteLeadRequest(BaseModel):
    job_lead_id: int


class PromoteLeadResponse(BaseModel):
    job_application: JobApplication
    message: str
