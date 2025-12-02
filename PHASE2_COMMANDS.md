# Phase 2: Commands and Next Steps

## ✅ Completed Steps

### 1. Dagshub Setup
- ✅ Account created: `HassanMohiuddin61101`
- ✅ Repository: `my-first-repo`
- ✅ Token configured in `.env`

### 2. DVC Setup
- ✅ DVC initialized
- ✅ MinIO remote configured (`minio-remote`)
- ✅ Data directories added to DVC:
  - `data/raw`
  - `data/processed`
  - `model`

### 3. MLflow Integration
- ✅ MLflow connected to Dagshub
- ✅ Model successfully logged to MLflow
- ✅ Run ID: `1622d6439fdb4a5a87aa539d0f76cacb`
- ✅ Experiment: `crypto_trend_prediction`

## 🔄 Next Steps

### Step 1: Push Data to MinIO (DVC)

**Prerequisites:** MinIO must be running

```powershell
# Start MinIO if not running
docker-compose -f docker-compose.yml up -d

# Push data to MinIO via DVC
.\venv\Scripts\Activate.ps1
dvc push
```

**Verify in MinIO:**
- Go to http://localhost:9001
- Login: `minioadmin` / `minioadmin`
- Check bucket: `dvc-data`

### Step 2: Test DVC Integration in ETL Pipeline

The ETL DAG now includes a DVC versioning task. Test it:

1. **Start Airflow** (if not running):
```powershell
docker-compose -f docker-compose-airflow.yml up -d
```

2. **Trigger the DAG:**
   - Go to http://localhost:8080
   - Find `binance_etl_pipeline` DAG
   - Click "Trigger DAG"
   - Watch for `version_data_with_dvc` task

### Step 3: Test Model Training DAG

1. **Trigger the model training DAG:**
   - In Airflow UI, find `model_training_mlflow` DAG
   - Click "Trigger DAG"
   - This will log the model to MLflow

2. **Verify in Dagshub:**
   - Go to: https://dagshub.com/HassanMohiuddin61101/my-first-repo
   - Navigate to "Experiments" tab
   - You should see runs with metrics and parameters

### Step 4: View MLflow Experiments

```powershell
# List experiments
.\venv\Scripts\Activate.ps1
python -c "from src.utils.mlflow_config import setup_mlflow; import mlflow; setup_mlflow(); client = mlflow.tracking.MlflowClient(); exps = client.search_experiments(); [print(f'{e.name} (ID: {e.experiment_id})') for e in exps]"

# Compare models
python -c "from src.models.compare_models import compare_experiments; compare_experiments('crypto_trend_prediction', 'accuracy')"
```

## 📊 Verification Checklist

- [ ] MinIO running and accessible
- [ ] DVC push successful (data in MinIO)
- [ ] ETL DAG runs successfully with DVC versioning
- [ ] Model training DAG logs to MLflow
- [ ] Experiments visible in Dagshub
- [ ] Model artifacts accessible in Dagshub

## 🔍 Troubleshooting

### DVC Push Fails
```powershell
# Check MinIO is running
docker ps | Select-String "minio"

# Check DVC remote configuration
dvc remote list
dvc remote modify minio-remote endpointurl http://localhost:9000
```

### MLflow Authentication Issues
```powershell
# Verify .env file has token
Get-Content .env | Select-String "DAGSHUB_USER_TOKEN"

# Test MLflow connection
python -c "from src.utils.mlflow_config import setup_mlflow; setup_mlflow()"
```

### DAG Import Errors
- Check that `src/` folder is mounted in Docker
- Verify all imports in DAG files
- Check Airflow logs: `docker logs airflow-scheduler`

## 📝 Summary

**Phase 2 Status:** ✅ **Core Setup Complete**

**What's Working:**
- ✅ Dagshub account and repository configured
- ✅ DVC initialized and configured with MinIO
- ✅ MLflow connected to Dagshub
- ✅ Model successfully logged to MLflow
- ✅ DVC integrated into ETL pipeline
- ✅ Model training DAG created

**Next Phase:** Phase 3 - CI/CD Pipeline (GitHub Actions, CML)

