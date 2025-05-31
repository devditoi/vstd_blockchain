# Define a block for the blockchain
from src.mmb_layer0.blockchain.core.transactionType import Transaction
from src.mmb_layer0.utils.hash import HashUtils
import jsonlight


# from rich import print


class Block:
    def __init__(self, index, previous_hash, timestamp, data: list[Transaction]):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data.copy()
        self.hash = HashUtils.sha256(str(self.index) + str(self.previous_hash) + str(self.timestamp) + str(self.data))
        self.signature = None
        self.address = None

    def to_string(self) -> str:
        return jsonlight.dumps({
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "data": self.data,
            "hash": self.hash,
            "signature": self.signature,
            "address": self.address
        }, indent=2)

    def get_string_for_signature(self) -> str:
        return jsonlight.dumps({
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "data": self.data,
            "hash": self.hash
        })

    def __repr__(self):
        return self.to_string()