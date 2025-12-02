# Phase 3: CI/CD Pipeline - Implementation Guide

## 🎯 Phase 3 Overview

Phase 3 focuses on **Continuous Integration and Continuous Deployment (CI/CD)** using GitHub Actions and CML (Continuous Machine Learning). This phase enables:
- Automated code quality checks
- Automated model training and comparison
- Model deployment pipelines
- Pull request-based workflows
- CML reports for model comparison

---

## 📋 Prerequisites

- ✅ Phase 1 Complete (Data ingestion pipeline)
- ✅ Phase 2 Complete (MLflow & DVC setup)
- ✅ GitHub repository created
- ✅ Git initialized locally
- ✅ Dagshub credentials configured

---

## 🛠️ Tools & Technologies

### **GitHub Actions**
- CI/CD automation
- Workflow orchestration
- Automated testing and deployment

### **CML (Continuous Machine Learning)**
- Model comparison reports
- ML experiment tracking in PRs
- Automated model evaluation

### **Git Branching Strategy**
- `feature` → `dev` → `test` → `master`
- Branch protection rules
- PR-based workflows

---

## 📦 Step 1: Setup Git Repository

### 1.1 Initialize Git (if not done)
```powershell
# Check if Git is initialized
git status

# If not initialized, run:
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

# Or if using SSH
git remote add origin git@github.com:your-username/your-repo.git
```

---

## 🔐 Step 2: Setup GitHub Secrets

### 2.1 Required Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add the following secrets:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `DAGSHUB_USER_TOKEN` | Dagshub API token | `e9be20dbbb...` |
| `DAGSHUB_USERNAME` | Dagshub username | `HassanMohiuddin61101` |
| `MLFLOW_TRACKING_URI` | MLflow tracking URI | `https://dagshub.com/.../repo.mlflow` |
| `MINIO_ENDPOINT` | MinIO endpoint | `localhost:9000` (or your MinIO URL) |
| `MINIO_ACCESS_KEY` | MinIO access key | `minioadmin` |
| `MINIO_SECRET_KEY` | MinIO secret key | `minioadmin` |
| `DOCKER_USERNAME` | Docker Hub username (optional) | `your-username` |
| `DOCKER_PASSWORD` | Docker Hub password (optional) | `your-password` |

### 2.2 How to Add Secrets

1. Go to: `https://github.com/your-username/your-repo/settings/secrets/actions`
2. Click "New repository secret"
3. Add each secret with its value
4. Click "Add secret"

---

## 🔄 Step 3: Create GitHub Actions Workflows

### 3.1 CI Workflow: Feature → Dev

**Purpose:** Code quality checks, linting, and basic tests

**File:** `.github/workflows/ci-feature-to-dev.yml`

### 3.2 CI Workflow: Dev → Test (Model Retraining)

**Purpose:** Retrain model, compare with production, generate CML report

**File:** `.github/workflows/ci-dev-to-test.yml`

### 3.3 CD Workflow: Test → Master (Production Deployment)

**Purpose:** Build Docker image, deploy model, verify deployment

**File:** `.github/workflows/cd-test-to-master.yml`

---

## 📊 Step 4: Setup CML Integration

### 4.1 Install CML
```powershell
.\venv\Scripts\Activate.ps1
pip install cml
```

### 4.2 Create Model Comparison Script

**File:** `scripts/compare_models_cml.py`

This script will:
- Load current and production models
- Compare metrics
- Generate comparison report
- Output for CML

---

## 🚀 Step 5: Create FastAPI Service

### 5.1 FastAPI Application

**File:** `src/api/main.py`

- REST API for model predictions
- Health check endpoint
- Prometheus metrics
- Model loading from MLflow

### 5.2 Dockerfile for API

**File:** `Dockerfile.api`

- Multi-stage build
- Optimized for production
- Includes model and dependencies

---

## ✅ Phase 3 Checklist

- [ ] Git repository initialized and branches created
- [ ] GitHub repository created and remote added
- [ ] GitHub secrets configured
- [ ] CI workflow for feature → dev created
- [ ] CI workflow for dev → test (with CML) created
- [ ] CD workflow for test → master created
- [ ] CML comparison script created
- [ ] FastAPI service created
- [ ] Dockerfile for API created
- [ ] Branch protection rules configured

---

## 📝 Expected Workflows

### Workflow 1: Feature → Dev
1. Developer creates feature branch
2. Opens PR to `dev`
3. GitHub Actions runs:
   - Code linting (pylint, black)
   - Unit tests
   - Code quality checks
4. PR approved → merged to `dev`

### Workflow 2: Dev → Test
1. PR from `dev` to `test`
2. GitHub Actions runs:
   - Trigger model retraining
   - Compare new model with production
   - Generate CML report in PR
3. PR approved → merged to `test`

### Workflow 3: Test → Master
1. PR from `test` to `master`
2. GitHub Actions runs:
   - Fetch model from MLflow
   - Build Docker image
   - Push to Docker Hub
   - Deploy and verify
3. PR approved → merged to `master` (production)

---

## 🔍 Verification

### Test CI Workflow
```powershell
# Create a test branch
git checkout -b feature/test-ci
git add .
git commit -m "Test CI workflow"
git push origin feature/test-ci

# Create PR to dev branch on GitHub
# Watch Actions tab for workflow execution
```

### Test CML Integration
```powershell
# Run CML comparison locally
python scripts/compare_models_cml.py
```

---

## 🎯 Next Steps (Phase 4)

Phase 3 provides the foundation for:
- **Phase 4**: Monitoring & Observability (Prometheus, Grafana)
- Production deployment
- Model serving infrastructure

---

**Phase 3 Status**: 🚀 **READY TO START**

