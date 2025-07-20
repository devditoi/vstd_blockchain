# Test 4
import multiprocessing
import pytest
import time
import random
from layer0.p2p.peer_type.remote_peer import RemotePeer
from layer0.p2p.udp_protocol import UDPProtocol
from layer0.node.node import Node

def start_node(port: int):
    node = Node()
    node.log_state()
    node.set_origin(f"127.0.0.1:{port}")
    __other = RemotePeer("127.0.0.1", 5000)
    # inspect(__other)
    node.node_event_handler.subscribe(__other)
    __protocol = UDPProtocol(node.node_event_handler, port)  # auto listen in background
    while True:
        pass

@pytest.fixture
def data():
    master = Node()
    master.import_key("validator_key")
    master.log_state()

    UDPProtocol(master.node_event_handler, 5000)
    master.set_origin("127.0.0.1:5000")
    # other = RemotePeer("127.0.0.1", 5000)
    # master.subscribe(other)

    # p1 = multiprocessing.Process(target=start_node, args=(5001,))
    # p2 = multiprocessing.Process(target=start_node, args=(5002,))
    # p1.start()
    # p2.start()

    # TODO: Somehow expanding the network? multiple node test?
    peers_test = random.randint(5, 15) # Temporary limit this shit

    processes = []
    for i in range(peers_test):
        port = 5001 + i
        p = multiprocessing.Process(target=start_node, args=(port,))
        p.start()

        processes.append(p)

    return master, peers_test, processes

@pytest.fixture(autouse=True)
def cleanup(data):
    yield # Run test

    for p in data[2]:
        p.terminate()

def length_polling(node, expected_peers, timeout=20, interval=0.5):
    max_iter = int(timeout * (1 + expected_peers / 10)/ interval)
    time_for_second_dial = 10
    time.sleep(time_for_second_dial)
    for _ in range(max_iter):
        if len(node.node_event_handler.peers) >= expected_peers:
            return True
        time.sleep(interval)
    return False

def test_network_check(data):

    # Wait at least 20 seconds
    master_node, peers, processes = data
    # check if all peers are connected
    #! current limit: 10 peers
    assert length_polling(master_node, min(peers, 10)), "Master peer connection timeout"

    # Check if a node can join the network
    node = Node()
    node.log_state()
    node.set_origin("127.0.0.1:2710")
    __other = RemotePeer("127.0.0.1", 5000) # This is the bootstrap node
    node.node_event_handler.subscribe(__other)
    __protocol = UDPProtocol(node.node_event_handler, 2710)

    # check if all peers are connected
    assert length_polling(node, min(peers, 10, 60)), "Peer connection timeout"
