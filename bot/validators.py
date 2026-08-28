import re
from bot.exceptions import ValidationError
from bot.constants import OrderSide, OrderType

def validate_symbol(symbol: str) -> str:
    """Validate and normalize trading symbol (e.g. BTCUSDT)."""
    if not symbol:
        raise ValidationError("Symbol is very much essential")
    
    clean_symbol = symbol.strip().upper()
    if not re.match(r"^[A-Z0-9]{3,20}$", clean_symbol):
        raise ValidationError(
            f"Invalid symbol: '{symbol}'. Use the uppercase alphanumeric strings like BTCUSDT or ETHUSDT."
        )
    return clean_symbol

def validate_side(side: str) -> OrderSide:
    """Validate and normalize order side (BUY/SELL)."""
    if not side:
        raise ValidationError("Order side is required.")
    
    clean_side = side.strip().upper()
    try:
        return OrderSide(clean_side)
    except ValueError:
        valid_sides = ", ".join([s.value for s in OrderSide])
        raise ValidationError(
            f"Invalid side: '{side}'. Must be one of: {valid_sides}."
        )

def validate_order_type(order_type: str) -> OrderType:
    """Validate and normalize order type (MARKET/LIMIT/STOP_LIMIT)."""
    if not order_type:
        raise ValidationError("Order type is required.")
    
    clean_type = order_type.strip().upper().replace("-", "_")
    if clean_type == "STOP":
        clean_type = "STOP_LIMIT"
        
    try:
        return OrderType(clean_type)
    except ValueError:
        valid_types = ", ".join([t.value for t in OrderType])
        raise ValidationError(
            f"Invalid order type: '{order_type}'. Must be one of: {valid_types}."
        )

def validate_quantity(quantity: float) -> float:
    """Validate that quantity is a positive float."""
    if quantity is None:
        raise ValidationError("Quantity is required.")
    try:
        val = float(quantity)
    except (ValueError, TypeError):
        raise ValidationError(f"Quantity must be a numeric value. Got '{quantity}'.")
    
    if val <= 0:
        raise ValidationError(f"Quantity must be greater than zero. Got: {val}")
    return val

def validate_price(price: float, order_type: OrderType) -> float:
    """Validate price for orders that require it."""
    if order_type in (OrderType.LIMIT, OrderType.STOP_LIMIT):
        if price is None:
            raise ValidationError(f"Price is required for {order_type.value} orders.")
        try:
            val = float(price)
        except (ValueError, TypeError):
            raise ValidationError(f"Price must be a numeric value. Got '{price}'.")
        if val <= 0:
            raise ValidationError(f"Price must be greater than zero. Got: {val}")
        return val
    return None

def validate_stop_price(stop_price: float, order_type: OrderType) -> float:
    """Validate stop price for STOP_LIMIT orders."""
    if order_type == OrderType.STOP_LIMIT:
        if stop_price is None:
            raise ValidationError("Stop price is required for STOP_LIMIT orders.")
        try:
            val = float(stop_price)
        except (ValueError, TypeError):
            raise ValidationError(f"Stop price must be a numeric value. Got '{stop_price}'.")
        if val <= 0:
            raise ValidationError(f"Stop price must be greater than zero. Got: {val}")
        return val
    return None
