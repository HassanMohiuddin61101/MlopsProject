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
    dagshub_token = os.getenv("DAGSHUB_USER_TOKEN")
    dagshub_username = os.getenv("DAGSHUB_USERNAME", "")
    
    if tracking_uri:
        # For Dagshub, include credentials in the URI format
        if "dagshub.com" in tracking_uri and dagshub_token and dagshub_username:
            # Format: https://username:token@dagshub.com/username/repo.mlflow
            if "@" not in tracking_uri:  # Only modify if credentials not already in URI
                # Extract the path after dagshub.com
                if tracking_uri.startswith("https://dagshub.com/"):
                    repo_path = tracking_uri.replace("https://dagshub.com/", "")
                    tracking_uri = f"https://{dagshub_username}:{dagshub_token}@dagshub.com/{repo_path}"
                elif tracking_uri.startswith("https://"):
                    # Handle case where URI might have different format
                    parts = tracking_uri.replace("https://", "").split("/", 1)
                    if len(parts) == 2:
                        tracking_uri = f"https://{dagshub_username}:{dagshub_token}@dagshub.com/{parts[1]}"
        
        mlflow.set_tracking_uri(tracking_uri)
        # Hide token in output for security
        safe_uri = tracking_uri.split("@")[0] + "@..." if "@" in tracking_uri else tracking_uri
        print(f"✅ MLflow tracking URI set to: {safe_uri}")
    else:
        print("⚠️  MLFLOW_TRACKING_URI not set, using local tracking")
    
    # Also set environment variables for MLflow client (backup method)
    if dagshub_token and dagshub_username:
        os.environ["MLFLOW_TRACKING_USERNAME"] = dagshub_username
        os.environ["MLFLOW_TRACKING_PASSWORD"] = dagshub_token
    
    return mlflow

