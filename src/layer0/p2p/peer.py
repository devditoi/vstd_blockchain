import typing
if typing.TYPE_CHECKING:
    from layer0.node.node import Node, NodeEvent

class Peer:
    def __init__(self, node: "Node" = None, address: str = None, ip: str = None, port: int = None):
        self.port = port
        self.ip = ip
        self.node = node # Just a fake node
        self.address = address

    def fire(self, event: "NodeEvent"):
        raise NotImplementedError()
