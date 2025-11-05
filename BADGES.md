# Badges for README

Add these badges to your main README.md to show project status:

## Basic Badges

```markdown
![Tests](https://github.com/YOUR_USERNAME/prospector/actions/workflows/test.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)
![Coverage](https://img.shields.io/badge/coverage-96%25-brightgreen)
```

## With Codecov (if configured)

```markdown
[![codecov](https://codecov.io/gh/YOUR_USERNAME/prospector/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/prospector)
```

## All Badges Combined

Replace `YOUR_USERNAME` with your actual GitHub username:

```markdown
# Prospector

![Tests](https://github.com/YOUR_USERNAME/prospector/actions/workflows/test.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)
![Coverage](https://img.shields.io/badge/coverage-96%25-brightgreen)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/prospector/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/prospector)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

AI-powered job application management system
```

## Preview

The badges will look like this:

![Tests Badge](https://img.shields.io/badge/tests-passing-brightgreen)
![Python Badge](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)
![Coverage Badge](https://img.shields.io/badge/coverage-96%25-brightgreen)

## Alternative Badge Styles

### Flat Style
```markdown
![Tests](https://github.com/YOUR_USERNAME/prospector/actions/workflows/test.yml/badge.svg?style=flat)
```

### For the Badge Style
```markdown
![Tests](https://github.com/YOUR_USERNAME/prospector/actions/workflows/test.yml/badge.svg?style=for-the-badge)
```

### Plastic Style
```markdown
![Tests](https://github.com/YOUR_USERNAME/prospector/actions/workflows/test.yml/badge.svg?style=plastic)
```

## Updating Coverage Badge

The coverage percentage is currently hardcoded. To make it dynamic:

1. **Use Codecov**: Will automatically update based on test coverage
2. **Use Coverage Badge Action**: Automatically generates badge from coverage report
3. **Manual Update**: Update the percentage in the badge URL when coverage changes

### Automatic Coverage Badge (Recommended)

Add this to your workflow to automatically update the coverage badge:

```yaml
- name: Create Coverage Badge
  uses: schneegans/dynamic-badges-action@v1.7.0
  with:
    auth: ${{ secrets.GIST_SECRET }}
    gistID: YOUR_GIST_ID
    filename: prospector-coverage.json
    label: coverage
    message: ${{ steps.coverage.outputs.coverage }}%
    color: green
```

This requires:
1. Creating a GitHub personal access token with `gist` scope
2. Adding it as `GIST_SECRET` in repository secrets
3. Creating a gist to store the badge data

## License Badge

If you have a LICENSE file, add:

```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

## Additional Useful Badges

```markdown
![Last Commit](https://img.shields.io/github/last-commit/YOUR_USERNAME/prospector)
![Repo Size](https://img.shields.io/github/repo-size/YOUR_USERNAME/prospector)
![Issues](https://img.shields.io/github/issues/YOUR_USERNAME/prospector)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)
```

## Full Example

```markdown
# Prospector 🎯

![Tests](https://github.com/YOUR_USERNAME/prospector/actions/workflows/test.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)
![Coverage](https://img.shields.io/badge/coverage-96%25-brightgreen)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Last Commit](https://img.shields.io/github/last-commit/YOUR_USERNAME/prospector)

> AI-powered job application management system with resume matching and lead tracking

## Features

- 🤖 AI-powered job matching using OpenRouter
- 📊 96% test coverage
- 🚀 FastAPI backend
- 📝 Resume management
- 🎯 Lead tracking and promotion
- 📈 Application stage tracking

## Quick Start

\`\`\`bash
./run_tests.sh
\`\`\`

[Full documentation →](docs/)
```

Remember to replace `YOUR_USERNAME` with your actual GitHub username in all badge URLs!
