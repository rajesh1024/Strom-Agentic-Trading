import pytest
from src.services.market_data.engine import FeatureComputationEngine

def test_technical_indicators():
    engine = FeatureComputationEngine()
    # Create mock candles (30 days of data)
    candles = []
    for i in range(30):
        # Trending up
        price = 100.0 + i
        candles.append({
            "high": price + 1,
            "low": price - 1,
            "close": price,
            "volume": 1000
        })
    
    indicators = engine.compute_indicators(candles)
    assert indicators["rsi_14"] > 50.0
    assert indicators["atr_14"] > 0
    assert "vwap_dev" in indicators

def test_indicators_insufficient_data():
    engine = FeatureComputationEngine()
    indicators = engine.compute_indicators([{"close": 100}] * 5)
    assert indicators["rsi_14"] == 50.0
    assert indicators["atr_14"] == 0.0
