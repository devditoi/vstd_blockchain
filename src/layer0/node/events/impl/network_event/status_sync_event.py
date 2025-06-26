from layer0.node.events.EventHandler import EventHandler
from layer0.node.events.node_event import NodeEvent
import typing

if typing.TYPE_CHECKING:
    from layer0.node.node_event_handler import NodeEventHandler


class GetStatusEvent(EventHandler):
    def require_field(self):
        return []

    @staticmethod
    def event_name() -> str:
        return "get_status"

    def handle(self, event: "NodeEvent"):
        # Send back status
        status_event = NodeEvent("status", {
            "height": self.neh.node.get_height(),
            "hash": self.neh.node.blockchain.get_last_block().hash
        }, self.neh.node.address)
        self.neh.fire_to(event.origin, status_event)
        return False


class StatusEvent(EventHandler):
    def require_field(self):
        return ["height", "hash"]

    @staticmethod
    def event_name() -> str:
        return "status"

    def handle(self, event: "NodeEvent"):
        local_height = self.neh.node.get_height()
        remote_height = event.data.get("height")
        remote_hash = event.data.get("hash")

        if remote_height > local_height:
            # We are behind, request blocks
            get_blocks_event = NodeEvent("get_blocks", {
                "start_index": local_height,
                "end_index": remote_height
            }, self.neh.node.address)
            self.neh.fire_to(event.origin, get_blocks_event)
        return False
