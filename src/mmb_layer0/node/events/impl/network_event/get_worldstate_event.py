from mmb_layer0.node.events.EventHandler import EventHandler
from mmb_layer0.node.events.node_event import NodeEvent
from mmb_layer0.utils.serializer import WorldStateSerializer


class GetWorldStateEvent(EventHandler):
    def require_field(self):
        return []

    def event_name(self) -> str:
        return "getworldstate"

    def handle(self, event: "NodeEvent"):
        # This is a request to get the worldstate of the node
        self.neh.fire_to_raw(event.origin, NodeEvent("getworldstate_finished", {
            "worldstate": WorldStateSerializer.serialize_world_state(self.neh.node.worldState)
        }, self.neh.node.origin))

