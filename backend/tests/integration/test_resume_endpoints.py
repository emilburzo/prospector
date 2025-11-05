"""
Integration tests for resume endpoints
"""
import pytest
from app import models


class TestResumeEndpoints:
    """Test resume CRUD endpoints"""

    def test_create_resume(self, client):
        """Test creating a new resume"""
        response = client.post(
            "/api/resumes/",
            json={
                "content": "Software engineer with 5 years of experience",
                "file_name": "resume.txt"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Software engineer with 5 years of experience"
        assert data["file_name"] == "resume.txt"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data

    def test_create_resume_without_filename(self, client):
        """Test creating a resume without a file name"""
        response = client.post(
            "/api/resumes/",
            json={
                "content": "Brief resume content"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Brief resume content"
        assert data["file_name"] is None

    def test_list_resumes(self, client, multiple_resumes):
        """Test listing all resumes"""
        response = client.get("/api/resumes/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        # Should be ordered by created_at desc
        assert all("id" in resume for resume in data)

    def test_get_resume(self, client, sample_resume):
        """Test getting a specific resume"""
        response = client.get(f"/api/resumes/{sample_resume.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_resume.id
        assert data["content"] == sample_resume.content
        assert data["file_name"] == sample_resume.file_name

    def test_get_resume_not_found(self, client):
        """Test getting a non-existent resume"""
        response = client.get("/api/resumes/9999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_resume(self, client, sample_resume):
        """Test updating a resume"""
        response = client.put(
            f"/api/resumes/{sample_resume.id}",
            json={
                "content": "Updated resume content",
                "file_name": "updated_resume.txt"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Updated resume content"
        assert data["file_name"] == "updated_resume.txt"

    def test_update_resume_is_active(self, client, sample_resume):
        """Test updating resume active status"""
        response = client.put(
            f"/api/resumes/{sample_resume.id}",
            json={"is_active": False}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False

    def test_update_resume_not_found(self, client):
        """Test updating a non-existent resume"""
        response = client.put(
            "/api/resumes/9999",
            json={"content": "New content"}
        )
        assert response.status_code == 404

    def test_delete_resume(self, client, sample_resume):
        """Test deleting a resume"""
        resume_id = sample_resume.id
        response = client.delete(f"/api/resumes/{resume_id}")
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()

        # Verify it's deleted
        response = client.get(f"/api/resumes/{resume_id}")
        assert response.status_code == 404

    def test_delete_resume_not_found(self, client):
        """Test deleting a non-existent resume"""
        response = client.delete("/api/resumes/9999")
        assert response.status_code == 404

    def test_get_active_resume(self, client, multiple_resumes):
        """Test getting the active resume"""
        response = client.get("/api/resumes/active")
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True

    def test_get_active_resume_not_found(self, client):
        """Test getting active resume when none exists"""
        response = client.get("/api/resumes/active")
        assert response.status_code == 404

    def test_set_active_resume(self, client, multiple_resumes, db_session):
        """Test setting a resume as active"""
        # Get a non-active resume and the currently active one
        inactive_resume = [r for r in multiple_resumes if not r.is_active][0]
        old_active_id = [r for r in multiple_resumes if r.is_active][0].id

        # Set inactive resume as active using the PUT endpoint
        response = client.put(
            f"/api/resumes/{inactive_resume.id}",
            json={"is_active": True}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True
        assert data["id"] == inactive_resume.id

        # Verify old active resume is now inactive by fetching it fresh from the API
        response = client.get(f"/api/resumes/{old_active_id}")
        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_set_active_resume_not_found(self, client):
        """Test setting non-existent resume as active"""
        response = client.put(
            "/api/resumes/9999",
            json={"is_active": True}
        )
        assert response.status_code == 404
