
from rich import inspect
from layer0.blockchain.core.block import Block
from ..core.validator import Validator
import time
from layer0.config import ChainConfig
import logging

class ConsensusProcessor:
    @staticmethod
    def process_block(data, last_block: Block, consensus, broadcast_callback, world_state) -> Block | None:
        # Check block
        if not Validator.preblock_validate(data):
            return None
        
        # Validate validators configuration
        if not ChainConfig.config["validators"]:
            logging.warning("No validators configured in ChainConfig")
            return None

        # PoA validation

        print("chain.py:process_block: Mempool valid, create block")

        worldstate_hash = world_state.get_hash()

        # Create block with miner already set
        # Calculate next proposer index
        last_index = last_block.proposer_index
        try:
            next_index = (last_index + 1) % len(ChainConfig.config["validators"])
            miner = ChainConfig.config["validators"][next_index]
        except IndexError:
            logging.error("Validator index out of range")
            return None
            
        block = Block(
            index=last_block.index + 1,
            previous_hash=last_block.hash,
            timestamp=time.time() * 1000,
            worldstate_hash=worldstate_hash,
            data=data,
            miner=miner,
            proposer_index=next_index
       )

        # Validate block
        if not Validator.validate_block_without_chain(block, last_block.hash):
            print("chain.py:process_block: Block invalid")
            return None

        print("chain.py:process_block: Block valid, signing")

        # Sign block
        consensus.sign_block(block)

        # Broadcast block
        broadcast_callback(block)

        # callback(block)
        return block