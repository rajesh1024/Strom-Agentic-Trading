import time
import asyncio
from typing import List, Dict, Optional, Any
import httpx
import structlog
from src.config import settings
from src.services.execution.adapter import BrokerAdapter

logger = structlog.get_logger(__name__)

class DhanBrokerAdapter(BrokerAdapter):
    BASE_URL = "https://api.dhan.co"
    
    def __init__(self, client_id: str = None, access_token: str = None, mock: bool = False):
        self.client_id = client_id or settings.dhan_client_id or "MOCK_CLIENT_ID"
        self.access_token = access_token or settings.dhan_access_token or "MOCK_TOKEN"
        self.mock = mock
        self.headers = {
            "access-token": self.access_token,
            "client-id": self.client_id,
            "Content-Type": "application/json"
        }
        self.rate_limit = 10  # 10 req/sec
        self._request_times = []
        
        # Hardcoded mapping for common indices for testing/mocking
        self._instrument_map = {
            "NIFTY": "13",
            "BANKNIFTY": "25",
        }

    async def _check_rate_limit(self):
        now = time.time()
        # Remove requests older than 1 second
        self._request_times = [t for t in self._request_times if now - t < 1.0]
        
        if len(self._request_times) >= self.rate_limit:
            logger.warning("rate_limit_exceeded", count=len(self._request_times))
            raise Exception("Rate limit exceeded: > 10 requests per second")
        
        self._request_times.append(now)

    async def _make_request(self, method: str, path: str, payload: Dict = None) -> Dict:
        await self._check_rate_limit()
        
        if self.mock:
            return self._mock_response(method, path, payload)
            
        async with httpx.AsyncClient() as client:
            url = f"{self.BASE_URL}{path}"
            try:
                if method == "GET":
                    response = await client.get(url, headers=self.headers)
                elif method == "POST":
                    response = await client.post(url, headers=self.headers, json=payload)
                elif method == "DELETE":
                    response = await client.delete(url, headers=self.headers)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error("dhan_api_error", status_code=e.response.status_code, response=e.response.text)
                return self._handle_error(e.response)
            except Exception as e:
                logger.error("dhan_api_exception", error=str(e))
                raise

    def _handle_error(self, response: httpx.Response) -> Dict:
        try:
            error_data = response.json()
        except:
            error_data = {}
            
        error_code = error_data.get("errorCode", "UNKNOWN")
        message = error_data.get("errorMessage", response.text or "Unknown error")
        
        if response.status_code == 429:
            raise Exception(f"Dhan Rate limit exceeded: {message}")
        elif response.status_code == 401:
            raise Exception(f"Dhan Unauthorized: {message}")
            
        raise Exception(f"Dhan Error [{error_code}]: {message}")

    async def place_order(self, instrument: str, side: str, qty: int,
                          order_type: str, price: float | None,
                          trigger_price: float | None, tag: str) -> dict:
        """
        Place order on Dhan.
        instrument: internal instrument name (e.g. "NIFTY23MAR17500CE")
        side: "BUY" or "SELL"
        qty: quantity
        order_type: "LIMIT", "MARKET", "SL", "SLM"
        """
        # Map instrument to Dhan securityId
        security_id = self._instrument_map.get(instrument, instrument)
        
        # Determine product type
        product_type = "INTRADAY" if "MIS" in tag.upper() or "MIS" in order_type.upper() else "MARGIN"
        if "CNC" in tag.upper():
            product_type = "CNC"
        elif "NRML" in tag.upper():
            product_type = "MARGIN"

        payload = {
            "dhanClientId": self.client_id,
            "correlationId": f"ord_{int(time.time()*1000)}",
            "transactionType": side.upper(),
            "exchangeSegment": "NSE_FNO" if any(x in instrument for x in ["NIFTY", "BANKNIFTY"]) else "NSE_EQ",
            "productType": product_type,
            "orderType": order_type.upper(),
            "validity": "DAY",
            "securityId": security_id,
            "quantity": qty,
            "price": price or 0,
            "triggerPrice": trigger_price or 0,
        }
        
        result = await self._make_request("POST", "/orders", payload)
        
        return {
            "order_id": result.get("orderId"),
            "status": result.get("orderStatus", "PENDING"),
            "broker_ref": result.get("orderId"),
            "raw": result
        }

    async def get_order_status(self, order_id: str) -> dict:
        result = await self._make_request("GET", f"/orders/{order_id}")
        
        status_map = {
            "TRANSIT": "PENDING",
            "PENDING": "PENDING",
            "TRADED": "FILLED",
            "CANCELLED": "CANCELLED",
            "REJECTED": "REJECTED"
        }
        
        raw_status = result.get("orderStatus", "UNKNOWN")
        return {
            "order_id": order_id,
            "status": status_map.get(raw_status, raw_status),
            "filled_qty": result.get("tradedQuantity", 0),
            "avg_fill_price": result.get("avgPrice", 0),
            "raw": result
        }

    async def cancel_order(self, order_id: str) -> dict:
        result = await self._make_request("DELETE", f"/orders/{order_id}")
        return {
            "order_id": order_id,
            "cancelled": result.get("orderStatus") == "CANCELLED",
            "raw": result
        }

    async def get_positions(self) -> List[Dict[str, Any]]:
        result = await self._make_request("GET", "/positions")
        if not isinstance(result, list):
            return []
            
        positions = []
        for p in result:
            positions.append({
                "instrument": p.get("tradingSymbol"),
                "qty": p.get("netQty", 0),
                "avg_price": p.get("buyAvg", 0),
                "ltp": p.get("lastTradedPrice", 0),
                "pnl": p.get("unrealizedProfit", 0),
                "raw": p
            })
        return positions

    async def get_margins(self) -> Dict[str, Any]:
        result = await self._make_request("GET", "/margin")
        return {
            "used": result.get("utilizedMargin", 0),
            "available": result.get("availableBalance", 0),
            "total": result.get("availableBalance", 0) + result.get("utilizedMargin", 0),
            "raw": result
        }

    def _mock_response(self, method: str, path: str, payload: Dict) -> Dict:
        if path == "/orders":
            return {"orderId": "mock_ord_123", "orderStatus": "PENDING"}
        elif "/orders/" in path:
            if method == "GET":
                return {
                    "orderId": path.split("/")[-1],
                    "orderStatus": "TRADED",
                    "tradedQuantity": 10,
                    "avgPrice": 105.5
                }
            elif method == "DELETE":
                return {
                    "orderId": path.split("/")[-1],
                    "orderStatus": "CANCELLED"
                }
        elif path == "/positions":
            return [
                {
                    "tradingSymbol": "NIFTY23MAR17500CE",
                    "netQty": 50,
                    "buyAvg": 100.0,
                    "lastTradedPrice": 110.0,
                    "unrealizedProfit": 500.0
                }
            ]
        elif path == "/margin":
            return {
                "utilizedMargin": 50000,
                "availableBalance": 150000
            }
        return {}
