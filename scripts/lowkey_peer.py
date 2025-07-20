from layer0.node.node import Node
from layer0.p2p.peer_type.remote_peer import RemotePeer
from layer0.p2p.udp_protocol import UDPProtocol
from layer0.utils.crypto.signer import SignerFactory
from layer0.wallet.wallet import Wallet
from layer0.utils.logging_config import get_logger
import time

logger = get_logger(__name__)

if __name__ == '__main__':
    master = Node()
    # master.import_key("validator_key")
    master.log_state()

    protocol = UDPProtocol(master.node_event_handler, 2710)
    master.set_origin("127.0.0.1:2710")

    boostrap = RemotePeer("127.0.0.1", 5000)
    master.node_event_handler.subscribe(boostrap)

    w = Wallet(master)
    pmint_key, mint_key = SignerFactory().get_signer().load("mint_key")

    time.sleep(30)
    master.log_state()
    while True:
        # mint to self
        logger.info("Minting...")
        master.mint(w.address, mint_key, pmint_key)
        master.log_state()

        logger.info("--------------------------------Waiting for confirm transaction...")
        currentMempool = len(master.node_event_handler.node.blockchain.mempool)
        while len(master.node_event_handler.node.blockchain.mempool) == currentMempool:
            time.sleep(1)
        logger.info("--------------------------------Done. Transaction confirmed.")
        master.log_state()
        time.sleep(3)