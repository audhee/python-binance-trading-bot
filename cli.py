import typer
from rich.console import Console
from typing import Optional
from bot.config import config
from bot.client import BinanceFuturesClient
from bot.orders import OrderService
from bot.constants import OrderType, OrderSide
from bot.exceptions import (
    ValidationError,
    ConfigurationError,
    NetworkError,
    OrderPlacementError
)
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price
)

console = Console()

def print_error(reason: str, suggestion: str):
    """Print error details using the exact format requested."""
    console.print("\n[red]=================================[/red]")
    console.print("[bold red]             ERROR             [/bold red]")
    console.print("[red]=================================[/red]")
    console.print(f"\n[bold]Reason:[/bold]\n{reason}\n")
    console.print(f"[bold]Suggestion:[/bold]\n{suggestion}\n")

def get_suggestion_for_validation(err_msg: str) -> str:
    """Helper to return user-friendly hints for ValidationError."""
    err_lower = err_msg.lower()
    if "symbol" in err_lower:
        return "Use symbols like BTCUSDT or ETHUSDT."
    elif "side" in err_lower:
        return "Use BUY to go long, or SELL to go short."
    elif "order type" in err_lower:
        return "Use MARKET for instant execution, LIMIT to specify price, or STOP_LIMIT."
    elif "quantity" in err_lower:
        return "Ensure quantity is greater than 0 and matches contract minimums."
    elif "price" in err_lower:
        return "Provide a valid price greater than 0."
    elif "stop price" in err_lower:
        return "Provide a valid stop price greater than 0."
    return "Check CLI options and parameter formatting."

def run_interactive():
    """Fallback interactive order wizard."""
    console.print("[bold cyan]Welcome to the Binance Futures Interactive Order Wizard![/bold cyan]")
    console.print("Press Ctrl+C at any time to exit.\n")
    try:
        # Prompt for symbol
        symbol = console.input("[bold yellow]Enter Symbol (default BTCUSDT): [/bold yellow]").strip()
        if not symbol:
            symbol = "BTCUSDT"
            
        # Prompt for side
        side = console.input("[bold yellow]Enter Side (BUY/SELL, default BUY): [/bold yellow]").strip()
        if not side:
            side = "BUY"
            
        # Prompt for type
        order_type = console.input("[bold yellow]Enter Order Type (MARKET/LIMIT/STOP_LIMIT, default MARKET): [/bold yellow]").strip()
        if not order_type:
            order_type = "MARKET"
            
        # Prompt for quantity
        quantity_str = console.input("[bold yellow]Enter Quantity (e.g. 0.001): [/bold yellow]").strip()
        try:
            quantity = float(quantity_str) if quantity_str else None
        except ValueError:
            quantity = quantity_str  # Let validators raise validation error
            
        price = None
        stop_price = None
        
        # Normalizing type for conditional price prompts
        normalized_type = order_type.upper().replace("-", "_")
        if normalized_type == "STOP":
            normalized_type = "STOP_LIMIT"
            
        if normalized_type in ("LIMIT", "STOP_LIMIT"):
            price_str = console.input("[bold yellow]Enter Price: [/bold yellow]").strip()
            try:
                price = float(price_str) if price_str else None
            except ValueError:
                price = price_str
                
        if normalized_type == "STOP_LIMIT":
            stop_price_str = console.input("[bold yellow]Enter Stop Price: [/bold yellow]").strip()
            try:
                stop_price = float(stop_price_str) if stop_price_str else None
            except ValueError:
                stop_price = stop_price_str
                
        # Validate inputs
        valid_symbol = validate_symbol(symbol)
        valid_side = validate_side(side)
        valid_type = validate_order_type(order_type)
        valid_quantity = validate_quantity(quantity)
        valid_price = validate_price(price, valid_type)
        valid_stop_price = validate_stop_price(stop_price, valid_type)
        
        execute_and_display(
            valid_symbol, valid_side, valid_type, valid_quantity, valid_price, valid_stop_price
        )
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Interactive wizard cancelled.[/yellow]")
        raise typer.Exit(code=0)

def execute_and_display(
    symbol: str,
    side: OrderSide,
    order_type: OrderType,
    quantity: float,
    price: Optional[float],
    stop_price: Optional[float]
):
    """Orchestrate validation, request display, API client calls and response formatting."""
    # Print Order Request Summary
    console.print("\n=================================")
    console.print("Order Request Summary")
    console.print("=================================")
    console.print(f"Symbol      : {symbol}")
    console.print(f"Side        : {side.value}")
    console.print(f"Order Type  : {order_type.value}")
    console.print(f"Quantity    : {quantity}")
    if price is not None:
        console.print(f"Price       : {price}")
    if stop_price is not None:
        console.print(f"Stop Price  : {stop_price}")
    console.print()

    # Initialize Client & Service
    client = BinanceFuturesClient(
        api_key=config.api_key,
        secret_key=config.secret_key,
        base_url=config.base_url
    )
    
    # Synchronize client time offset with server time
    client.sync_server_time()
    
    service = OrderService(client)
    response = service.execute_order(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
        stop_price=stop_price
    )
    
    # Format & Print Response
    console.print("=================================")
    console.print("Order Response")
    console.print("=================================")
    
    order_id = response.get("orderId", "N/A")
    status = response.get("status", "N/A")
    executed_qty = response.get("executedQty", "N/A")
    
    # Fallback to general price if avgPrice is 0.0 or not present
    avg_price = response.get("avgPrice")
    if not avg_price or float(avg_price) == 0:
        avg_price = response.get("price", "N/A")
        
    console.print(f"Order ID    : {order_id}")
    console.print(f"Status      : {status}")
    console.print(f"ExecutedQty : {executed_qty}")
    console.print(f"Avg Price   : {avg_price}")
    console.print()
    console.print("[bold green]SUCCESS[/bold green]")

def main(
    symbol: Optional[str] = typer.Option(None, "--symbol", help="Trading symbol (e.g. BTCUSDT)"),
    side: Optional[str] = typer.Option(None, "--side", help="Order side (BUY or SELL)"),
    order_type: Optional[str] = typer.Option(None, "--type", help="Order type (MARKET, LIMIT, STOP_LIMIT)"),
    quantity: Optional[float] = typer.Option(None, "--quantity", help="Order quantity"),
    price: Optional[float] = typer.Option(None, "--price", help="Limit price (required for LIMIT / STOP_LIMIT)"),
    stop_price: Optional[float] = typer.Option(None, "--stop-price", help="Stop trigger price (required for STOP_LIMIT)")
):
    """Binance Futures Testnet CLI bot interface."""
    try:
        # Check config variables
        config.validate()
        
        # If no arguments provided at all, drop into the interactive prompt wizard
        if (
            symbol is None
            and side is None
            and order_type is None
            and quantity is None
            and price is None
            and stop_price is None
        ):
            run_interactive()
            return
            
        # Ensure we have all core required fields if run in command line argument mode
        missing = []
        if symbol is None:
            missing.append("--symbol")
        if side is None:
            missing.append("--side")
        if order_type is None:
            missing.append("--type")
        if quantity is None:
            missing.append("--quantity")
            
        if missing:
            raise ValidationError(
                f"Missing required arguments: {', '.join(missing)}.\n"
                f"For help, run with --help. Or run without any arguments to start interactive wizard."
            )
            
        # Validate inputs
        valid_symbol = validate_symbol(symbol)
        valid_side = validate_side(side)
        valid_type = validate_order_type(order_type)
        valid_quantity = validate_quantity(quantity)
        valid_price = validate_price(price, valid_type)
        valid_stop_price = validate_stop_price(stop_price, valid_type)
        
        # Execute and display order response
        execute_and_display(
            valid_symbol, valid_side, valid_type, valid_quantity, valid_price, valid_stop_price
        )

    except ValidationError as e:
        print_error(str(e), get_suggestion_for_validation(str(e)))
        raise typer.Exit(code=1)
        
    except ConfigurationError as e:
        print_error(
            str(e),
            "Generate Testnet keys on testnet.binancefuture.com and paste them in a .env file."
        )
        raise typer.Exit(code=1)
        
    except NetworkError as e:
        print_error(
            "Unable to connect to Binance.",
            f"{str(e)}\n\nVerify internet connection, proxy settings, or Binance server status."
        )
        raise typer.Exit(code=1)
        
    except OrderPlacementError as e:
        print_error(
            f"Binance Exception (Code: {e.code}): {e.message}",
            "Ensure the symbol is correct, your account has sufficient margin/USDT balance, and orders satisfy size limits."
        )
        raise typer.Exit(code=1)
        
    except Exception as e:
        import traceback
        print_error(
            f"An unexpected error occurred: {str(e)}",
            f"Traceback:\n{traceback.format_exc()}\nPlease report this issue or retry."
        )
        raise typer.Exit(code=1)

if __name__ == "__main__":
    typer.run(main)
