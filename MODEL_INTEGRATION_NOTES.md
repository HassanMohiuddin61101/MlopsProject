# Model Integration Notes

## Model Architecture
- **Type**: Deep Q-Network (DQN) / Conservative Q-Learning (CQL)
- **Input Features**: 7 features
- **Architecture**: 7 → 8 → 8 → 2 (BULLISH/BEARISH) - **8-8 network**
- **Model File**: `model/dqn_trend_model_trend.pkl`
- **Training Script**: `model/train_v5.py` (Note: script shows 32-16, but saved model is 8-8)

## 7 Model Features (Exact Match with Training)

1. **One-bar return** - Percentage change in close price
2. **RSI (14-period)** - Relative Strength Index
3. **MA fast/slow ratio** - Ratio of 10-period MA to 20-period MA
4. **Price vs MA20** - Price deviation from 20-period moving average
5. **50-bar trend strength** - Price change over 50 bars
6. **Volume / EMA20 ratio** - Volume relative to 20-period EMA
7. **Volatility** - Rolling standard deviation of returns (20-period)

**All features are robustly normalized** using median/MAD normalization with tanh compression (matching training).

## Binance API Configuration

Updated to match training script format:
- **BASE_URL**: `https://api.binance.com`
- **INTERVAL**: `1h` (1-hour timeframe)
- **SYMBOL**: From environment variable `BINANCE_TARGET` or default `BTCUSDT`

Uses REST API directly (not python-binance library) to match training script.

## Updated Files

### 1. `src/data/extract.py`
- ✅ Updated to use Binance REST API (matching train_v5.py)
- ✅ Uses BASE_URL and INTERVAL configuration
- ✅ Returns DataFrame with index as open_time (matching training format)
- ✅ Retrieves OHLCV (Open, High, Low, Close, Volume) data

### 2. `src/data/transform.py`
- ✅ Completely rewritten to extract exact 7 features
- ✅ Uses same robust normalization as training (median/MAD + tanh)
- ✅ Matches `extract_state_features()` from train_v5.py

### 3. `src/models/predict.py` (NEW)
- ✅ Model loading utility with 8-8 architecture support
- ✅ Custom QNetwork8x8 class matching saved model architecture
- ✅ Prediction function for single features
- ✅ Batch prediction from DataFrame
- ✅ Handles 8-8 architecture (not 32-16 from current training script)

### 4. `requirements.txt`
- ✅ Added `torch==2.1.0` (PyTorch for model)
- ✅ Added `requests==2.31.0` (for Binance REST API)

### 5. `dags/binance_etl_dag.py`
- ✅ Updated to use new transform function
- ✅ Handles open_time index properly

## Usage Example

```python
from src.data.extract import extract_binance_data
from src.data.transform import transform_data
from src.models.predict import load_model, predict_trend

# 1. Extract data
df, path = extract_binance_data(symbol='BTCUSDT', interval='1h', limit=100)

# 2. Transform to get 7 features
transformed_df = transform_data(df)

# 3. Load model
agent, device = load_model()

# 4. Get features for prediction (last row)
features = transformed_df[['feature_1_return', 'feature_2_rsi', 
                          'feature_3_ma_ratio', 'feature_4_price_vs_ma20',
                          'feature_5_trend_strength', 'feature_6_volume_ratio',
                          'feature_7_volatility']].iloc[-1].values

# 5. Predict
prediction = predict_trend(features, agent, device)
print(f"Predicted trend: {prediction['trend']}")
print(f"Confidence: {prediction['confidence']}")
```

## Feature Column Names

After transformation, features are named:
- `feature_1_return`
- `feature_2_rsi`
- `feature_3_ma_ratio`
- `feature_4_price_vs_ma20`
- `feature_5_trend_strength`
- `feature_6_volume_ratio`
- `feature_7_volatility`

## Important Notes

1. **Minimum Data Required**: Need at least 50 bars for trend strength calculation
2. **Normalization**: Features are normalized using rolling windows (50 bars default)
3. **Model Input**: Model expects exactly 7 features in the order above
4. **Output**: Model predicts BULLISH (0) or BEARISH (1) trend

## Environment Variables

Add to `.env`:
```
BINANCE_TARGET=BTCUSDT  # Trading pair symbol
```

Optional (for authenticated API):
```
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
```

