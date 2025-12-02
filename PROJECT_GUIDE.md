# MLOps Real-Time Predictive System - Implementation Guide

## Project Overview
Building a Real-Time Predictive System (RPS) for cryptocurrency volatility prediction using Binance API, with full MLOps pipeline automation.

**Status:**
- ✅ Trained PKL model ready
- ✅ Binance API selected and configured
- ✅ MinIO selected for storage

---

## Phase I: Problem Definition and Data Ingestion

### Step 1: Project Setup

#### 1.1 Initialize Project Structure
```bash
# Create project directory structure
mkdir -p src/{data,models,utils,api}
mkdir -p dags
mkdir -p tests
mkdir -p docker
mkdir -p monitoring/{prometheus,grafana}
mkdir -p .github/workflows
```

#### 1.2 Install Required Applications

**Python Environment:**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core dependencies
pip install pandas numpy scikit-learn
pip install apache-airflow
pip install mlflow dagshub
pip install dvc dvc-s3  # For MinIO integration
pip install fastapi uvicorn prometheus-client
pip install python-binance  # Binance API client
pip install minio  # MinIO Python client
pip install pandas-profiling  # For data quality reports
```

**Docker:**
- Install Docker Desktop: https://www.docker.com/products/docker-desktop

**MinIO:**
```bash
# Run MinIO locally using Docker
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  --name minio \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  minio/minio server /data --console-address ":9001"
```

**Apache Airflow (Option 1 - Local Setup):**
```bash
# Initialize Airflow
export AIRFLOW_HOME=$(pwd)/airflow
airflow db init
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password admin

# Start Airflow (in separate terminals)
airflow webserver --port 8080
airflow scheduler
```

**Apache Airflow (Option 2 - Astronomer Cloud - Recommended):**
Astronomer provides a managed Airflow platform that simplifies deployment and scaling.

1. **Create Astronomer Account:**
   - Go to https://www.astronomer.io/
   - Sign up for a free account (Astronomer Cloud)
   - Create a new workspace

2. **Install Astronomer CLI:**
```bash
# Install Astronomer CLI
curl -sSL install.astronomer.io | sudo bash

# Or using pip
pip install astronomer-cli

# Verify installation
astro version
```

3. **Login to Astronomer:**
```bash
# Login to your Astronomer account
astro auth login

# Or set up authentication token
export ASTRONOMER_API_TOKEN=your_token_here
```

4. **Initialize Astronomer Project:**
```bash
# Initialize Astronomer project in your repo
astro dev init

# This creates:
# - .astro/ directory with config
# - Dockerfile for custom image
# - requirements.txt for Python packages
# - dags/ folder (if not exists)
```

5. **Configure Dependencies:**
**File: `requirements.txt` (in project root or .astro/):**
```txt
pandas
numpy
scikit-learn
python-binance
minio
pandas-profiling
mlflow
dagshub
dvc
dvc-s3
```

6. **Deploy to Astronomer:**
```bash
# Deploy DAGs to Astronomer Cloud
astro deploy

# Or deploy to local Astronomer environment
astro dev start  # Starts local Airflow with Astronomer runtime
```

7. **Access Astronomer UI:**
   - Local: http://localhost:8080 (admin/admin)
   - Cloud: Access via Astronomer Cloud dashboard

**Benefits of Astronomer:**
- ✅ Managed infrastructure (no need to maintain Airflow servers)
- ✅ Automatic scaling and resource management
- ✅ Built-in monitoring and logging
- ✅ Easy DAG deployment via CLI
- ✅ Integration with cloud providers (AWS, GCP, Azure)
- ✅ Free tier available for development

**Note:** Dagshub remains separate and is used for MLflow tracking and DVC remote storage, not for Airflow.

---

### Step 2: Data Ingestion with Apache Airflow

#### 2.1 Create Data Extraction Script

**File: `src/data/extract.py`**
```python
from binance.client import Client
import pandas as pd
from datetime import datetime
import os

def extract_binance_data(symbol='BTCUSDT', interval='1h', limit=100):
    """
    Extract data from Binance API
    """
    client = Client()  # Use your API keys from environment variables
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_volume', 'trades', 'taker_buy_base',
        'taker_buy_quote', 'ignore'
    ])
    
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['collection_time'] = datetime.now()
    
    # Save raw data with timestamp
    output_path = f"data/raw/binance_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    return df, output_path
```

#### 2.2 Create Data Quality Check Script

**File: `src/data/quality_check.py`**
```python
import pandas as pd
import sys

def data_quality_check(df, null_threshold=0.01):
    """
    Mandatory quality gate: Check for data quality issues
    """
    total_rows = len(df)
    issues = []
    
    # Check for null values in key columns
    key_columns = ['open', 'high', 'low', 'close', 'volume']
    for col in key_columns:
        null_count = df[col].isnull().sum()
        null_ratio = null_count / total_rows if total_rows > 0 else 0
        
        if null_ratio > null_threshold:
            issues.append(f"Column {col} has {null_ratio:.2%} null values (threshold: {null_threshold:.2%})")
    
    # Schema validation
    required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        issues.append(f"Missing required columns: {missing_columns}")
    
    if issues:
        print("Data Quality Check FAILED:")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)
    
    print("Data Quality Check PASSED")
    return True
```

#### 2.3 Create Data Transformation Script

**File: `src/data/transform.py`**
```python
import pandas as pd
import numpy as np

def transform_data(df):
    """
    Clean and engineer features for time-series prediction
    """
    # Convert to numeric
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Sort by timestamp
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    # Feature engineering
    df['returns'] = df['close'].pct_change()
    df['volatility'] = df['returns'].rolling(window=24).std()
    
    # Lag features
    for lag in [1, 2, 3, 6, 12]:
        df[f'close_lag_{lag}'] = df['close'].shift(lag)
        df[f'volume_lag_{lag}'] = df['volume'].shift(lag)
    
    # Rolling statistics
    df['close_ma_6'] = df['close'].rolling(window=6).mean()
    df['close_ma_24'] = df['close'].rolling(window=24).mean()
    df['volume_ma_6'] = df['volume'].rolling(window=6).mean()
    
    # Time-based features
    df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
    df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
    
    # Target variable: Next hour volatility
    df['target_volatility'] = df['volatility'].shift(-1)
    
    # Drop rows with NaN (from lag features)
    df = df.dropna().reset_index(drop=True)
    
    return df
```

#### 2.4 Create Pandas Profiling Report Script

**File: `src/data/profile.py`**
```python
import pandas as pd
from pandas_profiling import ProfileReport
import mlflow

def generate_data_profile(df, output_path="data_profile.html"):
    """
    Generate data quality report and log to MLflow
    """
    profile = ProfileReport(df, title="Binance Data Quality Report")
    profile.to_file(output_path)
    
    # Log to MLflow
    mlflow.log_artifact(output_path, "data_profiles")
    
    return output_path
```

#### 2.5 Create MinIO Upload Script

**File: `src/utils/minio_client.py`**
```python
from minio import Minio
from minio.error import S3Error
import os

def upload_to_minio(file_path, bucket_name, object_name):
    """
    Upload file to MinIO storage
    """
    client = Minio(
        "localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    
    # Create bucket if it doesn't exist
    found = client.bucket_exists(bucket_name)
    if not found:
        client.make_bucket(bucket_name)
    
    # Upload file
    client.fput_object(bucket_name, object_name, file_path)
    print(f"Uploaded {file_path} to {bucket_name}/{object_name}")
    
    return f"s3://{bucket_name}/{object_name}"
```

#### 2.6 Create Airflow DAG

**File: `dags/binance_etl_dag.py`**
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
sys.path.append('/path/to/your/project/src')

from data.extract import extract_binance_data
from data.quality_check import data_quality_check
from data.transform import transform_data
from data.profile import generate_data_profile
from utils.minio_client import upload_to_minio

default_args = {
    'owner': 'mlops-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'binance_etl_pipeline',
    default_args=default_args,
    description='Binance data ETL pipeline',
    schedule_interval=timedelta(hours=1),  # Run every hour
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['binance', 'etl', 'mlops'],
)

# Task 1: Extract
extract_task = PythonOperator(
    task_id='extract_binance_data',
    python_callable=extract_binance_data,
    dag=dag,
)

# Task 2: Quality Check
quality_check_task = PythonOperator(
    task_id='data_quality_check',
    python_callable=lambda: data_quality_check(extract_task.output),
    dag=dag,
)

# Task 3: Transform
transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=lambda: transform_data(extract_task.output),
    dag=dag,
)

# Task 4: Generate Profile
profile_task = PythonOperator(
    task_id='generate_data_profile',
    python_callable=lambda: generate_data_profile(transform_task.output),
    dag=dag,
)

# Task 5: Upload to MinIO
upload_task = PythonOperator(
    task_id='upload_to_minio',
    python_callable=lambda: upload_to_minio(
        transform_task.output,
        'processed-data',
        f"binance_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    ),
    dag=dag,
)

# Define task dependencies
extract_task >> quality_check_task >> transform_task >> profile_task >> upload_task
```

**Commands (Local Airflow):**
```bash
# Copy DAG to Airflow dags folder
cp dags/binance_etl_dag.py $AIRFLOW_HOME/dags/

# Verify DAG is loaded
airflow dags list | grep binance_etl_pipeline
```

**Commands (Astronomer):**
```bash
# Place DAG in dags/ folder (Astronomer auto-detects)
# DAG should be in: dags/binance_etl_dag.py

# Deploy to Astronomer Cloud
astro deploy

# Or test locally with Astronomer
astro dev start
# Access UI at http://localhost:8080

# View logs
astro dev logs

# Stop local environment
astro dev stop
```

---

### Step 3: Data Versioning with DVC

#### 3.1 Initialize DVC with MinIO Remote

```bash
# Initialize DVC
dvc init

# Configure MinIO as remote storage
dvc remote add -d minio s3://dvc-data
dvc remote modify minio endpointurl http://localhost:9000
dvc remote modify minio access_key_id minioadmin
dvc remote modify minio secret_access_key minioadmin

# Add processed data to DVC
dvc add data/processed/binance_data.csv

# Commit DVC metadata to Git
git add data/processed/binance_data.csv.dvc .dvc/config
git commit -m "Add processed data with DVC"

# Push data to MinIO
dvc push
```

---

## Phase II: Experimentation and Model Management

### Step 4: MLflow & Dagshub Integration

#### 4.1 Setup Dagshub

1. **Create Dagshub Account:**
   - Go to https://dagshub.com
   - Create a new repository
   - Note your repository URL: `https://dagshub.com/username/repo-name`

2. **Configure MLflow Tracking:**
```bash
# Set MLflow tracking URI
export MLFLOW_TRACKING_URI=https://dagshub.com/username/repo-name.mlflow
export DAGSHUB_USER_TOKEN=your_token_here
```

#### 4.2 Create Training Script with MLflow

**File: `src/models/train.py`**
```python
import mlflow
import mlflow.sklearn
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np
from datetime import datetime

def train_model(data_path):
    """
    Train model with MLflow tracking
    """
    # Load data
    df = pd.read_csv(data_path)
    
    # Prepare features and target
    feature_cols = [col for col in df.columns if col not in ['target_volatility', 'timestamp', 'collection_time']]
    X = df[feature_cols]
    y = df['target_volatility']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Start MLflow run
    with mlflow.start_run():
        # Log parameters
        mlflow.log_param("model_type", "RandomForestRegressor")
        mlflow.log_param("n_estimators", 100)
        mlflow.log_param("max_depth", 10)
        mlflow.log_param("train_size", len(X_train))
        mlflow.log_param("test_size", len(X_test))
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        model.fit(X_train, y_train)
        
        # Predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Log metrics
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("r2_score", r2)
        
        # Log model
        mlflow.sklearn.log_model(model, "model")
        
        # Save model as pickle (for compatibility)
        model_path = "models/model.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        mlflow.log_artifact(model_path, "models")
        
        print(f"Model trained - RMSE: {rmse:.4f}, MAE: {mae:.4f}, R2: {r2:.4f}")
        
        return model, rmse, mae, r2

if __name__ == "__main__":
    import sys
    data_path = sys.argv[1] if len(sys.argv) > 1 else "data/processed/binance_data.csv"
    train_model(data_path)
```

#### 4.3 Integrate Training into Airflow DAG

**Update `dags/binance_etl_dag.py`** to include training task:
```python
from models.train import train_model

# Add training task after upload
train_task = PythonOperator(
    task_id='train_model',
    python_callable=lambda: train_model(transform_task.output),
    dag=dag,
)

# Update dependencies
upload_task >> train_task
```

**Commands:**
```bash
# Run training manually to test
python src/models/train.py data/processed/binance_data.csv

# Check MLflow UI
mlflow ui --backend-store-uri https://dagshub.com/username/repo-name.mlflow
```

---

## Phase III: Continuous Integration & Deployment (CI/CD)

### Step 5: Git Workflow and CI Pipeline

#### 5.1 Setup Git Branching Strategy

```bash
# Initialize Git repository
git init
git remote add origin https://github.com/username/mlops-project.git

# Create branches
git checkout -b dev
git checkout -b test
git checkout -b master

# Set default branch to dev
git checkout dev
```

#### 5.2 Create GitHub Actions Workflows

**File: `.github/workflows/ci-feature-to-dev.yml`**
```yaml
name: CI - Feature to Dev

on:
  pull_request:
    branches:
      - dev

jobs:
  code-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pylint black pytest
      
      - name: Lint with pylint
        run: pylint src/
      
      - name: Format check with black
        run: black --check src/
      
      - name: Run unit tests
        run: pytest tests/
```

**File: `.github/workflows/ci-dev-to-test.yml`**
```yaml
name: CI - Dev to Test (Model Retraining)

on:
  pull_request:
    branches:
      - test

jobs:
  model-retraining:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install cml
      
      - name: Run Airflow DAG
        run: |
          # Trigger Airflow DAG to retrain model
          airflow dags trigger binance_etl_pipeline
      
      - name: Compare Models with CML
        env:
          REPO_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
        run: |
          cml runner \
            --labels cml \
            --cloud aws \
            --cloud-type t2.micro \
            --workdir . \
            -- python scripts/compare_models.py
      
      - name: CML Report
        env:
          REPO_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          echo "## Model Comparison Report" >> report.md
          echo "New model RMSE: X.XX" >> report.md
          echo "Production model RMSE: Y.YY" >> report.md
          cml publish report.md --pr
```

**File: `.github/workflows/cd-test-to-master.yml`**
```yaml
name: CD - Test to Master (Production Deployment)

on:
  push:
    branches:
      - master

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Fetch Model from MLflow
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
        run: |
          python scripts/fetch_model.py
      
      - name: Build Docker image
        run: |
          docker build -t username/mlops-api:${{ github.sha }} .
          docker tag username/mlops-api:${{ github.sha }} username/mlops-api:latest
      
      - name: Push Docker image
        run: |
          docker push username/mlops-api:${{ github.sha }}
          docker push username/mlops-api:latest
      
      - name: Deploy and Verify
        run: |
          docker run -d -p 8000:8000 --name mlops-api username/mlops-api:latest
          sleep 10
          curl http://localhost:8000/health
          docker stop mlops-api
          docker rm mlops-api
```

#### 5.3 Setup PR Approval Requirements

1. Go to GitHub repository Settings → Branches
2. Add branch protection rules:
   - **test branch**: Require 1 approval before merging
   - **master branch**: Require 1 approval before merging

#### 5.4 Create FastAPI Prediction Service

**File: `src/api/main.py`**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import pandas as pd
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response
import time

app = FastAPI(title="MLOps Prediction API")

# Prometheus metrics
REQUEST_COUNT = Counter('api_requests_total', 'Total API requests')
REQUEST_LATENCY = Histogram('api_request_latency_seconds', 'API request latency')
PREDICTION_COUNT = Counter('predictions_total', 'Total predictions made')

# Load model
with open('models/model.pkl', 'rb') as f:
    model = pickle.load(f)

class PredictionRequest(BaseModel):
    features: dict

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/predict")
async def predict(request: PredictionRequest):
    start_time = time.time()
    REQUEST_COUNT.inc()
    
    try:
        # Convert features to DataFrame
        df = pd.DataFrame([request.features])
        
        # Make prediction
        prediction = model.predict(df)[0]
        PREDICTION_COUNT.inc()
        
        latency = time.time() - start_time
        REQUEST_LATENCY.observe(latency)
        
        return {
            "prediction": float(prediction),
            "latency_ms": latency * 1000
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type="text/plain")
```

#### 5.5 Create Dockerfile

**File: `Dockerfile`**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY models/ ./models/

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**File: `requirements.txt`**
```
fastapi==0.104.1
uvicorn==0.24.0
pandas==2.1.3
scikit-learn==1.3.2
prometheus-client==0.19.0
pydantic==2.5.0
```

**Commands:**
```bash
# Build Docker image
docker build -t mlops-api:v1.0.0 .

# Test locally
docker run -p 8000:8000 mlops-api:v1.0.0

# Test health endpoint
curl http://localhost:8000/health

# Test prediction endpoint
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": {"open": 50000, "high": 51000, "low": 49000, "close": 50500, "volume": 1000000}}'
```

---

## Phase IV: Monitoring and Observability

### Step 6: Prometheus and Grafana Setup

#### 6.1 Create Prometheus Configuration

**File: `monitoring/prometheus/prometheus.yml`**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'mlops-api'
    static_configs:
      - targets: ['host.docker.internal:8000']
```

#### 6.2 Create Docker Compose for Monitoring

**File: `docker-compose.monitoring.yml`**
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana

volumes:
  grafana-storage:
```

**Commands:**
```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Access Prometheus: http://localhost:9090
# Access Grafana: http://localhost:3000 (admin/admin)
```

#### 6.3 Create Grafana Dashboard

1. **Login to Grafana** (http://localhost:3000)
2. **Add Prometheus Data Source:**
   - Configuration → Data Sources → Add data source
   - Select Prometheus
   - URL: http://prometheus:9090
   - Save & Test

3. **Create Dashboard:**
   - Create → Dashboard → Add visualization
   - **Panel 1: Request Count**
     - Query: `rate(api_requests_total[5m])`
     - Visualization: Graph
   
   - **Panel 2: Request Latency**
     - Query: `histogram_quantile(0.95, api_request_latency_seconds_bucket)`
     - Visualization: Graph
   
   - **Panel 3: Prediction Count**
     - Query: `rate(predictions_total[5m])`
     - Visualization: Stat

#### 6.4 Setup Grafana Alerts

1. **Create Alert Rule:**
   - Go to Alerting → Alert Rules → New alert rule
   - **Condition:** `histogram_quantile(0.95, api_request_latency_seconds_bucket) > 0.5`
   - **Evaluation:** Every 1m, For 5m
   - **Notification:** Log to file or Slack webhook

**File: `monitoring/grafana/alert-rules.yml`**
```yaml
groups:
  - name: mlops_alerts
    interval: 1m
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.95, api_request_latency_seconds_bucket) > 0.5
        for: 5m
        annotations:
          summary: "API latency exceeds 500ms"
      
      - alert: DataDrift
        expr: data_drift_ratio > 0.1
        for: 5m
        annotations:
          summary: "Data drift detected"
```

---

## Summary Checklist

### Applications & Tools Required:
- ✅ **Python 3.9+** - Core development
- ✅ **Apache Airflow** - Orchestration
- ✅ **Astronomer** (Optional) - Managed Airflow platform (recommended for production)
- ✅ **MinIO** - Object storage (S3-compatible)
- ✅ **DVC** - Data versioning
- ✅ **MLflow** - Experiment tracking
- ✅ **Dagshub** - MLflow hosting & collaboration (separate from Airflow)
- ✅ **Git & GitHub** - Version control
- ✅ **GitHub Actions** - CI/CD automation
- ✅ **CML** - Model comparison reports
- ✅ **Docker** - Containerization
- ✅ **FastAPI** - REST API service
- ✅ **Prometheus** - Metrics collection
- ✅ **Grafana** - Visualization & alerting

### Key Commands Summary:

```bash
# 1. Start MinIO
docker run -d -p 9000:9000 -p 9001:9001 --name minio \
  -e "MINIO_ROOT_USER=minioadmin" -e "MINIO_ROOT_PASSWORD=minioadmin" \
  minio/minio server /data --console-address ":9001"

# 2. Initialize Airflow (Choose one option)

# Option A: Local Airflow
export AIRFLOW_HOME=$(pwd)/airflow
airflow db init
airflow webserver --port 8080 &
airflow scheduler &

# Option B: Astronomer (Recommended)
astro dev init
astro dev start  # For local development
# Or deploy to cloud: astro deploy

# 3. Initialize DVC with MinIO
dvc init
dvc remote add -d minio s3://dvc-data
dvc remote modify minio endpointurl http://localhost:9000

# 4. Setup MLflow with Dagshub
export MLFLOW_TRACKING_URI=https://dagshub.com/username/repo-name.mlflow

# 5. Build and run API
docker build -t mlops-api:v1.0.0 .
docker run -p 8000:8000 mlops-api:v1.0.0

# 6. Start monitoring
docker-compose -f docker-compose.monitoring.yml up -d
```

### Next Steps:
1. ✅ Complete Phase I: Data ingestion pipeline
2. ✅ Complete Phase II: Model training with MLflow
3. ✅ Complete Phase III: CI/CD setup
4. ✅ Complete Phase IV: Monitoring setup
5. ✅ Test end-to-end pipeline
6. ✅ Document and prepare presentation

---

## Troubleshooting

### Common Issues:

1. **Airflow DAG not appearing:**
   - **Local Airflow:** Check DAG file is in `$AIRFLOW_HOME/dags/`
   - **Astronomer:** Check DAG file is in `dags/` folder in project root
   - Check for syntax errors: `python dags/binance_etl_dag.py`
   - **Local:** Restart Airflow scheduler
   - **Astronomer:** Run `astro dev restart` or check logs with `astro dev logs`

2. **MinIO connection issues:**
   - Verify MinIO is running: `docker ps | grep minio`
   - Check credentials match in code

3. **MLflow tracking fails:**
   - Verify Dagshub token is set: `echo $DAGSHUB_USER_TOKEN`
   - Check MLflow tracking URI is correct

4. **Docker build fails:**
   - Ensure all dependencies in `requirements.txt`
   - Check Dockerfile syntax

5. **Prometheus not scraping:**
   - Verify API is exposing `/metrics` endpoint
   - Check Prometheus config targets are correct

