from layer0.blockchain.processor.block_processor import BlockProcessor
from layer0.node.events.EventHandler import EventHandler
from layer0.node.events.node_event import NodeEvent
import typing
from rich import print

if typing.TYPE_CHECKING:
    pass


class GetBlocksEvent(EventHandler):
    @staticmethod
    def require_field():
        return ["start_index", "end_index"]

    @staticmethod
    def event_name() -> str:
        return "get_blocks"

    def handle(self, event: "NodeEvent"):
        start_index = event.data["start_index"]
        end_index = event.data["end_index"]

        print(f"[{self.neh.node.origin}] GetBlocksEvent.handle: receiving request for blocks from {start_index} to {end_index} from {event.origin}")

        if end_index > self.neh.node.blockchain.get_height():
            print(f"[{self.neh.node.origin}] GetBlocksEvent.handle: end_index {end_index} is greater than current blockchain height {self.neh.node.blockchain.get_height()}. Adjusting to height.")
            return False

        blocks = []
        for i in range(start_index, min(start_index + 30, end_index)): # Send 50 blocks at a time
            blocks.append(self.neh.node.blockchain.get_block(i).to_string())

        print(f"[{self.neh.node.origin}] GetBlocksEvent.handle: sending back {len(blocks)} blocks to {event.origin}")

        # Send back blocks
        blocks_event = NodeEvent("blocks", {
            "blocks": blocks
        }, self.neh.node.address)
        self.neh.fire_to(event.origin, blocks_event)
        return False


class BlocksEvent(EventHandler):
    @staticmethod
    def require_field():
        return ["blocks"]

    @staticmethod
    def event_name() -> str:
        return "blocks"

    def handle(self, event: NodeEvent) -> bool:
        blocks_data = event.data['blocks']
        self.neh.node.logger.log(f"[bold blue][{self.neh.node.origin}] BlocksEvent.handle:[/] received {len(blocks_data)} blocks from {event.origin}")

        if not blocks_data:
            return False

        blocks = [Block.from_json(block_data) for block_data in blocks_data]
        
        for block in blocks:
            if self.neh.node.blockchain.get_block(block.index) and self.neh.node.blockchain.get_block(block.index).hash == block.hash:
                self.neh.node.logger.log(f"[bold yellow][{self.neh.node.origin}] BlocksEvent.handle:[/] Block #{block.index} from {event.origin} already exists")
                continue

            if block.index <= self.neh.node.blockchain.get_height():
                self.neh.node.logger.log(f"[bold yellow][{self.neh.node.origin}] BlocksEvent.handle:[/] Received block with lower or equal index than current blockchain height, Not implemented yet")
                continue

            self.neh.node.logger.log(f"[bold blue][{self.neh.node.origin}] BlocksEvent.handle:[/] adding block {block.index} to blockchain")
            if not self.neh.node.blockchain.add_block(block, self.neh.node.worldState):
                self.neh.node.logger.log(f"[bold red][{self.neh.node.origin}] BlocksEvent.handle:[/] Failed to add block #{block.index} from {event.origin} to chain")
                return False
        
        self.neh.node.logger.log(f"[bold green][{self.neh.node.origin}] BlocksEvent.handle:[/] Successfully added {len(blocks)} blocks from {event.origin} to chain")
        return True