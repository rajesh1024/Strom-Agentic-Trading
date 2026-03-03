import pytest
from src.services.market_data.engine import FeatureComputationEngine
from src.models.market import CryptoOrderbook, DepthLevel
from datetime import datetime

def test_crypto_imbalance():
    engine = FeatureComputationEngine()
    ob = CryptoOrderbook(
        symbol="BTCUSDT",
        bids=[DepthLevel(price=60000, qty=10.0)],
        asks=[DepthLevel(price=60001, qty=5.0)],
        timestamp=datetime.utcnow(),
        last_update_id=1
    )
    metrics = engine.compute_crypto_metrics(ob)
    # (10-5)/(10+5) = 5/15 = 0.3333
    assert metrics["orderbook_imbalance"] == pytest.approx(0.3333, abs=0.001)

def test_crypto_feature_vector():
    engine = FeatureComputationEngine()
    from src.models.market import OptionChainResponse, OptionStrike
    from datetime import date
    
    chain = OptionChainResponse(
        underlying="BTC", spot_price=65000.0, timestamp=datetime.utcnow(),
        expiry=date(2026, 3, 27), chain=[]
    )
    candles = [{"close": 65000, "high": 65100, "low": 64900, "volume": 100} for _ in range(30)]
    ob = CryptoOrderbook(
        symbol="BTCUSDT", bids=[DepthLevel(price=64999, qty=1.0)], asks=[DepthLevel(price=65001, qty=1.0)],
        timestamp=datetime.utcnow(), last_update_id=1
    )
    
    fv = engine.compute_feature_vector(chain, candles, asset_class="crypto", orderbook=ob)
    assert fv.funding_rate == 0.0001
    assert fv.orderbook_imbalance == 0.0
    assert fv.liquidation_density == 0.02
