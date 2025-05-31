import time

# import json
from rsa import PublicKey
# import jsonlight
from rich import print

from src.mmb_layer0.blockchain.chain.block_validator import BlockValidator
# from mmb_layer0.blockchain.block_processor import BlockProcessor
# from mmb_layer0.blockchain.transaction_processor import TransactionProcessor
from src.mmb_layer0.blockchain.validator import Validator
from src.mmb_layer0.blockchain.block import Block
from src.mmb_layer0.blockchain.transactionType import Transaction
class Chain:
    def __init__(self) -> None:
        print("chain.py:__init__: Create genesis block")
        genesis_tx = Transaction("0x0", "genesis", 0, 0)
        genesis_block: Block = Block(0, "0", 0, [genesis_tx])
        print("chain.py:__init__: Add genesis block to chain")
        self.chain = [genesis_block]
        print("chain.py:__init__: Set chain length to 1")
        self.length = 1
        print("chain.py:__init__: Create mempool")
        self.mempool: list[Transaction] = []
        # self.interval = 10 # 10 seconds before try to send and validate
        print("chain.py:__init__: Set max block size to 2")
        self.max_block_size = 2 # maximum number of transactions in a block

    def add_block(self, block, initially = False) -> Block | None:
        if not BlockValidator.validate_block(block, self, initially): # Validate block
            return None
        # print("chain.py:add_block: Add new block to chain")
        self.chain.append(block)
        # print("chain.py:add_block: Increment chain length")
        self.length += 1
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
        return self.length

    def add_transaction(self, transaction: Transaction, signature: bytes, publicKey: PublicKey, execution_callback) -> None:
        if not Validator.onchain_validate(transaction, signature, publicKey): # Validate transaction
            return
        print("chain.py:add_transaction: Add new transaction to mempool")
        print(transaction)
        self.mempool.append(transaction)
        if len(self.mempool) >= self.max_block_size:
            # print("chain.py:add_transaction: Process block")
            self.process_block(execution_callback)


    def process_block(self, callback) -> None:
        # Check block
        if not Validator.preblock_validate(self.mempool):
            return

        print("chain.py:process_block: Process block")
        # print(block)
        data = self.mempool
        block = Block(self.length, self.get_last_block().hash, time.time(), data)
        # print("chain.py:process_block: Add new block to chain")
        self.add_block(block)
        print(block)
        # print("chain.py:process_block: Clear mempool")
        self.mempool = []
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