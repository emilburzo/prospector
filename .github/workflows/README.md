# GitHub Actions Workflows

This directory contains the CI/CD workflows for the Prospector project.

## Available Workflows

### Test Workflow (`test.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests targeting `main` or `develop` branches

**What it does:**
1. ✅ Runs tests on multiple Python versions (3.11, 3.12, 3.13)
2. 📊 Generates coverage reports
3. ☁️ Uploads coverage to Codecov (optional)
4. 🏷️ Creates coverage badge
5. 📝 Provides test summary in PR

**Environment Variables:**
- `DATABASE_URL`: Set to `sqlite:///:memory:` for testing
- `OPENROUTER_API_KEY`: Set to `test-key-for-ci` for testing

**Matrix Testing:**
The workflow runs tests on multiple Python versions to ensure compatibility:
- Python 3.11
- Python 3.12
- Python 3.13

**Caching:**
pip dependencies are cached to speed up workflow runs.

**Coverage Reporting:**
- Coverage reports are generated in XML and terminal formats
- Coverage is uploaded to Codecov (if `CODECOV_TOKEN` secret is configured)
- Coverage badge is generated and uploaded as an artifact

## Setup

### Required Secrets

None required for basic functionality. Optional secrets:

#### Codecov Integration (Optional)
To enable Codecov integration:

1. Sign up at [codecov.io](https://codecov.io)
2. Add your repository
3. Get your Codecov token
4. Add it as a repository secret:
   - Go to: Repository → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `CODECOV_TOKEN`
   - Value: Your Codecov token

### Badge Setup

Add these badges to your README.md:

```markdown
## Status

![Tests](https://github.com/YOUR_USERNAME/prospector/actions/workflows/test.yml/badge.svg)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/prospector/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/prospector)
```

Replace `YOUR_USERNAME` with your GitHub username.

## Workflow Details

### Steps Breakdown

1. **Checkout code**: Uses `actions/checkout@v4` to clone the repository

2. **Set up Python**: Uses `actions/setup-python@v5` with caching enabled
   - Caches pip dependencies based on `backend/requirements.txt`
   - Reduces workflow time by ~30-60 seconds

3. **Install dependencies**: Installs Python packages from `requirements.txt`

4. **Run tests**: Executes pytest with coverage
   ```bash
   cd backend
   pytest --cov=app --cov-report=xml --cov-report=term-missing
   ```

5. **Upload coverage** (Python 3.13 only): Uploads to Codecov

6. **Generate badge** (Python 3.13 + main branch only): Creates coverage SVG badge

7. **Test Summary**: Adds summary to GitHub Actions UI

## Local Testing

To test the workflow locally before pushing:

```bash
# Install act (GitHub Actions local runner)
# macOS:
brew install act

# Linux:
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run the workflow
act push

# Run a specific job
act push -j test

# Run with specific Python version
act push -j test -e '{"matrix": {"python-version": "3.13"}}'
```

## Troubleshooting

### Tests Failing in CI but Pass Locally

1. **Check Python version**: Ensure local Python matches CI Python version
   ```bash
   python --version
   ```

2. **Check environment variables**: CI uses in-memory SQLite
   ```bash
   export DATABASE_URL="sqlite:///:memory:"
   export OPENROUTER_API_KEY="test-key-for-ci"
   pytest
   ```

3. **Clean environment**: CI runs in a fresh environment
   ```bash
   # Test in a fresh virtual environment
   python -m venv test_venv
   source test_venv/bin/activate
   pip install -r backend/requirements.txt
   cd backend && pytest
   ```

### Coverage Upload Failing

- Ensure `CODECOV_TOKEN` is set (if using Codecov)
- Check that coverage.xml is generated in `backend/coverage.xml`
- The workflow sets `fail_ci_if_error: false` so coverage upload failures won't fail the build

### Workflow Not Triggering

Check that:
1. Workflow file is in `.github/workflows/` directory
2. File has `.yml` or `.yaml` extension
3. YAML syntax is valid
4. Branch name matches trigger configuration

### Slow Workflow Runs

Optimization tips:
1. Pip caching is enabled (should save 30-60 seconds)
2. Consider reducing Python version matrix if not needed
3. Use `--no-cov` for faster test runs if coverage isn't needed:
   ```yaml
   pytest --no-cov
   ```

## Extending the Workflow

### Add Linting

```yaml
- name: Lint with flake8
  run: |
    pip install flake8
    flake8 backend/app --count --select=E9,F63,F7,F82 --show-source --statistics
```

### Add Type Checking

```yaml
- name: Type check with mypy
  run: |
    pip install mypy
    mypy backend/app
```

### Add Security Scanning

```yaml
- name: Security check with bandit
  run: |
    pip install bandit
    bandit -r backend/app
```

### Notifications

Add Slack/Discord notifications:

```yaml
- name: Notify on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## Best Practices

1. ✅ **Keep workflows fast** - Use caching, parallel jobs
2. ✅ **Test on multiple Python versions** - Catch compatibility issues
3. ✅ **Use secrets for sensitive data** - Never hardcode tokens
4. ✅ **Fail fast** - Stop on first failure to save CI minutes
5. ✅ **Add status badges** - Show build status in README
6. ✅ **Test locally** - Use `act` or Docker to test workflows

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [pytest Documentation](https://docs.pytest.org/)
- [Codecov Documentation](https://docs.codecov.com/)
