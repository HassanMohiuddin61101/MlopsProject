"""
Binance ETL Pipeline DAG
Apache Airflow DAG for extracting, transforming, and loading Binance cryptocurrency data
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
    from data.extract import extract_binance_data
    from data.quality_check import data_quality_check
    from data.transform import transform_data, extract_model_features
    from data.profile import generate_data_profile
    from utils.minio_client import upload_to_minio
except ImportError as e:
    # If imports fail, the DAG will show as broken - this helps debug
    raise ImportError(f"Failed to import modules. Check if src/ folder is mounted: {e}")

# Default arguments for the DAG
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
    'binance_etl_pipeline',
    default_args=default_args,
    description='Binance cryptocurrency data ETL pipeline with quality checks',
    schedule_interval=timedelta(hours=1),  # Run every hour
    start_date=datetime(2024, 1, 1),
    catchup=False,  # Don't backfill past runs
    tags=['binance', 'etl', 'mlops', 'crypto'],
)

# Task 1: Extract data from Binance API
def extract_task_func(**context):
    """Extract data from Binance"""
    df, raw_path = extract_binance_data(symbol='BTCUSDT', interval='1h', limit=100)
    # Store path in XCom for next task
    return raw_path

extract_task = PythonOperator(
    task_id='extract_binance_data',
    python_callable=extract_task_func,
    dag=dag,
)

# Task 2: Data Quality Check (Mandatory Quality Gate)
def quality_check_task_func(**context):
    """Perform data quality check"""
    # Get raw data path from previous task
    ti = context['ti']
    raw_path = ti.xcom_pull(task_ids='extract_binance_data')
    
    # Load data and check quality
    import pandas as pd
    df = pd.read_csv(raw_path)
    data_quality_check(df)
    
    return raw_path

quality_check_task = PythonOperator(
    task_id='data_quality_check',
    python_callable=quality_check_task_func,
    dag=dag,
)

# Task 3: Transform data and engineer features (7 model features)
def transform_task_func(**context):
    """Transform and engineer the exact 7 features used by the DQN model"""
    # Get raw data path from previous task
    ti = context['ti']
    raw_path = ti.xcom_pull(task_ids='data_quality_check')
    
    # Load data
    import pandas as pd
    df = pd.read_csv(raw_path)
    
    # Set index if open_time column exists
    if 'open_time' in df.columns:
        df['open_time'] = pd.to_datetime(df['open_time'])
        df.set_index('open_time', inplace=True)
    
    # Transform (extracts 7 model features)
    output_dir = "data/processed"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f"{output_dir}/binance_processed_{timestamp}.csv"
    
    transformed_df = transform_data(df, output_path=output_path)
    
    return output_path

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_task_func,
    dag=dag,
)

# Task 4: Generate data profile report
def profile_task_func(**context):
    """Generate data quality profile"""
    # Get transformed data path
    ti = context['ti']
    processed_path = ti.xcom_pull(task_ids='transform_data')
    
    # Load data
    import pandas as pd
    df = pd.read_csv(processed_path)
    
    # Generate profile
    profile_path = generate_data_profile(df, run_name="binance_etl")
    
    return processed_path  # Return processed path for next task

profile_task = PythonOperator(
    task_id='generate_data_profile',
    python_callable=profile_task_func,
    dag=dag,
)

# Task 5: Upload to MinIO
def upload_task_func(**context):
    """Upload processed data to MinIO"""
    # Get processed data path
    ti = context['ti']
    processed_path = ti.xcom_pull(task_ids='transform_data')
    
    # Upload to MinIO
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    object_name = f"binance_data_{timestamp}.csv"
    
    s3_path = upload_to_minio(
        processed_path,
        bucket_name='processed-data',
        object_name=object_name
    )
    
    print(f"✅ Data uploaded to: {s3_path}")
    return s3_path

upload_task = PythonOperator(
    task_id='upload_to_minio',
    python_callable=upload_task_func,
    dag=dag,
)

# Task 6: Version data with DVC
def version_data_task_func(**context):
    """Version processed data with DVC"""
    import subprocess
    import os
    
    # Add processed data to DVC
    processed_dir = "data/processed"
    if os.path.exists(processed_dir):
        try:
            # Add to DVC (this will create/update .dvc file)
            result = subprocess.run(
                ["dvc", "add", processed_dir],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ DVC add output: {result.stdout}")
            
            # Push to MinIO remote
            push_result = subprocess.run(
                ["dvc", "push"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ DVC push output: {push_result.stdout}")
            print("✅ Data versioned with DVC and pushed to MinIO")
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️  DVC operation failed: {e.stderr}")
            # Don't fail the DAG if DVC fails - it's optional
    else:
        print(f"⚠️  Processed data directory not found: {processed_dir}")
    
    return "DVC versioning completed"

version_task = PythonOperator(
    task_id='version_data_with_dvc',
    python_callable=version_data_task_func,
    dag=dag,
)

# Define task dependencies (execution order)
extract_task >> quality_check_task >> transform_task >> profile_task >> upload_task >> version_task

