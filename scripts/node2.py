from mmb_layer0.node.node import Node
from mmb_layer0.p2p.peer_type.remote_peer import RemotePeer
from mmb_layer0.p2p.udp_protocol import UDPProtocol

master = Node()
master.import_key("validator_key")
master.debug()

protocol = UDPProtocol(master, 5001)
master.set_origin("127.0.0.1:5001")
other = RemotePeer("127.0.0.1", 5000)
master.subscribe(other)

while True:
    pass