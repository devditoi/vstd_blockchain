from mmb_layer0.node.events.EventHandler import EventHandler
from mmb_layer0.node.node_event_handler import NodeEventHandler, NodeEvent
from mmb_layer0.p2p.peer_type.remote_peer import RemotePeer
from mmb_layer0.utils.network_utils import is_valid_origin
from mmb_layer0.utils.serializer import PeerSerializer


class PeerDiscoveryEvent(EventHandler):
    def __init__(self, node_event_handler: "NodeEventHandler"):
        super().__init__(node_event_handler)

    @staticmethod
    def event_name() -> str:
        return "peer_discovery"

    def require_field(self):
        return ["origin"]

    def handle(self, event: "NodeEvent"):

        if not self.neh.check_connection(event.origin):
            data = is_valid_origin(event.origin)
            if not data:
                return False
            ip, port = data
            peer = RemotePeer(ip, int(port))
            # inspect(peer)
            self.neh.subscribe(peer) # Add connection to this peer
            return False

        self.neh.fire_to(event.origin, NodeEvent("peer_discovery_fullfilled",
    {
            "peers": PeerSerializer.serialize_multi_peers(self.neh.peers.copy())
        },
        self.neh.node.origin))

        return False

class PeerDiscoveryFullfilledEvent(EventHandler):
    def __init__(self, node_event_handler: "NodeEventHandler"):
        super().__init__(node_event_handler)

    @staticmethod
    def event_name() -> str:
        return "peer_discovery_fullfilled"

    def require_field(self):
        return ["peers"]

    def handle(self, event: "NodeEvent"):
        peers = PeerSerializer.deserialize_multi_peers(event.data["peers"])
        for peer in peers:
            if self.neh.check_connection(peer.address):
                # print(f"[NodeEventHandler] [bold green]{self.node.origin}[/bold green]: Already subscribed to {peer.address}")
                continue
            if peer.address == self.neh.node.origin:  # Don't subscribe to yourself lol
                # print(f"[NodeEventHandler] [bold green]{self.node.origin}[/bold green]: Don't subscribe to yourself")
                continue
            self.neh.subscribe(peer)

        print(f"[NodeEventHandler] [bold green]{self.neh.node.origin}[/bold green]: Subscribed to {len(self.peers)} peers")
        # inspect(self.peers)

        return False  # Don't relay