"""
Test configuration and fixtures
"""
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from faker import Faker

# Set test database URL before importing anything that uses it
# Note: This needs to be set early to avoid database connection errors
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("OPENROUTER_API_KEY", "test-key")

# Clear the settings cache to ensure test environment is used
from app.config import get_settings
get_settings.cache_clear()

from app.database import Base, get_db
from app import models

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

fake = Faker()


@pytest.fixture(scope="function")
def db_engine():
    """Create a test database engine"""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a test database session"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session override"""
    # Import app here to avoid database connection on module import
    from app.main import app

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_resume(db_session):
    """Create a sample resume for testing"""
    resume = models.Resume(
        content="Experienced software engineer with 5+ years in Python and FastAPI.",
        file_name="resume.txt",
        is_active=True
    )
    db_session.add(resume)
    db_session.commit()
    db_session.refresh(resume)
    return resume


@pytest.fixture
def sample_job_application(db_session):
    """Create a sample job application for testing"""
    application = models.JobApplication(
        company_name="Tech Corp",
        role_name="Senior Software Engineer",
        stage=models.JobStage.APPLIED,
        job_ad_content="Looking for a senior engineer with Python experience.",
        match_percentage=85.5,
        match_reasoning="Strong match based on experience."
    )
    db_session.add(application)
    db_session.commit()
    db_session.refresh(application)
    return application


@pytest.fixture
def sample_job_lead(db_session):
    """Create a sample job lead for testing"""
    lead = models.JobLead(
        company_name="StartUp Inc",
        role_name="Backend Developer",
        job_ad_content="Seeking a backend developer with Python skills.",
        is_promoted=False
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    return lead


@pytest.fixture
def multiple_resumes(db_session):
    """Create multiple resumes for testing"""
    resumes = [
        models.Resume(content=f"Resume content {i}", file_name=f"resume_{i}.txt", is_active=i == 0)
        for i in range(3)
    ]
    for resume in resumes:
        db_session.add(resume)
    db_session.commit()
    for resume in resumes:
        db_session.refresh(resume)
    return resumes


@pytest.fixture
def multiple_job_applications(db_session):
    """Create multiple job applications for testing"""
    applications = [
        models.JobApplication(
            company_name=f"Company {i}",
            role_name=f"Role {i}",
            stage=models.JobStage.APPLIED if i % 2 == 0 else models.JobStage.IN_PROGRESS,
            job_ad_content=f"Job ad content {i}",
            match_percentage=80.0 + i
        )
        for i in range(5)
    ]
    for app in applications:
        db_session.add(app)
    db_session.commit()
    for app in applications:
        db_session.refresh(app)
    return applications
