# vstd_wallet_cli.py

import random
import time
import json
import os
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from layer0.blockchain.core.transaction_type import MintBurnTransaction, Transaction
from layer0.config import ChainConfig
from layer0.p2p.peer_type.remote_peer import RemotePeer
from layer0.wallet.wallet_remote import WalletRemote

app = typer.Typer()
console = Console()

CONFIG_DIR = os.path.expanduser("~/.vstd_wallet")
ALIAS_FILE = os.path.join(CONFIG_DIR, "recipients.json")

# ------------------ UTILS ------------------
def ensure_config():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(ALIAS_FILE):
        with open(ALIAS_FILE, "w") as f:
            json.dump({}, f)

def load_aliases():
    with open(ALIAS_FILE) as f:
        return json.load(f)

def resolve_alias(name_or_address: str) -> str:
    aliases = load_aliases()
    return aliases.get(name_or_address.lower(), name_or_address)

def parse_amount(input_str: str) -> int:
    return int(float(input_str) * ChainConfig.NativeTokenValue)

def format_number_with_spaces(number: float, decimal_places: int = 6) -> str:
    is_negative = number < 0
    abs_number = abs(number)
    integer_part = int(abs_number)
    fractional_part = abs_number - integer_part
    integer_str = str(integer_part)
    formatted_integer_parts = []
    for i in range(len(integer_str) - 1, -1, -1):
        formatted_integer_parts.append(integer_str[i])
        if i > 0 and (len(integer_str) - i) % 3 == 0:
            formatted_integer_parts.append(' ')
    formatted_integer = "".join(reversed(formatted_integer_parts))
    formatted_fractional = f"{fractional_part:.{decimal_places}f}"[2:]
    result = f"{formatted_integer}.{formatted_fractional}"
    return "-" + result if is_negative else result

def confirm_and_sign(wallet: WalletRemote, tx: Transaction) -> bool:
    console.print("\n[bold yellow]Please confirm the transaction:[/bold yellow]")
    table = Table(box=None)
    table.add_row("From:", f"[green]{tx.sender}[/green]")
    table.add_row("To:", f"[cyan]{tx.to}[/cyan]")
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
        console.print("[bold green]\u2713 Transaction signed and sent.[/bold green]")
        return True
    else:
        console.print("[bold red]\u2717 Transaction cancelled.[/bold red]")
        return False

# ------------------ CORE COMMANDS ------------------
@app.command()
def run():
    """Start the wallet in interactive mode."""
    ensure_config()
    PORT: int = random.randint(8000, 9999)
    master = RemotePeer("127.0.0.1", 5000)
    wallet = WalletRemote(master, "127.0.0.1", PORT)

    if Confirm.ask("\n[bold]Do you want to be minter?[/bold]"):
        wallet.import_key("mint_key")

    while True:
        console.clear()
        console.print(Panel("[bold blue]VSTD Terminal Wallet[/bold blue]", subtitle=wallet.address[:20] + "...", width=60))
        table = Table(show_header=True, header_style="bold magenta", box=None)
        table.add_column("Option", style="dim", width=12)
        table.add_column("Action")
        table.add_row("1", "View Balance")
        table.add_row("2", "Mint VSTD")
        table.add_row("3", "Pay VSTD")
        table.add_row("4", "Manage Aliases")
        table.add_row("0", "[red]Exit[/red]")
        console.print(table)
        choice = Prompt.ask("\n[bold green]Select an option[/]")

        if choice == "1":
            console.print(f"[cyan]Your address:[/] [bold green]{wallet.address}[/]")
            console.print(f"[cyan]Your balance:[/] [bold green]{format_number_with_spaces(wallet.get_balance() / ChainConfig.NativeTokenValue)} VSTD[/]")
        elif choice == "2":
            amount_str = Prompt.ask("[yellow]Enter amount of VSTD to mint[/]")
            try:
                amount = parse_amount(amount_str)
                tx = MintBurnTransaction(wallet.address, wallet.address, amount, int(time.time() * 1000), wallet.nonce + 1, 0)
                confirm_and_sign(wallet, tx)
            except Exception as e:
                console.print(f"[red]Invalid amount: {e}[/]")
        elif choice == "3":
            amount_str = Prompt.ask("[yellow]Enter amount of VSTD to pay[/]")
            recipient = Prompt.ask("[yellow]Enter recipient address or alias[/]")
            try:
                amount = parse_amount(amount_str)
                tx = wallet.pay(amount, resolve_alias(recipient))
                confirm_and_sign(wallet, tx)
            except Exception as e:
                console.print(f"[red]Error:[/] {e}")
        elif choice == "4":
            aliases = load_aliases()
            console.print(json.dumps(aliases, indent=2))
            if Confirm.ask("Do you want to add a new alias?"):
                name = Prompt.ask("Alias name").lower()
                address = Prompt.ask("Address")
                aliases[name] = address
                with open(ALIAS_FILE, "w") as f:
                    json.dump(aliases, f, indent=2)
                console.print(f"[green]Alias '{name}' added for {address}[/]")
        elif choice == "0":
            break
        else:
            console.print("[red]Invalid choice[/]")

        console.print("\nPress [bold cyan]Enter[/] to continue...")
        input("")

if __name__ == "__main__":
    app()
