# Phase 2 Setup Script
# Configures Dagshub, DVC, and MLflow

param(
    [string]$DagshubUsername = "",
    [string]$DagshubRepo = "",
    [string]$DagshubToken = ""
)

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

# Read token from file if not provided
if (-not $DagshubToken) {
    if (Test-Path "toke.txt") {
        $DagshubToken = (Get-Content "toke.txt" -Raw).Trim()
        Write-Host "✅ Token loaded from toke.txt" -ForegroundColor Green
    } else {
        Write-Host "❌ Token not found. Please provide token." -ForegroundColor Red
        exit 1
    }
}

# Prompt for username and repo if not provided
if (-not $DagshubUsername) {
    $DagshubUsername = Read-Host "Enter your Dagshub username"
}

if (-not $DagshubRepo) {
    $DagshubRepo = Read-Host "Enter your Dagshub repository name"
}

# Update .env file
Write-Host "`nUpdating .env file..." -ForegroundColor Cyan
$envContent = @"
# Binance API Configuration
BINANCE_TARGET=BTCUSDT
BINANCE_INTERVAL=1h

# MinIO Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Dagshub Configuration
DAGSHUB_USERNAME=$DagshubUsername
DAGSHUB_REPO=$DagshubRepo
DAGSHUB_USER_TOKEN=$DagshubToken

# MLflow Tracking URI (Dagshub)
MLFLOW_TRACKING_URI=https://dagshub.com/$DagshubUsername/$DagshubRepo.mlflow
"@

Set-Content -Path ".env" -Value $envContent
Write-Host "✅ .env file updated" -ForegroundColor Green

# Initialize DVC
Write-Host "`nInitializing DVC..." -ForegroundColor Cyan
if (-not (Test-Path ".dvc")) {
    dvc init
    Write-Host "✅ DVC initialized" -ForegroundColor Green
} else {
    Write-Host "✅ DVC already initialized" -ForegroundColor Green
}

# Configure DVC remote (MinIO)
Write-Host "`nConfiguring DVC remote (MinIO)..." -ForegroundColor Cyan
$remoteExists = dvc remote list 2>&1 | Select-String "minio-remote"
if (-not $remoteExists) {
    dvc remote add -d minio-remote s3://dvc-data
    dvc remote modify minio-remote endpointurl http://localhost:9000
    dvc remote modify minio-remote access_key_id minioadmin
    dvc remote modify minio-remote secret_access_key minioadmin
    Write-Host "✅ DVC remote configured" -ForegroundColor Green
} else {
    Write-Host "✅ DVC remote already configured" -ForegroundColor Green
}

# Verify DVC configuration
Write-Host "`nDVC Remote Configuration:" -ForegroundColor Cyan
dvc remote list

# Test MLflow connection
Write-Host "`nTesting MLflow connection..." -ForegroundColor Cyan
python -c "from src.utils.mlflow_config import setup_mlflow; import mlflow; mlflow_client = setup_mlflow(); client = mlflow.tracking.MlflowClient(); experiments = client.search_experiments(); print(f'✅ MLflow connected. Found {len(experiments)} experiments.')"

Write-Host "`n✅ Phase 2 setup complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Verify Dagshub repository exists: https://dagshub.com/$DagshubUsername/$DagshubRepo" -ForegroundColor White
Write-Host "2. Run: python -c `"from src.models.train_with_mlflow import log_model_to_mlflow; log_model_to_mlflow('model/dqn_trend_model_trend.pkl', metrics={'test_accuracy': 0.85}, params={'architecture': '8-8'})`"" -ForegroundColor White

