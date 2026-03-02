import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

from src.main import app
from src.services.market_data.vendor import MockDataVendor, DataVendorAdapter
from src.services.market_data.service import MarketDataService
from src.models.market import OptionChainResponse
from src.models.base import Underlying


client = TestClient(app, raise_server_exceptions=False)


class TestMockDataVendor:
    @pytest.mark.asyncio
    async def test_get_option_chain_nifty(self):
        vendor = MockDataVendor()
        result = await vendor.get_option_chain("NIFTY", "2026-03-05")

        assert result.underlying == Underlying.NIFTY
        assert result.spot_price == 24850.55
        assert result.expiry.isoformat() == "2026-03-05"
        assert len(result.chain) == 3
        assert result.stale is False

    @pytest.mark.asyncio
    async def test_get_option_chain_banknifty(self):
        vendor = MockDataVendor()
        result = await vendor.get_option_chain("BANKNIFTY", "2026-03-04")

        assert result.underlying == Underlying.BANKNIFTY
        assert result.spot_price == 52430.4
        assert result.expiry.isoformat() == "2026-03-04"
        assert len(result.chain) == 3

    @pytest.mark.asyncio
    async def test_get_option_chain_invalid_underlying(self):
        vendor = MockDataVendor()
        with pytest.raises(ValueError, match="Unknown underlying"):
            await vendor.get_option_chain("INVALID", "2026-03-05")

    @pytest.mark.asyncio
    async def test_get_option_chain_invalid_expiry(self):
        vendor = MockDataVendor()
        with pytest.raises(ValueError, match="Expiry.*not available"):
            await vendor.get_option_chain("NIFTY", "2026-03-01")

    @pytest.mark.asyncio
    async def test_health_check(self):
        vendor = MockDataVendor()
        assert await vendor.health_check() is True

    @pytest.mark.asyncio
    async def test_stale_detection_after_threshold(self):
        vendor = MockDataVendor()

        await vendor.get_option_chain("NIFTY", "2026-03-05")

        vendor._last_fetch_time["NIFTY"] = datetime.utcnow() - timedelta(seconds=31)

        result = await vendor.get_option_chain("NIFTY", "2026-03-05")
        assert result.stale is True

    @pytest.mark.asyncio
    async def test_fresh_data_not_stale(self):
        vendor = MockDataVendor()

        result = await vendor.get_option_chain("NIFTY", "2026-03-05")
        assert result.stale is False


class TestMarketDataService:
    @pytest.mark.asyncio
    async def test_get_option_chain_normalizes_and_flags_stale(self):
        vendor = MockDataVendor()
        service = MarketDataService(vendor=vendor)

        result = await service.get_option_chain("NIFTY", "2026-03-05")

        assert isinstance(result, OptionChainResponse)
        assert result.underlying == Underlying.NIFTY

    @pytest.mark.asyncio
    async def test_get_features_computes_correctly(self):
        vendor = MockDataVendor()
        service = MarketDataService(vendor=vendor)

        features = await service.get_features("NIFTY", "2026-03-05")

        assert features.pcr > 0
        assert features.iv_skew is not None
        assert features.max_pain > 0
        assert len(features.oi_change_ce_top5) == 3
        assert len(features.oi_change_pe_top5) == 3
        assert features.regime_features is not None


class TestMarketDataAPI:
    def test_get_option_chain_nifty_returns_200(self):
        response = client.get(
            "/api/v1/market-data/option-chain/NIFTY", params={"expiry": "2026-03-05"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["underlying"] == "NIFTY"
        assert "chain" in data
        assert "spot_price" in data

    def test_get_option_chain_banknifty_returns_200(self):
        response = client.get(
            "/api/v1/market-data/option-chain/BANKNIFTY", params={"expiry": "2026-03-04"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["underlying"] == "BANKNIFTY"

    def test_get_option_chain_invalid_underlying_returns_404(self):
        response = client.get(
            "/api/v1/market-data/option-chain/INVALID", params={"expiry": "2026-03-05"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_features_nifty_returns_200(self):
        response = client.get("/api/v1/market-data/features/NIFTY", params={"expiry": "2026-03-05"})
        assert response.status_code == 200
        data = response.json()
        assert "pcr" in data
        assert "iv_skew" in data
        assert "max_pain" in data

    def test_get_features_banknifty_returns_200(self):
        response = client.get(
            "/api/v1/market-data/features/BANKNIFTY", params={"expiry": "2026-03-04"}
        )
        assert response.status_code == 200

    def test_get_features_invalid_underlying_returns_404(self):
        response = client.get("/api/v1/market-data/features/INVALID")
        assert response.status_code == 404

    def test_market_data_health_check(self):
        response = client.get("/api/v1/market-data/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_option_chain_missing_expiry_param(self):
        response = client.get("/api/v1/market-data/option-chain/NIFTY")
        assert response.status_code == 422
