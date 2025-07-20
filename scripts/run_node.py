from layer0.node.node import Node
from layer0.p2p.peer_type.remote_peer import RemotePeer
from layer0.p2p.udp_protocol import UDPProtocol
from rich import print
import os
import shutil
from layer0.utils.logging_config import get_logger, setup_logging
# Initialize logging with both console and file handlers
# Initialize basic logging first
setup_logging(console_log=True, file_log=True)
logger = get_logger(__name__)

# Test 1
# node = Node()
# node.log_state()
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
# node.log_state()
# node2.log_state()


# Test 2
# node = Node()
# node.log_state()
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
# # node.log_state()
# # leader.log_state()
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
# # node.log_state()
# # leader.log_state()
# # print(wallet.get_balance())
# # print(wallet2.get_balance())


# Test 3
# node = Node()
# node.log_state()
#
# leader = Node()
# leader.import_key("validator_key")


# Test 4
import multiprocessing
from layer0.utils.logging_config import get_logger, setup_logging
def start_node(port: int):
    node = Node()
    node.log_state()
    setup_logging(
        node_address=node.address,
        console_log=True,
        file_log=True
    )
    node.set_origin(f"127.0.0.1:{port}")
    __other = RemotePeer("127.0.0.1", 5000)
    # inspect(__other)
    node.node_event_handler.subscribe(__other)
    __protocol = UDPProtocol(node.node_event_handler, port)  # auto listen in background

    while True:
        pass

logger = get_logger(__name__)

def clear_blockchain_node():
    for path in os.listdir():
        if path.startswith("chain_") and path.endswith("_blockchain"):
            logger.info(f"Try to remove: {path}")
            shutil.rmtree(path)

        if path.startswith("chain_") and path.endswith("_transaction"):
            logger.info(f"Try to remove: {path}")
            shutil.rmtree(path)


if __name__ == '__main__':
    clear_blockchain_node()

    master = Node()
    master.import_key("validator_key")
    master.log_state()
    
    # Reconfigure logging with node address
    setup_logging(
        node_address=master.address,
        console_log=True,
        file_log=True
    )

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
        p = multiprocessing.Process(
            target=start_node,
            args=(port,)
        )
        p.start()

    while True:
        pass