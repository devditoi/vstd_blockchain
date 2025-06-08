import threading

from mmb_layer0.blockchain.core.block import Block
from ..core.validator import Validator
from ..core.block import Block
import time
class ConsensusProcessor:
    @staticmethod
    def process_block(data, last_block: Block, consensus, broadcast_callback) -> Block | None:
        # Check block
        if not Validator.preblock_validate(data):
            return None

        # PoA validation

        print("chain.py:process_block: Mempool valid, create block")
        block = Block(last_block.index + 1, last_block.hash, time.time(), data)

        # Validate block
        if not Validator.validate_block_without_chain(block, last_block.hash):
            print("chain.py:process_block: Block invalid")
            return None

        # Sign block
        consensus.sign_block(block)

        # Broadcast block
        broadcast_callback(block)

        # callback(block)

        return block