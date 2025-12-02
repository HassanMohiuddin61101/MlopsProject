# GitHub Repository Setup - Step by Step

## 🎯 Your Repository
**URL**: https://github.com/HassanMohiuddin61101/MlopsProject.git

---

## 📋 Step 1: Connect Local Repository to GitHub

### 1.1 Check Current Git Status
```powershell
# Check if Git is initialized
git status

# Check remote (if any)
git remote -v
```

### 1.2 Add GitHub Remote
```powershell
# Add remote (if not already added)
git remote add origin https://github.com/HassanMohiuddin61101/MlopsProject.git

# Or update if exists
git remote set-url origin https://github.com/HassanMohiuddin61101/MlopsProject.git

# Verify
git remote -v
```

---

## 🌿 Step 2: Create Branching Strategy

### 2.1 Create Branches
```powershell
# Make sure you're on main/master
git checkout -b main  # or master, depending on your default

# Create dev branch
git checkout -b dev

# Create test branch
git checkout -b test

# Go back to main
git checkout main
```

### 2.2 Push All Branches
```powershell
# Push main branch
git push -u origin main

# Push dev branch
git checkout dev
git push -u origin dev

# Push test branch
git checkout test
git push -u origin test

# Set dev as default working branch
git checkout dev
```

---

## 📦 Step 3: Stage and Commit All Files

### 3.1 Add All Files
```powershell
# Make sure you're on dev branch
git checkout dev

# Add all files (except those in .gitignore)
git add .

# Check what will be committed
git status
```

### 3.2 Commit Changes
```powershell
# Commit all Phase 1, 2, and 3 work
git commit -m "Initial commit: Complete MLOps pipeline

- Phase 1: Data ingestion with Airflow and MinIO
- Phase 2: Model management with MLflow, DVC, and Dagshub
- Phase 3: CI/CD pipeline with GitHub Actions and CML
- FastAPI service for model predictions
- Docker configuration for deployment"
```

### 3.3 Push to GitHub
```powershell
# Push to dev branch
git push -u origin dev
```

---

## 🔐 Step 4: Setup GitHub Secrets

### 4.1 Go to Repository Settings
1. Navigate to: https://github.com/HassanMohiuddin61101/MlopsProject/settings/secrets/actions
2. Click "New repository secret"

### 4.2 Add Required Secrets

Add these secrets one by one:

| Secret Name | Value | Where to Get |
|------------|-------|--------------|
| `DAGSHUB_USER_TOKEN` | `e9be20dbbb000e4c37dc7a9ae1b1b604b1743a9f` | From `toke.txt` |
| `DAGSHUB_USERNAME` | `HassanMohiuddin61101` | Your Dagshub username |
| `MLFLOW_TRACKING_URI` | `https://dagshub.com/HassanMohiuddin61101/my-first-repo.mlflow` | From `.env` |
| `MINIO_ENDPOINT` | `localhost:9000` | Your MinIO endpoint |
| `MINIO_ACCESS_KEY` | `minioadmin` | MinIO access key |
| `MINIO_SECRET_KEY` | `minioadmin` | MinIO secret key |

**Optional Secrets** (for Docker Hub):
- `DOCKER_USERNAME` - Your Docker Hub username
- `DOCKER_PASSWORD` - Your Docker Hub password

### 4.3 Verify Secrets
- Go to: https://github.com/HassanMohiuddin61101/MlopsProject/settings/secrets/actions
- You should see all secrets listed

---

## 🧪 Step 5: Test CI/CD Workflows

### 5.1 Create a Test Feature Branch
```powershell
# Create feature branch from dev
git checkout dev
git checkout -b feature/test-ci

# Make a small change (add a comment to any file)
# For example, add a comment to README or any Python file

# Commit and push
git add .
git commit -m "Test CI workflow"
git push -u origin feature/test-ci
```

### 5.2 Create Pull Request
1. Go to: https://github.com/HassanMohiuddin61101/MlopsProject/pulls
2. Click "New Pull Request"
3. Select: `feature/test-ci` → `dev`
4. Click "Create Pull Request"
5. Watch the "Checks" tab for workflow execution

### 5.3 Verify Workflow Runs
- Go to: https://github.com/HassanMohiuddin61101/MlopsProject/actions
- You should see "CI - Feature to Dev" workflow running
- Wait for it to complete (should show green checkmark)

---

## 📊 Step 6: Test Model Retraining Workflow

### 6.1 Create PR from Dev to Test
```powershell
# Make sure you're on dev
git checkout dev

# Create a branch for test
git checkout -b test/test-model-retraining

# Make a small change
# Commit and push
git add .
git commit -m "Test model retraining workflow"
git push -u origin test/test-model-retraining
```

### 6.2 Create PR
1. Go to: https://github.com/HassanMohiuddin61101/MlopsProject/pulls
2. Create PR: `test/test-model-retraining` → `test`
3. Watch for CML report in PR comments

---

## ✅ Verification Checklist

- [ ] Git remote added and verified
- [ ] All branches created (main, dev, test)
- [ ] Code committed and pushed to dev
- [ ] GitHub secrets configured
- [ ] Test PR created to dev
- [ ] CI workflow runs successfully
- [ ] Ready for production use

---

## 🚀 Quick Commands Summary

```powershell
# 1. Setup remote
git remote add origin https://github.com/HassanMohiuddin61101/MlopsProject.git

# 2. Create branches
git checkout -b main
git checkout -b dev
git checkout -b test

# 3. Commit and push
git checkout dev
git add .
git commit -m "Initial commit: Complete MLOps pipeline"
git push -u origin dev

# 4. Push all branches
git push -u origin main
git push -u origin test
```

---

## 📝 Next Steps After Setup

1. **Configure Branch Protection** (Optional but recommended):
   - Go to: Settings → Branches
   - Add protection rules for `test` and `main` branches
   - Require PR reviews before merging

2. **Test Complete Pipeline**:
   - Create feature → dev PR
   - Create dev → test PR (with CML report)
   - Create test → main PR (deployment)

3. **Monitor Workflows**:
   - Check Actions tab regularly
   - Fix any workflow errors
   - Optimize workflow performance

---

## 🔍 Troubleshooting

### Remote Already Exists
```powershell
# Remove and re-add
git remote remove origin
git remote add origin https://github.com/HassanMohiuddin61101/MlopsProject.git
```

### Push Fails
```powershell
# Pull first (if repo has content)
git pull origin main --allow-unrelated-histories

# Then push
git push -u origin dev
```

### Workflow Not Triggering
- Check branch names match workflow triggers
- Verify file paths in workflow `paths:` section
- Check GitHub Actions tab for errors

---

**Ready to push your code!** 🚀

