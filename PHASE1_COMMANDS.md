# Phase 1: Setup and Data Ingestion - Command Sequence

Follow these commands **in order** to set up Phase 1 of the MLOps project.

## Prerequisites Check
- ✅ Docker Desktop installed and running
- ✅ Python 3.11 installed
- ✅ Internet connection

---

## Step 1: Create and Activate Virtual Environment

**Terminal 1 (Main Terminal):**
```powershell
# Navigate to project directory
cd D:\MLOPSProj

# Create virtual environment with Python 3.11
py -3.11 -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run this first:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verify activation (should show (venv) prefix)
python --version
```

---

## Step 2: Install Dependencies

**Terminal 1 (with venv activated):**
```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Verify key packages
python -c "import pandas; import airflow; import mlflow; print('✅ All packages installed')"
```

---

## Step 3: Start MinIO (Object Storage)

**Terminal 1 (with venv activated):**
```powershell
# Start MinIO using Docker Compose
docker-compose up -d

# Verify MinIO is running
docker ps | Select-String minio

# Access MinIO Console: http://localhost:9001
# Login: minioadmin / minioadmin
```

**Alternative (if docker-compose doesn't work):**
```powershell
docker run -d -p 9000:9000 -p 9001:9001 --name minio -e "MINIO_ROOT_USER=minioadmin" -e "MINIO_ROOT_PASSWORD=minioadmin" minio/minio server /data --console-address ":9001"
```

---

## Step 4: Configure Environment Variables

**Terminal 1:**
```powershell
# Copy example env file
Copy-Item .env.example .env

# Edit .env file with your credentials (optional for now)
# For now, you can use public Binance API (rate-limited)
# Later add your Binance API keys if needed
```

---

## Step 5: Test Data Extraction (Standalone Test)

**Terminal 1 (with venv activated):**
```powershell
# Test data extraction
python -m src.data.extract

# Should create: data/raw/binance_BTCUSDT_YYYYMMDD_HHMMSS.csv
```

---

## Step 6: Test Data Quality Check

**Terminal 1:**
```powershell
# Test quality check (will use the latest extracted file)
python -m src.data.quality_check
```

---

## Step 7: Test Data Transformation

**Terminal 1:**
```powershell
# Test transformation
python -m src.data.transform

# Should create transformed data with features
```

---

## Step 8: Test MinIO Connection

**Terminal 1:**
```powershell
# Test MinIO client
python -m src.utils.minio_client

# Should show available buckets
```

---

## Step 9: Initialize Airflow

**Terminal 1:**
```powershell
# Set Airflow home directory
$env:AIRFLOW_HOME = "$PWD\airflow"

# Initialize Airflow database
airflow db init

# Create Airflow admin user
airflow users create --username admin --firstname Admin --lastname User --role Admin --email admin@example.com --password admin
```

---

## Step 10: Start Airflow Services

**⚠️ IMPORTANT: Windows Compatibility Issue**

Airflow has compatibility issues on Windows due to Unix-only dependencies. **Recommended: Use Docker** (see Option A below).

**Option A - Docker (RECOMMENDED for Windows):**

```powershell
# Start Airflow using Docker Compose
docker-compose -f docker-compose-airflow.yml up -d

# Check status
docker-compose -f docker-compose-airflow.yml ps

# View logs
docker-compose -f docker-compose-airflow.yml logs -f
```

**Access Airflow UI:** http://localhost:8080
- Username: `admin`
- Password: `admin`

**Option B - Native Windows (May have issues):**

If you want to try native Windows (not recommended due to compatibility issues):

**Terminal 2 (New Terminal):**
```powershell
cd D:\MLOPSProj
.\venv\Scripts\Activate.ps1
$env:AIRFLOW_HOME = "$PWD\airflow"

# Try standalone mode (may still have issues)
python start_airflow_windows.py
```

**Note:** Native Windows installation has known issues with daemon/fcntl modules. Docker is the recommended solution.

---

## Step 11: Copy DAG to Airflow

**Terminal 1:**
```powershell
# Create dags directory in airflow folder
New-Item -ItemType Directory -Force -Path "$PWD\airflow\dags"

# Copy DAG file
Copy-Item "dags\binance_etl_dag.py" "$PWD\airflow\dags\binance_etl_dag.py"

# Verify DAG is detected (wait a few seconds for Airflow to refresh)
# Check Airflow UI: http://localhost:8080
```

---

## Step 12: Test the Complete Pipeline

**In Airflow UI (http://localhost:8080):**
1. Find `binance_etl_pipeline` DAG
2. Toggle it ON (if paused)
3. Click "Trigger DAG" to run manually
4. Monitor the execution in the Graph View

**Or via command line (Terminal 1):**
```powershell
# Trigger DAG manually
airflow dags trigger binance_etl_pipeline

# Check DAG status
airflow dags list
```

---

## Step 13: Verify Results

**Terminal 1:**
```powershell
# Check extracted data
Get-ChildItem data\raw\ | Select-Object -Last 1

# Check processed data
Get-ChildItem data\processed\ | Select-Object -Last 1

# Check data profiles
Get-ChildItem data\profiles\ | Select-Object -Last 1

# Verify MinIO bucket (via browser: http://localhost:9001)
# Or check via Python:
python -c "from src.utils.minio_client import get_minio_client; client = get_minio_client(); buckets = client.list_buckets(); print([b.name for b in buckets])"
```

---

## Troubleshooting

### Issue: Airflow DAG not appearing
```powershell
# Check DAG file syntax
python dags\binance_etl_dag.py

# Restart Airflow scheduler (Terminal 3)
# Press Ctrl+C, then run: airflow scheduler
```

### Issue: MinIO connection failed
```powershell
# Check if MinIO is running
docker ps

# Restart MinIO
docker-compose restart
```

### Issue: Import errors
```powershell
# Make sure venv is activated
.\venv\Scripts\Activate.ps1

# Reinstall packages
pip install -r requirements.txt
```

---

## Next Steps (After Phase 1 is Complete)

1. ✅ Phase 1 Complete: Data ingestion pipeline working
2. ⏭️ Phase 2: MLflow & Dagshub integration for model training
3. ⏭️ Phase 3: CI/CD setup with GitHub Actions
4. ⏭️ Phase 4: Monitoring with Prometheus & Grafana

---

## Summary of Running Services

- **Terminal 1**: Main terminal for commands
- **Terminal 2**: Airflow Webserver (http://localhost:8080)
- **Terminal 3**: Airflow Scheduler
- **Docker**: MinIO (http://localhost:9001)

All services should be running simultaneously for the complete pipeline to work.

