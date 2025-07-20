from layer0.blockchain.core.validator import Validator
from layer0.node.events.node_event import NodeEvent
from layer0.utils.hash import HashUtils
from layer0.config import FeatureFlags
from layer0.blockchain.processor.transaction_processor import TransactionProcessor
from layer0.blockchain.core.transaction_type import Transaction, ValidatorTransactionData, ValidatorTransaction
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
import typing
if typing.TYPE_CHECKING:
    from layer0.blockchain.core.block import Block

logger = get_logger(__name__)

class Node:
    def __init__(self, dummy = False) -> None:
        logger.info("Initializing Node")

        self.worldState: WorldState = WorldState()
        self.worldState.get_eoa("0x0")
        self.nativeTokenSupply = int(ChainConfig().NativeTokenValue * ChainConfig().NativeTokenQuantity)

        self.chain_file = "chain.json"
        self.version = "v0.0.1"
        self.origin = ""  # Initialize origin attribute as empty string

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
        if self.chain_config.validators:
            self.isValidator = self.address in self.chain_config.validators
        else:
            self.isValidator = False

        self.consensus = ProofOfAuthority(self.address, self.privateKey, self.chain_config)
        
        # Set blockchain callbacks
        self.blockchain.set_initial_data(
            self.consensus,
            self.execution,
            self.node_event_handler.propose_block,
            self.worldState,
            self.node_event_handler
        )
        
    def import_key(self, filename: str) -> None:
        """Load validator keys from file"""
        self.publicKey, self.privateKey = self.signer.load(filename)
        self.address = self.signer.address(self.publicKey)
        
        # Update the consensus object with new keys
        self.consensus = ProofOfAuthority(self.address, self.privateKey, self.chain_config)
        
        # Update the chain object with new keys
        self.blockchain.consensus = self.consensus
        
        # Recalculate validator status
        self.isValidator = self.address in self.chain_config.validators
        
        logger.info(f"Imported validator key: {self.address[:8]}...")
    
    def propose_block(self, block: "Block"):
        self.node_event_handler.propose_block(block)

    def set_origin(self, origin: str) -> None:
        self.origin = origin
        
    # def became_validator(self):
    #     # self.isValidator = True
    #     # self.blockchain.isValidator = True
        
    #     # TODO: Here need to send custom transaction that confirm you are validator
    #     data: ValidatorTransactionData = cast(ValidatorTransactionData, {
    #         "validator": self.address,
    #         "proof": "0x0"
    #     })
    #     tx: ValidatorTransaction = ValidatorTransaction(self.address, data, int(time.time() * 1000), 0, 0)
        
    #     # Propose the transaction
    #     self.propose_tx(tx, tx.signature, self.publicKey)

    # def import_key(self, filename: str) -> None:
    #     self.signer = SignerFactory("ecdsa`").get_signer()
    #     print(self.signer)
    #     self.publicKey, self.privateKey = self.signer.load(filename)
    #     self.address = self.signer.address(self.publicKey)
    #     self.consensus = ProofOfAuthority(self.address, self.privateKey)
    #     self.blockchain.set_initial_data(self.consensus, self.execution, self.node_event_handler.propose_block, self.worldState, self.node_event_handler)
    #     print(f"{self.address[:4]}:node.py:import_key: Imported key " + self.address)

    def export_key(self, filename: str) -> None:
        self.signer.save(filename, self.publicKey, self.privateKey)
        print(f"{self.address[:4]}:node.py:export_key: Exported key " + self.address)

    #! Depricated, not called by node anymore, typical admin wallet, address, contract.
    # TODO: When approuch smart contract. This will be use to overcollateral.V
    # def mint(self, address: str, privateKey: any, publicKey: any) -> None:
    #     # print("node.py:faucet: Processing 100 native tokens to address")
    #     amount = int(100 * ChainConfig.NativeTokenValue)
    #     tx = MintBurnTransaction(address, amount, self.mintburn_nonce + 1, 0)
    #     self.mintburn_nonce += 1
    #     sign = self.signer.sign(tx.to_verifiable_string(), privateKey)
    #     self.propose_tx(tx, sign, publicKey)

    def get_height(self) -> int:
        return self.blockchain.get_height()

    def get_balance(self, address) -> int:
        return self.worldState.get_eoa(address).balance

    def get_native_token_supply(self) -> int:
        return self.nativeTokenSupply

    def get_nonce(self, address: str) -> int:
        return self.worldState.get_eoa(address).nonce

    def get_tx(self, tx_hash) -> "Transaction | None":
        return self.blockchain.get_tx(tx_hash)

    def get_txs(self) -> list[str]:
        return self.blockchain.get_txs()

    def get_block(self, height: int) -> "Block | None":
        return self.blockchain.get_block(height)

    def query_tx(self, query: str, field: str | None = None):
        return self.blockchain.query_tx(query, field)

    def query_block(self, query: str, field: str | None = None) -> list[str]:
        return self.blockchain.query_block(query, field)

    def propose_tx(self, tx: "Transaction", signature, publicKey):
        """
        :param tx: Transaction
        :param signature: Signature (HEX)
        :param publicKey: Public key (HEX)
        :return:
        """
        self.node_event_handler.broadcast(NodeEvent("tx", {
            "tx": tx,
            "signature": signature,
            "publicKey": publicKey, #! Assume the public key are HEXDECIMAL
        }, self.origin))

    def process_tx(self, tx: Transaction, signature, publicKey):
        print(f"{self.address[:4]}:node.py:process_tx: Add pool " + tx.Txtype + " transaction")

        # self.blockchain.temporary_add_to_mempool(tx)
        pK = SignerFactory().get_signer().deserialize(publicKey)
        if FeatureFlags.DEBUG:
            addr = SignerFactory().get_signer().address(pK)
            print(f"{self.address[:4]}:node.py:process_tx: Transaction sender address: {addr}")
            
            print(HashUtils.sha256(tx.to_verifiable_string()))

                
            print("------------------------------------------------------- START THE HARD PART GG")

        if not Validator.validate_transaction_with_worldstate(tx, self.worldState): # Validate transaction
            return
        
        # 3 thing need to verify
        # 1. Trnansaction hash
        # 2. Signature
        # 3. Public key
        if FeatureFlags.DEBUG:
            print (f"{self.address[:4]}:node.py:process_tx: Transaction hash: {HashUtils.sha256(tx.to_verifiable_string())}")
            print (f"{self.address[:4]}:node.py:process_tx: Transaction signature: {signature}")
            print (f"{self.address[:4]}:node.py:process_tx: Transaction public key: {publicKey}")
        
        if not Validator.validate_transaction_raw(tx):
            print(f"{self.address[:4]}:node.py:process_tx: Transaction is invalid - raw validation failed")
            return
        
        
        if not Validator.validate_transaction_with_signature(tx, signature, pK):
            print(f"{self.address[:4]}:node.py:process_tx: Transaction signature is invalid")
            return
        else:
            print(f"{self.address[:4]}:node.py:process_tx: Transaction signature is valid")

        print(f"{self.address[:4]}:node.py:process_tx: Give transaction to blockchain nonce: " + str(tx.nonce))
        # print(tx, signature, publicKey)


        self.blockchain.add_transaction(tx, signature, publicKey)

    def execution(self, block: "Block"):

        if block.index == 0:
            # Don't process genesis block
            return

        # Block execution only happend after block is processed
        excecutor = TransactionProcessor(block, self.worldState)
        excecutor.process()