from bot.client import BinanceFuturesClient
from bot.constants import OrderType, OrderSide
from bot.logging_config import logger

class OrderService:
    """Service layer coordinating order placement logic."""
    
    def __init__(self, client: BinanceFuturesClient):
        self.client = client
        
    def execute_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: float,
        price: float = None,
        stop_price: float = None
    ) -> dict:
        """Directs the order request to the appropriate Binance Client method."""
        logger.info(
            f"Processing {order_type.value} order request for {symbol}: "
            f"Side={side.value}, Quantity={quantity}, Price={price}, StopPrice={stop_price}"
        )
        
        if order_type == OrderType.MARKET:
            raw_response = self.client.create_market_order(
                symbol=symbol,
                side=side.value,
                quantity=quantity
            )
        elif order_type == OrderType.LIMIT:
            raw_response = self.client.create_limit_order(
                symbol=symbol,
                side=side.value,
                quantity=quantity,
                price=price
            )
        elif order_type == OrderType.STOP_LIMIT:
            raw_response = self.client.create_stop_limit_order(
                symbol=symbol,
                side=side.value,
                quantity=quantity,
                price=price,
                stop_price=stop_price
            )
        else:
            raise ValueError(f"Unsupported order type: {order_type}")
            
        logger.info(f"Order executed successfully on Testnet. Order ID: {raw_response.get('orderId')}")
        return raw_response
