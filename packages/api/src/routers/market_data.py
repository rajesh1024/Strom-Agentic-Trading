from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
import structlog

from src.models.market import OptionChainResponse, FeatureVector
from src.models.base import Underlying
from src.services.market_data import DataVendorAdapter, MockDataVendor, MarketDataService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/v1/market-data", tags=["market-data"])


def get_market_data_service() -> MarketDataService:
    vendor: DataVendorAdapter = MockDataVendor()
    return MarketDataService(vendor=vendor)


@router.get(
    "/option-chain/{underlying}",
    response_model=OptionChainResponse,
    summary="Get option chain for underlying",
)
async def get_option_chain(
    underlying: str,
    expiry: str = Query(..., description="Expiry date YYYY-MM-DD"),
    service: MarketDataService = Depends(get_market_data_service),
):
    underlying_upper = underlying.upper()
    if underlying_upper not in [u.value for u in Underlying]:
        raise HTTPException(
            status_code=404,
            detail=f"Underlying {underlying} not found. Valid values: NIFTY, BANKNIFTY",
        )

    try:
        result = await service.get_option_chain(underlying_upper, expiry)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("option_chain_error", underlying=underlying, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch option chain")


@router.get(
    "/features/{underlying}",
    response_model=FeatureVector,
    summary="Get computed features for underlying",
)
async def get_features(
    underlying: str,
    expiry: Optional[str] = Query(None, description="Expiry date YYYY-MM-DD"),
    service: MarketDataService = Depends(get_market_data_service),
):
    underlying_upper = underlying.upper()
    if underlying_upper not in [u.value for u in Underlying]:
        raise HTTPException(
            status_code=404,
            detail=f"Underlying {underlying} not found. Valid values: NIFTY, BANKNIFTY",
        )

    if not expiry:
        if underlying_upper == "NIFTY":
            expiry = "2026-03-05"
        elif underlying_upper == "BANKNIFTY":
            expiry = "2026-03-04"

    try:
        result = await service.get_features(underlying_upper, str(expiry))
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("features_error", underlying=underlying, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to compute features")


@router.get("/health", summary="Health check for data vendor")
async def market_data_health(
    service: MarketDataService = Depends(get_market_data_service),
):
    is_healthy = await service.health_check()
    if not is_healthy:
        raise HTTPException(status_code=503, detail="Data vendor unhealthy")
    return {"status": "ok", "vendor": "mock"}
