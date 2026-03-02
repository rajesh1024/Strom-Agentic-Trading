import json
import os
import sys
from pathlib import Path
from pydantic import ValidationError

# Add packages/api to path to import models
root_dir = Path(__file__).parent.parent
api_src = root_dir / "packages" / "api"
sys.path.append(str(api_src))

from src.models import (
    OptionChainResponse, FeatureVector, TradeSignal, PortfolioState, 
    RiskParams, RiskDecision, CryptoOrderbook
)

def validate_fixture(file_path, model, is_list=False):
    print(f"Validating {file_path}...")
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    try:
        if is_list:
            for item in data:
                model.model_validate(item)
        else:
            model.model_validate(data)
        print(f"✅ {file_path} is valid.")
        return True
    except ValidationError as e:
        print(f"❌ {file_path} validation failed!")
        print(e.json())
        return False
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    fixtures_dir = root_dir / "data" / "fixtures"
    
    validations = [
        ("sample_option_chain.json", OptionChainResponse, True),
        ("sample_feature_vector.json", FeatureVector, False),
        ("sample_signals.json", TradeSignal, True),
        ("sample_portfolio.json", PortfolioState, False),
        ("sample_risk_params.json", RiskParams, False),
        ("sample_risk_decision.json", RiskDecision, False),
        ("sample_crypto_orderbook.json", CryptoOrderbook, False)
    ]
    
    all_passed = True
    for filename, model, is_list in validations:
        path = fixtures_dir / filename
        if not validate_fixture(path, model, is_list):
            all_passed = False
            
    if all_passed:
        print("\nAll fixtures validated successfully! 🚀")
        sys.exit(0)
    else:
        print("\nSome fixtures failed validation.")
        sys.exit(1)

if __name__ == "__main__":
    main()
