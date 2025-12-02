# Windows Airflow Solution

## The Problem
Airflow's webserver uses Gunicorn by default, which requires Unix-only modules (`fcntl`, `pwd`, `resource`, `daemon`). These don't exist on Windows.

## Best Solution: Use Standalone Mode

**Standalone mode** is the most Windows-compatible option. It starts both webserver and scheduler together and handles Windows better.

### Run This:

```powershell
python start_airflow_windows.py
```

This uses `airflow standalone` which:
- ✅ Starts both webserver AND scheduler
- ✅ Better Windows compatibility
- ✅ Simpler (one command instead of two)
- ✅ Automatically creates admin user

## Alternative: Use Docker (Recommended for Production)

If you continue having issues, consider using Docker:

```powershell
# Use Docker Compose for Airflow (add to docker-compose.yml)
docker-compose -f docker-compose-airflow.yml up -d
```

This runs Airflow in a Linux container, avoiding all Windows compatibility issues.

## Alternative: Use WSL (Windows Subsystem for Linux)

If you have WSL installed:
```bash
# In WSL terminal
cd /mnt/d/MLOPSProj
source venv/bin/activate
export AIRFLOW_HOME=$(pwd)/airflow
airflow webserver --port 8080
```

## Current Status

The startup scripts patch Unix modules, but Gunicorn still has issues. **Use `start_airflow_windows.py` (standalone mode)** for the best Windows experience.

