# Push BizReg Project to GitHub

This guide walks through setting up and pushing your project to GitHub.

## Step 1: Configure Git Locally

```powershell
# Navigate to project root
cd "c:\Users\archi\OneDrive\Desktop\Internship Project"

# Set your git user (if not already configured)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Verify git is initialized
git status
```

## Step 2: Add Remote Repository

```powershell
# Add your GitHub repository as remote
git remote add origin https://github.com/Archie-ctr/Internship-project.git

# Verify remote was added
git remote -v
```

If remote already exists, update it:
```powershell
git remote set-url origin https://github.com/Archie-ctr/Internship-project.git
```

## Step 3: Stage All Files

```powershell
# Add all files
git add .

# Review what will be committed
git status

# Or check specific files
git diff --cached --name-only
```

## Step 4: Create Initial Commit

```powershell
git commit -m "Initial commit: Day 1 - Project architecture and scaffolding

- Add comprehensive Day 1 analysis document
- Add architecture diagrams (12 Mermaid diagrams)
- Configure GitHub Actions CI/CD pipelines
  - Backend: Python linting, security, testing
  - Frontend: TypeScript, build, security checks
  - Database: Alembic migration validation
  - Deployment: Docker image building
  - Quality: SonarCloud, Code Climate, OWASP checks
- Add workflow documentation
- Configure .gitignore for Python and Node.js

Phase 1 Status:
✅ Project scaffolding
✅ System architecture documented
✅ CI/CD pipelines configured
✅ Development environment ready"
```

## Step 5: Create or Switch to Main Branch

```powershell
# Check current branch
git branch

# If not on main, create or switch to main
git checkout -b main
# or
git checkout main

# Set main as default branch for push
git branch -M main
```

## Step 6: Push to GitHub

```powershell
# Push to GitHub (first time)
git push -u origin main

# For subsequent pushes
git push origin main
```

**Expected output:**
```
Enumerating objects: XX, done.
Counting objects: 100% (XX/XX), done.
Delta compression using up to 8 threads
Compressing objects: 100% (XX/XX), done.
Writing objects: 100% (XX/XX), X.XXX MiB | X.XXX MiB/s
Creating branch references/heads/main
remote: Resolving deltas: 100% (XX/XX), done
remote: 
remote: Create a pull request for 'main' on GitHub by visiting:
remote:      https://github.com/Archie-ctr/Internship-project/pull/new/main
remote:
To https://github.com/Archie-ctr/Internship-project.git
 * [new branch]      main -> main
Branch 'main' is set up to track 'origin/main'.
```

## Step 7: Verify on GitHub

1. Go to https://github.com/Archie-ctr/Internship-project
2. Verify all files are pushed
3. Check Actions tab to see workflows
4. Review commits in the Commits tab

## Step 8: Configure Repository Settings

### Branch Protection (Optional but Recommended)

1. Go to Settings → Branches
2. Add rule for `main` branch
3. Enable:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
     - Select: `backend-tests`, `frontend-tests`, `db-migrations`
   - ✅ Require branches to be up to date before merging
   - ✅ Require code reviews before merging (set to 1)

### Enable GitHub Actions

1. Go to Settings → Actions
2. Ensure "All actions and reusable workflows" is selected
3. Allow all actions

### Configure Secrets (for Quality Workflows)

Go to Settings → Secrets and variables → Actions

Optional secrets:
- `SONAR_TOKEN` - For SonarCloud analysis
- `CODE_CLIMATE_REPORTER_ID` - For Code Climate reporting
- `CODECOV_TOKEN` - For Codecov integration (if needed)

## Step 9: Create Development Branch

```powershell
# Create feature branch for Phase 2
git checkout -b phase-2-database

# Make your changes...

# When ready, push feature branch
git push -u origin phase-2-database

# Create Pull Request on GitHub
# Then merge to main after checks pass
```

## Common Git Commands

```powershell
# Check status
git status

# View recent commits
git log --oneline -10

# View changes
git diff

# Stage specific file
git add backend/requirements.txt

# Unstage file
git reset HEAD frontend/package.json

# Commit with message
git commit -m "Descriptive commit message"

# Push to remote
git push origin main

# Pull latest changes
git pull origin main

# Create new branch
git checkout -b new-feature-branch

# Delete branch
git branch -d branch-name

# View all branches
git branch -a

# Merge branch
git checkout main
git merge feature-branch

# Rebase (advanced)
git rebase main

# View git config
git config --global --list
```

## Workflow for New Phases

1. **Create feature branch**
   ```powershell
   git checkout -b phase-X-description
   ```

2. **Make changes** (development work)

3. **Commit regularly**
   ```powershell
   git add .
   git commit -m "Phase X: Descriptive message"
   ```

4. **Push to GitHub**
   ```powershell
   git push origin phase-X-description
   ```

5. **Create Pull Request** on GitHub

6. **GitHub Actions runs** (automated checks)

7. **Review and merge** (after tests pass)

8. **Delete feature branch**
   ```powershell
   git branch -d phase-X-description
   git push origin --delete phase-X-description
   ```

## Troubleshooting

### "fatal: not a git repository"
```powershell
# Initialize git if needed
git init

# Then add remote
git remote add origin https://github.com/Archie-ctr/Internship-project.git
```

### "Permission denied (publickey)"
- Set up SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
- Or use HTTPS with Personal Access Token

### "The remote repository is not empty"
- You can still push: `git push -u origin main --force` (use with caution)
- Or clone existing repo: `git clone https://github.com/Archie-ctr/Internship-project.git`

### "Updates were rejected"
```powershell
# Fetch latest changes
git fetch origin

# Rebase your changes
git rebase origin/main

# Then push
git push origin main
```

## Next Steps

After pushing to GitHub:

1. ✅ Monitor GitHub Actions for workflow execution
2. ✅ Fix any failing tests/checks
3. ✅ Add status badges to README.md
4. ✅ Plan Phase 2 work
5. ✅ Share repository link with team

---

**Repository**: https://github.com/Archie-ctr/Internship-project  
**GitHub Actions**: https://github.com/Archie-ctr/Internship-project/actions
