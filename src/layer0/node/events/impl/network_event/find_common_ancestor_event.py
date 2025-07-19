import logging
from builtins import staticmethod

from layer0.node.events.EventHandler import EventHandler
from layer0.node.events.node_event import NodeEvent
import typing

if typing.TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# Remote side event
class GetAncestorHashesEvent(EventHandler):
    
    @staticmethod
    def require_field():
        return ["max_depth", "from_height"]

    @staticmethod
    def event_name() -> str:
        return "get_ancestor_hashes"

    def handle(self, event: "NodeEvent"):
        ancestor = []
        from_height = int(event.data["from_height"])
        max_depth = int(event.data["max_depth"])

        for i in range(from_height, max(from_height - max_depth, -1), -1):
            ancestor.append({
                "height": i,
                "hash": self.neh.node.blockchain.get_block(i).hash
            })

        ancestor_event = NodeEvent("ancestor_hashes", {
            "ancestor_hashes": ancestor,
            "highest_height": self.neh.node.blockchain.get_height()
        }, self.neh.node.origin)

        self.neh.fire_to(event.origin, ancestor_event) # This get event is send by some other peer. Even origin is the address of that peers

        return False # Don't relay

# Client side event
class AncestorHashesEvent(EventHandler):
    
    @staticmethod
    def require_field():
        return ["ancestor_hashes", "highest_height"]

    @staticmethod
    def event_name() -> str:
        return "ancestor_hashes"

    def handle(self, event: "NodeEvent"):
        ancestors = event.data["ancestor_hashes"]
        highest_height = int(event.data["highest_height"])
        local_hashes = self.neh.node.blockchain.chain.get_chain_hashes()

        # Convert local_hashes to dict for quick lookup by height
        local_hash_dict = {block["height"]: block["hash"] for block in local_hashes}

        # Tìm common ancestor (cao nhất, cùng height và hash)
        common_ancestor_height = None
        for remote_block in ancestors:
            height = remote_block["height"]
            hash_ = remote_block["hash"]
            if height in local_hash_dict and local_hash_dict[height] == hash_:
                common_ancestor_height = height
                break

        if common_ancestor_height is not None:
            logger.info(f"[SYNC] Common ancestor found at height {common_ancestor_height}")
            # Gửi request block sync từ ancestor đến head
            get_blocks_event = NodeEvent("get_blocks", {
                "start_index": common_ancestor_height,
                "end_index": highest_height, # Highest
            }, self.neh.node.address)
            # inspect(get_blocks_event)
            self.neh.fire_to(event.origin, get_blocks_event) # Send back where this came from to request a full sync
        else:
            logger.warning("[SYNC] No common ancestor found — full resync might be needed.")


