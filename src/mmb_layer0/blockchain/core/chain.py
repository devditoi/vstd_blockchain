import time

# import json
from rsa import PublicKey
# import jsonlight
from rich import print

# from mmb_layer0.blockchain.transaction_processor import TransactionProcessor
from src.mmb_layer0.blockchain.core.validator import Validator
from src.mmb_layer0.blockchain.core.block import Block
from src.mmb_layer0.blockchain.core.transactionType import Transaction
class Chain:
    def __init__(self) -> None:
        print("chain.py:__init__: Initializing Chain")
        genesis_tx = Transaction("0x0", "genesis", 0, 0)
        genesis_block: Block = Block(0, "0", 0, [genesis_tx])
        self.chain = [genesis_block]
        self.length = 1
        self.mempool: list[Transaction] = []
        self.mempool_tx_id: set[str] = set()
        # self.interval = 10 # 10 seconds before try to send and validate
        self.max_block_size = 1 # maximum number of transactions in a block

    def add_block(self, block: Block, initially = False) -> Block | None:
        if not Validator.validate_block(block, self, initially): # Validate block
            return None
        print("chain.py:add_block: Block valid, add to chain")
        print(block)
        self.chain.append(block)
        # print("chain.py:add_block: Increment chain length")
        self.length += 1
        # Clear tx in mempool
        for tx in block.data:
            self.mempool.remove(tx)
            self.mempool_tx_id.remove(tx.hash)

        return block

    def get_block(self, index) -> Block:
        if index >= self.length:
            print("chain.py:get_block: Index out of range")
            raise Exception("Index out of range")
        # print("chain.py:get_block: Return block at index", index)
        return self.chain[index]

    def get_last_block(self) -> Block:
        # print("chain.py:get_last_block: Return last block")
        return self.chain[-1]

    def get_height(self) -> int:
        # print("chain.py:get_height: Return chain length")
        if self.length != len(self.chain):
            print("chain.py:get_height: Chain length does not match length")
            raise Exception("Chain length does not match length")
        return self.length

    def contain_transaction(self, transaction: Transaction) -> bool:
        return transaction.hash in self.mempool_tx_id

    def temporary_add_to_mempool(self, transaction: Transaction) -> None:
        self.mempool_tx_id.add(transaction.hash)

    def add_transaction(self, transaction: Transaction, signature: bytes, publicKey: PublicKey, execution_callback, consensus, broadcast_callback) -> None:
        if not Validator.onchain_validate(transaction, signature, publicKey): # Validate transaction
            return

        print("chain.py:add_transaction: Transaction valid, add to mempool")
        print(transaction)
        self.mempool.append(transaction)
        # Add transaction ID (hash) to set for check it later
        # self.mempool_tx_id.add(transaction.hash)

        if not consensus.is_leader():
            print("chain.py:add_transaction: Not leader, return")
            return

        if len(self.mempool) >= self.max_block_size:
            # print("chain.py:add_transaction: Process block")
            self.process_block(execution_callback, consensus, broadcast_callback)


    def process_block(self, callback, consensus, broadcast_callback) -> None:
        # Check block
        if not Validator.preblock_validate(self.mempool):
            return

        # PoA validation

        print("chain.py:process_block: Mempool valid, create block")
        # print(block)
        data = self.mempool
        block = Block(self.length, self.get_last_block().hash, time.time(), data)

        # Sign block
        consensus.sign_block(block)

        # print("chain.py:process_block: Add new block to chain")
        # self.add_block(block)
        # print(block)
        # print("chain.py:process_block: Clear mempool")
        # self.mempool = []

        # Broadcast block
        broadcast_callback(block)

        callback(block)

    #
    # def check_sync(self, other) -> bool:
    #     for block in other.chain:
    #         if block.hash != self.get_block(block.index).hash:
    #             # print("chain.py:check_sync: Block hashes do not match")
    #             return False
    #
    #     # print(self.get_height(), other.get_height())
    #     return self.get_height() == other.get_height()

    # def __jsondump__(self):
    #     return {
    #         "chain": self.chain,
    #         "length": self.length,
    #         "mempool": self.mempool,
    #         "max_block_size": self.max_block_size
    #     }

    def debug_chain(self):
        # print("chain.py:debug_chain:----------------------Print chain----------------------------")
        # print("chain.py:debug_chain: Print chain")
        for block in self.chain:
            print(block.to_string())

        print("chain.py:debug_chain: Print mempool")
        for tx in self.mempool:
            print(tx.to_string())
        # print("chain.py:debug_chain:--------------------------------------------------")