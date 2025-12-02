# Phase 3: CI/CD Pipeline - Commands and Setup

## 🎯 Phase 3 Overview

Phase 3 sets up **Continuous Integration and Continuous Deployment (CI/CD)** using GitHub Actions and CML.

---

## ✅ Step 1: Setup Git Repository

### 1.1 Check Git Status
```powershell
# Check if Git is initialized
git status

# If not initialized, initialize it
git init
```

### 1.2 Create Branching Strategy
```powershell
# Create branches
git checkout -b dev
git checkout -b test
git checkout -b master

# Set default branch to dev
git checkout dev
```

### 1.3 Add Remote Repository
```powershell
# Add GitHub remote (replace with your repo URL)
git remote add origin https://github.com/your-username/your-repo.git

# Verify remote
git remote -v
```

---

## 🔐 Step 2: Setup GitHub Secrets

### 2.1 Go to GitHub Repository Settings

1. Navigate to: `https://github.com/your-username/your-repo/settings/secrets/actions`
2. Click "New repository secret"
3. Add each secret:

| Secret Name | Value | How to Get |
|------------|-------|------------|
| `DAGSHUB_USER_TOKEN` | Your Dagshub token | From `toke.txt` or Dagshub settings |
| `DAGSHUB_USERNAME` | `HassanMohiuddin61101` | Your Dagshub username |
| `MLFLOW_TRACKING_URI` | `https://dagshub.com/HassanMohiuddin61101/my-first-repo.mlflow` | From `.env` |
| `MINIO_ENDPOINT` | `localhost:9000` | Your MinIO endpoint |
| `MINIO_ACCESS_KEY` | `minioadmin` | MinIO access key |
| `MINIO_SECRET_KEY` | `minioadmin` | MinIO secret key |
| `DOCKER_USERNAME` | (Optional) | Docker Hub username |
| `DOCKER_PASSWORD` | (Optional) | Docker Hub password |

### 2.2 Verify Secrets
```powershell
# Secrets are stored in GitHub, not locally
# You can verify they exist in GitHub UI
```

---

## 📦 Step 3: Install CML

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Install CML
pip install cml

# Verify installation
cml --version
```

---

## 🧪 Step 4: Test Scripts Locally

### 4.1 Test Model Comparison Script
```powershell
.\venv\Scripts\Activate.ps1
python scripts/compare_models_cml.py
```

### 4.2 Test Model Fetch Script
```powershell
.\venv\Scripts\Activate.ps1
python scripts/fetch_model_from_mlflow.py
```

### 4.3 Test FastAPI Service
```powershell
.\venv\Scripts\Activate.ps1
python -m uvicorn src.api.main:app --reload

# In another terminal, test the API
curl http://localhost:8000/health
curl http://localhost:8000/metrics
```

---

## 🚀 Step 5: Test CI/CD Workflows

### 5.1 Commit and Push Code
```powershell
# Add all files
git add .

# Commit
git commit -m "Add Phase 3: CI/CD pipeline setup"

# Push to dev branch
git push origin dev
```

### 5.2 Create Test PR

1. **Create a feature branch:**
```powershell
git checkout -b feature/test-ci
# Make a small change (e.g., add a comment)
git add .
git commit -m "Test CI workflow"
git push origin feature/test-ci
```

2. **Create PR on GitHub:**
   - Go to your GitHub repository
   - Click "New Pull Request"
   - Select `feature/test-ci` → `dev`
   - Create PR
   - Watch the Actions tab for workflow execution

### 5.3 Test Model Retraining Workflow

1. **Create PR from dev to test:**
```powershell
git checkout dev
git checkout -b test/test-model-retraining
# Make changes
git add .
git commit -m "Test model retraining workflow"
git push origin test/test-model-retraining
```

2. **Create PR on GitHub:**
   - Create PR: `test/test-model-retraining` → `test`
   - Watch for CML report in PR comments

---

## 🐳 Step 6: Test Docker Build

### 6.1 Build Docker Image Locally
```powershell
docker build -f Dockerfile.api -t mlops-api:test .
```

### 6.2 Run Docker Container
```powershell
docker run -d -p 8000:8000 --name mlops-api-test mlops-api:test
```

### 6.3 Test API
```powershell
# Health check
curl http://localhost:8000/health

# Metrics
curl http://localhost:8000/metrics

# Stop container
docker stop mlops-api-test
docker rm mlops-api-test
```

---

## 📊 Step 7: Verify Workflows

### 7.1 Check Workflow Files
```powershell
# List workflow files
Get-ChildItem .github\workflows\

# Verify syntax (optional)
# GitHub Actions will validate on push
```

### 7.2 View Workflow Runs
- Go to: `https://github.com/your-username/your-repo/actions`
- You should see workflow runs for each PR

---

## 🔍 Troubleshooting

### Workflow Not Triggering
- Check branch names match workflow triggers
- Verify file paths in workflow `paths:` match your changes
- Check GitHub Actions tab for errors

### CML Report Not Appearing
- Verify `REPO_TOKEN` secret is set (usually `GITHUB_TOKEN` is automatic)
- Check CML script runs successfully
- Verify MLflow credentials are correct

### Docker Build Fails
- Check Dockerfile syntax
- Verify all dependencies in `requirements.txt`
- Check model files exist in `model/` directory

### Model Loading Fails
- Verify model file exists: `model/dqn_trend_model_trend.pkl`
- Check model path in `src/models/predict.py`
- Verify PyTorch is installed

---

## 📝 Next Steps

1. ✅ Setup Git repository and branches
2. ✅ Configure GitHub secrets
3. ✅ Install CML
4. ✅ Test scripts locally
5. ✅ Create test PRs
6. ✅ Verify workflows run successfully
7. ⏭️ **Phase 4**: Monitoring & Observability

---

## 🎉 Phase 3 Checklist

- [ ] Git repository initialized
- [ ] Branches created (dev, test, master)
- [ ] GitHub remote added
- [ ] GitHub secrets configured
- [ ] CML installed
- [ ] Workflow files created
- [ ] Scripts tested locally
- [ ] Test PRs created
- [ ] Workflows verified
- [ ] Docker build tested

---

**Phase 3 Status**: 🚀 **SETUP COMPLETE - READY TO TEST**

