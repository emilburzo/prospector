"""
Integration tests for job leads endpoints
"""
import pytest
from unittest.mock import patch, AsyncMock, Mock
from app import models


class TestJobLeadsEndpoints:
    """Test job leads CRUD endpoints"""

    def test_create_lead(self, client):
        """Test creating a new job lead"""
        response = client.post(
            "/api/leads/",
            json={
                "company_name": "Tech Startup",
                "role_name": "Backend Developer",
                "job_ad_content": "Looking for an experienced backend developer",
                "job_url": "https://example.com/job"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["company_name"] == "Tech Startup"
        assert data["role_name"] == "Backend Developer"
        assert data["job_ad_content"] == "Looking for an experienced backend developer"
        assert data["job_url"] == "https://example.com/job"
        assert data["is_promoted"] is False
        assert "id" in data

    def test_create_lead_minimal(self, client):
        """Test creating a lead with minimal fields"""
        response = client.post(
            "/api/leads/",
            json={
                "job_ad_content": "Minimal job ad content"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["job_ad_content"] == "Minimal job ad content"

    def test_list_leads(self, client, db_session):
        """Test listing all job leads"""
        # Create multiple leads
        for i in range(3):
            lead = models.JobLead(
                company_name=f"Company {i}",
                role_name=f"Role {i}",
                job_ad_content=f"Content {i}"
            )
            db_session.add(lead)
        db_session.commit()

        response = client.get("/api/leads/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_leads_with_company_filter(self, client, db_session):
        """Test filtering leads by company name"""
        leads = [
            models.JobLead(company_name="Tech Corp", role_name="Dev", job_ad_content="Content 1"),
            models.JobLead(company_name="StartUp Inc", role_name="Dev", job_ad_content="Content 2"),
            models.JobLead(company_name="Tech Industries", role_name="Dev", job_ad_content="Content 3"),
        ]
        for lead in leads:
            db_session.add(lead)
        db_session.commit()

        response = client.get("/api/leads/?company=Tech")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("Tech" in lead["company_name"] for lead in data)

    def test_list_leads_with_promoted_filter(self, client, db_session):
        """Test filtering leads by promoted status"""
        leads = [
            models.JobLead(company_name="Company 1", job_ad_content="Content 1", is_promoted=True),
            models.JobLead(company_name="Company 2", job_ad_content="Content 2", is_promoted=False),
            models.JobLead(company_name="Company 3", job_ad_content="Content 3", is_promoted=False),
        ]
        for lead in leads:
            db_session.add(lead)
        db_session.commit()

        response = client.get("/api/leads/?promoted=false")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(not lead["is_promoted"] for lead in data)

    def test_list_leads_sorted_by_match(self, client, db_session):
        """Test sorting leads by match percentage"""
        leads = [
            models.JobLead(company_name="C1", job_ad_content="Content 1", match_percentage=70.0),
            models.JobLead(company_name="C2", job_ad_content="Content 2", match_percentage=90.0),
            models.JobLead(company_name="C3", job_ad_content="Content 3", match_percentage=80.0),
        ]
        for lead in leads:
            db_session.add(lead)
        db_session.commit()

        response = client.get("/api/leads/?sort_by_match=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["match_percentage"] == 90.0
        assert data[1]["match_percentage"] == 80.0
        assert data[2]["match_percentage"] == 70.0

    def test_get_lead(self, client, sample_job_lead):
        """Test getting a specific lead"""
        response = client.get(f"/api/leads/{sample_job_lead.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_job_lead.id
        assert data["company_name"] == sample_job_lead.company_name

    def test_get_lead_not_found(self, client):
        """Test getting a non-existent lead"""
        response = client.get("/api/leads/9999")
        assert response.status_code == 404

    def test_update_lead(self, client, sample_job_lead):
        """Test updating a lead"""
        response = client.put(
            f"/api/leads/{sample_job_lead.id}",
            json={
                "company_name": "Updated Company",
                "role_name": "Updated Role"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["company_name"] == "Updated Company"
        assert data["role_name"] == "Updated Role"

    def test_update_lead_not_found(self, client):
        """Test updating a non-existent lead"""
        response = client.put(
            "/api/leads/9999",
            json={"company_name": "Updated"}
        )
        assert response.status_code == 404

    def test_delete_lead(self, client, sample_job_lead):
        """Test deleting a lead"""
        lead_id = sample_job_lead.id
        response = client.delete(f"/api/leads/{lead_id}")
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()

        # Verify it's deleted
        response = client.get(f"/api/leads/{lead_id}")
        assert response.status_code == 404

    def test_delete_lead_not_found(self, client):
        """Test deleting a non-existent lead"""
        response = client.delete("/api/leads/9999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_analyze_lead_success(self, client, sample_job_lead, sample_resume):
        """Test analyzing a lead with a resume"""
        mock_analysis = {
            "match_percentage": 85.0,
            "reasoning": "Strong match based on experience"
        }

        with patch('app.routers.job_leads.OpenRouterService') as mock_service:
            mock_instance = Mock()
            mock_instance.analyze_job_match = AsyncMock(return_value=mock_analysis)
            mock_service.return_value = mock_instance

            response = client.post(f"/api/leads/{sample_job_lead.id}/analyze")
            assert response.status_code == 200
            data = response.json()
            assert data["match_percentage"] == 85.0
            assert data["reasoning"] == "Strong match based on experience"

    def test_analyze_lead_not_found(self, client):
        """Test analyzing a non-existent lead"""
        response = client.post("/api/leads/9999/analyze")
        assert response.status_code == 404
        assert "lead not found" in response.json()["detail"].lower()

    def test_analyze_lead_no_active_resume(self, client, sample_job_lead):
        """Test analyzing a lead when no active resume exists"""
        response = client.post(f"/api/leads/{sample_job_lead.id}/analyze")
        assert response.status_code == 404
        assert "resume" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_promote_lead_success(self, client, sample_job_lead):
        """Test promoting a lead to a job application"""
        mock_extracted = {
            "company_name": "Extracted Company",
            "role_name": "Extracted Role",
            "extracted_content": "Extracted content"
        }

        with patch('app.routers.job_leads.OpenRouterService') as mock_service:
            mock_instance = Mock()
            mock_instance.extract_job_application_fields = AsyncMock(return_value=mock_extracted)
            mock_service.return_value = mock_instance

            response = client.post(f"/api/leads/{sample_job_lead.id}/promote")
            assert response.status_code == 200
            data = response.json()
            assert "job_application" in data
            assert "message" in data
            assert "promoted" in data["message"].lower()

            # Verify the lead is deleted
            verify_response = client.get(f"/api/leads/{sample_job_lead.id}")
            assert verify_response.status_code == 404

    def test_promote_lead_not_found(self, client):
        """Test promoting a non-existent lead"""
        response = client.post("/api/leads/9999/promote")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_promote_lead_preserves_company_name(self, client, db_session):
        """Test that promotion preserves lead company name over extracted 'Unknown'"""
        lead = models.JobLead(
            company_name="Original Company",
            role_name="Original Role",
            job_ad_content="Job ad content"
        )
        db_session.add(lead)
        db_session.commit()
        db_session.refresh(lead)

        mock_extracted = {
            "company_name": "Unknown",
            "role_name": "Extracted Role",
            "extracted_content": "Content"
        }

        with patch('app.routers.job_leads.OpenRouterService') as mock_service:
            mock_instance = Mock()
            mock_instance.extract_job_application_fields = AsyncMock(return_value=mock_extracted)
            mock_service.return_value = mock_instance

            response = client.post(f"/api/leads/{lead.id}/promote")
            assert response.status_code == 200
            data = response.json()
            # Should use the original company name, not "Unknown"
            assert data["job_application"]["company_name"] == "Original Company"
