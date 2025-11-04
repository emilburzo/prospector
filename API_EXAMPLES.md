# Prospector API Examples

This document provides examples of how to use the Prospector API.

## Setup

First, make sure you have your environment configured:

```bash
# Create .env file
cp .env.example .env

# Edit .env and add your OpenRouter API key
# OPENROUTER_API_KEY=your_actual_api_key
```

## Starting the Application

### Using Docker Compose (Recommended)

```bash
docker compose up -d
```

The application will be available at http://localhost:8000

### Local Development

```bash
# Install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start PostgreSQL (you need a running instance)
# Update .env with your local PostgreSQL connection string

# Run the application
uvicorn app.main:app --reload
```

## API Examples

### 1. Resume Management

#### Upload a Resume
```bash
curl -X POST "http://localhost:8000/api/resumes/" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "John Doe\nSoftware Engineer\n\nExperience:\n- 5 years Python development\n- FastAPI, Django, Flask\n- PostgreSQL, MongoDB\n\nSkills:\n- Python, JavaScript, SQL\n- Docker, Kubernetes\n- AWS, GCP",
    "filename": "john_doe_resume.txt"
  }'
```

#### Get Active Resume
```bash
curl -X GET "http://localhost:8000/api/resumes/active"
```

### 2. Job Leads

#### Create a Job Lead (with automatic ranking)
```bash
curl -X POST "http://localhost:8000/api/leads/?rank_immediately=true" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Tech Corp",
    "role_name": "Senior Python Developer",
    "job_posting": "We are looking for a Senior Python Developer with 5+ years of experience. Must have:\n- Strong Python skills\n- Experience with FastAPI or Django\n- PostgreSQL knowledge\n- Docker and Kubernetes experience\n\nNice to have:\n- AWS or GCP experience\n- Microservices architecture",
    "source": "LinkedIn",
    "url": "https://example.com/job/12345"
  }'
```

#### List All Job Leads (sorted by match percentage)
```bash
curl -X GET "http://localhost:8000/api/leads/?sort_by_match=true"
```

#### Rank a Specific Job Lead
```bash
curl -X POST "http://localhost:8000/api/leads/1/rank"
```

#### Promote Job Lead to Application
```bash
curl -X POST "http://localhost:8000/api/leads/1/promote"
```

### 3. Job Applications

#### Create a Job Application
```bash
curl -X POST "http://localhost:8000/api/applications/" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Tech Corp",
    "role_name": "Senior Python Developer",
    "stage": "applied",
    "job_ad": "Full job description here...",
    "cover_letter": "Dear Hiring Manager...",
    "notes": "Applied through LinkedIn. Recruiter is Jane Smith.",
    "job_match_percentage": 85.5
  }'
```

#### List All Applications
```bash
curl -X GET "http://localhost:8000/api/applications/"
```

#### Filter Applications by Stage
```bash
curl -X GET "http://localhost:8000/api/applications/?stage=in_progress"
```

#### Update Application Stage
```bash
curl -X PUT "http://localhost:8000/api/applications/1" \
  -H "Content-Type: application/json" \
  -d '{
    "stage": "offer",
    "notes": "Received offer on 2024-01-15. Salary: $120k"
  }'
```

#### Delete an Application
```bash
curl -X DELETE "http://localhost:8000/api/applications/1"
```

## Application Stages

The following stages are available for job applications:

- `not_started` - Job identified but not yet applied
- `applied` - Application submitted
- `in_progress` - Interview process ongoing
- `offer` - Offer received
- `rejected` - Application rejected
- `no_answer` - No response from company

When you update a stage, the system automatically tracks the history with timestamps.

## Using the Web UI

Navigate to http://localhost:8000 in your browser to access the web interface.

The UI provides:
1. **Job Applications Tab** - View and manage all your job applications
2. **Job Leads Tab** - Add new job leads and see them ranked by AI
3. **Resume Tab** - Upload and manage your resume

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Tips

1. **Upload your resume first** - The AI ranking system needs your resume to calculate match percentages
2. **Use "rank_immediately=true"** when creating job leads to get instant AI analysis
3. **Review the reasoning** - The AI provides detailed reasoning for each match percentage
4. **Promote high matches** - Use the promote feature to quickly convert promising leads to applications
5. **Track stage history** - The system automatically tracks all stage changes with timestamps

## Troubleshooting

### OpenRouter API Issues

If you get errors related to OpenRouter:
1. Check that your API key is correctly set in `.env`
2. Verify the model name is valid (see OpenRouter documentation)
3. Check your API credits/quota

### Database Issues

If you get database connection errors:
1. Ensure PostgreSQL is running
2. Verify the `DATABASE_URL` in `.env` is correct
3. Check database credentials

### Docker Issues

If Docker containers fail to start:
```bash
# Clean up and rebuild
docker compose down -v
docker compose build --no-cache
docker compose up -d
```
