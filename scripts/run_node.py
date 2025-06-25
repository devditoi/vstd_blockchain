from mmb_layer0.config import ChainConfig
from mmb_layer0.node.node import Node
from mmb_layer0.p2p.peer_type.local_peer import LocalPeer
from mmb_layer0.p2p.peer_type.remote_peer import RemotePeer
from mmb_layer0.p2p.udp_protocol import UDPProtocol
from mmb_layer0.utils.crypto.signer import SignerFactory
from mmb_layer0.wallet.wallet import Wallet
from rich import print, inspect
import time


# Test 1
# node = Node()
# node.debug()
# node2 = Node()
# # node2.sync(NodeSerializer.to_json(node))
# node.subscribe(node2)
# w1 = Wallet(node)
# privateK = rsa.PrivateKey.load_pkcs1(open("private_key.pem", "rb").read())
# # # # print(privateK)
# node.mint(w1.address, privateK)
# node.mint(w1.address, privateK)
#
# print(NodeSyncServices.check_sync(node2, node))
# node.debug()
# node2.debug()


# Test 2
# node = Node()
# node.debug()
#
# leader = Node()
# leader.import_key("validator_key")
#
# node.subscribe(leader) # and backwards
#
# wallet = Wallet(node)
# wallet2 = Wallet(leader)
# pmint_key, mint_key = SignerFactory().get_signer().load("mint_key")
# node.mint(wallet.address, mint_key, pmint_key)
# #
# # node.debug()
# # leader.debug()
# #
# # i = 0
# # # Leader block creation in the background
# # while i < 15:
# #     time.sleep(2)
# #     # NodeSyncServices.check_sync(node, leader)
# #     if wallet.get_balance() > int(0.01 * ChainConfig.NativeTokenValue):
# #         wallet.pay(int(0.01 * ChainConfig.NativeTokenValue), wallet2.address)
# #     print(wallet2.get_balance())
# #     i += 1
# #
# # node.debug()
# # leader.debug()
# # print(wallet.get_balance())
# # print(wallet2.get_balance())


# Test 3
# node = Node()
# node.debug()
#
# leader = Node()
# leader.import_key("validator_key")


# Test 4
import multiprocessing
def start_node(port: int):
    node = Node()
    node.debug()
    node.set_origin(f"127.0.0.1:{port}")
    __other = RemotePeer("127.0.0.1", 5000)
    # inspect(__other)
    node.node_event_handler.subscribe(__other)
    __protocol = UDPProtocol(node.node_event_handler, port)  # auto listen in background

    while True:
        pass

if __name__ == '__main__':
    master = Node()
    master.import_key("validator_key")
    master.debug()

    protocol = UDPProtocol(master.node_event_handler, 5000)
    master.set_origin("127.0.0.1:5000")
    # other = RemotePeer("127.0.0.1", 5000)
    # master.subscribe(other)

    # p1 = multiprocessing.Process(target=start_node, args=(5001,))
    # p2 = multiprocessing.Process(target=start_node, args=(5002,))
    # p1.start()
    # p2.start()

    peers_test = 1
    for i in range(peers_test):
        port = 5001 + i
        p = multiprocessing.Process(target=start_node, args=(port,))
        p.start()

    while True:
        pass