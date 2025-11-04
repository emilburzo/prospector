# Prospector

AI-powered job application management system that helps you track applications and discover the best job opportunities using AI/LLM technology.

## Features

### 1. Job Application Tracker
Track all your job applications in one place with:
- Company name and role tracking
- Application stage management (Not Started, Applied, In Progress, Offer, Rejected, No Answer)
- Complete stage change history with timestamps
- Storage for job ads, cover letters, and application materials
- Notes and match percentage tracking
- Comprehensive timeline of your job search

### 2. Job Lead Finder
Discover and rank job opportunities with AI:
- Add job postings via UI or API
- AI-powered match analysis using your resume
- Automatic ranking by match percentage
- Detailed reasoning for each match score
- One-click promotion to application tracker
- AI-assisted field extraction when promoting leads

## Technology Stack

- **Backend**: FastAPI (Python 3.12)
- **Frontend**: React 18 + Vite + TailwindCSS
- **Database**: PostgreSQL 16
- **AI/LLM**: OpenRouter API
- **Deployment**: Docker + Kubernetes (k3s ready)
- **UI Theme**: Modern dark theme

## Prerequisites

- Docker and Docker Compose
- OpenRouter API key ([Get one here](https://openrouter.ai/))
- For k3s deployment: Kubernetes cluster with kubectl configured

## Quick Start (Development)

1. Clone the repository:
```bash
git clone <repository-url>
cd prospector
```

2. Create a `.env` file:
```bash
cp .env.example .env
```

3. Edit `.env` and add your OpenRouter API key:
```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
```

4. Start the application:
```bash
docker-compose up -d
```

5. Access the application:
- Frontend: http://localhost:5173
- API Documentation: http://localhost:8000/docs
- Database: localhost:5432

## Production Deployment

### Building the Production Image

```bash
docker build -t prospector:latest .
```

### Deploy to k3s

1. Update the secrets in `k8s-deployment.yaml`:
```yaml
stringData:
  database-url: "postgresql://user:password@postgres:5432/prospector"
  openrouter-api-key: "your-actual-api-key"
  openrouter-model: "anthropic/claude-3.5-sonnet"
```

2. Apply the Kubernetes manifests:
```bash
kubectl apply -f k8s-deployment.yaml
```

3. Get the service URL:
```bash
kubectl get svc -n prospector
```

## Usage Guide

### 1. Setting Up Your Resume

1. Navigate to the **Resumes** tab
2. Click **New Resume**
3. Paste your resume text (plain text format works best)
4. Give it a descriptive name
5. The resume will automatically be set as active

### 2. Adding Job Leads

1. Go to the **Job Leads** tab
2. Click **New Lead**
3. Fill in:
   - Company name
   - Role name
   - Job URL (optional)
   - Job ad content (paste the full job posting)
4. Click **Create**

### 3. Analyzing Job Matches

1. In the Job Leads list, click **Analyze** on any lead
2. The AI will compare the job posting with your active resume
3. You'll receive:
   - A match percentage (0-100)
   - Detailed reasoning explaining the match
4. Use **Sort by Match** to see your best opportunities first

### 4. Promoting Leads to Applications

1. Click **Promote** on a job lead
2. AI will automatically extract relevant information
3. The lead becomes a tracked application
4. Add cover letters, notes, and track your progress

### 5. Managing Applications

1. Navigate to the **Applications** tab
2. Update application stages as you progress
3. View complete history of stage changes
4. Add notes, cover letters, and other materials
5. Track which applications are most promising

## API Endpoints

### Resumes
- `GET /api/resumes` - List all resumes
- `GET /api/resumes/active` - Get active resume
- `POST /api/resumes` - Create new resume
- `PUT /api/resumes/{id}` - Update resume
- `DELETE /api/resumes/{id}` - Delete resume

### Job Applications
- `GET /api/applications` - List applications (with filters)
- `GET /api/applications/{id}` - Get specific application
- `POST /api/applications` - Create application
- `PUT /api/applications/{id}` - Update application
- `DELETE /api/applications/{id}` - Delete application
- `GET /api/applications/{id}/history` - Get stage history

### Job Leads
- `GET /api/leads` - List leads (with sorting)
- `GET /api/leads/{id}` - Get specific lead
- `POST /api/leads` - Create lead
- `PUT /api/leads/{id}` - Update lead
- `DELETE /api/leads/{id}` - Delete lead
- `POST /api/leads/{id}/analyze` - Analyze job match with AI
- `POST /api/leads/{id}/promote` - Promote lead to application

Full API documentation available at `/docs` when running.

## Environment Variables

### Required
- `DATABASE_URL` - PostgreSQL connection string
- `OPENROUTER_API_KEY` - Your OpenRouter API key

### Optional
- `OPENROUTER_MODEL` - AI model to use (default: anthropic/claude-3.5-sonnet)
- `OPENROUTER_BASE_URL` - OpenRouter API URL (default: https://openrouter.ai/api/v1)

## Architecture

```
prospector/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── models.py    # Database models
│   │   ├── schemas.py   # Pydantic schemas
│   │   ├── database.py  # DB connection
│   │   ├── config.py    # Configuration
│   │   ├── main.py      # FastAPI app
│   │   ├── routers/     # API endpoints
│   │   └── services/    # Business logic
│   └── requirements.txt
├── frontend/            # React frontend
│   ├── src/
│   │   ├── pages/       # Main pages
│   │   ├── api/         # API client
│   │   ├── App.jsx      # Main app
│   │   └── main.jsx     # Entry point
│   └── package.json
├── docker-compose.yml   # Development setup
├── Dockerfile          # Production image
├── k8s-deployment.yaml # Kubernetes manifests
└── README.md
```

## Database Schema

### Resumes
- Stores resume versions
- Only one can be active at a time
- Used for AI analysis

### Job Applications
- Complete application tracking
- Stage management with history
- Storage for all materials

### Job Leads
- Potential opportunities
- AI match analysis results
- Can be promoted to applications

### Stage History
- Tracks all stage changes
- Maintains complete timeline
- Provides audit trail

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Database Migrations

Using SQLAlchemy, models are automatically created on startup. For production, consider using Alembic for migrations:

```bash
cd backend
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Customization

### Changing AI Models

Edit the `OPENROUTER_MODEL` environment variable. Compatible models include:
- `anthropic/claude-3.5-sonnet` (default, recommended)
- `anthropic/claude-3-opus`
- `openai/gpt-4-turbo`
- `openai/gpt-4`

See [OpenRouter documentation](https://openrouter.ai/docs) for more options.

### Customizing the UI

The UI uses TailwindCSS. Colors are defined in `frontend/tailwind.config.js`:

```javascript
colors: {
  dark: { /* dark theme colors */ },
  accent: { /* accent colors */ }
}
```

## Troubleshooting

### "No active resume found" error
- Create a resume in the Resumes tab
- Make sure it's set as active (green badge)

### AI analysis failing
- Check your OpenRouter API key in `.env`
- Verify you have credits/access to the selected model
- Check backend logs: `docker-compose logs backend`

### Database connection errors
- Ensure PostgreSQL is running: `docker-compose ps`
- Check DATABASE_URL is correct
- Verify network connectivity

### Frontend not loading
- Clear browser cache
- Check console for errors
- Verify backend is accessible at the API URL

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use this for your job search!

## Support

For issues and questions:
- Check the [API documentation](http://localhost:8000/docs) when running
- Review logs: `docker-compose logs`
- Open an issue on GitHub

## Roadmap

Future enhancements:
- Email notifications for stage changes
- Calendar integration for interviews
- Chrome extension for one-click job import
- Analytics dashboard
- Export to PDF/CSV
- Integration with LinkedIn
- Automated follow-up reminders

---

Good luck with your job search!