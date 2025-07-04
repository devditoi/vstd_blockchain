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

        print(f"TransactionProcessor:process: Process block #{self.block.index}")
        # print(self.block)
        for tx in self.block.data:
            print("TransactionProcessor:process: Process " + tx.Txtype + " transaction")

            if tx.gas_limit < tx.estimated_gas():
                print("TransactionProcessor:process: Transaction gas precomputed limit exceeded")
                tx.status = "failed"
                continue # Pass this transaction (aka fail safe)

            # Check if the user has enough gas
            if self.worldState.get_eoa(tx.sender).balance < tx.gas_limit:
                print("TransactionProcessor:process: Transaction sender does not have enough balance")
                tx.status = "failed"
                continue # Pass this transaction

            # Deduct the gas
            gas_allowed: int = tx.gas_limit
            neoa: EOA = self.worldState.get_eoa(tx.sender)
            neoa.balance -= gas_allowed
            self.worldState.set_eoa(tx.sender, neoa)

            # Execute transaction and calculate gas used
            state, gas_used = tx.process(self.worldState)

            # Subtract the gas
            gas_leftover: int = gas_allowed - gas_used

            # Gas
            # Half gone to miner wallet
            # Half disapears

            miner_reward: int = gas_used // 2
            burned: int = gas_used - miner_reward

            if not self.block.miner:
                print("TransactionProcessor:process: Block miner is not set, cannot transfer gas to miner")
                # Need to revert the whole transaction
                self.worldState = backup.clone()
                tx.status = "failed_revert"
                continue

            # Transfer to miner
            neoa = self.worldState.get_eoa(self.block.miner)
            neoa.balance += miner_reward
            self.worldState.set_eoa(self.block.miner, neoa)

            # Transfer to 0 (Burn address)
            neoa = self.worldState.get_eoa("0")
            neoa.balance += burned
            self.worldState.set_eoa("0", neoa)

            if gas_leftover < 0:
                print("TransactionProcessor:process: Transaction gas limit exceeded")
                tx.status = "failed" # And still eat the gas
                continue

            # Transfer back gas to the sender
            neoa = self.worldState.get_eoa(tx.sender)
            neoa.balance += gas_leftover
            self.worldState.set_eoa(tx.sender, neoa)

            if not state: # Deep fail, require revert
                print("TransactionProcessor:process: Transaction failed, reverse the transaction")
                self.worldState = backup.clone()
                tx.status = "failed_revert"
                continue # After reverse the transaction, everything is fine

            backup = self.worldState.clone() # Backup the world state of current transaction

            # Update nonce
            neoa = self.worldState.get_eoa(tx.sender)
            neoa.nonce += 1
            self.worldState.set_eoa(tx.sender, neoa)

            tx.status = "succeeded"
            tx.gas_used = gas_used
            tx.block_index = self.block.index

            print(f"TransactionProcessor:process: Transaction succeeded, gas limit {tx.gas_limit}, gas used {tx.gas_used}, returned gas {gas_leftover}, burned {burned}")

        # set block receipts root
        self.block.receipts_root = self.block.get_receipts_root()

        return True

    @staticmethod
    def check_valid_transaction(transaction_raw: str) -> bool:
        try:
            transaction = json.loads(transaction_raw)

            if any([key not in transaction for key in ["Txtype", "data", "signature", "publicKey"]]):
                
                # Find missing keys
                missing_keys = [key for key in ["Txtype", "data", "signature", "publicKey"] if key not in transaction]
                print(f"TransactionProcessor:check_valid_transaction: Missing keys: {missing_keys}")
                
                return False
            

            return True
        except json.JSONDecodeError:
            return False

    @staticmethod
    def cast_transaction(transaction_raw: str) -> Transaction:
        transaction = json.loads(transaction_raw)
        # print(transaction)
        transaction_data = transaction["data"]
        # print(transaction)

        tx: Transaction = cast_raw_transaction(transaction, transaction_data)
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
    #     print("TransactionProcessor:process_native_transaction: Process native transaction, gas fee: " + str(transaction.gas_limit))
    #
    #     # Update world state
    #     sender = transaction.sender
    #     receiver = transaction.to
    #     amount = transaction.transactionData["amount"]
    #     gasPrice = transaction.gas_limit
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
