from layer0.blockchain.processor.transaction_processor import TransactionProcessor
from layer0.blockchain.core.block import Block
import json

class BlockProcessor:
    @staticmethod
    def cast_block(block_json: str):
        """
        Converts a JSON string representation of a block into a Block object.

        Args:
            block_json (str): The JSON string representing the block.

        Returns:
            Block: A Block object with its attributes populated from the JSON data.
        """
        if block_json is None:
            return Block(0, "", 0, "", [])
        block_data = json.loads(block_json)
        transaction_list = [TransactionProcessor.cast_transaction(tx) for tx in block_data.get("transactions", [])]
        raw_block = Block(block_data["index"], block_data["previous_hash"], block_data["timestamp"], block_data["world_state_hash"], transaction_list.copy())
        raw_block.signature = block_data["signature"]
        raw_block.address = block_data["address"]
        raw_block.world_state_hash = block_data["world_state_hash"]
        raw_block.miner = block_data["miner"]
        # raw_block.receipts_root = block_data["receipts_root"]
        return raw_block
