# 1 node has 1 blockchain and 1 WorldState
import time

from ecdsa import SigningKey, VerifyingKey
from rsa import PrivateKey, PublicKey
from .blockchain.chain.chain import Chain
from .blockchain.consensus import ProofOfAuthority
from .blockchain.transactionType import Transaction, MintBurnTransaction
from .blockchain.transaction_processor import TransactionProcessor
from .blockchain.validator import Validator
from src.mmb_layer0.blockchain.chain.worldstate import WorldState
from .config import MMBConfig
from .utils.hash import HashUtils
from rich import print, inspect
from .blockchain.block import Block


class NodeEvent:
    def __init__(self, eventType, data, origin) -> None:
        self.eventType = eventType
        self.data = data
        self.origin = origin

class Node:
    def __init__(self) -> None:
        print("node.py:__init__: Initializing Node")
        self.blockchain: Chain = Chain()

        self.worldState: WorldState = WorldState()

        self.worldState.get_eoa("0x0")

        self.nativeTokenSupply = int(MMBConfig.NativeTokenValue * MMBConfig.NativeTokenQuantity)

        self.chain_file = "chain.json"
        self.version = open("node_ver.txt", "r").read()

        self.publicKey, self.privateKey = HashUtils.ecdsa_keygen()
        self.address = HashUtils.get_address_ecdsa(self.publicKey)

        self.node_subscribtions = []

        self.mintburn_nonce = 1

        print(f"{self.address[:4]}:node.py:__init__: Initialized node")

        self.consensus = ProofOfAuthority(self.address, self.privateKey)

    def import_key(self, filename: str) -> None:
        with open(filename, "r") as f:
            self.privateKey = SigningKey.from_string(f.read())
        with open(filename + ".pub", "r") as f:
            self.publicKey = VerifyingKey.from_string(f.read())
        self.address = HashUtils.get_address_ecdsa(self.publicKey)
        self.consensus = ProofOfAuthority(self.address, self.privateKey)
        print(f"{self.address[:4]}:node.py:import_key: Imported key " + self.address)

    def subscribe(self, node):
        if node in self.node_subscribtions:
            return
        self.node_subscribtions.append(node)
        node.subscribe(self)

    def process_event(self, event: NodeEvent) -> bool:
        print(f"{self.address[:4]}:node.py:process_event: Node {self.address} received event {event.eventType}")
        # inspect(event)
        if event.eventType == "tx":
            if self.blockchain.contain_transaction(event.data["tx"]): # Already processed
                return False
            self.blockchain.temporary_add_to_mempool(event.data["tx"])
            print(f"{self.address[:4]}:node.py:process_event: Processing transaction")
            self.process_tx(event.data["tx"], event.data["signature"], event.data["publicKey"])
            return True
        elif event.eventType == "block":
            if not self.consensus.is_valid(event.data["block"]): # Not a valid block
                return False
            return True if self.blockchain.add_block(event.data["block"]) else False
        return False # don't send unknown events

    def fire_event(self, event: NodeEvent):
        # time.sleep(1)
        if not self.process_event(event): # Already processed and broadcast
            return
        for node in self.node_subscribtions:
            # time.sleep(1)
            if node.address == event.origin:
                continue
            node.fire_event(event)

    def mint(self, address: str, privateKey: PrivateKey):
        # print("node.py:faucet: Processing 100 native tokens to address")
        amount = int(100 * MMBConfig.NativeTokenValue)
        tx = MintBurnTransaction(address, amount, self.mintburn_nonce + 1, 100)
        self.mintburn_nonce += 1
        sign = HashUtils.ecdsa_sign(tx.to_string(), privateKey)
        self.propose_tx(tx, sign, PublicKey.load_pkcs1(open(MMBConfig.MINT_KEY, "rb").read()))

    # def sync(self, other_json: str):
    #     # sync from another node
    #     other_obj = json.loads(other_json)
    #     print("node.py:sync: Syncing from " + other_obj["address"])
    #     blockchain_data = json.loads(other_obj["blockchain"])
    #     # Check height
    #     if self.blockchain.get_height() > blockchain_data["length"]:
    #         return

        # print(blockchain_data)
        # # Sync blocks
        # for i in range(self.blockchain.get_height(), blockchain_data["length"]):
        #     print(f"node.py:sync: Syncing block #{i}")
        #     block_data = blockchain_data["chain"][i]
        #     new_block = self.blockchain.add_block(BlockProcessor.cast_block(block_data))
        #     self.execution(new_block)

    # def check_sync(self, other_json: str):
    #     other_node = NodeSerializer.deserialize_node(other_json)
    #     return NodeSyncServices.check_sync(self, other_node)

    def get_height(self) -> int:
        return self.blockchain.get_height()

    def get_balance(self, address) -> int:
        return self.worldState.get_eoa(address).balance

    def get_native_token_supply(self) -> int:
        return self.nativeTokenSupply

    def get_nonce(self, address: str) -> int:
        return self.worldState.get_eoa(address).nonce

    def propose_tx(self, tx: Transaction, signature, publicKey):
        self.fire_event(NodeEvent("tx", {
            "tx": tx,
            "signature": signature,
            "publicKey": publicKey
        }, self.address))

    def process_tx(self, tx: Transaction, signature, publicKey):
        print(f"{self.address[:4]}:node.py:process_tx: Processing " + tx.Txtype + " transaction")

        # self.blockchain.temporary_add_to_mempool(tx)

        if not Validator.offchain_validate(tx, self.worldState): # Validate transaction
            return

        print(f"{self.address[:4]}:node.py:process_tx: Give transaction to blockchain nonce: " + str(tx.nonce))
        # print(tx, signature, publicKey)
        self.blockchain.add_transaction(tx, signature, publicKey, self.execution, self.consensus, self.propose_block)

    def propose_block(self, block: Block):
        self.fire_event(NodeEvent("block", {
            "block": block
        }, self.address))

    def execution(self, block: Block):
        # Block execution only happend after block is processed
        excecutor = TransactionProcessor(block, self.worldState)
        excecutor.process()

    # def save_chain(self):
    #     print("node.py:save_chain: Saving chain")
    #     chain_data = self.to_json()
    #     with open(self.chain_file, "w") as f:
    #         f.write(chain_data)
    #     print("node.py:save_chain: Saved chain")
    #
    # def load_chain(self):
    #     print("node.py:load_chain: Loading chain")
    #     chain_data = ""
    #     with open(self.chain_file, "r") as f:
    #         chain_data = f.read()
    #
    #     if chain_data == "":
    #         print("node.py:load_chain: No chain data found")
    #         return

        # self.blockchain = jsonlight.loads(Chain, chain_data)
        # self.blockchain.build_chain(chain_data)
        # self.blockchain.build_mempool(chain_data)
        # print("node.py:load_chain: Loaded chain")


    def debug(self):
        print(f"{self.address[:4]}:node.py:debug:-------------------------------Debug node----------------------")
        self.blockchain.debug_chain()
        print(self.worldState)
        print(self.address, self.publicKey, self.privateKey)
        print(f"{self.address[:4]}:node.py:debug:-------------------------------Debug node----------------------")