"""
MinIO Client Utility
Handles file uploads to MinIO object storage
"""
from minio import Minio
from minio.error import S3Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_minio_client():
    """
    Create and return MinIO client
    
    Returns:
        Minio: Configured MinIO client
    """
    # Get configuration from environment variables or use defaults
    minio_endpoint = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
    minio_access_key = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
    minio_secret_key = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
    minio_secure = os.getenv('MINIO_SECURE', 'False').lower() == 'true'
    
    client = Minio(
        minio_endpoint,
        access_key=minio_access_key,
        secret_key=minio_secret_key,
        secure=minio_secure
    )
    
    return client

def upload_to_minio(file_path, bucket_name, object_name=None):
    """
    Upload file to MinIO storage
    
    Args:
        file_path: Local path to file to upload
        bucket_name: MinIO bucket name
        object_name: Object name in bucket (default: filename from file_path)
    
    Returns:
        str: S3-style path to uploaded object
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Use filename as object name if not provided
    if object_name is None:
        object_name = os.path.basename(file_path)
    
    try:
        client = get_minio_client()
        
        # Create bucket if it doesn't exist
        found = client.bucket_exists(bucket_name)
        if not found:
            client.make_bucket(bucket_name)
            print(f"✅ Created bucket: {bucket_name}")
        
        # Upload file
        client.fput_object(bucket_name, object_name, file_path)
        print(f"✅ Uploaded {file_path} to {bucket_name}/{object_name}")
        
        # Return S3-style path
        s3_path = f"s3://{bucket_name}/{object_name}"
        return s3_path
    
    except S3Error as e:
        print(f"❌ MinIO S3 Error: {str(e)}")
        raise
    except Exception as e:
        print(f"❌ Error uploading to MinIO: {str(e)}")
        raise

def download_from_minio(bucket_name, object_name, file_path):
    """
    Download file from MinIO storage
    
    Args:
        bucket_name: MinIO bucket name
        object_name: Object name in bucket
        file_path: Local path to save downloaded file
    """
    try:
        client = get_minio_client()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else '.', exist_ok=True)
        
        # Download file
        client.fget_object(bucket_name, object_name, file_path)
        print(f"✅ Downloaded {bucket_name}/{object_name} to {file_path}")
        
        return file_path
    
    except S3Error as e:
        print(f"❌ MinIO S3 Error: {str(e)}")
        raise
    except Exception as e:
        print(f"❌ Error downloading from MinIO: {str(e)}")
        raise

if __name__ == "__main__":
    # Test MinIO connection
    try:
        client = get_minio_client()
        print("✅ MinIO client created successfully")
        
        # List buckets
        buckets = client.list_buckets()
        print(f"📦 Available buckets: {[b.name for b in buckets]}")
    except Exception as e:
        print(f"❌ Error connecting to MinIO: {str(e)}")
        print("💡 Make sure MinIO is running: docker run -d -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address ':9001'")

