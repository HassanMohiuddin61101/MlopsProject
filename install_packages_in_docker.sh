#!/bin/bash
# Install packages directly into running Airflow containers
# Much faster than rebuilding Docker images

echo "Installing packages into Airflow containers..."

# Install into webserver
docker exec airflow-webserver pip install pandas==1.5.3 numpy==1.24.3 requests==2.31.0 minio==7.2.0 pandas-profiling==3.6.6 python-dotenv==1.0.0

# Install into scheduler  
docker exec airflow-scheduler pip install pandas==1.5.3 numpy==1.24.3 requests==2.31.0 minio==7.2.0 pandas-profiling==3.6.6 python-dotenv==1.0.0

echo "✅ Packages installed! Restarting Airflow services..."
docker-compose -f docker-compose-airflow.yml restart airflow-webserver airflow-scheduler

echo "✅ Done! Check Airflow UI in 30 seconds."

