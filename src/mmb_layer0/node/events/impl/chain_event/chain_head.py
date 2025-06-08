from mmb_layer0.blockchain.processor.block_processor import BlockProcessor
from mmb_layer0.node.events.EventHandler import EventHandler
import typing
if typing.TYPE_CHECKING:
    from mmb_layer0.node.node_event_handler import NodeEvent
from mmb_layer0.blockchain.core.block import Block


class ChainHeadEvent(EventHandler):
    def require_field(self):
        return [] # Not required

    @staticmethod
    def event_name() -> str:
        return "chain_head"

    def handle(self, event: "NodeEvent"):
        if self.neh.node.blockchain.is_genesis():
            # There is nothing to sync
            return False

        # Sending chain head to peer
        chain_head = self.neh.node.blockchain.get_last_block()

        self.neh.fire_to(event.origin, NodeEvent("chain_head_fullfilled", {
            "block": chain_head
        }, self.neh.node.origin))

        return False

class ChainHeadFullfilledEvent(EventHandler):
    def require_field(self):
        return ["block"] # Required

    @staticmethod
    def event_name() -> str:
        return "chain_head_fullfilled"

    def handle(self, event: "NodeEvent"):
        # Receiving chain head from peer
        chain_head = event.data["block"]
        if not isinstance(chain_head, Block):
            chain_head = BlockProcessor.cast_block(chain_head)

        current_chain_head = self.neh.node.blockchain.get_last_block()

        # inspect(chain_head)
        # inspect(current_chain_head)

        if current_chain_head.index > chain_head.index:
            print(f"[NodeEventHandler] [bold green]{self.neh.node.origin}[/bold green]: I have the longer chain")
            return False  # I have the longer chain

        # Only when them get the longer or equal chain

        # Check the current block and peer block to seeking for error
        synced = self.neh.node.blockchain.get_last_block().hash == chain_head.hash

        print(f"[NodeEventHandler] [bold green]{self.neh.node.origin}[/bold green]: Synced: {synced}")

        if not synced:
            # One of the 2 is wrong, either me or peer
            # Sending full chain request to peer
            req = NodeEvent("full_chain", {}, self.neh.node.origin)
            self.neh.fire_to(event.origin, req)

        return False