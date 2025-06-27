import time

# from ecdsa import VerifyingKey
# import json
from rsa import PublicKey
# import jsonlight
from rich import print, inspect
import threading

from layer0.blockchain.chain.saver_impl.filebase_saver import FilebaseSaver, FilebaseDatabase
from layer0.blockchain.consensus.consensus_processor import ConsensusProcessor
# from layer0.blockchain.transaction_processor import TransactionProcessor
from layer0.blockchain.core.validator import Validator
from layer0.blockchain.core.block import Block
from layer0.blockchain.core.transaction_type import Transaction
from layer0.config import ChainConfig
from layer0.utils.crypto.signer import SignerFactory

# from layer0.node_sync_services import NodeSyncServices

class Chain:
    def __init__(self, chain_id: str, dummy = True) -> None:
        print("chain.py:__init__: Initializing Chain")
        self.genesis_tx = Transaction("0x0", "genesis", "0", 0, 0)
        self.genesis_block: Block = Block(0, "0", 0, "0", [self.genesis_tx])
        self.chain = FilebaseSaver(FilebaseDatabase(
            f"chain_{chain_id}_blockchain",
            f"chain_{chain_id}_transaction",
        ))

        self.height = 1
        self.mempool: list[Transaction] = []
        self.mempool_tx_id: set[str] = set()
        self.interval = 10 # 10 seconds before try to send and validate
        self.max_block_size = 10 # maximum number of transactions in a block
        self.last_block_time = time.time()

        self.consensus = None
        self.execution_callback = None
        self.broadcast_callback = None
        self.world_state = None

        self.reset_chain()
        if not dummy:
            self.thread = threading.Thread(target=self.__process_block_thread, daemon=True)
            self.thread.start()

        self.mempool_lock = threading.Lock()

    def is_genesis(self):
        return self.chain.get_height()

    def reset_chain(self):
        print("chain.py:reset_chain: Reset chain")
        # self.chain = [self.genesis_block]
        self.chain.clear()
        self.chain.add_block(self.genesis_block)

    def get_tx(self, tx_hash) -> Transaction | None:
        return self.chain.get_tx(tx_hash)

    def set_initial_data(self, consensus, execution_callback, broadcast_callback, world_state):
        self.consensus = consensus
        self.execution_callback = execution_callback
        self.broadcast_callback = broadcast_callback
        self.world_state = world_state

        print("chain.py:set_initial_data: Set callbacks")

    def add_block(self, block: Block, initially = False, delay_flush = False) -> Block | None:
        #** Delay flush: Delay the flush of the block to the next flush interval (manually)
        if not Validator.validate_block_on_chain(block, self, initially): # Validate block
            print("chain.py:add_block: Block is invalid")
            return None
        if not Validator.validate_block_without_chain(block, self.get_latest_block().hash): # Validate block
            print("chain.py:add_block: Block is invalid")
            return None
        print(f"chain.py:add_block: Block #{block.index} valid, add to chain")

        # Execute first, add later
        if self.execution_callback:
            # Execute block
            self.execution_callback(block)

        # inspect(block)
        # inspect(block.data[0])
        # inspect(self.world_state)

        inspect(self.world_state)

        # print(block)
        self.chain.add_block(block, delay_flush)
        self.height += 1

        # If the length is greater than max block history, remove the first block
        # Not DELETE Old block, delete the data (Somehow)
        if self.height > ChainConfig.BLOCK_HISTORY_LIMIT:
            # TODO: Implement this later
            pass
            # self.chain[self.height - ChainConfig.BLOCK_HISTORY_LIMIT].data = None

        # Remove transactions from mempool
        for tx in block.data:
            for tx2 in self.mempool:
                if tx.hash == tx2.hash:
                    self.mempool.remove(tx2)
                    self.mempool_tx_id.remove(tx2.hash)


        return block

    def get_block(self, index) -> Block:
        """
        Get a block at a certain index

        Args:
            index (int): The index of the block to retrieve

        Returns:
            Block: The block at the given index

        Raises:
            Exception: If the index is out of range
        """
        if index >= self.get_height():
            print("chain.py:get_block: Index out of range")
            raise Exception("Index out of range")
        # print("chain.py:get_block: Return block at index", index)
        return self.chain.get_block(index)

    def get_latest_block(self) -> Block | None:
        # print("chain.py:get_last_block: Return last block")
        return self.chain.get_block(self.chain.get_height() - 1) # Get block at height is ineed last block

    def get_height(self) -> int:
        # print("chain.py:get_height: Return chain length")
        return self.chain.get_height()

    def contain_transaction(self, transaction: Transaction) -> bool:
        return transaction.hash in self.mempool_tx_id

    def temporary_add_to_mempool(self, transaction: Transaction) -> None:
        self.mempool_tx_id.add(transaction.hash)

    def add_transaction(self, transaction: Transaction, signature: bytes, publicKey: str) -> None:
        if not Validator.validate_transaction_with_signature(transaction, signature, SignerFactory().get_signer().deserialize(publicKey)): # Validate transaction
            self.mempool_lock.release()
            return

        print("chain.py:add_transaction: Transaction valid, add to mempool")
        # print(transaction)

        self.mempool_lock.acquire()
        self.mempool.append(transaction)
        self.mempool_lock.release()

        # if not self.consensus.is_leader(): # Check if leader
        #     # print("chain.py:add_transaction: Not leader, return")
        #     return

    # PROPOSE BLOCK, CREATE BLOCK
    # TODO Need to refactor this to own file, consensus logic
    def __process_block_thread(self):
        # Check some conditions
        while True:
            if self.consensus is None or self.broadcast_callback is None:
                print(
                    "chain.py:__process_block_thread: Consensus or  broadcast callback is not set, return")
                time.sleep(1)
            else:
                break

        # Check if leader
        if not self.consensus.is_leader():
            # print("chain.py:__process_block_thread: Not leader, return")
            return

        # return # Testing purposes

        # Process block loop
        while True:
            if len(self.mempool) >= self.max_block_size or float(time.time() - self.last_block_time) >= self.interval:
                print("chain.py:__process_block_thread: Process block")
                self.last_block_time = time.time()
                if len(self.mempool) == 0:
                    # TODO Disable filling block for now
                    #! Need filling block
                    # Create filling block
                    # ConsensusProcessor.process_block([], self.get_latest_block(), self.consensus, self.broadcast_callback, self.world_state)
                    # Ima to lazy to create filiing block
                    continue

                self.mempool_lock.acquire()

                block_to_process = min(len(self.mempool), self.max_block_size)
                pool = self.mempool[:block_to_process]
                self.mempool = self.mempool[block_to_process:]

                block = ConsensusProcessor.process_block(pool, self.get_latest_block(), self.consensus, self.broadcast_callback, self.world_state)
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
        for block in range(self.chain.get_height()):
            print(self.chain.get_block(block).to_string())

        print("chain.py:debug_chain: Print mempool")
        for tx in self.mempool:
            print(tx.to_string())
        # print("chain.py:debug_chain:--------------------------------------------------")