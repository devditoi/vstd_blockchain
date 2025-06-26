from layer0.node.node import Node
from layer0.p2p.peer_type.remote_peer import RemotePeer
from layer0.p2p.udp_protocol import UDPProtocol

master = Node()
# master.import_key("validator_key")
master.debug()

protocol = UDPProtocol(master.node_event_handler, 9999)
master.set_origin("127.0.0.1:9999")
other = RemotePeer("127.0.0.1", 5000)
master.node_event_handler.subscribe(other)

while True:
    pass