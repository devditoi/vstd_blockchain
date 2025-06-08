from abc import ABC, abstractmethod
import jsonlight
from rsa import PublicKey
from rich import print

from mmb_layer0.utils.hash import HashUtils


class ITransaction(ABC):
    @abstractmethod
    def to_string(self) -> str:
        pass

class Transaction(ITransaction):
    def __init__(self, sender: str, Txtype: str, nonce: int, gasPrice: int) -> None:
        self.sender = sender
        self.Txtype = Txtype
        self.signature = None
        self.publicKey = None
        self.transactionData: dict = {}
        self.gasPrice = gasPrice
        self.nonce = nonce
        self.hash = HashUtils.sha256(self.to_verifiable_string()) # Hash id of each transaction
        
    def to_string(self) -> str:
        return jsonlight.dumps({
            "sender": self.sender,
            "Txtype": self.Txtype,
            "nonce": self.nonce,
            "gasPrice": self.gasPrice,
            "data": self.transactionData,
            "hash": self.hash,
            "signature": self.signature,
            "publicKey": self.publicKey,
        })

    def to_verifiable_string(self) -> str:
        return jsonlight.dumps({
            "sender": self.sender,
            "Txtype": self.Txtype,
            "nonce": self.nonce,
            "gasPrice": self.gasPrice,
            "data": self.transactionData,
        })

    def __repr__(self):
        return self.to_string()

class NativeTransaction(Transaction):
    def __init__(self, sender: str, receiver: str, amount: int, nonce: int, gasPrice: int) -> None:
        super().__init__(sender, "native", nonce, gasPrice)
        self.transactionData["receiver"] = receiver
        self.transactionData["amount"] = amount

class StakeTransaction(Transaction):
    def __init__(self, sender: str, receiver: str, amount: int, nonce: int, gasPrice:int) -> None:
        super().__init__(sender, "token", nonce, gasPrice)
        self.transactionData["receiver"] = receiver
        self.transactionData["amount"] = amount # if it negative means unstake

class SmartContractTransaction(Transaction):
    def __init__(self, sender: str, nonce: int, gasPrice: int) -> None:
        super().__init__(sender, "smartcontract", nonce, gasPrice)

class SmartContractDeployTransaction(Transaction):
    def __init__(self, sender: str, data: str, nonce: int, gasPrice: int) -> None:
        super().__init__(sender, "smartcontractdeploy", nonce, gasPrice)
        self.transactionData["data"] = data

class SmartContractCallTransaction(Transaction):
    def __init__(self, sender: str, data: str, nonce: int, gasPrice: int) -> None:
        super().__init__(sender, "smartcontractcall", nonce, gasPrice)
        self.transactionData["data"] = data

class MintBurnTransaction(Transaction):
    def __init__(self, receiver: str, amount: int, nonce: int, gasPrice: int) -> None:
        super().__init__("0x0", "mintburn", nonce, gasPrice)
        self.transactionData["receiver"] = receiver
        self.transactionData["amount"] = amount
