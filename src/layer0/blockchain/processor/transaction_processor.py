from layer0.blockchain.core.block import Block
from layer0.blockchain.core.transaction_type import Transaction, NativeTransaction, MintBurnTransaction, NopTransaction
from layer0.blockchain.core.worldstate import WorldState
import json
from rich import print


def cast_raw_transaction(transaction, transaction_data):
    match transaction["Txtype"]:
        case "mintburn":
            return MintBurnTransaction(transaction["to"], transaction_data["amount"],
                                       transaction["nonce"], transaction["gasLimit"])
        case "native":
            return NativeTransaction(transaction["sender"], transaction["to"],
                                     transaction_data["amount"], transaction["nonce"], transaction["gasLimit"])
        case _:
            return NopTransaction()


class TransactionProcessor:
    def __init__(self, block: Block, worldState: WorldState) -> None:
        self.block = block
        # self.transaction = transaction
        self.worldState = worldState

    def process(self) -> bool:

        # Save the backup world state
        backup = self.worldState.clone()

        # TODO After processing transaction, check the world state hash to match with the block worldstate hash
        current_worldstate_hash = self.worldState.get_hash()
        if current_worldstate_hash != self.block.world_state_hash:
            print(
                "World state hash does not match with block worldstate hash, Either block invalid or world state corrupted")
            # Reverse the transaction
            self.worldState = backup.clone()
            return False

        print(f"TransactionProcessor:process: Process block #{self.block.index}")
        # print(self.block)
        for tx in self.block.data:
            print("TransactionProcessor:process: Process " + tx.Txtype + " transaction")
            # if isinstance(tx, NativeTransaction):
            #     state, gas = self.process_native_transaction(tx)
            # elif isinstance(tx, MintBurnTransaction):
            #     state, gas = self.process_mint_burn_transaction(tx)
            # elif isinstance(tx, Transaction):
            #     print("Transaction type is not supported")
            #     return False

            # Deduct the gas
            gas_allowed = tx.gasLimit
            neoa = self.worldState.get_eoa(tx.sender)
            neoa.balance -= gas_allowed
            self.worldState.set_eoa(tx.sender, neoa)

            # Execute transaction and calculate gas used
            state, gas_used = tx.process(self.worldState)

            # Subtract the gas
            gas_leftover = gas_allowed - gas_used

            # Transfer back gas to the sender
            neoa = self.worldState.get_eoa(tx.sender)
            neoa.balance += gas_leftover
            self.worldState.set_eoa(tx.sender, neoa)

            if not state:
                print("TransactionProcessor:process: Transaction failed, reverse the transaction")
                self.worldState = backup.clone()
                return False

            # Update nonce
            neoa = self.worldState.get_eoa(tx.sender)
            neoa.nonce += 1
            self.worldState.set_eoa(tx.sender, neoa)


        return True

    @staticmethod
    def cast_transaction(transaction_raw: str):
        transaction = json.loads(transaction_raw)
        # print(transaction)
        transaction_data = transaction["data"]
        # print(transaction)

        tx = cast_raw_transaction(transaction, transaction_data)
        tx.signature = transaction["signature"]
        tx.publicKey = transaction["publicKey"]

        return tx

    # def process_mint_burn_transaction(self, transaction: Transaction) -> (bool, int):
    #     print("TransactionProcessor:process_mint_burn_transaction: Process mint burn transaction")
    #
    #     # Update world state
    #     receiver = transaction.to
    #     amount = transaction.transactionData["amount"]
    #
    #     if self.worldState.get_eoa(receiver).balance + amount < 0:
    #         # Clear the balance
    #         neoa = self.worldState.get_eoa(receiver)
    #         neoa.balance = 0
    #         self.worldState.set_eoa(receiver, neoa)
    #         return False
    #
    #     neoa = self.worldState.get_eoa(receiver)
    #     neoa.balance += amount
    #     self.worldState.set_eoa(receiver, neoa)
    #
    #     return True

    # def process_native_transaction(self, transaction: NativeTransaction) -> (bool, int):
    #
    #     if transaction.sender == transaction.transactionData["receiver"]:
    #         print(f"[Skip] Tx {transaction.hash[:8]} is noop (sender == receiver)")
    #         return True
    #
    #     print("TransactionProcessor:process_native_transaction: Process native transaction, gas fee: " + str(transaction.gasLimit))
    #
    #     # Update world state
    #     sender = transaction.sender
    #     receiver = transaction.to
    #     amount = transaction.transactionData["amount"]
    #     gasPrice = transaction.gasLimit
    #
    #     # self.worldState.get_eoa(sender).balance -= amount + gasPrice
    #     # self.worldState.get_eoa(receiver).balance += amount
    #
    #     neoa = self.worldState.get_eoa(sender)
    #     neoa.balance -= amount + gasPrice
    #     self.worldState.set_eoa(sender, neoa)
    #
    #     neoa = self.worldState.get_eoa(receiver)
    #     neoa.balance += amount
    #     self.worldState.set_eoa(receiver, neoa)
    #
    #     return True
