import logging
from layer0.node.events.EventHandler import EventHandler
from layer0.node.events.node_event import NodeEvent
import typing

if typing.TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class GetStatusEvent(EventHandler):
    @staticmethod
    def require_field():
        return []

    @staticmethod
    def event_name() -> str:
        return "get_status"

    def handle(self, event: "NodeEvent"):

        if self.neh.node.blockchain.get_latest_block() is None:
            return False

        # Send back status
        status_event = NodeEvent("status", {
            "height": self.neh.node.blockchain.get_height(),
            "hash": self.neh.node.blockchain.get_latest_block().hash
        }, self.neh.node.address)
        self.neh.fire_to(event.origin, status_event)
        return False


class StatusEvent(EventHandler):
    @staticmethod
    def require_field():
        return ["height", "hash"]

    @staticmethod
    def event_name() -> str:
        return "status"

    def handle(self, event: "NodeEvent"):
        local_height = self.neh.node.blockchain.get_height()
        local_hash = self.neh.node.blockchain.get_latest_block().hash
        remote_height = event.data.get("height")
        remote_hash = event.data.get("hash")

        # logger.debug("[StatusEvent] handle: local_height:", local_height, "remote_height:", remote_height, "remote_hash:", remote_hash)

        if remote_height > local_height:
            logger.info("[StatusEvent] handle: Remote node is ahead, requesting blocks")
            # We are behind, request blocks (Find common ancestor first!!! and also send in batch not send all at once)
            # get_blocks_event = NodeEvent("get_blocks", {
            #     "start_index": local_height,
            #     "end_index": remote_height
            # }, self.neh.node.address)
            # self.neh.fire_to(event.origin, get_blocks_event)

            # Find common ancestor
            common_ancestor_event: NodeEvent = NodeEvent(
                "get_ancestor_hashes",
                {
                    "from_height": local_height,
                    "max_depth": 20
                },
                self.neh.node.address
            )
            self.neh.fire_to(event.origin, common_ancestor_event)
            return False
        if remote_hash != local_hash:
            # Reorg logic, currently ignore
            logger.warning("[StatusEvent] handle: Reorg, wait for more confirmation")
        return False
