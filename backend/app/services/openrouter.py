import httpx
from typing import Dict, Any
from app.config import get_settings


class OpenRouterService:
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.openrouter_base_url
        self.api_key = self.settings.openrouter_api_key
        self.model = self.settings.openrouter_model

    async def analyze_job_match(self, job_ad: str, resume: str) -> Dict[str, Any]:
        """
        Analyze how well a job posting matches a resume.
        Returns a dictionary with match_percentage and reasoning.
        """
        prompt = f"""You are a professional career advisor. Analyze how well this job posting matches the candidate's resume.

Job Posting:
{job_ad}

Resume:
{resume}

Please provide:
1. A match percentage (0-100) indicating how well the candidate's experience and skills align with the job requirements
2. A detailed reasoning explaining the match percentage, highlighting strengths and gaps

IMPORTANT: In the reasoning field, format your response with proper paragraph breaks. Use \\n\\n to separate major sections and \\n for list items.

Format your response EXACTLY as JSON:
{{
  "match_percentage": <number between 0 and 100>,
  "reasoning": "<detailed explanation with \\n for line breaks>"
}}"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()

            content = result["choices"][0]["message"]["content"]

            # Parse the JSON response
            import json
            analysis = json.loads(content)

            return {
                "match_percentage": float(analysis["match_percentage"]),
                "reasoning": analysis["reasoning"]
            }

    async def extract_job_application_fields(self, job_ad: str) -> Dict[str, Any]:
        """
        Extract structured information from a job posting to populate job application fields.
        """
        prompt = f"""Extract structured information from this job posting.

Job Posting:
{job_ad}

Please extract:
1. Company name (if mentioned)
2. Role/position name
3. Any other relevant details

Format your response EXACTLY as JSON:
{{
  "company_name": "<company name or 'Unknown' if not found>",
  "role_name": "<role/position name>",
  "extracted_content": "<cleaned and formatted job posting content>"
}}"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()

            content = result["choices"][0]["message"]["content"]

            # Parse the JSON response
            import json
            extracted = json.loads(content)

            return extracted
