from src.mmb_layer0.blockchain.chain.chain import Chain
from src.mmb_layer0.blockchain.block import Block

class BlockValidator:
    @staticmethod
    def validate_block(block: Block, chain: Chain, initially = False) -> bool:
        if block.index != chain.length and not initially:
            print("chain.py:add_block: Block index does not match chain length")
            return False

        if block.previous_hash != chain.get_last_block().hash:
            print("chain.py:add_block: Block previous hash does not match last block hash")
            return False

        if block.hash == chain.get_last_block().hash:
            print("chain.py:add_block: Block hash already exists")
            return False

        return True
