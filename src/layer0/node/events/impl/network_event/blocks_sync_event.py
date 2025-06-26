from layer0.blockchain.core.validator import Validator
from layer0.blockchain.processor.block_processor import BlockProcessor
from layer0.node.events.EventHandler import EventHandler
from layer0.node.events.node_event import NodeEvent
import typing
from layer0.blockchain.core.block import Block

if typing.TYPE_CHECKING:
    from layer0.node.node_event_handler import NodeEventHandler


class GetBlocksEvent(EventHandler):
    def require_field(self):
        return ["start_index", "end_index"]

    @staticmethod
    def event_name() -> str:
        return "get_blocks"

    def handle(self, event: "NodeEvent"):
        start_index = event.data["start_index"]
        end_index = event.data["end_index"]

        print(f"[{self.neh.node.address}] GetBlocksEvent.handle: receiving request for blocks from {start_index} to {end_index} from {event.origin}")

        blocks = []
        for i in range(start_index, end_index):
            blocks.append(self.neh.node.blockchain.get_block(i).to_string())

        print(f"[{self.neh.node.address}] GetBlocksEvent.handle: sending back {len(blocks)} blocks to {event.origin}")

        # Send back blocks
        blocks_event = NodeEvent("blocks", {
            "blocks": blocks
        }, self.neh.node.address)
        self.neh.fire_to(event.origin, blocks_event)
        return False


class BlocksEvent(EventHandler):
    def require_field(self):
        return ["blocks"]

    @staticmethod
    def event_name() -> str:
        return "blocks"

    def handle(self, event: "NodeEvent"):
        blocks_data = event.data["blocks"]
        print(f"[{self.neh.node.address}] BlocksEvent.handle: received {len(blocks_data)} blocks from {event.origin}")

        # Need to check where to overwrite and remove all block in that case
        # TODO: Find smallest height block and start purging from top to there height before add new block
        # TODO: Need to implement state diff logic for reverse


        for block_data in blocks_data:
            block = BlockProcessor.cast_block(block_data)
            print(f"[{self.neh.node.address}] BlocksEvent.handle: adding block {block.index} to blockchain")
            self.neh.node.blockchain.add_block(block) # Perment write to disk

        return False