from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Job Application Schemas
class StageHistoryItem(BaseModel):
    date: datetime
    before_stage: str
    after_stage: str


class JobApplicationBase(BaseModel):
    company_name: str
    role_name: str
    stage: str = "not_started"
    job_ad: Optional[str] = None
    cover_letter: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    job_match_percentage: Optional[float] = None


class JobApplicationCreate(JobApplicationBase):
    pass


class JobApplicationUpdate(BaseModel):
    company_name: Optional[str] = None
    role_name: Optional[str] = None
    stage: Optional[str] = None
    job_ad: Optional[str] = None
    cover_letter: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    job_match_percentage: Optional[float] = None


class JobApplicationResponse(JobApplicationBase):
    id: int
    stage_date: datetime
    history: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Job Lead Schemas
class JobLeadBase(BaseModel):
    company_name: str
    role_name: str
    job_posting: str
    source: Optional[str] = None
    url: Optional[str] = None


class JobLeadCreate(JobLeadBase):
    pass


class JobLeadResponse(JobLeadBase):
    id: int
    match_percentage: Optional[float] = None
    match_reasoning: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobLeadRankRequest(BaseModel):
    job_lead_ids: List[int]


class JobLeadPromoteRequest(BaseModel):
    job_lead_id: int


# Resume Schemas
class ResumeCreate(BaseModel):
    content: str
    filename: Optional[str] = None


class ResumeResponse(BaseModel):
    id: int
    content: str
    filename: Optional[str] = None
    is_active: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# AI Response Schemas
class MatchResult(BaseModel):
    match_percentage: float
    reasoning: str


class ExtractedJobFields(BaseModel):
    company_name: str
    role_name: str
    job_ad: str
    additional_info: Optional[Dict[str, Any]] = None
