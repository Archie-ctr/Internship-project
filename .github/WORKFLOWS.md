# GitHub Actions CI/CD Workflows

This project uses GitHub Actions to automate testing, linting, security checks, and deployment.

## Configured Workflows

### 1. **Backend Tests & Lint** (`.github/workflows/backend-tests.yml`)

Runs on every push/PR affecting `backend/` directory.

**Jobs:**
- **Lint** - Code style checks (Black, isort, Flake8)
- **Security** - Vulnerability scanning (Bandit, Safety)
- **Test** - Unit tests with coverage (pytest)
- **Type Check** - Static type checking (mypy)

**Requirements:**
- Python 3.11+ installed
- pytest, pytest-cov, black, isort, flake8, bandit, safety, mypy

**Triggers:**
- `push` to `main` or `develop` with changes in `backend/`
- `pull_request` to `main` or `develop` with changes in `backend/`

---

### 2. **Frontend Tests & Lint** (`.github/workflows/frontend-tests.yml`)

Runs on every push/PR affecting `frontend/` directory.

**Jobs:**
- **Lint** - ESLint and Prettier formatting checks
- **Type Check** - TypeScript type checking
- **Build** - Next.js production build
- **Security** - npm audit vulnerability check
- **Test** - Unit tests (if configured)

**Requirements:**
- Node.js 18+ and npm
- ESLint, Prettier, TypeScript

**Triggers:**
- `push` to `main` or `develop` with changes in `frontend/`
- `pull_request` to `main` or `develop` with changes in `frontend/`

---

### 3. **Database Migrations** (`.github/workflows/db-migrations.yml`)

Validates database schema changes and migrations.

**Jobs:**
- **Migration Check** - Alembic syntax and upgrade/downgrade testing
- **Migration Naming** - Validates migration file naming convention (YYYYMMDD_HHMM_description.py)

**Requirements:**
- PostgreSQL 16 running (Docker service)
- Alembic for migration management

**Triggers:**
- `push` to `main` or `develop` with changes in `backend/alembic/`
- `pull_request` to `main` or `develop` with changes in `backend/alembic/`

---

### 4. **Deploy to Production** (`.github/workflows/deploy.yml`)

Builds and pushes Docker images to container registry.

**Jobs:**
- **Build Backend** - Docker image for FastAPI
- **Build Frontend** - Docker image for Next.js
- **Notify** - Deployment status notification

**Requirements:**
- Docker buildx configured
- Container registry credentials (GitHub Packages)
- `GITHUB_TOKEN` secrets

**Triggers:**
- `push` to `main` branch only
- Manual trigger via `workflow_dispatch`

**Outputs:**
- Backend image: `ghcr.io/[repo]/backend:latest`
- Frontend image: `ghcr.io/[repo]/frontend:latest`

---

### 5. **Code Quality & Coverage** (`.github/workflows/quality.yml`)

Comprehensive code quality analysis and coverage reporting.

**Jobs:**
- **SonarCloud** - Code quality metrics (requires Sonar setup)
- **Code Climate** - Code climate analysis (requires Code Climate setup)
- **Dependency Check** - OWASP dependency vulnerabilities
- **Codecov** - Coverage badge generation

**Requirements:**
- `SONAR_TOKEN` secret (optional)
- `CODE_CLIMATE_REPORTER_ID` secret (optional)
- Codecov account (optional)

**Triggers:**
- `push` to `main` or `develop`
- `pull_request` to `main` or `develop`

---

## Setting Up GitHub Actions Secrets

### Required Secrets

Add these to your GitHub repository under Settings → Secrets and variables → Actions:

1. **`SONAR_TOKEN`** (Optional - for SonarCloud)
   - Get from: https://sonarcloud.io
   - Used for: Code quality scanning
   - Setup: Create a SonarCloud account and generate token

2. **`CODE_CLIMATE_REPORTER_ID`** (Optional - for Code Climate)
   - Get from: https://codeclimate.com
   - Used for: Code coverage reporting
   - Setup: Create a Code Climate account and generate reporter ID

3. **`GITHUB_TOKEN`** (Auto-provided)
   - Used for: GitHub package registry access
   - Note: Automatically provided by GitHub Actions

### How to Add Secrets

1. Go to your repository on GitHub
2. Click Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add secret name and value
5. Click "Add secret"

---

## Local Testing Before Push

### Test Backend

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install black isort flake8 pytest

# Format code
black app/

# Sort imports
isort app/

# Lint
flake8 app/

# Run tests
pytest
```

### Test Frontend

```bash
cd frontend
npm install

# Type check
npm run type-check || true

# Lint
npm run lint || true

# Build
npm run build

# Run tests
npm test
```

### Test Migrations

```bash
cd backend
alembic check
alembic upgrade head
```

---

## Workflow Status & Badges

View workflow status in your README:

```markdown
[![Backend Tests](https://github.com/Archie-ctr/Internship-project/actions/workflows/backend-tests.yml/badge.svg)](https://github.com/Archie-ctr/Internship-project/actions/workflows/backend-tests.yml)
[![Frontend Tests](https://github.com/Archie-ctr/Internship-project/actions/workflows/frontend-tests.yml/badge.svg)](https://github.com/Archie-ctr/Internship-project/actions/workflows/frontend-tests.yml)
[![Database Migrations](https://github.com/Archie-ctr/Internship-project/actions/workflows/db-migrations.yml/badge.svg)](https://github.com/Archie-ctr/Internship-project/actions/workflows/db-migrations.yml)
[![Deploy](https://github.com/Archie-ctr/Internship-project/actions/workflows/deploy.yml/badge.svg)](https://github.com/Archie-ctr/Internship-project/actions/workflows/deploy.yml)
```

---

## Monitoring Workflows

1. Go to your repository
2. Click "Actions" tab
3. View workflow runs and their status
4. Click on a run to see detailed logs
5. Each job shows pass/fail with output

---

## Troubleshooting

### Workflow not triggering?

- Check that files match the `paths` filter
- Ensure branch is `main` or `develop`
- Verify `.yml` file syntax is correct
- Check repository settings → Actions permissions

### Tests failing in CI but passing locally?

- Check Python/Node version differences
- Verify all dependencies are listed
- Check for hardcoded paths/environments
- Review CI logs for detailed error messages

### Coverage not uploading?

- Install Codecov app in your repository
- Add `CODECOV_TOKEN` if needed
- Verify coverage reports are generated
- Check Codecov dashboard for upload status

---

## Best Practices

1. **Run tests locally** before pushing
2. **Keep `.env` out of git** (add to `.gitignore`)
3. **Use feature branches** for development
4. **Require passing checks** before merge
5. **Review workflow logs** for optimization opportunities
6. **Update dependencies regularly** to avoid security issues
7. **Add migration tests** for all schema changes

---

## Next Steps

1. Push workflows to GitHub
2. Configure repository secrets (if using SonarCloud/Code Climate)
3. Enable branch protection rules (require passing checks)
4. View Actions tab to confirm workflows run
5. Add status badges to README.md

For more info: https://docs.github.com/en/actions
