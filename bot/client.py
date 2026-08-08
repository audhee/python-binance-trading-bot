import hmac
import hashlib
import time
import requests
from urllib.parse import urlencode
from bot.logging_config import logger, redact_sensitive
from bot.exceptions import NetworkError, OrderPlacementError

class BinanceFuturesClient:
    """Binance Futures Testnet API Client Wrapper."""
    
    def __init__(self, api_key: str, secret_key: str, base_url: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key
        })
        self.time_offset = 0
        
    def sync_server_time(self):
        """Fetch server time from Binance and calculate local clock offset."""
        try:
            url = f"{self.base_url}/fapi/v1/time"
            logger.info(f"Syncing time with Binance Futures Testnet at {url}...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            server_time = response.json()["serverTime"]
            local_time = int(time.time() * 1000)
            self.time_offset = server_time - local_time
            logger.info(f"Time synced and are Offset: {self.time_offset}ms (Server time: {server_time})")
        except requests.RequestException as e:
            logger.warning(f"Could not synchronize server time (using local clock)s. Error: {e}")
            self.time_offset = 0
            
    def _get_timestamp(self) -> int:
        return int(time.time() * 1000) + self.time_offset
        
    def _generate_signature(self, query_string: str) -> str:
        return hmac.new(
            self.secret_key.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
    def send_signed_request(self, method: str, path: str, params: dict) -> dict:
        """Sends a signed HTTP request to the Binance Futures API."""
        params = params.copy()
        params["timestamp"] = self._get_timestamp()
        
        # Build query parameters & sign
        query_string = urlencode(params)
        signature = self._generate_signature(query_string)
        query_string += f"&signature={signature}"
        
        url = f"{self.base_url}{path}"
        
        # Secure logging
        safe_params = redact_sensitive(params)
        logger.info(f"Request: {method} {path} - Params: {safe_params}")
        
        try:
            if method.upper() == "POST":
                response = self.session.post(
                    url,
                    data=query_string,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=15
                )
            elif method.upper() == "GET":
                response = self.session.get(
                    url,
                    params=query_string,
                    timeout=15
                )
            else:
                raise ValueError(f"Unsupported request method: {method}")
                
            status_code = response.status_code
            try:
                response_json = response.json()
            except ValueError:
                response_json = {"raw_content": response.text}
                
            safe_response = redact_sensitive(response_json)
            
            if response.ok:
                logger.info(f"Response (HTTP {status_code}): Order Successful. Details: {safe_response}")
                return response_json
            else:
                logger.error(f"Response Error (HTTP {status_code}): {safe_response}")
                api_code = response_json.get("code", -9999)
                api_msg = response_json.get("msg", "Unknown Binance API Error")
                raise OrderPlacementError(code=api_code, message=api_msg, status_code=status_code)
                
        except requests.Timeout as e:
            logger.error(f"Network timeout: {e}")
            raise NetworkError(f"Connection timeout while calling Binance API: {e}")
        except requests.ConnectionError as e:
            logger.error(f"Network connection error: {e}")
            raise NetworkError(f"Unable to connect to Binance API: {e}")
        except requests.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            raise NetworkError(f"HTTP request to Binance failed: {e}")

    def create_market_order(self, symbol: str, side: str, quantity: float) -> dict:
        """Place a MARKET order."""
        params = {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": str(quantity)
        }
        return self.send_signed_request("POST", "/fapi/v1/order", params)
        
    def create_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> dict:
        """Place a LIMIT order (with GTC Time In Force)."""
        params = {
            "symbol": symbol,
            "side": side,
            "type": "LIMIT",
            "quantity": str(quantity),
            "price": str(price),
            "timeInForce": "GTC"
        }
        return self.send_signed_request("POST", "/fapi/v1/order", params)
        
    def create_stop_limit_order(self, symbol: str, side: str, quantity: float, price: float, stop_price: float) -> dict:
        """Place a STOP_LIMIT order (STOP with GTC Time In Force)."""
        params = {
            "symbol": symbol,
            "side": side,
            "type": "STOP",
            "quantity": str(quantity),
            "price": str(price),
            "stopPrice": str(stop_price),
            "timeInForce": "GTC"
        }
        return self.send_signed_request("POST", "/fapi/v1/order", params)
