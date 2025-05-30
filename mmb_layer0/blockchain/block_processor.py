from mmb_layer0.blockchain.transaction_processor import TransactionProcessor
from mmb_layer0.blockchain.block import Block
import json

class BlockProcessor:
    @staticmethod
    def cast_block(block_json: str):
        block_data = json.loads(block_json)
        transaction_list = [TransactionProcessor.cast_transaction(tx) for tx in block_data["data"]]
        return Block(block_data["index"], block_data["previous_hash"], block_data["timestamp"], transaction_list)
