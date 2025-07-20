import logging
from layer0.utils.ThreadUtils import defer
from layer0.blockchain.core.worldstate import WorldState
from layer0.blockchain.core.chain import Chain
from layer0.blockchain.consensus.poa_consensus import ProofOfAuthority
from layer0.node.remote_node import RemoteNode
from layer0.node.node_event_handler import NodeEventHandler
from layer0.utils.crypto.signer import SignerFactory
from layer0.config import ChainConfig
from layer0.utils.logging_config import get_logger

logger = get_logger(__name__)

class Node:
    def __init__(self, dummy = False) -> None:
        logger.info("Initializing Node")

        self.worldState: WorldState = WorldState()
        self.worldState.get_eoa("0x0")
        self.nativeTokenSupply = int(ChainConfig().NativeTokenValue * ChainConfig().NativeTokenQuantity)

        self.chain_file = "chain.json"
        self.version = "v0.0.1"

        self.signer = SignerFactory().get_signer()
        self.publicKey, self.privateKey = self.signer.gen_key()
        self.address = self.signer.address(self.publicKey)

        self.blockchain: Chain = Chain(self.address, dummy)
        self.isValidator = False
        
        logger.info(f"Initialized node")
        self.node_event_handler = NodeEventHandler(self)

        # Create ChainConfig instance
        self.chain_config = ChainConfig()
        
        # Check if validators are configured
        if not self.chain_config.validators:
            logger.warning("No validators configured - node will not participate in consensus")
            self.isValidator = False
        else:
            self.isValidator = self.address in self.chain_config.validators

        self.consensus = ProofOfAuthority(self.address, self.privateKey, self.chain_config)
        
        # Set blockchain callbacks
        self.blockchain.set_initial_data(
            self.consensus,
            self.execute_block,
            self.broadcast,
            self.worldState,
            self.node_event_handler
        )

    def execute_block(self, block):
        # Simplified for brevity
        pass

    def broadcast(self, event):
        # Simplified for brevity
        pass