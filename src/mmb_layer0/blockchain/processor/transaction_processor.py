from src.mmb_layer0.blockchain.core.block import Block
from src.mmb_layer0.blockchain.core.transactionType import Transaction, NativeTransaction, MintBurnTransaction
from src.mmb_layer0.blockchain.core.worldstate import WorldState
import json
from rich import print

class TransactionProcessor:
    def __init__(self, block: Block, worldState: WorldState) -> None:
        self.block = block
        # self.transaction = transaction
        self.worldState = worldState

    def process(self) -> None:
        print("TransactionProcessor:process: Process block")
        print(self.block)
        for tx in self.block.data:
            print("TransactionProcessor:process: Process " + tx.Txtype + " transaction")
            if isinstance(tx, NativeTransaction):
                self.process_native_transaction(tx)
            elif isinstance(tx, MintBurnTransaction):
                self.process_mint_burn_transaction(tx)
            elif isinstance(tx, Transaction):
                print("Transaction type is not supported")
                continue

            # Update nonce
            neoa = self.worldState.get_eoa(tx.sender)
            neoa.nonce += 1
            self.worldState.set_eoa(tx.sender, neoa)

    @staticmethod
    def cast_transaction(transaction_raw: str):
        transaction = json.loads(transaction_raw)
        # print(transaction)
        transaction_data = transaction["data"]
        # print(transaction_data)
        match transaction["Txtype"]:
            case "mintburn":
                return MintBurnTransaction(transaction_data["receiver"], transaction_data["amount"], transaction["nonce"], transaction["gasPrice"])
            case "native":
                return NativeTransaction(transaction["sender"], transaction_data["receiver"], transaction_data["amount"], transaction["nonce"], transaction["gasPrice"])
            case _:
                raise Exception("Transaction type is not supported")


    def process_mint_burn_transaction(self, transaction: Transaction) -> None:
        print("TransactionProcessor:process_mint_burn_transaction: Process mint burn transaction")

        # Update world state
        receiver = transaction.transactionData["receiver"]
        amount = transaction.transactionData["amount"]

        if self.worldState.get_eoa(receiver).balance + amount < 0:
            # Clear the balance
            neoa = self.worldState.get_eoa(receiver)
            neoa.balance = 0
            self.worldState.set_eoa(receiver, neoa)
            return

        neoa = self.worldState.get_eoa(receiver)
        neoa.balance += amount
        self.worldState.set_eoa(receiver, neoa)

    def process_native_transaction(self, transaction: NativeTransaction) -> None:
        print("TransactionProcessor:process_native_transaction: Process native transaction, gas fee: " + str(transaction.gasPrice))

        # Update world state
        sender = transaction.sender
        receiver = transaction.transactionData["receiver"]
        amount = transaction.transactionData["amount"]
        gasPrice = transaction.gasPrice

        # self.worldState.get_eoa(sender).balance -= amount + gasPrice
        # self.worldState.get_eoa(receiver).balance += amount

        neoa = self.worldState.get_eoa(sender)
        neoa.balance -= amount + gasPrice
        self.worldState.set_eoa(sender, neoa)

        neoa = self.worldState.get_eoa(receiver)
        neoa.balance += amount
        self.worldState.set_eoa(receiver, neoa)
