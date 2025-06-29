import threading

from layer0.blockchain.core.block import Block
from ..core.validator import Validator
from ..core.block import Block
import time
class ConsensusProcessor:
    @staticmethod
    def process_block(data, last_block: Block, consensus, broadcast_callback, world_state) -> Block | None:
        # Check block
        if not Validator.preblock_validate(data):
            return None

        # PoA validation

        print("chain.py:process_block: Mempool valid, create block")

        worldstate_hash = world_state.get_hash()

        block = Block(last_block.index + 1, last_block.hash, time.time() * 1000, worldstate_hash, data)

        # Validate block
        if not Validator.validate_block_without_chain(block, last_block.hash):
            print("chain.py:process_block: Block invalid")
            return None

        print("chain.py:process_block: Block valid, signing")

        # Sign block
        consensus.sign_block(block)

        block.miner = consensus.get_validators() # Hardcoded

        # Broadcast block
        broadcast_callback(block)

        # callback(block)
        return block