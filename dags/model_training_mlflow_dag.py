"""
Model Training and MLflow Logging DAG
Logs trained models to MLflow (Dagshub) for experiment tracking
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import with error handling
try:
    from models.train_with_mlflow import log_training_run
    from models.registry import register_model_from_run
except ImportError as e:
    raise ImportError(f"Failed to import modules: {e}")

# Default arguments
default_args = {
    'owner': 'mlops-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'model_training_mlflow',
    default_args=default_args,
    description='Train and log model to MLflow (Dagshub)',
    schedule_interval=None,  # Manual trigger only
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['mlflow', 'training', 'model-registry'],
)

# Task 1: Log model to MLflow
def log_model_task_func(**context):
    """Log trained model to MLflow"""
    model_path = "model/dqn_trend_model_trend.pkl"
    
    # Example training metrics (replace with actual metrics from training)
    training_metrics = {
        "accuracy": 0.85,
        "precision": 0.82,
        "recall": 0.88,
        "f1_score": 0.85,
        "loss": 0.15
    }
    
    # Model hyperparameters
    model_params = {
        "architecture": "8-8",
        "input_features": 7,
        "output_actions": 2,
        "learning_rate": 0.001,
        "batch_size": 32,
        "epochs": 100
    }
    
    # Data information
    data_info = {
        "symbol": "BTCUSDT",
        "interval": "1h",
        "data_points": 100
    }
    
    # Log to MLflow
    run_id = log_training_run(
        model_path=model_path,
        training_metrics=training_metrics,
        model_params=model_params,
        data_info=data_info
    )
    
    # Store run_id in XCom for next task
    return run_id

log_model_task = PythonOperator(
    task_id='log_model_to_mlflow',
    python_callable=log_model_task_func,
    dag=dag,
)

# Task 2: Register model (optional - for model registry)
def register_model_task_func(**context):
    """Register model in MLflow model registry"""
    ti = context['ti']
    run_id = ti.xcom_pull(task_ids='log_model_to_mlflow')
    
    if run_id:
        try:
            result = register_model_from_run(
                run_id=run_id,
                model_name="dqn_trend_model"
            )
            print(f"✅ Model registered: {result.name} v{result.version}")
            return f"Model version {result.version} registered"
        except Exception as e:
            print(f"⚠️  Model registration failed: {str(e)}")
            return f"Registration failed: {str(e)}"
    else:
        print("⚠️  No run_id available for model registration")
        return "No run_id"

register_model_task = PythonOperator(
    task_id='register_model',
    python_callable=register_model_task_func,
    dag=dag,
)

# Define task dependencies
log_model_task >> register_model_task

