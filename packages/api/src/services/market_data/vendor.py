from abc import ABC, abstractmethod
from datetime import datetime, timedelta, date
from typing import Any, Dict, List, Optional
import structlog

from src.models.market import OptionChainResponse, OptionStrike

logger = structlog.get_logger(__name__)


class DataVendorAdapter(ABC):
    @abstractmethod
    async def get_option_chain(self, underlying: str, expiry: str) -> OptionChainResponse:
        """Get option chain. Returns normalized OptionChainResponse."""

    @abstractmethod
    async def get_spot_price(self, underlying: str) -> float:
        """Get current spot price."""

    @abstractmethod
    async def get_historical(
        self, instrument: str, start: str, end: str, interval: str = "1min"
    ) -> List[Dict[str, Any]]:
        """Get historical OHLCV data."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if vendor API is reachable."""


class MockDataVendor(DataVendorAdapter):
    STALE_THRESHOLD_SECONDS = 30

    def __init__(self):
        self._underlying_data: Dict[str, Dict[str, Any]] = {
            "NIFTY": {
                "spot_price": 24850.55,
                "expiry": "2026-03-05",
                "chain": [
                    {
                        "strike": 24800,
                        "ce_ltp": 120.5,
                        "pe_ltp": 45.2,
                        "ce_oi": 550000,
                        "pe_oi": 1200000,
                        "ce_iv": 14.5,
                        "pe_iv": 16.2,
                        "ce_greeks": {
                            "delta": 0.65,
                            "gamma": 0.001,
                            "theta": -10.5,
                            "vega": 5.2,
                        },
                        "pe_greeks": {
                            "delta": -0.35,
                            "gamma": 0.001,
                            "theta": -8.5,
                            "vega": 4.8,
                        },
                    },
                    {
                        "strike": 24900,
                        "ce_ltp": 65.4,
                        "pe_ltp": 95.8,
                        "ce_oi": 1850000,
                        "pe_oi": 450000,
                        "ce_iv": 14.8,
                        "pe_iv": 16.5,
                        "ce_greeks": {
                            "delta": 0.42,
                            "gamma": 0.0015,
                            "theta": -12.2,
                            "vega": 5.8,
                        },
                        "pe_greeks": {
                            "delta": -0.58,
                            "gamma": 0.0015,
                            "theta": -10.8,
                            "vega": 5.5,
                        },
                    },
                    {
                        "strike": 25000,
                        "ce_ltp": 28.5,
                        "pe_ltp": 145.2,
                        "ce_oi": 2200000,
                        "pe_oi": 380000,
                        "ce_iv": 15.2,
                        "pe_iv": 17.0,
                        "ce_greeks": {
                            "delta": 0.22,
                            "gamma": 0.0018,
                            "theta": -14.5,
                            "vega": 6.2,
                        },
                        "pe_greeks": {
                            "delta": -0.78,
                            "gamma": 0.0018,
                            "theta": -12.8,
                            "vega": 6.0,
                        },
                    },
                ],
            },
            "BANKNIFTY": {
                "spot_price": 52430.4,
                "expiry": "2026-03-04",
                "chain": [
                    {
                        "strike": 52400,
                        "ce_ltp": 340.2,
                        "pe_ltp": 210.5,
                        "ce_oi": 250000,
                        "pe_oi": 600000,
                        "ce_iv": 18.2,
                        "pe_iv": 20.5,
                        "ce_greeks": {
                            "delta": 0.55,
                            "gamma": 0.0005,
                            "theta": -45.0,
                            "vega": 15.2,
                        },
                        "pe_greeks": {
                            "delta": -0.45,
                            "gamma": 0.0005,
                            "theta": -40.0,
                            "vega": 14.8,
                        },
                    },
                    {
                        "strike": 52500,
                        "ce_ltp": 185.5,
                        "pe_ltp": 385.2,
                        "ce_oi": 420000,
                        "pe_oi": 280000,
                        "ce_iv": 18.5,
                        "pe_iv": 21.0,
                        "ce_greeks": {
                            "delta": 0.38,
                            "gamma": 0.0006,
                            "theta": -52.0,
                            "vega": 16.5,
                        },
                        "pe_greeks": {
                            "delta": -0.62,
                            "gamma": 0.0006,
                            "theta": -48.0,
                            "vega": 16.0,
                        },
                    },
                    {
                        "strike": 52600,
                        "ce_ltp": 95.8,
                        "pe_ltp": 520.5,
                        "ce_oi": 550000,
                        "pe_oi": 180000,
                        "ce_iv": 19.0,
                        "pe_iv": 21.5,
                        "ce_greeks": {
                            "delta": 0.25,
                            "gamma": 0.0007,
                            "theta": -58.0,
                            "vega": 17.8,
                        },
                        "pe_greeks": {
                            "delta": -0.75,
                            "gamma": 0.0007,
                            "theta": -55.0,
                            "vega": 17.2,
                        },
                    },
                ],
            },
        }
        self._last_fetch_time: Dict[str, datetime] = {}

    def _is_stale(self, underlying: str) -> bool:
        if underlying not in self._last_fetch_time:
            return False
        elapsed = datetime.utcnow() - self._last_fetch_time[underlying]
        return elapsed > timedelta(seconds=self.STALE_THRESHOLD_SECONDS)

    async def get_option_chain(self, underlying: str, expiry: str) -> OptionChainResponse:
        underlying_upper = underlying.upper()
        if underlying_upper not in self._underlying_data:
            raise ValueError(f"Unknown underlying: {underlying}")

        data = self._underlying_data[underlying_upper]

        if data["expiry"] != expiry:
            raise ValueError(
                f"Expiry {expiry} not available for {underlying}. Available: {data['expiry']}"
            )

        is_stale = self._is_stale(underlying_upper)
        self._last_fetch_time[underlying_upper] = datetime.utcnow()

        chain: List[OptionStrike] = []
        for strike_data in data["chain"]:
            chain.append(
                OptionStrike(
                    strike=strike_data["strike"],
                    ce_ltp=strike_data["ce_ltp"],
                    pe_ltp=strike_data["pe_ltp"],
                    ce_oi=strike_data["ce_oi"],
                    pe_oi=strike_data["pe_oi"],
                    ce_iv=strike_data["ce_iv"],
                    pe_iv=strike_data["pe_iv"],
                    ce_greeks=strike_data["ce_greeks"],
                    pe_greeks=strike_data["pe_greeks"],
                )
            )

        return OptionChainResponse(
            underlying=underlying_upper,
            spot_price=data["spot_price"],
            timestamp=datetime.utcnow(),
            expiry=date.fromisoformat(data["expiry"]),
            chain=chain,
            stale=is_stale,
        )

    async def get_spot_price(self, underlying: str) -> float:
        underlying_upper = underlying.upper()
        if underlying_upper not in self._underlying_data:
            raise ValueError(f"Unknown underlying: {underlying}")
        return self._underlying_data[underlying_upper]["spot_price"]

    async def get_historical(
        self,
        instrument: str,
        start: str,
        end: str,
        interval: str = "1min",
    ) -> List[Dict[str, Any]]:
        return []

    async def health_check(self) -> bool:
        return True
