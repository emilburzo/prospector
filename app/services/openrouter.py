import httpx
import json
from app.config import get_settings


class OpenRouterService:
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.openrouter_api_key
        self.model = self.settings.openrouter_model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    async def _make_request(self, messages: list, temperature: float = 0.7) -> str:
        """Make a request to OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.base_url,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

    async def calculate_job_match(self, job_posting: str, resume: str) -> dict:
        """Calculate match percentage and reasoning for a job posting against a resume"""
        messages = [
            {
                "role": "system",
                "content": "You are an expert recruiter analyzing job matches. Analyze the job posting against the candidate's resume and provide a match percentage (0-100) and detailed reasoning."
            },
            {
                "role": "user",
                "content": f"""Analyze this job posting against the candidate's resume:

JOB POSTING:
{job_posting}

RESUME:
{resume}

Provide your response in JSON format with the following structure:
{{
    "match_percentage": <number between 0-100>,
    "reasoning": "<detailed explanation of the match>"
}}

Consider:
- Skills match
- Experience level match
- Role responsibilities alignment
- Industry/domain fit
- Cultural and value alignment based on company description"""
            }
        ]
        
        response = await self._make_request(messages, temperature=0.3)
        
        # Try to parse JSON from the response
        try:
            # Handle markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response)
            return {
                "match_percentage": float(result.get("match_percentage", 0)),
                "reasoning": result.get("reasoning", "")
            }
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback: try to extract percentage from text
            return {
                "match_percentage": 0.0,
                "reasoning": f"Error parsing AI response: {str(e)}\n\nRaw response: {response}"
            }

    async def extract_job_fields(self, job_posting: str) -> dict:
        """Extract structured fields from a job posting"""
        messages = [
            {
                "role": "system",
                "content": "You are an expert at extracting structured information from job postings."
            },
            {
                "role": "user",
                "content": f"""Extract the following information from this job posting:

JOB POSTING:
{job_posting}

Provide your response in JSON format with the following structure:
{{
    "company_name": "<company name>",
    "role_name": "<job title/role>",
    "job_ad": "<full job description>",
    "additional_info": {{
        "location": "<location if mentioned>",
        "salary_range": "<salary if mentioned>",
        "employment_type": "<full-time/part-time/contract>",
        "remote_policy": "<remote/hybrid/onsite>",
        "key_requirements": ["<requirement1>", "<requirement2>"]
    }}
}}

Extract as much information as possible. If certain fields are not present in the job posting, use null or empty values."""
            }
        ]
        
        response = await self._make_request(messages, temperature=0.3)
        
        # Try to parse JSON from the response
        try:
            # Handle markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response)
            return result
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback: return basic structure
            return {
                "company_name": "Unknown",
                "role_name": "Unknown",
                "job_ad": job_posting,
                "additional_info": {"error": f"Failed to parse: {str(e)}"}
            }
