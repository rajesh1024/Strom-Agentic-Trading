import math
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np
import scipy.stats as si
import structlog
from src.models.market import FeatureVector, RegimeFeatures, OptionStrike, OptionChainResponse, CryptoOrderbook

logger = structlog.get_logger(__name__)

class FeatureComputationEngine:
    """
    Core engine for deterministic market computations.
    Calculates Greeks, Options metrics, Technical Indicators, and Crypto specific features.
    """

    def calculate_greeks(self, S: float, K: float, T: float, sigma: float, r: float = 0.07, is_call: bool = True) -> Dict[str, float]:
        """
        Calculate Black-Scholes Greeks using scipy.
        S: Spot price
        K: Strike price
        T: Time to expiry in years
        sigma: Implied volatility (decimal, e.g. 0.15)
        r: Risk-free rate (decimal, e.g. 0.07)
        """
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0}

        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        if is_call:
            delta = si.norm.cdf(d1)
            theta = -(S * si.norm.pdf(d1) * sigma / (2 * np.sqrt(T))) - r * K * np.exp(-r * T) * si.norm.cdf(d2)
        else:
            delta = si.norm.cdf(d1) - 1
            theta = -(S * si.norm.pdf(d1) * sigma / (2 * np.sqrt(T))) + r * K * np.exp(-r * T) * si.norm.cdf(-d2)

        gamma = si.norm.pdf(d1) / (S * sigma * np.sqrt(T))
        vega = S * si.norm.pdf(d1) * np.sqrt(T) / 100 # Vega per 1% change

        return {
            "delta": round(float(delta), 4),
            "gamma": round(float(gamma), 6),
            "theta": round(float(theta / 365.25), 4), # Daily theta
            "vega": round(float(vega), 4)
        }

    def compute_pcr(self, chain: List[OptionStrike]) -> float:
        total_ce_oi = sum(s.ce_oi for s in chain)
        total_pe_oi = sum(s.pe_oi for s in chain)
        if total_ce_oi == 0:
            return 0.0
        return round(total_pe_oi / total_ce_oi, 2)

    def compute_max_pain(self, chain: List[OptionStrike]) -> int:
        """Find the strike where total pain to option buyers is minimum."""
        strikes = [s.strike for s in chain]
        if not strikes:
            return 0
            
        pains = []
        for target_strike in strikes:
            total_pain = 0
            for s in chain:
                total_pain += max(0, target_strike - s.strike) * s.ce_oi
                total_pain += max(0, s.strike - target_strike) * s.pe_oi
            pains.append((target_strike, total_pain))
            
        if not pains:
            return 0
        return min(pains, key=lambda x: x[1])[0]

    def compute_indicators(self, candles: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate technical indicators (RSI, ATR, VWAP) matching standard formulas."""
        if len(candles) < 20: 
            return {"rsi_14": 50.0, "atr_14": 0.0, "vwap_dev": 0.0}

        closes = np.array([c["close"] for c in candles], dtype=float)
        highs = np.array([c["high"] for c in candles], dtype=float)
        lows = np.array([c["low"] for c in candles], dtype=float)
        volumes = np.array([c["volume"] for c in candles], dtype=float)

        # RSI calculation (14 periods) - Wilder's smoothing
        delta = np.diff(closes)
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        
        avg_gain = np.mean(gain[:14])
        avg_loss = np.mean(loss[:14])
        
        # Wilder's Smoothing for the rest
        for i in range(14, len(delta)):
            avg_gain = (avg_gain * 13 + gain[i]) / 14
            avg_loss = (avg_loss * 13 + loss[i]) / 14
            
        if avg_loss == 0:
            rsi = 100.0 if avg_gain > 0 else 50.0
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        # ATR calculation (14 periods) - Wilder's smoothing
        # TR = max(H-L, |H-Cp|, |L-Cp|)
        tr1 = highs[1:] - lows[1:]
        tr2 = np.abs(highs[1:] - closes[:-1])
        tr3 = np.abs(lows[1:] - closes[:-1])
        true_range = np.maximum(tr1, np.maximum(tr2, tr3))
        
        atr = np.mean(true_range[:14])
        for i in range(14, len(true_range)):
            atr = (atr * 13 + true_range[i]) / 14

        # VWAP calculation
        typical_price = (highs + lows + closes) / 3
        cumulative_tp_v = np.sum(typical_price * volumes)
        cumulative_v = np.sum(volumes)
        
        if cumulative_v == 0:
            vwap_dev = 0.0
        else:
            vwap = cumulative_tp_v / cumulative_v
            vwap_dev = (closes[-1] - vwap) / vwap

        return {
            "rsi_14": round(float(rsi), 2),
            "atr_14": round(float(atr), 4),
            "vwap_dev": round(float(vwap_dev), 6)
        }

    def compute_crypto_metrics(self, orderbook: CryptoOrderbook) -> Dict[str, float]:
        bid_qty = sum(l.qty for l in orderbook.bids)
        ask_qty = sum(l.qty for l in orderbook.asks)
        
        imbalance = 0.0
        if (bid_qty + ask_qty) > 0:
            imbalance = (bid_qty - ask_qty) / (bid_qty + ask_qty)
            
        return {
            "orderbook_imbalance": round(float(imbalance), 4),
            "liquidation_density": 0.02 # Placeholder for complex logic
        }

    def compute_feature_vector(self, 
                               chain_resp: OptionChainResponse, 
                               historical: List[Dict[str, Any]],
                               asset_class: str = "equity",
                               orderbook: Optional[CryptoOrderbook] = None) -> FeatureVector:
        """Assemble all components into a single FeatureVector."""
        try:
            pcr = self.compute_pcr(chain_resp.chain)
            max_pain = self.compute_max_pain(chain_resp.chain)
            indicators = self.compute_indicators(historical)
            
            # Simple regime metrics
            regime = RegimeFeatures(
                volatility_rank=0.5,
                trend_strength=0.6,
                mean_reversion_score=0.4
            )
            
            fv = FeatureVector(
                pcr=pcr,
                iv_skew=0.0,
                max_pain=max_pain,
                oi_change_ce_top5=[],
                oi_change_pe_top5=[],
                vwap_deviation=indicators["vwap_dev"],
                atr_14=indicators["atr_14"],
                rsi_14=indicators["rsi_14"],
                regime_features=regime
            )
            
            if asset_class == "crypto" and orderbook:
                crypto_metrics = self.compute_crypto_metrics(orderbook)
                fv.funding_rate = 0.0001
                fv.open_interest_usd = 1000000000.0
                fv.liquidation_levels = [chain_resp.spot_price * 0.95, chain_resp.spot_price * 1.05]
                fv.liquidation_density = crypto_metrics["liquidation_density"]
                fv.orderbook_imbalance = crypto_metrics["orderbook_imbalance"]
                
            return fv
        except Exception as e:
            logger.error("feature_computation_failed", error=str(e))
            return FeatureVector(
                pcr=0.0, iv_skew=0.0, max_pain=0,
                oi_change_ce_top5=[], oi_change_pe_top5=[],
                vwap_deviation=0.0, atr_14=0.0, rsi_14=50.0,
                regime_features=RegimeFeatures(volatility_rank=0.5, trend_strength=0.0, mean_reversion_score=0.0)
            )
