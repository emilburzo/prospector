# 🎯 Prospector - AI-Powered Job Application Tracker

Prospector is a comprehensive job application tracking and lead finding system that uses AI/LLM to automate the tedious parts of job hunting, making it easier for humans to review and manage their job search.

## Features

### 1. Job Application Tracker
Track all your job applications with:
- Company name and role details
- Application stage tracking (not started, applied, in progress, offer, rejected, no answer)
- Stage history with timestamps
- Job ad storage
- Cover letters and additional application materials
- Notes and comments
- AI-generated match percentage

### 2. Job Lead Finder
Manage potential job opportunities with:
- Store job postings from any source
- AI-powered job matching using your resume
- Match percentage and detailed reasoning
- Easy sorting by match percentage
- One-click promotion to job application tracker
- Automatic field extraction using AI

### 3. Resume Management
- Store and manage multiple resumes
- Set active resume for job matching
- Text-based resume storage

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **AI/LLM**: OpenRouter API (configurable model)
- **Frontend**: Vanilla JavaScript with modern UI
- **Deployment**: Docker & Docker Compose
- **Stateless**: Designed for Kubernetes (k3s) deployment

## Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenRouter API key (get one at https://openrouter.ai/)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/emilburzo/prospector.git
cd prospector
```

2. Create a `.env` file from the example:
```bash
cp .env.example .env
```

3. Edit `.env` and add your OpenRouter API key:
```env
DATABASE_URL=postgresql://prospector:prospector@db:5432/prospector
OPENROUTER_API_KEY=your_actual_api_key_here
OPENROUTER_MODEL=anthropic/claude-3-haiku
```

4. Start the application:
```bash
docker-compose up -d
```

5. Access the application:
- Web UI: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Usage

### 1. Upload Your Resume
1. Go to the "Resume" tab
2. Paste your resume content or upload a file
3. Save as active resume

### 2. Add Job Leads
1. Go to the "Job Leads" tab
2. Add a new job lead with the job posting text
3. The system will automatically rank it against your resume
4. View match percentage and reasoning

### 3. Promote to Application
1. Review job leads sorted by match percentage
2. Click "Promote" on promising leads
3. The system will extract structured fields using AI
4. Track the application through its lifecycle

### 4. Manage Applications
1. Go to the "Job Applications" tab
2. View all your applications
3. Filter by stage
4. Update stages as you progress
5. Add notes and additional information

## API Endpoints

### Job Applications
- `POST /api/applications/` - Create job application
- `GET /api/applications/` - List all applications
- `GET /api/applications/{id}` - Get specific application
- `PUT /api/applications/{id}` - Update application
- `DELETE /api/applications/{id}` - Delete application

### Job Leads
- `POST /api/leads/` - Create job lead (with optional immediate ranking)
- `GET /api/leads/` - List all leads (sortable by match %)
- `GET /api/leads/{id}` - Get specific lead
- `POST /api/leads/{id}/rank` - Rank a job lead
- `POST /api/leads/rank-batch` - Rank multiple leads
- `POST /api/leads/{id}/promote` - Promote lead to application
- `DELETE /api/leads/{id}` - Delete lead

### Resumes
- `POST /api/resumes/` - Create resume from text
- `POST /api/resumes/upload` - Upload resume file
- `GET /api/resumes/` - List all resumes
- `GET /api/resumes/active` - Get active resume
- `GET /api/resumes/{id}` - Get specific resume
- `PUT /api/resumes/{id}/activate` - Set resume as active
- `DELETE /api/resumes/{id}` - Delete resume

## Kubernetes Deployment

The application is designed to be stateless and can be deployed to k3s or any Kubernetes cluster.

### Example Kubernetes Deployment

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: prospector-secrets
type: Opaque
stringData:
  openrouter-api-key: "your-api-key"
  database-url: "postgresql://user:pass@postgres-service:5432/prospector"

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prospector
spec:
  replicas: 2
  selector:
    matchLabels:
      app: prospector
  template:
    metadata:
      labels:
        app: prospector
    spec:
      containers:
      - name: prospector
        image: prospector:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: prospector-secrets
              key: database-url
        - name: OPENROUTER_API_KEY
          valueFrom:
            secretKeyRef:
              name: prospector-secrets
              key: openrouter-api-key
        - name: OPENROUTER_MODEL
          value: "anthropic/claude-3-haiku"

---
apiVersion: v1
kind: Service
metadata:
  name: prospector-service
spec:
  selector:
    app: prospector
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `OPENROUTER_MODEL`: Model to use (default: anthropic/claude-3-haiku)

### Recommended Models

- `anthropic/claude-3-haiku` - Fast and cost-effective (recommended)
- `anthropic/claude-3-sonnet` - More capable, higher cost
- `openai/gpt-3.5-turbo` - Good balance
- `openai/gpt-4` - Most capable, highest cost

## Development

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up local database
# Make sure PostgreSQL is running locally

# Run migrations
alembic upgrade head

# Start the application
uvicorn app.main:app --reload
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Architecture

```
┌─────────────────┐
│   Frontend UI   │
│  (HTML/JS/CSS)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI API   │
│   (Python)      │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌──────┐  ┌──────────┐
│ SQL  │  │OpenRouter│
│ DB   │  │   API    │
└──────┘  └──────────┘
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this for your job search!

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env file
- Verify database credentials

### OpenRouter API Issues
- Verify API key is correct
- Check API quota/credits
- Ensure model name is valid

### Docker Issues
- Run `docker-compose down -v` to clean up volumes
- Rebuild with `docker-compose build --no-cache`

## Support

For issues and questions, please open a GitHub issue.