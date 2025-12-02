# Airflow on Windows - Important Note

## The Problem

Airflow's scheduler, triggerer, and webserver spawn as separate processes. When using standalone mode, these child processes don't inherit the Python module mocks we set up in the parent script. This causes `pwd`, `fcntl`, and `daemon` import errors.

## Solutions (Ranked by Recommendation)

### 1. ✅ Use Docker (BEST SOLUTION)

**Why:** Runs Airflow in a Linux container, avoiding all Windows compatibility issues.

**How:**
```powershell
docker-compose -f docker-compose-airflow.yml up -d
```

**Pros:**
- ✅ No Windows compatibility issues
- ✅ Production-ready
- ✅ Isolated environment
- ✅ Easy to manage

**Cons:**
- Requires Docker Desktop
- Slightly more setup

### 2. ⚠️ Skip Airflow for Phase 1 Testing

**Why:** You can test all pipeline components individually without Airflow.

**How:**
- Test data extraction: `python -m src.data.extract`
- Test transformation: `python -m src.data.transform`
- Test MinIO upload: `python -m src.utils.minio_client`
- Set up Airflow later in Docker for full integration

**Pros:**
- ✅ Can complete Phase 1 testing
- ✅ No compatibility issues
- ✅ Faster iteration

**Cons:**
- Not the full MLOps pipeline
- Need to set up Airflow later

### 3. ❌ Native Windows (NOT RECOMMENDED)

**Why:** Too many compatibility issues with Unix-only modules.

**Issues:**
- `pwd` module doesn't exist
- `fcntl` module doesn't exist  
- `daemon` package requires Unix
- Child processes don't inherit mocks
- Gunicorn requires Unix

## Recommendation

**For Phase 1:** Test components individually, then use Docker for Airflow integration.

**For Production:** Always use Docker for Airflow.

## Next Steps

1. Complete Steps 5-8 (test individual components)
2. Set up Airflow in Docker (Option A)
3. Or proceed to Phase 2 and set up Airflow later

