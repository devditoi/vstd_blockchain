from layer0.node.node import Node
from layer0.p2p.peer_type.remote_peer import RemotePeer
from layer0.p2p.udp_protocol import UDPProtocol

master = Node()
master.log_state()
protocol = UDPProtocol(master.node_event_handler, 5000) # auto listen in background
master.set_origin("127.0.0.1:5000")
other = RemotePeer("127.0.0.1", 5001)
master.node_event_handler.subscribe(other)

while True:
    pass