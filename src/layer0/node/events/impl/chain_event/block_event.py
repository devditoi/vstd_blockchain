from layer0.blockchain.core.block import Block

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

        self.neh.node.logger.log(f"[bold blue]{self.neh.node.origin}:block_event.py:handle:[/] Received block #{block.index} from {event.origin}")

        if block.hash == self.neh.node.blockchain.get_latest_block().hash: # Block is already exist
            self.neh.node.logger.log(f"[bold yellow]{self.neh.node.origin}:block_event.py:handle:[/] Block #{block.index} from {event.origin} already exists")
            return False

        if not Validator.validate_block_without_chain(block, self.neh.node.blockchain.get_latest_block().hash):  # Not a valid block
            self.neh.node.logger.log(f"[bold red]{self.neh.node.origin}:block_event.py:handle:[/] Block #{block.index} from {event.origin} is invalid (without chain)")
            return False

        if not self.neh.node.consensus.is_valid(block):  # Not a valid block
            self.neh.node.logger.log(f"[bold red]{self.neh.node.origin}:block_event.py:handle:[/] Block #{block.index} from {event.origin} is invalid (consensus)")
            return False

        
        final_block: Block | None = self.neh.node.blockchain.add_block(block)
        
        if final_block:
            self.neh.node.logger.log(f"[bold green]{self.neh.node.origin}:block_event.py:handle:[/] Successfully added block #{block.index} from {event.origin} to chain")
            return True
        else:
            self.neh.node.logger.log(f"[bold red]{self.neh.node.origin}:block_event.py:handle:[/] Failed to add block #{block.index} from {event.origin} to chain")
            return False