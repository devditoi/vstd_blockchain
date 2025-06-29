import random

from layer0.blockchain.core.transaction_type import MintBurnTransaction, Transaction
from layer0.config import ChainConfig
from layer0.p2p.peer_type.remote_peer import RemotePeer
from layer0.wallet.wallet_remote import WalletRemote
import locale
import typer
from rich import print
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
import time

console = Console()
app = typer.Typer()

def format_number_with_spaces(number: float, decimal_places: int = 6) -> str:
    """
    Formats a number by adding spaces as thousands separators to the integer part
    and maintaining the fractional part to a specified number of decimal places.

    Args:
        number (float): The number to format.
        decimal_places (int): The number of decimal places to include in the fractional part.

    Returns:
        str: The formatted string.
    """
    if not isinstance(number, (int, float)):
        raise TypeError("Input must be an integer or a float.")

    # Determine if the number is negative
    is_negative = number < 0
    abs_number = abs(number)

    # Separate integer and fractional parts
    integer_part = int(abs_number)
    fractional_part = abs_number - integer_part

    # Format the integer part with spaces
    integer_str = str(integer_part)
    formatted_integer_parts = []
    # Iterate from right to left, adding spaces every 3 digits
    for i in range(len(integer_str) - 1, -1, -1):
        formatted_integer_parts.append(integer_str[i])
        if i > 0 and (len(integer_str) - i) % 3 == 0:
            formatted_integer_parts.append(' ')
    # Reverse the list and join to get the correctly spaced integer string
    formatted_integer = "".join(reversed(formatted_integer_parts))

    # Format the fractional part
    # We convert to string first, then remove the "0." if it exists
    formatted_fractional = f"{fractional_part:.{decimal_places}f}"[2:]

    # Combine parts and add back the negative sign if necessary
    result = f"{formatted_integer}.{formatted_fractional}"
    if is_negative:
        result = "-" + result

    return result

def confirm_and_sign(tx: Transaction) -> bool:
    """
    Hiển thị thông tin transaction và hỏi người dùng có muốn ký không.
    """
    console.print("\n[bold yellow]Please confirm the transaction:[/bold yellow]")

    table = Table(box=None)
    table.add_row("From:", f"[green]{tx.sender}[/green]")
    table.add_row("To:", f"[cyan]{tx.to}[/cyan]")
    # table.add_row("Amount:", f"[bold]{tx.amount / ChainConfig.NativeTokenValue:.6f} VSTD[/bold]")
    for key, value in tx.transactionData.items():
        if key == "amount":
            value = format_number_with_spaces(float(value) / ChainConfig.NativeTokenValue) + " VSTD"
        table.add_row(str(key), str(value))
    table.add_row("Fee:", f"{tx.gas_limit / ChainConfig.NativeTokenValue:.6f} VSTD")
    table.add_row("Nonce:", f"{tx.nonce}")
    table.add_row("Type:", f"{tx.Txtype}")
    console.print(table)

    if Confirm.ask("\n[bold]Do you want to sign and send this transaction?[/bold]"):
        wallet.sign_and_post_transaction(tx)
        console.print("[bold green]✓ Transaction signed and sent.[/bold green]")
        return True
    else:
        console.print("[bold red]✗ Transaction cancelled.[/bold red]")
        return False

# ---- INIT WALLET ----

# Choose random port
PORT = random.randint(8000, 9999)

master = RemotePeer("127.0.0.1", 5000)
wallet = WalletRemote(master, "127.0.0.1", PORT)

if Confirm.ask("\n[bold]Do you want to be minter?[/bold]"):
    wallet.import_key("mint_key")



# ---- ACTIONS ----
def show_balance():
    console.print(f"[cyan]Your address:[/] [bold green]{wallet.address}[/]")
    console.print(f"[cyan]Your balance:[/] [bold green]{format_number_with_spaces(wallet.get_balance() / ChainConfig.NativeTokenValue)} VSTD[/]")


def mint_tokens():
    amount_str = Prompt.ask("[yellow]Enter amount of VSTD to mint[/]")
    try:
        amount = int(float(amount_str) * ChainConfig.NativeTokenValue)
        tx = MintBurnTransaction(wallet.address, wallet.address, amount, int(time.time() * 1000), wallet.nonce + 1, 0)
        # wallet.sign_and_post_transaction(tx)
        if confirm_and_sign(tx):
            console.print(f"[green]✓ Minted {format_number_with_spaces(amount / ChainConfig.NativeTokenValue)} VSTD successfully.[/]")
    except ValueError:
        console.print("[red]Invalid amount.[/]")

def pay_tokens():
    amount_str = Prompt.ask("[yellow]Enter amount of VSTD to pay[/]")
    address = Prompt.ask("[yellow]Enter recipient address[/]")
    try:
        amount = int(float(amount_str) * ChainConfig.NativeTokenValue)
        wallet.pay(amount, address)
        if confirm_and_sign(wallet.pay(amount, address)):
            console.print(f"[green]✓ Paid {format_number_with_spaces(amount / ChainConfig.NativeTokenValue)} VSTD to {address} successfully.[/]")
        # console.print(f"[dim]Network fee: {ChainConfig.NativeTokenGigaweiValue / ChainConfig.NativeTokenValue} VSTD[/]")
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")

# ---- MAIN LOOP ----
def main_loop():
    while True:
        console.clear()
        console.print(Panel("[bold blue]VSTD Terminal Wallet[/bold blue]", subtitle=wallet.address[:20] + "...", width=60))

        table = Table(show_header=True, header_style="bold magenta", box=None)
        table.add_column("Option", style="dim", width=12)
        table.add_column("Action")
        table.add_row("1", "View Balance")
        table.add_row("2", "Mint VSTD")
        table.add_row("3", "Pay VSTD")
        table.add_row("0", "[red]Exit[/red]")
        console.print(table)

        choice = Prompt.ask("\n[bold green]Select an option[/]")

        if choice == "1":
            show_balance()
        elif choice == "2":
            mint_tokens()
        elif choice == "3":
            pay_tokens()
        elif choice == "0":
            console.print("[yellow]Exiting wallet...[/]")
            break
        else:
            console.print("[red]Invalid choice[/]")

        console.print("\nPress [bold cyan]Enter[/] to continue...")
        input("")

# ---- Entry Point ----
@app.command()
def run():
    main_loop()

if __name__ == "__main__":
    app()
