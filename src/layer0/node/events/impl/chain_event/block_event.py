from layer0.blockchain.core.block import Block
from rich import inspect

from layer0.blockchain.core.validator import Validator
from layer0.blockchain.processor.block_processor import BlockProcessor
from layer0.node.events.EventHandler import EventHandler
from layer0.node.events.node_event import NodeEvent

class BlockEvent(EventHandler):
    @staticmethod
    def event_name() -> str:
        return "block"

    @staticmethod
    def require_field() -> list[str]:
        return ["block"]

    def handle(self, event: "NodeEvent") -> bool:

        block = event.data["block"]

        if isinstance(block, str):
            block: Block = BlockProcessor.cast_block(event.data["block"])

        # print(event.origin)
        # inspect(block)

        if block.hash == self.neh.node.blockchain.get_latest_block().hash: # Block is already exist
            return False

        if not Validator.validate_block_without_chain(block, self.neh.node.blockchain.get_latest_block().hash):  # Not a valid block
            print("validator.py:validate_block_without_chain: Block is invalid")
            return False

        if not self.neh.node.consensus.is_valid(block):  # Not a valid block
            print("consensus.py:is_valid: Block is invalid")
            return False

        final_block: Block | None = self.neh.node.blockchain.add_block(block)

        return True if final_block else False