import pytest
import json
import os
from src.services.market_data.engine import FeatureComputationEngine

def test_greeks_accuracy():
    engine = FeatureComputationEngine()
    # Load reference
    with open("data/fixtures/ref_greeks.json") as f:
        ref = json.load(f)["reference_greeks"]
    
    # Test Call
    c_greeks = engine.calculate_greeks(ref["S"], ref["K"], ref["T"], ref["v"], ref["r"], is_call=True)
    assert c_greeks["delta"] == pytest.approx(ref["call"]["delta"], abs=0.01)
    assert c_greeks["gamma"] == pytest.approx(ref["call"]["gamma"], abs=0.01)
    assert c_greeks["vega"] == pytest.approx(ref["call"]["vega"], abs=0.01)
    
    # Test Put
    p_greeks = engine.calculate_greeks(ref["S"], ref["K"], ref["T"], ref["v"], ref["r"], is_call=False)
    assert p_greeks["delta"] == pytest.approx(ref["put"]["delta"], abs=0.01)

def test_pcr_max_pain():
    engine = FeatureComputationEngine()
    from src.models.market import OptionStrike
    chain = [
        OptionStrike(strike=90, ce_ltp=10, pe_ltp=1, ce_oi=1000, pe_oi=5000, ce_iv=0.2, pe_iv=0.2),
        OptionStrike(strike=100, ce_ltp=5, pe_ltp=5, ce_oi=2000, pe_oi=2000, ce_iv=0.2, pe_iv=0.2),
        OptionStrike(strike=110, ce_ltp=1, pe_ltp=10, ce_oi=5000, pe_oi=1000, ce_iv=0.2, pe_iv=0.2),
    ]
    assert engine.compute_pcr(chain) == 1.0 # (5+2+1)/(1+2+5)
    assert engine.compute_max_pain(chain) == 100
