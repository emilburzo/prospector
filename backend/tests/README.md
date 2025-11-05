# Test Suite

This directory contains the comprehensive test suite for the Prospector backend application.

## Overview

- **Total Tests**: 78
- **Code Coverage**: 96%
- **Test Framework**: pytest with pytest-asyncio and pytest-cov

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and test configuration
├── unit/                    # Unit tests
│   ├── test_models.py       # Database model tests
│   └── test_openrouter_service.py  # OpenRouter service tests
└── integration/             # Integration tests
    ├── test_job_applications_endpoints.py
    ├── test_job_leads_endpoints.py
    └── test_resume_endpoints.py
```

## Running Tests

### Quick Start

From the project root directory:

```bash
./run_tests.sh
```

This script will:
1. Create a virtual environment if it doesn't exist
2. Install all dependencies
3. Run the full test suite with coverage report

### Manual Testing

If you prefer to run tests manually:

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run tests from backend directory
cd backend
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_models.py

# Run specific test class
pytest tests/unit/test_models.py::TestResumeModel

# Run specific test method
pytest tests/unit/test_models.py::TestResumeModel::test_create_resume

# Run with coverage report
pytest --cov=app --cov-report=html
```

## Test Categories

### Unit Tests

**test_models.py** - Database model tests (15 tests)
- Resume model CRUD operations
- Job Application model with all fields
- Stage History model and relationships
- Job Lead model with promotion logic
- JobStage enum values
- Cascade deletion behavior

**test_openrouter_service.py** - OpenRouter service tests (13 tests)
- JSON cleaning function for control characters
- Job match analysis with mocked API
- Job application field extraction
- Error handling for API failures
- Percentage conversion and data types

### Integration Tests

**test_resume_endpoints.py** - Resume API endpoints (14 tests)
- Create, read, update, delete operations
- Active resume management
- File name handling
- Error cases (404s)

**test_job_applications_endpoints.py** - Job Application API endpoints (17 tests)
- Application lifecycle management
- Stage transitions and history
- Filtering by stage and company
- Pagination support
- Stage date tracking

**test_job_leads_endpoints.py** - Job Lead API endpoints (19 tests)
- Lead creation and management
- Lead analysis with AI (mocked)
- Lead promotion to applications
- Filtering and sorting
- Company name preservation logic

## Test Fixtures

Common fixtures are defined in `conftest.py`:

- `db_engine`: In-memory SQLite database engine
- `db_session`: Test database session
- `client`: FastAPI test client with database override
- `sample_resume`: Pre-created resume for testing
- `sample_job_application`: Pre-created job application
- `sample_job_lead`: Pre-created job lead
- `multiple_resumes`: Multiple resumes for list testing
- `multiple_job_applications`: Multiple applications for filtering tests

## Coverage Report

After running tests, view the HTML coverage report:

```bash
# Open in browser
open backend/htmlcov/index.html  # macOS
xdg-open backend/htmlcov/index.html  # Linux
start backend/htmlcov/index.html  # Windows
```

### Current Coverage by Module

| Module | Coverage |
|--------|----------|
| app/models.py | 100% |
| app/schemas.py | 100% |
| app/config.py | 100% |
| app/routers/resumes.py | 100% |
| app/routers/job_applications.py | 100% |
| app/services/openrouter.py | 100% |
| app/routers/job_leads.py | 89% |
| app/main.py | 88% |
| app/database.py | 69% |
| **TOTAL** | **96%** |

## Mocking Strategy

### External APIs

All OpenRouter API calls are mocked using `unittest.mock`:

```python
with patch('httpx.AsyncClient') as mock_client:
    mock_response_obj = Mock()
    mock_response_obj.json = Mock(return_value=mock_data)
    mock_post = AsyncMock(return_value=mock_response_obj)
    mock_client.return_value.__aenter__.return_value.post = mock_post
```

### Database

Tests use an in-memory SQLite database that's created fresh for each test:
- Fast execution (no I/O overhead)
- Isolated tests (no shared state)
- Automatic cleanup

## Writing New Tests

### Example Test Structure

```python
def test_feature_name(self, client, sample_fixture):
    """Test description"""
    # Arrange
    data = {"field": "value"}

    # Act
    response = client.post("/api/endpoint", json=data)

    # Assert
    assert response.status_code == 200
    assert response.json()["field"] == "value"
```

### Best Practices

1. **One assertion per test** (when possible) - Makes failures easier to debug
2. **Use descriptive test names** - Should describe what is being tested
3. **Test happy path and edge cases** - Both success and failure scenarios
4. **Use fixtures** - Avoid duplicate setup code
5. **Mock external dependencies** - Tests should not depend on external services
6. **Clean up after tests** - Use fixtures with proper teardown

## Continuous Integration

To integrate with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r backend/requirements.txt
    cd backend
    pytest --cov=app --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: backend/coverage.xml
```

## Troubleshooting

### Database Connection Errors

If you see `could not translate host name "db"`:
- Tests should automatically use SQLite in-memory database
- Check that `conftest.py` is setting `DATABASE_URL` environment variable

### Import Errors

If you see `ModuleNotFoundError`:
- Ensure you're in the `backend` directory when running tests
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Async Test Warnings

If you see `RuntimeWarning: coroutine was never awaited`:
- Ensure async tests are properly decorated with `@pytest.mark.asyncio`
- Check that AsyncMock is used correctly for mocking async functions

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all tests pass: `pytest`
3. Check coverage hasn't decreased: `pytest --cov=app`
4. Aim for >95% coverage on new code
5. Add integration tests for API endpoints
6. Add unit tests for business logic

## Dependencies

Testing dependencies are included in `backend/requirements.txt`:

```
pytest==8.3.4            # Test framework
pytest-asyncio==0.24.0   # Async test support
pytest-cov==6.0.0        # Coverage reporting
faker==33.1.0            # Test data generation
```
