import time
from layer0.blockchain.core.transaction_type import MintBurnTransaction
from layer0.config import ChainConfig
from layer0.p2p.peer_type.remote_peer import RemotePeer
from layer0.wallet.wallet_remote import WalletRemote
from layer0.utils.logger import Logger

logger = Logger("lowkey_wallet")

master: RemotePeer = RemotePeer("127.0.0.1", 5000)
wallet: WalletRemote = WalletRemote(master, "127.0.0.1", 2809)
wallet.import_key("mint_key")


while True:
    command: str = input("> Enter command ('get_balance' or 'mint <amount>'): ").strip()
    if command == "get_balance":
        balance: int = wallet.get_balance()
        logger.log(f"[bold green]Balance:[/] {balance}")
    elif command.startswith("mint "):
        try:
            amount: int = int(int(command.split()[1]) * ChainConfig.NativeTokenValue)
            tx = MintBurnTransaction(
                sender=wallet.address,
                receiver=wallet.address,
                amount=amount,
                timestamp=int(time.time() * 1000),
                nonce=wallet.nonce + 1,
                gas_limit=0
            )
            wallet.sign_and_post_transaction(tx)
            logger.log(f"[bold green]Minted {amount / ChainConfig.NativeTokenValue} MMB successfully.[/]")
        except (IndexError, ValueError):
            logger.log("[bold red]Invalid amount. Please enter a valid number.[/]")
    elif command.startswith("pay "):
        try:
            amount = int(float(command.split()[1]) * ChainConfig.NativeTokenValue)
            payee_address: str = command.split()[2]
            wallet.pay(amount, payee_address)
            logger.log(f"[bold green]Paid {amount / ChainConfig.NativeTokenValue} MMB to {payee_address} successfully. (fee: { ChainConfig.NativeTokenGigaweiValue / ChainConfig.NativeTokenValue} MMB)[/]")
        except (IndexError, ValueError):
            logger.log("[bold red]Invalid amount or payee address. Please enter a valid number and address.[/]")
    else:
        logger.log("[bold red]Unknown command. Please enter 'get_balance' or 'mint <amount>'.[/]")
