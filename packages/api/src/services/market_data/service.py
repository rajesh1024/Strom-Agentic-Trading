from datetime import datetime, timedelta
from typing import Optional
import structlog

from src.models.market import OptionChainResponse, FeatureVector, RegimeFeatures
from src.models.base import Underlying
from src.services.market_data.vendor import DataVendorAdapter
from src.events.event_bus import EventBus
from src.events.stream_names import MARKET_TICKS

logger = structlog.get_logger(__name__)


class MarketDataService:
    STALE_THRESHOLD_SECONDS = 30

    def __init__(self, vendor: DataVendorAdapter, event_bus: Optional[EventBus] = None):
        self._vendor = vendor
        self._event_bus = event_bus

    async def get_option_chain(self, underlying: str, expiry: str) -> OptionChainResponse:
        logger.info(
            "fetching_option_chain",
            underlying=underlying,
            expiry=expiry,
        )
        response = await self._vendor.get_option_chain(underlying, expiry)
        response.stale = self._is_stale(response.timestamp)

        if self._event_bus:
            await self._publish_tick(response)

        logger.info(
            "option_chain_fetched",
            underlying=underlying,
            expiry=expiry,
            stale=response.stale,
            strikes=len(response.chain),
        )
        return response

    def _is_stale(self, timestamp: datetime) -> bool:
        elapsed = datetime.utcnow() - timestamp
        return elapsed > timedelta(seconds=self.STALE_THRESHOLD_SECONDS)

    async def _publish_tick(self, response: OptionChainResponse) -> None:
        if not self._event_bus:
            return

        try:
            await self._event_bus.publish(
                MARKET_TICKS,
                {
                    "underlying": response.underlying.value,
                    "spot": response.spot_price,
                    "timestamp": response.timestamp.isoformat(),
                },
            )
            logger.debug("market_tick_published", underlying=response.underlying.value)
        except Exception as e:
            logger.error("failed_to_publish_tick", error=str(e))

    async def get_features(self, underlying: str, expiry: str) -> FeatureVector:
        chain_response = await self.get_option_chain(underlying, expiry)

        if chain_response.stale:
            logger.warning("using_stale_data_for_features", underlying=underlying)

        chain = chain_response.chain
        spot = chain_response.spot_price

        total_ce_oi = sum(s.ce_oi for s in chain)
        total_pe_oi = sum(s.pe_oi for s in chain)
        pcr = total_pe_oi / total_ce_oi if total_ce_oi > 0 else 0.0

        ce_ivs = [s.ce_iv for s in chain]
        pe_ivs = [s.pe_iv for s in chain]
        avg_ce_iv = sum(ce_ivs) / len(ce_ivs) if ce_ivs else 0.0
        avg_pe_iv = sum(pe_ivs) / len(pe_ivs) if pe_ivs else 0.0
        iv_skew = (avg_pe_iv - avg_ce_iv) / avg_ce_iv if avg_ce_iv > 0 else 0.0

        oi_by_strike = {s.strike: s.ce_oi + s.pe_oi for s in chain}
        max_pain_strike = min(oi_by_strike.keys(), key=lambda k: oi_by_strike[k])
        max_pain = int(max_pain_strike)

        sorted_by_ce_oi = sorted(chain, key=lambda s: s.ce_oi, reverse=True)[:5]
        oi_change_ce_top5 = [
            {"strike": s.strike, "oi": s.ce_oi, "change_pct": 0.0} for s in sorted_by_ce_oi
        ]

        sorted_by_pe_oi = sorted(chain, key=lambda s: s.pe_oi, reverse=True)[:5]
        oi_change_pe_top5 = [
            {"strike": s.strike, "oi": s.pe_oi, "change_pct": 0.0} for s in sorted_by_pe_oi
        ]

        vwap_deviation = 0.0
        atr_14 = 150.0
        rsi_14 = 55.0

        regime_features = RegimeFeatures(
            volatility_rank=0.45,
            trend_strength=0.62,
            mean_reversion_score=0.38,
        )

        return FeatureVector(
            pcr=round(pcr, 4),
            iv_skew=round(iv_skew, 4),
            max_pain=max_pain,
            oi_change_ce_top5=oi_change_ce_top5,
            oi_change_pe_top5=oi_change_pe_top5,
            vwap_deviation=round(vwap_deviation, 4),
            atr_14=round(atr_14, 2),
            rsi_14=round(rsi_14, 2),
            regime_features=regime_features,
        )

    async def health_check(self) -> bool:
        return await self._vendor.health_check()
