import os
from dotenv import load_dotenv
from bot.exceptions import ConfigurationError

# Load environment variables from .env file
load_dotenv()

class Config:
    def __init__(self):
        # Allow reading either BINANCE_SECRET_KEY or BINANCE_API_SECRET
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.secret_key = os.getenv("BINANCE_SECRET_KEY") or os.getenv("BINANCE_API_SECRET")
        self.base_url = os.getenv("BASE_URL", "https://testnet.binancefuture.com")
        
    def validate(self):
        """Validate that all required configurations are present."""
        if not self.api_key or not self.api_key.strip():
            raise ConfigurationError(
                "BINANCE_API_KEY is not configured. Please define it in your .env file or environment variables."
            )
        if not self.secret_key or not self.secret_key.strip():
            raise ConfigurationError(
                "BINANCE_SECRET_KEY is not configured. Please define it in your .env file or environment variables."
            )

config = Config()
