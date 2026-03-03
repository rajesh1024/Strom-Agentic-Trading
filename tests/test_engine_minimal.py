import pytest
from src.services.market_data.engine import FeatureComputationEngine

def test_minimal():
    engine = FeatureComputationEngine()
    assert engine is not None
