from src.mmb_layer0.node.node import Node
from src.mmb_layer0.p2p.peer_type.remote_peer import RemotePeer
from src.mmb_layer0.p2p.udp_protocol import UDPProtocol

master = Node()
master.debug()
protocol = UDPProtocol(master, 5000) # auto listen in background
other = RemotePeer("127.0.0.1", 5001)
master.subscribe(other)

while True:
    pass