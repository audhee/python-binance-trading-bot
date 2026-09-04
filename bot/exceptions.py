class TradingBotException(Exception):
    """Base exception class for all trading bot related errors."""
    pass

class ValidationError(TradingBotException):
    """Raised when validation of input parameters fails."""
    """ Added the documentation """
    pass

class ConfigurationError(TradingBotException):
    """Raised when environment variables or configurations are missing or incorrect."""
    pass

class NetworkError(TradingBotException):
    """Raised when request timeout or connectivity issue occurs."""
    pass

class OrderPlacementError(TradingBotException):
    """Raised when the order could not be placed due to Binance API returning an error."""
    def __init__(self, code: int, message: str, status_code: int = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(f"Binance API Error Code :  (Code: {code}): {message}")
