# 1 node has 1 blockchain and 1 WorldState
from layer0.utils.logger import Logger
from layer0.blockchain.core.transaction_type import ValidatorTransactionData
from typing import cast
from layer0.blockchain.core.transaction_type import ValidatorTransaction
from layer0.smart_contract.sc_storage import CentralStorageConstructor
from typing import Any
from layer0.config import FeatureFlags
from layer0.utils.hash import HashUtils
import time
from layer0.blockchain.core.chain import Chain
from layer0.blockchain.consensus.poa_consensus import ProofOfAuthority
from layer0.blockchain.core.transaction_type import Transaction
from layer0.blockchain.processor.transaction_processor import TransactionProcessor
from layer0.blockchain.core.validator import Validator
from layer0.blockchain.core.worldstate import WorldState
from layer0.config import ChainConfig
import typing
from layer0.node.node_event_handler import NodeEventHandler

if typing.TYPE_CHECKING:
    pass
from layer0.node.events.node_event import NodeEvent
from layer0.utils.crypto.signer import SignerFactory
from rich import print
from layer0.blockchain.core.block import Block

class Node:
    def __init__(self, dummy = False) -> None:
        self.signer = SignerFactory().get_signer()
        self.publicKey, self.privateKey = self.signer.gen_key()
        self.address = self.signer.address(self.publicKey)
        self.logger = Logger(self.address)

        self.logger.log("[bold blue]node.py:__init__:[/] Initializing Node")

        self.worldState: WorldState = WorldState()
        self.worldState.get_eoa("0x0")

        self.nativeTokenSupply = int(ChainConfig.NativeTokenValue * ChainConfig.NativeTokenQuantity)

        self.chain_file = "chain.json"
        self.version = "v0.0.1"

        self.blockchain: Chain = Chain(self.address, dummy)
        
        self.isValidator = False

        self.logger.log(f"[bold green]{self.address[:4]}:node.py:__init__:[/] Initialized node")

        self.node_event_handler = NodeEventHandler(self)

        self.consensus = ProofOfAuthority(self.address, self.privateKey)
        
        self.worldState.add_validator(self.consensus.hardcoded_validator)
        
        self.blockchain.set_initial_data(self.consensus, self.execution, self.propose_block, self.worldState, self.node_event_handler)

        self.origin = ""

        self.chain_file = f"{self.address}_chain.json"
        
        self.smart_contract: dict[str, Any] = {}
        self.sc_storage = CentralStorageConstructor()

    def propose_block(self, block: Block):
        self.node_event_handler.propose_block(block)

    def set_origin(self, origin: str) -> None:
        self.origin = origin
        
    def became_validator(self):
        data: ValidatorTransactionData = cast(ValidatorTransactionData, {
            "validator": self.address,
            "proof": "0x0"
        })
        tx: ValidatorTransaction = ValidatorTransaction(self.address, data, int(time.time() * 1000), 0, 0)
        
        self.propose_tx(tx, tx.signature, self.publicKey)

    def import_key(self, filename: str) -> None:
        self.signer = SignerFactory("ecdsa`").get_signer()
        self.logger.log(self.signer)
        self.publicKey, self.privateKey = self.signer.load(filename)
        self.address = self.signer.address(self.publicKey)
        self.consensus = ProofOfAuthority(self.address, self.privateKey)
        self.blockchain.set_initial_data(self.consensus, self.execution, self.node_event_handler.propose_block, self.worldState, self.node_event_handler)
        self.logger.log(f"[bold green]{self.address[:4]}:node.py:import_key:[/] Imported key " + self.address)

    def export_key(self, filename: str) -> None:
        self.signer.save(filename, self.publicKey, self.privateKey)
        self.logger.log(f"[bold green]{self.address[:4]}:node.py:export_key:[/] Exported key " + self.address)

    def get_height(self) -> int:
        return self.blockchain.get_height()

    def get_balance(self, address) -> int:
        return self.worldState.get_eoa(address).balance

    def get_native_token_supply(self) -> int:
        return self.nativeTokenSupply

    def get_nonce(self, address: str) -> int:
        return self.worldState.get_eoa(address).nonce

    def get_tx(self, tx_hash) -> Transaction | None:
        return self.blockchain.get_tx(tx_hash)

    def get_txs(self) -> list[str]:
        return self.blockchain.get_txs()

    def get_block(self, height: int) -> Block | None:
        return self.blockchain.get_block(height)

    def query_tx(self, query: str, field: str | None = None) -> list[dict]:
        return self.blockchain.query_tx(query, field)

    def query_block(self, query: str, field: str | None = None) -> list[str]:
        return self.blockchain.query_block(query, field)

    def propose_tx(self, tx: Transaction, signature, publicKey):
        self.node_event_handler.broadcast(NodeEvent("tx", {
            "tx": tx,
            "signature": signature,
            "publicKey": publicKey,
        }, self.origin))

    def process_tx(self, tx: Transaction, signature, publicKey):
        self.logger.log(f"[bold blue]{self.address[:4]}:node.py:process_tx:[/] Add pool " + tx.Txtype + " transaction")

        pK = SignerFactory().get_signer().deserialize(publicKey)
        if FeatureFlags.DEBUG:
            addr = SignerFactory().get_signer().address(pK)
            self.logger.log(f"[bold blue]{self.address[:4]}:node.py:process_tx:[/] Transaction sender address: {addr}")
            
            self.logger.log(HashUtils.sha256(tx.to_verifiable_string()))

                
            self.logger.log("[bold yellow]------------------------------------------------------- START THE HARD PART GG[/]")

        if not Validator.validate_transaction_with_worldstate(tx, self.worldState):
            return
        
        if FeatureFlags.DEBUG:
            self.logger.log (f"[bold blue]{self.address[:4]}:node.py:process_tx:[/] Transaction hash: {HashUtils.sha256(tx.to_verifiable_string())}")
            self.logger.log (f"[bold blue]{self.address[:4]}:node.py:process_tx:[/] Transaction signature: {signature}")
            self.logger.log (f"[bold blue]{self.address[:4]}:node.py:process_tx:[/] Transaction public key: {publicKey}")
        
        if not Validator.validate_transaction_raw(tx):
            self.logger.log(f"[bold red]{self.address[:4]}:node.py:process_tx:[/] Transaction is invalid - raw validation failed")
            return
        
        
        if not Validator.validate_transaction_with_signature(tx, signature, pK):
            self.logger.log(f"[bold red]{self.address[:4]}:node.py:process_tx:[/] Transaction signature is invalid")
            return
        else:
            self.logger.log(f"[bold green]{self.address[:4]}:node.py:process_tx:[/] Transaction signature is valid")

        self.logger.log(f"[bold blue]{self.address[:4]}:node.py:process_tx:[/] Give transaction to blockchain nonce: " + str(tx.nonce))


        self.blockchain.add_transaction(tx, signature, publicKey)

    def execution(self, block: Block):

        if block.index == 0:
            return

        excecutor = TransactionProcessor(block, self.worldState)
        excecutor.process()

    def debug(self):
        self.logger.log(f"[bold magenta]{self.address[:4]}:node.py:debug:[/]-------------------------------Debug node----------------------")
        self.blockchain.debug_chain()
        self.logger.log(self.worldState)
        self.logger.log(f"Address: {self.address}, Public Key: {self.publicKey}, Private Key: {self.privateKey}")
        self.logger.log(f"[bold magenta]{self.address[:4]}:node.py:debug:[/]-------------------------------Debug node----------------------")