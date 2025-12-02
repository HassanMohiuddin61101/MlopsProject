"""
Fetch Model from MLflow Registry
Downloads the production model from MLflow for deployment
"""
import os
import sys
import mlflow
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.mlflow_config import setup_mlflow
from models.registry import get_latest_model

load_dotenv()

def fetch_production_model():
    """
    Fetch production model from MLflow registry
    """
    # Setup MLflow
    setup_mlflow()
    
    # Get production model
    model_uri = get_latest_model("dqn_trend_model", stage="Production")
    
    if not model_uri:
        print("⚠️  No production model found. Using latest model from experiment.")
        # Fallback: get latest model from experiment
        client = mlflow.tracking.MlflowClient()
        experiment = mlflow.get_experiment_by_name("crypto_trend_prediction")
        
        if experiment:
            runs = client.search_runs(
                experiment_ids=[experiment.experiment_id],
                order_by=["attributes.start_time DESC"],
                max_results=1
            )
            if runs:
                model_uri = f"runs:/{runs[0].info.run_id}/models"
                print(f"✅ Using latest model: {model_uri}")
            else:
                print("❌ No models found")
                return False
        else:
            print("❌ No experiment found")
            return False
    
    # Download model
    model_dir = "model/deployed"
    os.makedirs(model_dir, exist_ok=True)
    
    try:
        # Download model artifacts
        mlflow.artifacts.download_artifacts(
            artifact_uri=model_uri,
            dst_path=model_dir
        )
        print(f"✅ Model downloaded to: {model_dir}")
        return True
    except Exception as e:
        print(f"❌ Error downloading model: {str(e)}")
        return False

if __name__ == "__main__":
    fetch_production_model()

