import logging
from builtins import staticmethod
from layer0.node.events.EventHandler import EventHandler
from layer0.node.events.node_event import NodeEvent
from layer0.utils.serializer import WorldStateSerializer

logger = logging.getLogger(__name__)

class GetWorldStateEvent(EventHandler):
    
    @staticmethod
    def require_field():
        return []

    def event_name(self) -> str:
        return "getworldstate"

    def handle(self, event: "NodeEvent"):
        logger.debug(f"[{self.neh.node.origin}] GetWorldStateEvent.handle: received request for worldstate from {event.origin}")
        # This is a request to get the worldstate of the node
        self.neh.fire_to_raw(event.origin, NodeEvent("getworldstate_finished", {
            "worldstate": WorldStateSerializer.serialize_world_state(self.neh.node.worldState)
        }, self.neh.node.origin))

