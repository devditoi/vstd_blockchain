import typing
if typing.TYPE_CHECKING:
    from src.mmb_layer0.node.node import Node, NodeEvent

class Peer:
    def __init__(self, node: "Node" = None, address: str = None):
        self.node = node # Just a dummy node
        self.address = address

    def fire(self, event: "NodeEvent"):
        raise NotImplementedError()
