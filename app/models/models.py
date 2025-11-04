from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.sql import func
from app.database import Base


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False, index=True)
    role_name = Column(String, nullable=False)
    stage = Column(String, nullable=False, default="not_started")  # not_started, applied, in_progress, offer, rejected, no_answer
    stage_date = Column(DateTime(timezone=True), server_default=func.now())
    job_ad = Column(Text)
    cover_letter = Column(Text)
    additional_info = Column(JSON)  # For storing any other input fields
    notes = Column(Text)
    job_match_percentage = Column(Float)
    history = Column(JSON, default=list)  # List of {date, before_stage, after_stage}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class JobLead(Base):
    __tablename__ = "job_leads"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False, index=True)
    role_name = Column(String, nullable=False)
    job_posting = Column(Text, nullable=False)
    match_percentage = Column(Float, index=True)
    match_reasoning = Column(Text)
    source = Column(String)  # Where the job was found
    url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    filename = Column(String)
    is_active = Column(Integer, default=1)  # Only one active resume at a time
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
