import logging
from layer0.utils.crypto.signer import SignerFactory
from math import floor
from layer0.blockchain.core.block import Block
from ecdsa import VerifyingKey

from layer0.blockchain.processor.block_processor import BlockProcessor
from layer0.node.events.EventHandler import EventHandler
from layer0.node.events.node_event import NodeEvent

logger = logging.getLogger(__name__)

class BFTBlockEvent(EventHandler):
    @staticmethod
    def event_name() -> str:
        return "bft_confirm"
    
    @staticmethod
    def require_field() -> list[str]:
        return ["block", "receipts_root", "signatures", "address", "publicKey"]
    
    def contain_in_pool(self, block: Block) -> bool:

        return block.hash in self.neh.node.blockchain.block_bft_sign
    
    def get_block_in_pool(self, block_hash: str) -> Block | None:
        block: Block | None = None
        for block in self.neh.node.blockchain.block_bft_pool:
            if block.hash == block_hash:
                return block
            
        return None
    
    def handle(self, event: "NodeEvent") -> bool:
        block = event.data["block"]
        receipts_root: str = event.data["receipts_root"]
        if isinstance(block, str):
            block: Block = BlockProcessor.cast_block(event.data["block"])
            
        if not self.contain_in_pool(block):
            logger.warning("bft_block_event.py:handle: Block is not in pool")
            return False
        
        pending_block = self.get_block_in_pool(block.hash)
        
        if not pending_block:
            return False # Cannot find pending block in pool
        
        # Check my receipts root
        if pending_block.receipts_root != receipts_root:
            logger.error("bft_block_event.py:handle: Receipts root does not match")
            return False
        
        blockchain_instance = self.neh.node.blockchain
        
        sign: str = event.data["signatures"]
        address: str = event.data["address"]
        publicKey: str = event.data["publicKey"]
        pk_obj: VerifyingKey = SignerFactory().get_signer().deserialize(publicKey)
        
        # is the address is indeed with the public key?
        if not SignerFactory().get_signer().address(pk_obj) == address:
            logger.error("bft_block_event.py:handle: Address does not match")
            return False
        
        # Is the address is the validator?
        if address not in self.neh.node.worldState.get_validators():
            logger.error("bft_block_event.py:handle: Address is not a validator")
            return False
        
        # Is the signature valid?
        if not SignerFactory().get_signer().verify(block.get_string_for_signature(), sign, pk_obj):
            logger.error("bft_block_event.py:handle: Signature is not valid")
            return False
        
        # Is the signature already exist?
        if sign in blockchain_instance.block_bft_sign[block.hash]:
            logger.warning("bft_block_event.py:handle: Signature already exist")
            return False
        
        blockchain_instance.block_bft_sign[block.hash].append(sign)
        
        logger.info(f"bft_block_event.py:handle: Block #{block.index} has a vote!")
        logger.debug(f"Required votes: {floor(len(self.neh.node.worldState.get_validators()) / 1.5)}")
        
        if len(blockchain_instance.block_bft_sign[block.hash]) >= floor(len(self.neh.node.worldState.get_validators()) / 1.5):
            blockchain_instance.finalize_block(block)
        
        return True