# Define a block for the blockchain
from layer0.blockchain.core.transaction_type import Transaction
from layer0.utils.hash import HashUtils
import jsonlight
# from rich import print
class Block:
    def __init__(self, index, previous_hash, timestamp, worldstate_hash, data: list[Transaction]):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data.copy()
        self.hash = HashUtils.sha256(str(self.index) + str(self.previous_hash) + str(self.timestamp) + str(self.data))
        self.signature = None
        self.address = None
        self.world_state_hash = worldstate_hash
        self.receipts_root: str | None = None # None before finalized
        self.miner = None
        self.finalized = False

    def get_receipts_root(self) -> str:
        return HashUtils.sha256("".join([ x.get_receipt_hash() for x in self.data ]))

    def to_string(self) -> str:
        return jsonlight.dumps({
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "data": self.data,
            "hash": self.hash,
            "signature": self.signature,
            "address": self.address,
            "world_state_hash": self.world_state_hash,
            "miner": self.miner,
        }, indent=2)

    def get_string_for_signature(self) -> str:
        return jsonlight.dumps({
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "data": self.data,
            "hash": self.hash,
            "world_state_hash": self.world_state_hash,
            "miner": self.miner
        })

    def __repr__(self):
        return self.to_string()