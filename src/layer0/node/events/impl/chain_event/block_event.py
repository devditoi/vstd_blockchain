from mmb_layer0.blockchain.core.validator import Validator
from mmb_layer0.blockchain.processor.block_processor import BlockProcessor
from mmb_layer0.node.events.EventHandler import EventHandler
from mmb_layer0.node.events.node_event import NodeEvent

class BlockEvent(EventHandler):
    @staticmethod
    def event_name() -> str:
        return "block"

    def require_field(self):
        return ["block"]

    def handle(self, event: "NodeEvent"):

        block = event.data["block"]

        if isinstance(block, str):
            block = BlockProcessor.cast_block(event.data["block"])

        if not Validator.validate_block_without_chain(block, self.neh.node.blockchain.get_last_block().hash):  # Not a valid block
            return False

        if not self.neh.node.consensus.is_valid(block):  # Not a valid block
            return False

        block = self.neh.node.blockchain.add_block(block)

        return True if block else False