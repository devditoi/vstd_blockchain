from layer0.blockchain.core.worldstate import WorldState
from typing import cast
from typing import TypedDict
from abc import ABC, abstractmethod
import jsonlight
from rich import print

from layer0.config import ChainConfig
from layer0.utils.hash import HashUtils


class ITransaction(ABC):
    @abstractmethod
    def to_string(self) -> str:
        pass

class BaseTransactionData(TypedDict, total=False): 
    amount: int

class Transaction(ITransaction):
    def __init__(self, sender: str, to: str, Txtype: str, timestamp: int, nonce: int, gas_limit: int) -> None:
        self.sender = sender
        self.to = to
        self.Txtype = Txtype
        self.timestamp = timestamp
        self.signature : str | None = None
        self.publicKey : str | None = None
        self.transactionData: BaseTransactionData = {}
        self.gas_limit = gas_limit
        self.nonce = nonce
        self.chainId = 1 # Testnet
        self.hash = HashUtils.sha256(self.to_verifiable_string()) # Hash chain_id of each transaction

        # Offchain data
        self.status = "pending"
        self.gas_used = 0
        self.block_index = -1 # After processing, we will know what block it in
        self.logs = []
        
    def get_logs_hash(self):
        return HashUtils.sha256(jsonlight.dumps(self.logs)) # only need for block confirmation
    
    def get_receipt_hash(self) -> str:
        receipt_data = f"{self.status}{self.gas_used}{self.get_logs_hash()}"
        return HashUtils.sha256(receipt_data)

    def to_string(self) -> str:
        return jsonlight.dumps({
            "sender": self.sender,
            "to": self.to,
            "Txtype": self.Txtype,
            "nonce": self.nonce,
            "gas_limit": self.gas_limit,
            "data": self.transactionData,
            "hash": self.hash,
            "signature": self.signature,
            "publicKey": self.publicKey,
            "timestamp": self.timestamp
        }).replace(" ", "").replace("\n", "")

    def to_string_with_offchain_data(self) -> str:
        return jsonlight.dumps({
            "sender": self.sender,
            "to": self.to,
            "Txtype": self.Txtype,
            "nonce": self.nonce,
            "gas_limit": self.gas_limit,
            "data": self.transactionData,
            "hash": self.hash,
            "signature": self.signature,
            "publicKey": self.publicKey,
            "timestamp": self.timestamp,
            # Offchain data
            "status": self.status,
            "gas_used": self.gas_used,
            "block_index": self.block_index
        }).replace(" ", "").replace("\n", "")

    def to_verifiable_string(self) -> str:
        return jsonlight.dumps({
            "sender": self.sender,
            "Txtype": self.Txtype,
            "nonce": self.nonce,
            "gas_limit": self.gas_limit,
            "data": self.transactionData,
            "timestamp": self.timestamp,
        }).replace(" ", "").replace("\n", "")

    def __repr__(self):
        return self.to_string()

    # Status, gas used
    def process(self, worldState) -> tuple[bool, int]:
        return False, 0

    @staticmethod
    def estimated_gas() -> int:
        return 0

class NativeTransaction(Transaction):
    def __init__(self, sender: str, receiver: str, amount: int, timestamp: int, nonce: int, gas_limit: int) -> None:
        super().__init__(sender, receiver, "native", timestamp, nonce, gas_limit)
        self.transactionData["amount"] = amount


    def process(self, worldState) -> tuple[bool, int]:

        if self.sender == self.to:
            print(f"[Skip] Tx {self.hash[:8]} is noop (sender == receiver)")
            return True, self.estimated_gas()

        print("TransactionProcessor:process_native_transaction: Process native transaction")

        # Update world state
        sender = self.sender
        receiver = self.to
        amount = self.transactionData["amount"]

        # Check if the user has enough balance
        if worldState.get_eoa(sender).balance < amount:
            print("TransactionProcessor:process_native_transaction: Transaction sender does not have enough balance")
            return True, self.estimated_gas()

        # Deduct the sender
        neoa = worldState.get_eoa(sender)
        neoa.balance -= amount
        worldState.set_eoa(sender, neoa)

        # Add the receiver
        neoa = worldState.get_eoa(receiver)
        neoa.balance += amount
        worldState.set_eoa(receiver, neoa)

        return True, self.estimated_gas()

    @staticmethod
    def estimated_gas() -> int:
        return int(ChainConfig.NativeTokenGigaweiValue * 10)

# class StakeTransaction(Transaction):
#     def __init__(self, sender: str, receiver: str, amount: int, nonce: int, gasPrice:int) -> None:
#         super().__init__(sender, receiver, "token", nonce, gasPrice)
#         self.transactionData["amount"] = amount # if it negative means unstake

# class SmartContractTransaction(Transaction):
#     def __init__(self, sender: str, nonce: int, gasPrice: int) -> None:
#         super().__init__(sender, "smartcontract", nonce, gasPrice)
#

# Fixed: Make SmartContractDeployTransactionData inherit from BaseTransactionData
class SmartContractDeployTransactionData(BaseTransactionData):
    contract_name: str
    contract_code: str
    timestamp: int
    creator: str

class SmartContractDeployTransaction(Transaction):    
    def __init__(self, sender: str, data: SmartContractDeployTransactionData, timestamp: int, nonce: int, gas_limit: int) -> None:
        super().__init__(sender, "0", "smartcontractdeploy", timestamp, nonce, gas_limit)
        # data
        
        self.transactionData = cast(SmartContractDeployTransactionData, data)
        
    def process(self, worldState) -> tuple[bool, int]:
        
        # Deploy this contract
        
        contract_name: str = cast(str, self.transactionData.get("contract_name", ""))
        contract_code: str = cast(str, self.transactionData.get("contract_code", ""))
        
        if contract_name == "" or contract_code == "":
            print("TransactionProcessor:process_smart_contract_deploy_transaction: Contract name or contract code is empty")
            return False, self.estimated_gas()
        
        contract_address: str = HashUtils.sha256( contract_name + contract_code)
        
        # Examine the contract code
        
        
        return True, self.estimated_gas()
    
    def estimated_gas(self) -> int:
        return int(ChainConfig.NativeTokenGigaweiValue * 100)
#
# class SmartContractCallTransaction(Transaction):
#     def __init__(self, sender: str, data: str, nonce: int, gasPrice: int) -> None:
#         super().__init__(sender, "smartcontractcall", nonce, gasPrice)
#         self.transactionData["data"] = data
#
class MintBurnTransaction(Transaction):
    def __init__(self, sender: str, receiver: str, amount: int, timestamp: int, nonce: int, gas_limit: int) -> None:
        super().__init__(sender, receiver, "mintburn", timestamp, nonce, gas_limit)
        # self.transactionData["receiver"] = receiver
        self.transactionData["amount"] = amount

    @staticmethod
    def estimated_gas() -> int:
        return 0

    def process(self, worldState) -> tuple[bool, int]:
        print("TransactionProcessor:process_mint_burn_transaction: Process mint burn transaction")
        # Update world state
        receiver: str = self.to
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

class ValidatorTransactionData(BaseTransactionData):
    validator: str # the address
    proof: str # The puzzle

class ValidatorTransaction(Transaction):
    def __init__(self, sender: str, validator: ValidatorTransactionData, timestamp: int, nonce: int, gas_limit: int) -> None:
        super().__init__(sender, "0", "validator", timestamp, nonce, gas_limit)
        # data

        self.transactionData = cast(ValidatorTransactionData, validator)

    def process(self, worldState: WorldState) -> tuple[bool, int]:

        validator = cast(str, self.transactionData.get("validator", ""))
        
        if validator == "":
            print("TransactionProcessor:process_validator_transaction: Validator is empty")

        if self.sender == validator:
            print("TransactionProcessor:process_validator_transaction: Process validator transaction")
            
            worldState.add_validator(validator)
            
            return True, self.estimated_gas()

        print("TransactionProcessor:process_validator_transaction: Validator is not the sender")
        return False, self.estimated_gas()
    
    def estimated_gas(self) -> int:
        return int(ChainConfig.NativeTokenGigaweiValue * 0) # Free for now.

class NopTransaction(Transaction):
    def __init__(self) -> None:
        super().__init__("0x0", "0x0", "nop", 0, 0, 0)

    def process(self, worldState) -> tuple[bool, int]:
        print("TransactionProcessor:process_nop_transaction: Process noop transaction")
        return True, 0