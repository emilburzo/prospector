from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class JobStage(str, enum.Enum):
    NOT_STARTED = "not_started"
    APPLIED = "applied"
    IN_PROGRESS = "in_progress"
    OFFER = "offer"
    REJECTED = "rejected"
    NO_ANSWER = "no_answer"


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    file_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False, index=True)
    role_name = Column(String, nullable=False)
    stage = Column(SQLEnum(JobStage), nullable=False, default=JobStage.NOT_STARTED)
    stage_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    job_ad_content = Column(Text, nullable=True)
    cover_letter = Column(Text, nullable=True)
    application_notes = Column(Text, nullable=True)  # Other inputs when applying
    notes = Column(Text, nullable=True)
    match_percentage = Column(Float, nullable=True)
    match_reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    stage_history = relationship("StageHistory", back_populates="job_application", cascade="all, delete-orphan")


class StageHistory(Base):
    __tablename__ = "stage_history"

    id = Column(Integer, primary_key=True, index=True)
    job_application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=False)
    previous_stage = Column(SQLEnum(JobStage), nullable=True)
    new_stage = Column(SQLEnum(JobStage), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    job_application = relationship("JobApplication", back_populates="stage_history")


class JobLead(Base):
    __tablename__ = "job_leads"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False, index=True)
    role_name = Column(String, nullable=False)
    job_ad_content = Column(Text, nullable=False)
    job_url = Column(String, nullable=True)
    match_percentage = Column(Float, nullable=True)
    match_reasoning = Column(Text, nullable=True)
    is_promoted = Column(Boolean, default=False)
    promoted_to_application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
