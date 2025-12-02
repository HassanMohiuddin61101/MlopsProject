"""
FastAPI Prediction Service
REST API for model predictions with Prometheus metrics
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import sys
import torch
import numpy as np
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response
import time
from typing import Dict, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.predict import load_model, predict_trend

app = FastAPI(
    title="MLOps Crypto Prediction API",
    description="API for cryptocurrency trend prediction using DQN model",
    version="1.0.0"
)

# Prometheus metrics
REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('api_request_latency_seconds', 'API request latency', ['endpoint'])
PREDICTION_COUNT = Counter('predictions_total', 'Total predictions made')
PREDICTION_ERRORS = Counter('prediction_errors_total', 'Total prediction errors')

# Load model on startup
model_agent = None
device = None

@app.on_event("startup")
async def load_model_on_startup():
    """Load model when API starts"""
    global model_agent, device
    try:
        model_agent, device = load_model()
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"⚠️  Error loading model: {str(e)}")
        model_agent = None
        device = None

class PredictionRequest(BaseModel):
    """Request model for predictions"""
    features: Dict[str, float]  # 7 features as dictionary

class PredictionResponse(BaseModel):
    """Response model for predictions"""
    trend: str  # "BULLISH" or "BEARISH"
    confidence: float
    prediction_time: float

@app.get("/health")
def health_check():
    """Health check endpoint"""
    start_time = time.time()
    REQUEST_COUNT.labels(method='GET', endpoint='/health').inc()
    
    status = {
        "status": "healthy",
        "model_loaded": model_agent is not None,
        "timestamp": time.time()
    }
    
    latency = time.time() - start_time
    REQUEST_LATENCY.labels(endpoint='/health').observe(latency)
    
    return status

@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Make prediction from features"""
    start_time = time.time()
    REQUEST_COUNT.labels(method='POST', endpoint='/predict').inc()
    
    if model_agent is None:
        REQUEST_LATENCY.labels(endpoint='/predict').observe(time.time() - start_time)
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Extract features in correct order
        feature_names = [
            'feature_1_return',
            'feature_2_rsi',
            'feature_3_ma_ratio',
            'feature_4_price_vs_ma20',
            'feature_5_trend_strength',
            'feature_6_volume_ratio',
            'feature_7_volatility'
        ]
        
        # Build feature array
        features = np.array([request.features.get(name, 0.0) for name in feature_names], dtype=np.float32)
        
        if len(features) != 7:
            raise ValueError("Expected 7 features")
        
        # Make prediction
        prediction = predict_trend(features, model_agent, device)
        
        PREDICTION_COUNT.inc()
        
        latency = time.time() - start_time
        REQUEST_LATENCY.labels(endpoint='/predict').observe(latency)
        
        return PredictionResponse(
            trend=prediction['trend'],
            confidence=prediction['confidence'],
            prediction_time=latency
        )
    
    except Exception as e:
        PREDICTION_ERRORS.inc()
        latency = time.time() - start_time
        REQUEST_LATENCY.labels(endpoint='/predict').observe(latency)
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "MLOps Crypto Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "metrics": "/metrics"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

