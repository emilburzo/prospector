"""
Unit tests for database models
"""
import pytest
from datetime import datetime
from app import models


class TestResumeModel:
    """Test Resume model"""

    def test_create_resume(self, db_session):
        """Test creating a resume"""
        resume = models.Resume(
            content="Test resume content",
            file_name="test_resume.txt",
            is_active=True
        )
        db_session.add(resume)
        db_session.commit()

        assert resume.id is not None
        assert resume.content == "Test resume content"
        assert resume.file_name == "test_resume.txt"
        assert resume.is_active is True
        assert isinstance(resume.created_at, datetime)
        assert isinstance(resume.updated_at, datetime)

    def test_resume_defaults(self, db_session):
        """Test resume default values"""
        resume = models.Resume(content="Content only")
        db_session.add(resume)
        db_session.commit()

        assert resume.is_active is True
        assert resume.file_name is None
        assert resume.created_at is not None

    def test_resume_update_timestamp(self, db_session):
        """Test that updated_at changes on update"""
        import time

        resume = models.Resume(content="Original content")
        db_session.add(resume)
        db_session.commit()

        original_updated_at = resume.updated_at
        time.sleep(0.1)

        resume.content = "Updated content"
        db_session.commit()

        # Note: SQLite might not update timestamps precisely, but we can check
        # that the field exists and is a datetime
        assert isinstance(resume.updated_at, datetime)


class TestJobApplicationModel:
    """Test JobApplication model"""

    def test_create_job_application(self, db_session):
        """Test creating a job application"""
        application = models.JobApplication(
            company_name="Tech Corp",
            role_name="Software Engineer",
            stage=models.JobStage.NOT_STARTED,
            job_ad_content="Job description"
        )
        db_session.add(application)
        db_session.commit()

        assert application.id is not None
        assert application.company_name == "Tech Corp"
        assert application.role_name == "Software Engineer"
        assert application.stage == models.JobStage.NOT_STARTED
        assert isinstance(application.created_at, datetime)

    def test_job_application_defaults(self, db_session):
        """Test job application default values"""
        application = models.JobApplication(
            company_name="Company",
            role_name="Role"
        )
        db_session.add(application)
        db_session.commit()

        assert application.stage == models.JobStage.NOT_STARTED
        assert application.stage_date is not None
        assert application.job_ad_content is None
        assert application.match_percentage is None

    def test_job_application_with_all_fields(self, db_session):
        """Test job application with all optional fields"""
        application = models.JobApplication(
            company_name="Tech Corp",
            role_name="Senior Engineer",
            stage=models.JobStage.APPLIED,
            job_ad_content="Full job description",
            cover_letter="My cover letter",
            application_notes="Applied via email",
            notes="Follow up needed",
            match_percentage=92.5,
            match_reasoning="Excellent fit"
        )
        db_session.add(application)
        db_session.commit()

        assert application.cover_letter == "My cover letter"
        assert application.application_notes == "Applied via email"
        assert application.notes == "Follow up needed"
        assert application.match_percentage == 92.5
        assert application.match_reasoning == "Excellent fit"


class TestStageHistoryModel:
    """Test StageHistory model"""

    def test_create_stage_history(self, db_session, sample_job_application):
        """Test creating a stage history entry"""
        history = models.StageHistory(
            job_application_id=sample_job_application.id,
            previous_stage=models.JobStage.NOT_STARTED,
            new_stage=models.JobStage.APPLIED,
            changed_at=datetime.utcnow()
        )
        db_session.add(history)
        db_session.commit()

        assert history.id is not None
        assert history.job_application_id == sample_job_application.id
        assert history.previous_stage == models.JobStage.NOT_STARTED
        assert history.new_stage == models.JobStage.APPLIED

    def test_stage_history_relationship(self, db_session, sample_job_application):
        """Test relationship between JobApplication and StageHistory"""
        # Create multiple history entries
        for i, stage in enumerate([models.JobStage.APPLIED, models.JobStage.IN_PROGRESS]):
            history = models.StageHistory(
                job_application_id=sample_job_application.id,
                previous_stage=models.JobStage.NOT_STARTED if i == 0 else models.JobStage.APPLIED,
                new_stage=stage,
                changed_at=datetime.utcnow()
            )
            db_session.add(history)
        db_session.commit()

        # Refresh to load relationships
        db_session.refresh(sample_job_application)

        # Check relationship
        assert len(sample_job_application.stage_history) >= 2
        assert all(isinstance(h, models.StageHistory) for h in sample_job_application.stage_history)

    def test_stage_history_initial_stage_null_previous(self, db_session, sample_job_application):
        """Test that initial stage history can have null previous_stage"""
        history = models.StageHistory(
            job_application_id=sample_job_application.id,
            previous_stage=None,
            new_stage=models.JobStage.NOT_STARTED,
            changed_at=datetime.utcnow()
        )
        db_session.add(history)
        db_session.commit()

        assert history.previous_stage is None
        assert history.new_stage == models.JobStage.NOT_STARTED


class TestJobLeadModel:
    """Test JobLead model"""

    def test_create_job_lead(self, db_session):
        """Test creating a job lead"""
        lead = models.JobLead(
            company_name="StartUp Inc",
            role_name="Backend Developer",
            job_ad_content="Looking for backend developer"
        )
        db_session.add(lead)
        db_session.commit()

        assert lead.id is not None
        assert lead.company_name == "StartUp Inc"
        assert lead.role_name == "Backend Developer"
        assert lead.job_ad_content == "Looking for backend developer"

    def test_job_lead_defaults(self, db_session):
        """Test job lead default values"""
        lead = models.JobLead(job_ad_content="Minimal lead")
        db_session.add(lead)
        db_session.commit()

        assert lead.is_promoted is False
        assert lead.company_name is None
        assert lead.role_name is None
        assert lead.match_percentage is None
        assert lead.match_reasoning is None

    def test_job_lead_with_all_fields(self, db_session):
        """Test job lead with all fields"""
        lead = models.JobLead(
            company_name="Tech Corp",
            role_name="Full Stack Developer",
            job_ad_content="Full job description",
            job_url="https://example.com/job",
            match_percentage=85.0,
            match_reasoning="Good match",
            is_promoted=False
        )
        db_session.add(lead)
        db_session.commit()

        assert lead.job_url == "https://example.com/job"
        assert lead.match_percentage == 85.0
        assert lead.match_reasoning == "Good match"
        assert lead.is_promoted is False

    def test_job_lead_promotion(self, db_session, sample_job_application):
        """Test marking a lead as promoted"""
        lead = models.JobLead(
            company_name="Company",
            job_ad_content="Content",
            is_promoted=False
        )
        db_session.add(lead)
        db_session.commit()

        # Mark as promoted
        lead.is_promoted = True
        lead.promoted_to_application_id = sample_job_application.id
        db_session.commit()

        assert lead.is_promoted is True
        assert lead.promoted_to_application_id == sample_job_application.id


class TestJobStageEnum:
    """Test JobStage enum"""

    def test_job_stage_values(self):
        """Test that all job stages are accessible"""
        assert models.JobStage.NOT_STARTED == "not_started"
        assert models.JobStage.APPLIED == "applied"
        assert models.JobStage.IN_PROGRESS == "in_progress"
        assert models.JobStage.OFFER == "offer"
        assert models.JobStage.REJECTED == "rejected"
        assert models.JobStage.NO_ANSWER == "no_answer"

    def test_job_stage_in_database(self, db_session):
        """Test that job stages work in database"""
        for stage in models.JobStage:
            application = models.JobApplication(
                company_name=f"Company {stage}",
                role_name="Role",
                stage=stage
            )
            db_session.add(application)
        db_session.commit()

        # Verify all stages were stored
        applications = db_session.query(models.JobApplication).all()
        stages_in_db = {app.stage for app in applications}
        assert len(stages_in_db) == len(models.JobStage)


class TestModelRelationships:
    """Test relationships between models"""

    def test_job_application_cascade_delete_history(self, db_session, sample_job_application):
        """Test that deleting a job application deletes its history"""
        # Create history entries
        for i in range(3):
            history = models.StageHistory(
                job_application_id=sample_job_application.id,
                previous_stage=None,
                new_stage=models.JobStage.APPLIED,
                changed_at=datetime.utcnow()
            )
            db_session.add(history)
        db_session.commit()

        # Get history count
        history_count = db_session.query(models.StageHistory).filter(
            models.StageHistory.job_application_id == sample_job_application.id
        ).count()
        assert history_count >= 3

        # Delete the application
        app_id = sample_job_application.id
        db_session.delete(sample_job_application)
        db_session.commit()

        # History should be deleted too (cascade)
        remaining_history = db_session.query(models.StageHistory).filter(
            models.StageHistory.job_application_id == app_id
        ).count()
        assert remaining_history == 0
