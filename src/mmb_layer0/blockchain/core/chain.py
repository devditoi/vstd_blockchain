import time

# import json
from rsa import PublicKey
# import jsonlight
from rich import print
import threading
from mmb_layer0.blockchain.consensus.consensus_processor import ConsensusProcessor
# from mmb_layer0.blockchain.transaction_processor import TransactionProcessor
from mmb_layer0.blockchain.core.validator import Validator
from mmb_layer0.blockchain.core.block import Block
from mmb_layer0.blockchain.core.transactionType import Transaction
# from mmb_layer0.node_sync_services import NodeSyncServices


class Chain:
    def __init__(self) -> None:
        print("chain.py:__init__: Initializing Chain")
        genesis_tx = Transaction("0x0", "genesis", 0, 0)
        genesis_block: Block = Block(0, "0", 0, [genesis_tx])
        self.chain = [genesis_block]
        self.length = 1
        self.mempool: list[Transaction] = []
        self.mempool_tx_id: set[str] = set()
        self.interval = 10 # 10 seconds before try to send and validate
        self.max_block_size = 10 # maximum number of transactions in a block
        self.last_block_time = time.time()

        self.consensus = None
        self.execution_callback = None
        self.broadcast_callback = None

        self.thread = threading.Thread(target=self.__process_block_thread, daemon=True)
        self.thread.start()

        self.mempool_lock = threading.Lock()

    def set_callbacks(self, consensus, execution_callback, broadcast_callback):
        self.consensus = consensus
        self.execution_callback = execution_callback
        self.broadcast_callback = broadcast_callback

    def add_block(self, block: Block, initially = False) -> Block | None:
        if not Validator.validate_block(block, self, initially): # Validate block
            return None
        print("chain.py:add_block: Block valid, add to chain")
        print(block)
        self.chain.append(block)
        self.length += 1

        # Execute block
        self.execution_callback(block)

        # Remove transactions from mempool
        for tx in block.data:
            for tx2 in self.mempool:
                if tx.hash == tx2.hash:
                    self.mempool.remove(tx2)
                    self.mempool_tx_id.remove(tx2.hash)


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

    def add_transaction(self, transaction: Transaction, signature: bytes, publicKey: PublicKey) -> None:
        if not Validator.onchain_validate(transaction, signature, publicKey): # Validate transaction
            self.mempool_lock.release()
            return

        print("chain.py:add_transaction: Transaction valid, add to mempool")
        print(transaction)

        self.mempool_lock.acquire()
        self.mempool.append(transaction)
        self.mempool_lock.release()

        if not self.consensus.is_leader():
            # print("chain.py:add_transaction: Not leader, return")
            return

    def __process_block_thread(self):
        # Check some conditions
        while True:
            if self.consensus is None or self.broadcast_callback is None:
                print(
                    "chain.py:__process_block_thread: Consensus or execution callback or broadcast callback is not set, return")
                time.sleep(1)
            else:
                break

        # Check if leader
        if not self.consensus.is_leader():
            # print("chain.py:__process_block_thread: Not leader, return")
            return

        return # Testing purposes

        # Process block loop
        while True:
            if len(self.mempool) >= self.max_block_size or float(time.time() - self.last_block_time) >= self.interval:
                print("chain.py:__process_block_thread: Process block")
                self.last_block_time = time.time()
                if len(self.mempool) == 0:
                    # Create filling block
                    ConsensusProcessor.process_block([], self.get_last_block(), self.consensus, self.broadcast_callback)
                    continue

                self.mempool_lock.acquire()

                block_to_process = min(len(self.mempool), self.max_block_size)
                pool = self.mempool[:block_to_process]
                self.mempool = self.mempool[block_to_process:]

                block = ConsensusProcessor.process_block(pool, self.get_last_block(), self.consensus, self.broadcast_callback)
                if block:
                    print("chain.py:__process_block_thread: Block processed, delete transactions from mempool")
                    # for tx in block.data:
                    #     print(f"chain.py:__process_block_thread: Delete transaction " + tx.hash + " from mempool")
                        # for mtx in self.mempool:
                        #     if mtx.hash == tx.hash:
                        #         self.mempool.remove(mtx)
                        #         break
                        # self.mempool_tx_id.remove(tx.hash)

                self.mempool_lock.release()

            time.sleep(1)

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