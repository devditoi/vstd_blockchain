import pytest
from mmb_layer0.blockchain.core.block import Block
from mmb_layer0.node.node import Node
from mmb_layer0.p2p.peer_type.local_peer import LocalPeer


@pytest.fixture
def data():
    node1 = Node()
    node2 = Node()
    node1.import_key("validator_key")

    node1_protocol = LocalPeer(node1)
    node2_protocol = LocalPeer(node2)

    node1.node_event_handler.subscribe(node2_protocol)
    node2.node_event_handler.subscribe(node1_protocol)

