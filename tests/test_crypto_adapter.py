import pytest
import asyncio
from src.services.execution.crypto import CryptoBrokerAdapter
from src.services.market_data.crypto_vendor import CryptoDataVendor

@pytest.mark.asyncio
async def test_crypto_adapter_fractional_qty():
    adapter = CryptoBrokerAdapter(mock=True)
    # Testing fractional qty 0.001 BTC
    order = await adapter.place_order(
        instrument="BTCUSDT",
        side="BUY",
        qty=0.001,
        order_type="MARKET",
        price=None,
        trigger_price=None,
        tag="crypto_test"
    )
    assert "mock_crypto_" in order["order_id"]
    assert order["status"] == "FILLED"

@pytest.mark.asyncio
async def test_crypto_adapter_get_positions():
    adapter = CryptoBrokerAdapter(mock=True)
    positions = await adapter.get_positions()
    assert len(positions) == 1
    assert positions[0]["instrument"] == "BTCUSDT"
    assert positions[0]["qty"] == 0.05
    assert positions[0]["margin_mode"] == "cross"

@pytest.mark.asyncio
async def test_crypto_vendor_mock_ws():
    vendor = CryptoDataVendor(mock=True)
    await vendor.start_websocket(["BTCUSDT"])
    
    # Wait for a few ticks
    await asyncio.sleep(2)
    
    price = await vendor.get_spot_price("BTCUSDT")
    assert price != 0.0
    assert abs(price - 65000.0) < 100.0 # Should be near 65k but changed
    
    await vendor.stop_websocket()

@pytest.mark.asyncio
async def test_crypto_vendor_features_normalization():
    # This just ensures we can still use the FeatureVector with crypto fields
    from src.models.market import FeatureVector, RegimeFeatures
    
    features = FeatureVector(
        pcr=1.2,
        iv_skew=0.05,
        max_pain=65000,
        oi_change_ce_top5=[],
        oi_change_pe_top5=[],
        vwap_deviation=0.01,
        atr_14=500.0,
        rsi_14=65.0,
        regime_features=RegimeFeatures(volatility_rank=0.8, trend_strength=0.7, mean_reversion_score=0.3),
        funding_rate=0.0001,
        open_interest_usd=1500000000.0,
        liquidation_levels=[62000.0, 68000.0]
    )
    
    assert features.funding_rate == 0.0001
    assert features.open_interest_usd == 1500000000.0
    assert 62000.0 in features.liquidation_levels

@pytest.mark.asyncio
async def test_crypto_adapter_rate_limit():
    adapter = CryptoBrokerAdapter(mock=True)
    adapter.rate_limit = 5
    adapter._request_times = []
    
    for _ in range(5):
        await adapter.get_margins()
        
    with pytest.raises(Exception, match="Rate limit exceeded"):
        await adapter.get_margins()
