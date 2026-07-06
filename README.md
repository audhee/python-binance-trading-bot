# Binance Futures Testnet Trading Bot

A production-ready Python command-line application to place orders on the Binance Futures Testnet (USDT-M). Built with strict separation of concerns, comprehensive input validation, custom error handling, and secure logging.

---

## Architecture Design

This application is designed using a multi-tiered architecture:

```
                    User
                      │
                      ▼
             Command Line (Typer & Rich) [cli.py]
                      │
                      ▼
            Input Validation Layer [bot/validators.py]
                      │
                      ▼
             Order Service Layer [bot/orders.py]
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
 Binance Client [bot/client.py]   Logger Service [bot/logging_config.py]
        │                           │
        ▼                           ▼
 Binance Futures Testnet      logs/trading_bot.log
```

- **cli.py**: Handles parsing of user CLI parameters or interactive prompts, orchestrates validation, formats and prints rich console panels/errors, and exits with correct shell exit codes.
- **bot/validators.py**: Performs strict bounds and format checks on input parameters (symbol uppercase regex, side matching enums, conditional price checks).
- **bot/orders.py**: The service layer that receives requests and coordinates orders using the client.
- **bot/client.py**: Generates standard request headers and HMAC-SHA256 signatures. Synchronizes client offset with the Binance server time to avoid local clock desync errors.
- **bot/logging_config.py**: Handles logging to `logs/trading_bot.log`. Automatically redacts sensitive fields like API secret and signature to prevent leakage.
- **bot/config.py**: Automatically loads credentials from a `.env` file or environment variables.
- **bot/exceptions.py**: Defines a custom exception hierarchy mapping errors cleanly.

---

## Features
- **Supported Orders**: Market, Limit (requires Price), and Stop-Limit (requires Price and Stop Price) orders.
- **Sides**: BUY (Long) and SELL (Short).
- **Interactive Mode**: Running the CLI with no arguments starts an interactive order placement wizard.
- **Timestamp Desync Protection**: Client queries server time from Binance API to calculate system clock offsets automatically before signing.
- **Security Audit Proof**: Log configurations automatically filter and mask credentials and query signatures.

---

## Setup & Installation

### 1. Prerequisites
- Python 3.8 or higher.
- A Binance Futures Testnet account. You can register and generate keys on the [Binance Futures Testnet](https://testnet.binancefuture.com) website.

### 2. Install Dependencies
Clone the repository and install the required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configuration
Copy the template `.env.example` file to `.env`:
```bash
cp .env.example .env
```
Open `.env` and fill in your Binance Futures Testnet credentials:
```env
BINANCE_API_KEY=your_binance_testnet_api_key
BINANCE_SECRET_KEY=your_binance_testnet_secret_key
BASE_URL=https://testnet.binancefuture.com
```

---

## How to Run (Examples)

### 1. Market Order
Place a market order to buy 0.001 BTC:
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### 2. Limit Order
Place a limit order to sell 0.001 BTC at $105,000:
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 105000
```

### 3. Stop-Limit Order (Bonus Type)
Place a Stop-Limit order to buy 0.002 ETH when price triggers at $3,500, with limit entry at $3,510:
```bash
python cli.py --symbol ETHUSDT --side BUY --type STOP_LIMIT --quantity 0.002 --price 3510 --stop-price 3500
```

### 4. Interactive Mode
Run the script without any parameters to launch the CLI Order Wizard:
```bash
python cli.py
```

---

## Log Output Verification
All requests, API responses, errors, and network issues are logged into:
`logs/trading_bot.log`

Examples of what logs contain:
- Handlers and formatters setup.
- Time synchronization calculations.
- Request payloads with signatures and API keys masked to `********` for security.
- Success and failure details from Binance servers.
