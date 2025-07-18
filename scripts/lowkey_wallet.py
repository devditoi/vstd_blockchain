from layer0.config import ChainConfig
from layer0.p2p.peer_type.remote_peer import RemotePeer
from layer0.wallet.wallet_remote import WalletRemote

master: RemotePeer = RemotePeer("127.0.0.1", 5000)
wallet: WalletRemote = WalletRemote(master, "127.0.0.1", 2809)
wallet.import_key("mint_key")


while True:
    command: str = input("> Enter command ('get_balance' or 'mint <amount>'): ").strip()
    if command == "get_balance":
        balance: int = wallet.get_balance()
        print(f"Balance: {balance}")
    elif command.startswith("mint "):
        try:
            amount: int = int(int(command.split()[1]) * ChainConfig.NativeTokenValue)
            mint_for_myself(amount)
            print(f"Minted {amount / ChainConfig.NativeTokenValue} MMB successfully.")
        except (IndexError, ValueError):
            print("Invalid amount. Please enter a valid number.")
    elif command.startswith("pay "):
        try:
            amount = int(float(command.split()[1]) * ChainConfig.NativeTokenValue)
            payee_address: str = command.split()[2]
            wallet.pay(amount, payee_address)
            print(f"Paid {amount / ChainConfig.NativeTokenValue} MMB to {payee_address} successfully. (fee: { ChainConfig.NativeTokenGigaweiValue / ChainConfig.NativeTokenValue} MMB)")
        except (IndexError, ValueError):
            print("Invalid amount or payee address. Please enter a valid number and address.")
    else:
        print("Unknown command. Please enter 'get_balance' or 'mint <amount>'.")
