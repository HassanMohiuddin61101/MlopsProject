# Phase 2: Model Management - Implementation Guide

## 🎯 Phase 2 Overview

Phase 2 focuses on **Model Management** using MLflow for experiment tracking, DVC for data versioning, and Dagshub as the remote platform. This phase enables:
- Model versioning and registry
- Experiment tracking and comparison
- Data versioning with DVC
- Model training/retraining workflows
- Model deployment preparation

---

## 📋 Prerequisites

- ✅ Phase 1 Complete (Data ingestion pipeline working)
- ✅ MinIO running and accessible
- ✅ Python virtual environment set up
- ✅ Pre-trained model available (`model/dqn_trend_model_trend.pkl`)

---

## 🛠️ Tools & Technologies

### **MLflow**
- Experiment tracking and logging
- Model registry and versioning
- Model serving preparation

### **DVC (Data Version Control)**
- Data versioning and tracking
- Dataset management
- Integration with MinIO for remote storage

### **Dagshub**
- Remote MLflow tracking server
- DVC remote storage
- Free cloud platform for MLOps

---

## 📦 Step 1: Install Dependencies

### 1.1 Activate Virtual Environment
```powershell
# Activate venv
.\venv\Scripts\Activate.ps1
```

### 1.2 Install Phase 2 Packages
```powershell
# Install MLflow, DVC, and Dagshub
pip install mlflow>=2.9.0
pip install dagshub>=0.3.10
pip install dvc==3.38.1
pip install dvc-s3==3.1.0

# Verify installations
mlflow --version
dvc --version
```

---

## 🔐 Step 2: Setup Dagshub Account

### 2.1 Create Dagshub Account
1. Go to https://dagshub.com
2. Sign up for a free account (GitHub OAuth recommended)
3. Create a new repository (e.g., `mlops-crypto-predictor`)

### 2.2 Get Dagshub Token
1. Go to your Dagshub profile → Settings → Tokens
2. Generate a new token (copy it - you'll need it)
3. Save token securely

### 2.3 Configure Environment Variables
Add to `.env` file:
```env
# Dagshub Configuration
DAGSHUB_USERNAME=your_username
DAGSHUB_REPO=your_repo_name
DAGSHUB_USER_TOKEN=your_token_here

# MLflow Tracking URI (Dagshub)
MLFLOW_TRACKING_URI=https://dagshub.com/your_username/your_repo_name.mlflow
```

---

## 📊 Step 3: Initialize DVC for Data Versioning

### 3.1 Initialize DVC
```powershell
# Initialize DVC in project root
dvc init

# This creates:
# - .dvc/ directory
# - .dvcignore file
# - .dvc/config file
```

### 3.2 Configure DVC Remote (MinIO)
```powershell
# Add MinIO as DVC remote storage
dvc remote add -d minio-remote s3://dvc-data

# Configure MinIO endpoint
dvc remote modify minio-remote endpointurl http://localhost:9000
dvc remote modify minio-remote access_key_id minioadmin
dvc remote modify minio-remote secret_access_key minioadmin

# Verify configuration
dvc remote list
```

### 3.3 Add Data to DVC
```powershell
# Track data directories
dvc add data/raw
dvc add data/processed
dvc add model

# Commit to Git (DVC creates .dvc files)
git add data/raw.dvc data/processed.dvc model.dvc .dvcignore
git commit -m "Add data and model to DVC"
```

### 3.4 Push Data to MinIO
```powershell
# Push data to MinIO remote
dvc push

# Verify data in MinIO
# Check MinIO console: http://localhost:9001
# Look for bucket: dvc-data
```

---

## 🔬 Step 4: Setup MLflow with Dagshub

### 4.1 Configure MLflow Tracking
Create `src/utils/mlflow_config.py`:
```python
"""
MLflow Configuration for Dagshub
"""
import os
import mlflow
from dotenv import load_dotenv

load_dotenv()

def setup_mlflow():
    """
    Configure MLflow to use Dagshub as tracking server
    """
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
        print(f"✅ MLflow tracking URI set to: {tracking_uri}")
    else:
        print("⚠️  MLFLOW_TRACKING_URI not set, using local tracking")
    
    return mlflow
```

### 4.2 Create MLflow Experiment Tracking Module
Create `src/models/train_with_mlflow.py`:
```python
"""
Model Training with MLflow Tracking
Logs experiments, metrics, and models to Dagshub
"""
import mlflow
import mlflow.pytorch
import os
import pickle
import torch
from datetime import datetime
from src.utils.mlflow_config import setup_mlflow

def log_model_to_mlflow(
    model_path: str,
    model_name: str = "dqn_trend_model",
    experiment_name: str = "crypto_trend_prediction",
    metrics: dict = None,
    params: dict = None,
    tags: dict = None
):
    """
    Log trained model to MLflow registry
    
    Args:
        model_path: Path to .pkl model file
        model_name: Model name in registry
        experiment_name: MLflow experiment name
        metrics: Dictionary of metrics to log
        params: Dictionary of hyperparameters
        tags: Dictionary of tags
    """
    # Setup MLflow
    mlflow_client = setup_mlflow()
    
    # Set or create experiment
    mlflow.set_experiment(experiment_name)
    
    with mlflow.start_run():
        # Log parameters
        if params:
            mlflow.log_params(params)
        
        # Log metrics
        if metrics:
            mlflow.log_metrics(metrics)
        
        # Log tags
        if tags:
            mlflow.set_tags(tags)
        
        # Log model artifact
        mlflow.log_artifact(model_path, "models")
        
        # Log model as PyTorch model (if applicable)
        # Note: For .pkl files, we log as artifact
        artifact_path = f"models/{os.path.basename(model_path)}"
        mlflow.log_artifact(model_path, artifact_path)
        
        # Register model (optional - for model registry)
        # mlflow.register_model(f"runs:/{mlflow.active_run().info.run_id}/{artifact_path}", model_name)
        
        print(f"✅ Model logged to MLflow")
        print(f"   Run ID: {mlflow.active_run().info.run_id}")
        print(f"   Experiment: {experiment_name}")
        
        return mlflow.active_run().info.run_id
```

---

## 🔄 Step 5: Integrate MLflow into Training Workflow

### 5.1 Create Training DAG Task
Add to `dags/binance_etl_dag.py` or create new `dags/model_training_dag.py`:

```python
"""
Model Training DAG with MLflow Integration
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

from models.train_with_mlflow import log_model_to_mlflow

default_args = {
    'owner': 'mlops-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'model_training_mlflow',
    default_args=default_args,
    description='Train and log model to MLflow',
    schedule_interval=None,  # Manual trigger
    catchup=False,
    tags=['mlflow', 'training'],
)

def train_and_log_task(**context):
    """Train model and log to MLflow"""
    model_path = "model/dqn_trend_model_trend.pkl"
    
    # Example metrics (replace with actual training metrics)
    metrics = {
        "accuracy": 0.85,
        "precision": 0.82,
        "recall": 0.88,
        "f1_score": 0.85
    }
    
    # Example parameters
    params = {
        "architecture": "8-8",
        "input_features": 7,
        "output_actions": 2,
        "learning_rate": 0.001,
        "batch_size": 32
    }
    
    # Tags
    tags = {
        "model_type": "DQN",
        "task": "trend_prediction",
        "data_source": "binance"
    }
    
    # Log to MLflow
    run_id = log_model_to_mlflow(
        model_path=model_path,
        model_name="dqn_trend_model",
        experiment_name="crypto_trend_prediction",
        metrics=metrics,
        params=params,
        tags=tags
    )
    
    return run_id

train_task = PythonOperator(
    task_id='train_and_log_model',
    python_callable=train_and_log_task,
    dag=dag,
)
```

---

## 📈 Step 6: Create Model Registry Utilities

### 6.1 Create Model Registry Module
Create `src/models/registry.py`:

```python
"""
Model Registry Utilities
Manage model versions and deployments
"""
import mlflow
import os
from dotenv import load_dotenv
from src.utils.mlflow_config import setup_mlflow

load_dotenv()

def get_latest_model(model_name: str = "dqn_trend_model", stage: str = "Production"):
    """
    Get latest model from MLflow registry
    
    Args:
        model_name: Name of model in registry
        stage: Model stage (Production, Staging, Archived)
    
    Returns:
        Model artifact path
    """
    mlflow_client = setup_mlflow()
    
    try:
        # Get latest model version
        client = mlflow.tracking.MlflowClient()
        latest_version = client.get_latest_versions(model_name, stages=[stage])
        
        if latest_version:
            model_uri = f"models:/{model_name}/{stage}"
            print(f"✅ Found model: {model_uri}")
            return model_uri
        else:
            print(f"⚠️  No model found in {stage} stage")
            return None
    except Exception as e:
        print(f"❌ Error getting model: {str(e)}")
        return None

def promote_model_to_stage(
    model_name: str,
    version: int,
    stage: str = "Production"
):
    """
    Promote model version to a stage
    
    Args:
        model_name: Model name
        version: Model version number
        stage: Target stage (Production, Staging, Archived)
    """
    try:
        client = mlflow.tracking.MlflowClient()
        client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=stage
        )
        print(f"✅ Model {model_name} v{version} promoted to {stage}")
    except Exception as e:
        print(f"❌ Error promoting model: {str(e)}")
        raise
```

---

## 🔗 Step 7: Integrate DVC with Data Pipeline

### 7.1 Update ETL DAG to Version Data
Modify `dags/binance_etl_dag.py` to add DVC versioning task:

```python
# Add after upload_to_minio task
def version_data_task(**context):
    """Version processed data with DVC"""
    import subprocess
    
    # Add new data to DVC
    subprocess.run(["dvc", "add", "data/processed"], check=True)
    
    # Commit DVC files
    subprocess.run(["git", "add", "data/processed.dvc", ".gitignore"], check=True)
    
    # Push to MinIO
    subprocess.run(["dvc", "push"], check=True)
    
    print("✅ Data versioned with DVC")

version_task = PythonOperator(
    task_id='version_data_with_dvc',
    python_callable=version_data_task,
    dag=dag,
)

# Update task dependencies
upload_task >> version_task
```

---

## 🧪 Step 8: Test MLflow Integration

### 8.1 Test MLflow Connection
```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Test MLflow connection
python -c "import mlflow; from src.utils.mlflow_config import setup_mlflow; mlflow_client = setup_mlflow(); print('✅ MLflow connected')"
```

### 8.2 Test Model Logging
```powershell
# Test logging model to MLflow
python -c "
from src.models.train_with_mlflow import log_model_to_mlflow
log_model_to_mlflow(
    model_path='model/dqn_trend_model_trend.pkl',
    model_name='dqn_trend_model',
    metrics={'test_accuracy': 0.85},
    params={'architecture': '8-8'}
)
"
```

### 8.3 Verify in Dagshub
1. Go to your Dagshub repository
2. Navigate to "Experiments" tab
3. You should see your MLflow experiments
4. Click on a run to see metrics, parameters, and artifacts

---

## 📝 Step 9: Create Model Comparison Script

### 9.1 Create Comparison Utility
Create `src/models/compare_models.py`:

```python
"""
Model Comparison Utility
Compare different model versions and experiments
"""
import mlflow
from src.utils.mlflow_config import setup_mlflow

def compare_experiments(experiment_name: str, metric: str = "accuracy"):
    """
    Compare runs in an experiment
    
    Args:
        experiment_name: Name of MLflow experiment
        metric: Metric to compare
    """
    mlflow_client = setup_mlflow()
    
    # Get experiment
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if not experiment:
        print(f"❌ Experiment '{experiment_name}' not found")
        return
    
    # Get all runs
    client = mlflow.tracking.MlflowClient()
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=[f"metrics.{metric} DESC"]
    )
    
    print(f"\n📊 Top 5 Runs by {metric}:")
    print("-" * 80)
    
    for i, run in enumerate(runs[:5], 1):
        print(f"\n{i}. Run ID: {run.info.run_id}")
        print(f"   {metric}: {run.data.metrics.get(metric, 'N/A')}")
        print(f"   Parameters: {run.data.params}")
        print(f"   Status: {run.info.status}")
    
    return runs

if __name__ == "__main__":
    compare_experiments("crypto_trend_prediction", "accuracy")
```

---

## 🚀 Step 10: Setup Complete Workflow

### 10.1 Create Combined DAG
Create `dags/complete_mlops_dag.py` that combines:
- Data ingestion (from Phase 1)
- Data versioning (DVC)
- Model training/logging (MLflow)
- Model registry updates

### 10.2 Environment Setup Script
Create `scripts/setup_phase2.sh` (or `.ps1` for PowerShell):

```powershell
# Setup Phase 2 Environment
# Activate venv
.\venv\Scripts\Activate.ps1

# Initialize DVC
dvc init

# Configure DVC remote
dvc remote add -d minio-remote s3://dvc-data
dvc remote modify minio-remote endpointurl http://localhost:9000
dvc remote modify minio-remote access_key_id minioadmin
dvc remote modify minio-remote secret_access_key minioadmin

# Verify setup
dvc remote list
mlflow --version
```

---

## ✅ Phase 2 Checklist

- [ ] Dagshub account created and repository set up
- [ ] DVC initialized and configured with MinIO
- [ ] MLflow tracking URI configured (Dagshub)
- [ ] Model logging module created
- [ ] Model registry utilities created
- [ ] DVC integrated into data pipeline
- [ ] MLflow experiments visible in Dagshub
- [ ] Model comparison script working
- [ ] Training DAG created and tested

---

## 📊 Expected Results

After completing Phase 2, you should have:

1. **DVC Setup**
   - Data versioned in MinIO (`dvc-data` bucket)
   - `.dvc` files tracking data versions
   - Ability to checkout different data versions

2. **MLflow Integration**
   - Experiments tracked in Dagshub
   - Models logged with metrics and parameters
   - Model registry with versioning
   - Comparison tools for model selection

3. **Workflow Integration**
   - Automated model logging from training
   - Data versioning in ETL pipeline
   - Model registry for deployment

---

## 🔍 Verification Commands

```powershell
# Check DVC status
dvc status

# List DVC remotes
dvc remote list

# Check MLflow experiments
python -c "import mlflow; print(mlflow.list_experiments())"

# View Dagshub experiments
# Go to: https://dagshub.com/your_username/your_repo_name/experiments
```

---

## 🎯 Next Steps (Phase 3)

Phase 2 provides the foundation for:
- **Phase 3**: CI/CD Pipeline (GitHub Actions, CML)
- **Phase 4**: Monitoring & Observability (Prometheus, Grafana)

---

## 📝 Notes

- Dagshub provides free MLflow tracking (no local MLflow server needed)
- DVC uses MinIO for data versioning (local storage)
- Model artifacts are stored in Dagshub (MLflow artifacts)
- All experiments are tracked and searchable in Dagshub UI

---

**Phase 2 Status**: 🚀 **READY TO START**

