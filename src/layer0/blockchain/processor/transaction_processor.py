from layer0.blockchain.core.transaction_type import SmartContractDeployTransaction
from layer0.blockchain.core.worldstate import EOA
from layer0.blockchain.core.block import Block
from layer0.blockchain.core.transaction_type import Transaction, NativeTransaction, MintBurnTransaction, NopTransaction
from layer0.blockchain.core.worldstate import WorldState
import json
from rich import print


# Implement more transaction type here!!!
def cast_raw_transaction(transaction, transaction_data):
    match transaction["Txtype"]:
        case "mintburn":
            return MintBurnTransaction(transaction["sender"] ,transaction["to"], transaction_data["amount"], transaction["timestamp"],
                                        transaction["nonce"], transaction["gas_limit"])
        case "native":
            return NativeTransaction(transaction["sender"], transaction["to"],
                                        transaction_data["amount"], transaction["timestamp"], transaction["nonce"], transaction["gas_limit"])
        case "smartcontractdeploy":
            return SmartContractDeployTransaction(transaction["sender"], transaction_data, transaction["timestamp"], transaction["nonce"], transaction["gas_limit"])
        case _:
            return NopTransaction()


class TransactionProcessor:
    def __init__(self, block: Block, worldState: WorldState) -> None:
        self.block = block
        # self.transaction = transaction
        self.worldState = worldState

    def process(self) -> bool:

        # Save the backup world state
        backup: WorldState = self.worldState.clone()

        # TODO After processing transaction, check the world state hash to match with the block worldstate hash
        # current_worldstate_hash = self.worldState.get_hash()
        # if current_worldstate_hash != self.block.world_state_hash:
        #     print(
        #         "World state hash does not match with block worldstate hash, Either block invalid or world state corrupted")
        #     # Reverse the transaction
        #     self.worldState = backup.clone()
        #     return False

        #     )
        #
        # print(
        #     f"TransactionProcessor:process: Process block #{self.block.index}"
        # )
        # print(self.block)
        for tx in self.block.transactions:
            print(f"[bold blue]TransactionProcessor:process:[/] Process {tx.Txtype} transaction")
            if tx.gas_limit > self.block.gas_limit - self.block.gas_used:
                print("[bold red]TransactionProcessor:process:[/] Transaction gas precomputed limit exceeded")
                continue

            # Snapshot the world state
            # self.worldState.snapshot()

            if not self.worldState.get_eoa(tx.sender).balance >= tx.gas_limit:
                print("[bold red]TransactionProcessor:process:[/] Transaction sender does not have enough balance")
                continue

            # Deduct gas from sender
            self.worldState.get_eoa(tx.sender).balance -= tx.gas_limit

            # Process the transaction
            result, gas_used = tx.process(self.worldState)
            tx.gas_used = gas_used
            gas_leftover = tx.gas_limit - gas_used
            
            # Burn 1/2 of the leftover gas, and refund the other 1/2
            burned = gas_leftover // 2
            refund = gas_leftover - burned
            
            self.worldState.get_eoa(tx.sender).balance += refund

            # Transfer the gas used to the miner
            if self.block.miner:
                self.worldState.get_eoa(self.block.miner).balance += tx.gas_used
            else:
                print("[bold red]TransactionProcessor:process:[/] Block miner is not set, cannot transfer gas to miner")

            # Update the block gas used
            self.block.gas_used += tx.gas_used

            # Check if the transaction was successful
            if not result:
                # Revert the world state
                # self.worldState.revert()
                print("[bold red]TransactionProcessor:process:[/] Transaction failed, reverse the transaction")
                continue

            # Check if the block gas limit is exceeded
            if self.block.gas_used > self.block.gas_limit:
                # Revert the world state
                # self.worldState.revert()
                print("[bold red]TransactionProcessor:process:[/] Transaction gas limit exceeded")
                continue

            # Add the transaction to the list of processed transactions
            self.processed_transactions.append(tx)
            
            # Update the transaction status
            tx.status = "success"
            
            print(f"[bold green]TransactionProcessor:process:[/] Transaction succeeded, gas limit {tx.gas_limit}, gas used {tx.gas_used}, returned gas {gas_leftover}, burned {burned}")

        return self.processed_transactions

    def get_receipts_root(self) -> str:
        return HashUtils.sha256("".join([tx.get_receipt_hash() for tx in self.processed_transactions]))

    @staticmethod
    def check_valid_transaction(transaction: dict) -> bool:
        required_keys = ["sender", "to", "Txtype", "timestamp", "nonce", "gas_limit", "transactionData", "hash", "signature", "publicKey"]
        missing_keys = [key for key in required_keys if key not in transaction]
        if missing_keys:
            print(f"[bold red]TransactionProcessor:check_valid_transaction:[/] Missing keys: {missing_keys}")
            return False
        return True
    
    @staticmethod
    def from_dict(transaction: dict) -> 'Transaction':
        # print(transaction)
        if not TransactionProcessor.check_valid_transaction(transaction):
            raise ValueError("Invalid transaction format")
        # print(transaction)
        
        tx = Transaction(
            sender=transaction["sender"],
            to=transaction["to"],
            Txtype=transaction["Txtype"],
            timestamp=transaction["timestamp"],
            nonce=transaction["nonce"],
            gas_limit=transaction["gas_limit"]
        )
        tx.transactionData = transaction["transactionData"]
        tx.hash = transaction["hash"]
        tx.signature = transaction["signature"]
        tx.publicKey = transaction["publicKey"]
        return tx

    @staticmethod
    def cast_transaction(transaction: dict) -> 'Transaction':
        return TransactionProcessor.from_dict(transaction)
        

    # @staticmethod
    # def process_mint_burn_transaction(transaction: 'MintBurnTransaction', worldState: 'WorldState') -> None:
    #     print("TransactionProcessor:process_mint_burn_transaction: Process mint burn transaction")
    #     # Update world state
    #     receiver = transaction.to
    #     amount = transaction.transactionData["amount"]
    #
    #     neoa = worldState.get_eoa(receiver)
    #     neoa.balance += amount
    #     worldState.set_eoa(receiver, neoa)
    #
    # @staticmethod
    # def process_native_transaction(transaction: 'NativeTransaction', worldState: 'WorldState') -> None:
    #
    #     if transaction.sender == transaction.to:
    #         print(f"[Skip] Tx {transaction.hash[:8]} is noop (sender == receiver)")
    #         return
    #
    #     print("TransactionProcessor:process_native_transaction: Process native transaction, gas fee: " + str(transaction.gas_limit))
    #
    #     # Update world state
    #     sender = transaction.sender
    #     receiver = transaction.to
    #     amount = transaction.transactionData["amount"]
    #
    #     # Deduct the sender
    #     neoa = worldState.get_eoa(sender)
    #     neoa.balance -= amount
    #     worldState.set_eoa(sender, neoa)
    #
    #     # Add the receiver
    #     neoa = worldState.get_eoa(receiver)
    #     neoa.balance += amount
    #     worldState.set_eoa(receiver, neoa)
