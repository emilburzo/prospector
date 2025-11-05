"""
Integration tests for job applications endpoints
"""
import pytest
from app import models


class TestJobApplicationsEndpoints:
    """Test job applications CRUD endpoints"""

    def test_create_application(self, client):
        """Test creating a new job application"""
        response = client.post(
            "/api/applications/",
            json={
                "company_name": "Tech Corp",
                "role_name": "Senior Software Engineer",
                "stage": "not_started",
                "job_ad_content": "We're looking for a senior engineer"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["company_name"] == "Tech Corp"
        assert data["role_name"] == "Senior Software Engineer"
        assert data["stage"] == "not_started"
        assert "id" in data

    def test_create_application_with_optional_fields(self, client):
        """Test creating an application with optional fields"""
        response = client.post(
            "/api/applications/",
            json={
                "company_name": "StartUp Inc",
                "role_name": "Backend Developer",
                "stage": "applied",
                "job_ad_content": "Backend role",
                "cover_letter": "My cover letter",
                "application_notes": "Applied via LinkedIn",
                "notes": "Follow up in 2 weeks",
                "match_percentage": 90.5,
                "match_reasoning": "Excellent match"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["cover_letter"] == "My cover letter"
        assert data["application_notes"] == "Applied via LinkedIn"
        assert data["notes"] == "Follow up in 2 weeks"
        assert data["match_percentage"] == 90.5
        assert data["match_reasoning"] == "Excellent match"

    def test_list_applications(self, client, multiple_job_applications):
        """Test listing all job applications"""
        response = client.get("/api/applications/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_list_applications_with_stage_filter(self, client, multiple_job_applications):
        """Test filtering applications by stage"""
        response = client.get("/api/applications/?stage=applied")
        assert response.status_code == 200
        data = response.json()
        # From fixture, we have 3 applications with stage "applied" (indices 0, 2, 4)
        assert len(data) == 3
        assert all(app["stage"] == "applied" for app in data)

    def test_list_applications_with_company_filter(self, client, db_session):
        """Test filtering applications by company name"""
        apps = [
            models.JobApplication(company_name="Tech Corp", role_name="Dev", stage=models.JobStage.APPLIED, job_ad_content="Content 1"),
            models.JobApplication(company_name="StartUp Inc", role_name="Dev", stage=models.JobStage.APPLIED, job_ad_content="Content 2"),
            models.JobApplication(company_name="Tech Industries", role_name="Dev", stage=models.JobStage.APPLIED, job_ad_content="Content 3"),
        ]
        for app in apps:
            db_session.add(app)
        db_session.commit()

        response = client.get("/api/applications/?company=Tech")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("Tech" in app["company_name"] for app in data)

    def test_list_applications_pagination(self, client, multiple_job_applications):
        """Test pagination of applications list"""
        response = client.get("/api/applications/?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_application(self, client, sample_job_application):
        """Test getting a specific application"""
        response = client.get(f"/api/applications/{sample_job_application.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_job_application.id
        assert data["company_name"] == sample_job_application.company_name
        assert data["role_name"] == sample_job_application.role_name

    def test_get_application_not_found(self, client):
        """Test getting a non-existent application"""
        response = client.get("/api/applications/9999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_application(self, client, sample_job_application):
        """Test updating an application"""
        response = client.put(
            f"/api/applications/{sample_job_application.id}",
            json={
                "company_name": "Updated Company",
                "notes": "New notes"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["company_name"] == "Updated Company"
        assert data["notes"] == "New notes"

    def test_update_application_stage(self, client, sample_job_application, db_session):
        """Test updating application stage creates history entry"""
        old_stage = sample_job_application.stage

        response = client.put(
            f"/api/applications/{sample_job_application.id}",
            json={"stage": "in_progress"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["stage"] == "in_progress"

        # Verify stage history was created
        # Refresh to get updated relationships
        db_session.refresh(sample_job_application)
        history = sample_job_application.stage_history
        # Should have at least 1 entry for this update (initial history may or may not be present)
        assert len(history) >= 1
        latest_history = history[-1]
        assert latest_history.previous_stage == old_stage
        assert latest_history.new_stage == models.JobStage.IN_PROGRESS

    def test_update_application_not_found(self, client):
        """Test updating a non-existent application"""
        response = client.put(
            "/api/applications/9999",
            json={"notes": "Update"}
        )
        assert response.status_code == 404

    def test_delete_application(self, client, sample_job_application):
        """Test deleting an application"""
        app_id = sample_job_application.id
        response = client.delete(f"/api/applications/{app_id}")
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()

        # Verify it's deleted
        response = client.get(f"/api/applications/{app_id}")
        assert response.status_code == 404

    def test_delete_application_not_found(self, client):
        """Test deleting a non-existent application"""
        response = client.delete("/api/applications/9999")
        assert response.status_code == 404

    def test_get_application_history(self, client, sample_job_application, db_session):
        """Test getting application stage history"""
        # Create some stage changes
        stages = [models.JobStage.IN_PROGRESS, models.JobStage.OFFER]
        for stage in stages:
            client.put(
                f"/api/applications/{sample_job_application.id}",
                json={"stage": stage}
            )

        response = client.get(f"/api/applications/{sample_job_application.id}/history")
        assert response.status_code == 200
        data = response.json()
        # Should have at least 2 stage changes we made
        assert len(data) >= 2
        assert all("previous_stage" in entry for entry in data)
        assert all("new_stage" in entry for entry in data)
        assert all("changed_at" in entry for entry in data)

    def test_get_application_history_not_found(self, client):
        """Test getting history for non-existent application"""
        response = client.get("/api/applications/9999/history")
        assert response.status_code == 404

    def test_application_stage_date_updated(self, client, sample_job_application, db_session):
        """Test that stage_date is updated when stage changes"""
        import time

        # Get initial stage_date
        initial_stage_date = sample_job_application.stage_date

        # Wait a moment to ensure time difference
        time.sleep(0.1)

        # Update stage
        response = client.put(
            f"/api/applications/{sample_job_application.id}",
            json={"stage": "in_progress"}
        )
        assert response.status_code == 200

        # Refresh the application from database
        db_session.refresh(sample_job_application)

        # stage_date should be updated
        assert sample_job_application.stage_date > initial_stage_date

    def test_application_stage_date_not_updated_on_other_changes(self, client, sample_job_application, db_session):
        """Test that stage_date is NOT updated when other fields change"""
        initial_stage_date = sample_job_application.stage_date

        # Update a field other than stage
        response = client.put(
            f"/api/applications/{sample_job_application.id}",
            json={"notes": "New notes"}
        )
        assert response.status_code == 200

        # Refresh the application from database
        db_session.refresh(sample_job_application)

        # stage_date should remain the same
        assert sample_job_application.stage_date == initial_stage_date
