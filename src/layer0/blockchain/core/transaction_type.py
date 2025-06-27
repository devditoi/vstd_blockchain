from abc import ABC, abstractmethod
import jsonlight
from rsa import PublicKey
from rich import print

from layer0.config import ChainConfig
from layer0.utils.hash import HashUtils


class ITransaction(ABC):
    @abstractmethod
    def to_string(self) -> str:
        pass

class Transaction(ITransaction):
    def __init__(self, sender: str, to: str, Txtype: str, nonce: int, gasLimit: int) -> None:
        self.sender = sender
        self.to = to
        self.Txtype = Txtype
        self.signature = None
        self.publicKey = None
        self.transactionData: dict = {}
        self.gasLimit = gasLimit
        self.nonce = nonce
        self.chainId = 1 # Testnet
        self.hash = HashUtils.sha256(self.to_verifiable_string()) # Hash chain_id of each transaction

        self.status = "pending"

    def to_string(self) -> str:
        return jsonlight.dumps({
            "sender": self.sender,
            "to": self.to,
            "Txtype": self.Txtype,
            "nonce": self.nonce,
            "gasLimit": self.gasLimit,
            "data": self.transactionData,
            "hash": self.hash,
            "signature": self.signature,
            "publicKey": self.publicKey,
        })

    def to_string_with_status(self) -> str:
        return jsonlight.dumps({
            "sender": self.sender,
            "to": self.to,
            "Txtype": self.Txtype,
            "nonce": self.nonce,
            "gasLimit": self.gasLimit,
            "data": self.transactionData,
            "hash": self.hash,
            "signature": self.signature,
            "publicKey": self.publicKey,
            "status": self.status,
        })

    def to_verifiable_string(self) -> str:
        return jsonlight.dumps({
            "sender": self.sender,
            "Txtype": self.Txtype,
            "nonce": self.nonce,
            "gasLimit": self.gasLimit,
            "data": self.transactionData,
        })

    def __repr__(self):
        return self.to_string()

    # Status, gas used
    def process(self, worldState) -> (bool, int):
        ws = worldState
        sender = self.to
        print("Transaction type is not supported")

    @staticmethod
    def max_gas_usage() -> int:
        return 0

class NativeTransaction(Transaction):
    def __init__(self, sender: str, receiver: str, amount: int, nonce: int, gasLimit: int) -> None:
        super().__init__(sender, receiver, "native", nonce, gasLimit)
        self.transactionData["amount"] = amount


    def process(self, worldState) -> (bool, int):

        if self.sender == self.to:
            print(f"[Skip] Tx {self.hash[:8]} is noop (sender == receiver)")
            return True

        print("TransactionProcessor:process_native_transaction: Process native transaction")

        # Update world state
        sender = self.sender
        receiver = self.to
        amount = self.transactionData["amount"]

        # Check if the user has enough balance
        if worldState.get_eoa(sender).balance < amount:
            print("TransactionProcessor:process_native_transaction: Transaction sender does not have enough balance")
            return True, self.max_gas_usage()

        # Deduct the sender
        neoa = worldState.get_eoa(sender)
        neoa.balance -= amount
        worldState.set_eoa(sender, neoa)

        # Add the receiver
        neoa = worldState.get_eoa(receiver)
        neoa.balance += amount
        worldState.set_eoa(receiver, neoa)

        return True, self.max_gas_usage()

    @staticmethod
    def max_gas_usage() -> int:
        return int(ChainConfig.NativeTokenGigaweiValue * 10)

# class StakeTransaction(Transaction):
#     def __init__(self, sender: str, receiver: str, amount: int, nonce: int, gasPrice:int) -> None:
#         super().__init__(sender, receiver, "token", nonce, gasPrice)
#         self.transactionData["amount"] = amount # if it negative means unstake

# class SmartContractTransaction(Transaction):
#     def __init__(self, sender: str, nonce: int, gasPrice: int) -> None:
#         super().__init__(sender, "smartcontract", nonce, gasPrice)
#
# class SmartContractDeployTransaction(Transaction):
#     def __init__(self, sender: str, data: str, nonce: int, gasPrice: int) -> None:
#         super().__init__(sender, "smartcontractdeploy", nonce, gasPrice)
#         self.transactionData["data"] = data
#
# class SmartContractCallTransaction(Transaction):
#     def __init__(self, sender: str, data: str, nonce: int, gasPrice: int) -> None:
#         super().__init__(sender, "smartcontractcall", nonce, gasPrice)
#         self.transactionData["data"] = data
#
class MintBurnTransaction(Transaction):
    def __init__(self, sender: str, receiver: str, amount: int, nonce: int, gasLimit: int) -> None:
        super().__init__(sender, receiver, "mintburn", nonce, gasLimit)
        # self.transactionData["receiver"] = receiver
        self.transactionData["amount"] = amount

    @staticmethod
    def max_gas_usage() -> int:
        return 0

    def process(self, worldState) -> (bool, int):
        print("TransactionProcessor:process_mint_burn_transaction: Process mint burn transaction")
        # Update world state
        receiver = self.to
        amount = self.transactionData["amount"]

        if worldState.get_eoa(receiver).balance + amount < 0: # Ahh this is burn transaction
            # Clear the balance
            neoa = worldState.get_eoa(receiver)
            neoa.balance = 0
            worldState.set_eoa(receiver, neoa)
            return True, ChainConfig.NativeTokenGigaweiValue * 1000 # Charge fee for burning

        neoa = worldState.get_eoa(receiver)
        neoa.balance += amount
        worldState.set_eoa(receiver, neoa)

        return True, ChainConfig.NativeTokenGigaweiValue * 0 # Zero fees

class NopTransaction(Transaction):
    def __init__(self):
        super().__init__("0x0", "0x0", "nop", 0, 0)

    def process(self, worldState) -> (bool, int):
        print("TransactionProcessor:process_nop_transaction: Process noop transaction")
        return True, 0