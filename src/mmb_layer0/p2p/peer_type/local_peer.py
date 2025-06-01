from ..peer import Peer
from src.mmb_layer0.node.node import Node, NodeEvent


class LocalPeer(Peer):
    def __init__(self, node: Node):
        super().__init__(node, "127.0.0.1")

    def fire(self, event: NodeEvent):
        if self.node.address == event.origin:
            return
        self.node.broadcast(event)
