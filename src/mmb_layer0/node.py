# 1 node has 1 blockchain and 1 WorldState

from rsa import PrivateKey, PublicKey
from .blockchain.chain.chain import Chain
from .blockchain.transactionType import Transaction, MintBurnTransaction
from .blockchain.transaction_processor import TransactionProcessor
from .blockchain.validator import Validator
from src.mmb_layer0.blockchain.chain.worldstate import WorldState
from .config import MMBConfig
from .utils.hash import HashUtils
from rich import print
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
        print("node.py:__init__: Initialized blockchain")
        self.worldState: WorldState = WorldState()
        print("node.py:__init__: Initialized worldState")
        self.worldState.get_eoa("0x0")
        print("node.py:__init__: Added EOAs for address 0x0")
        self.nativeTokenSupply = int(MMBConfig.NativeTokenValue * MMBConfig.NativeTokenQuantity)
        print(f"node.py:__init__: Set native token supply to {self.nativeTokenSupply}")
        # Set faucet balance
        # self.faucetKeyPair = HashUtils.gen_key()
        # self.worldState.get_eoa(MMBConfig.FaucetAddress).balance = nativeTokenSupply

        self.chain_file = "chain.json"
        self.version = open("node_ver.txt", "r").read()

        self.publicKey, self.privateKey = HashUtils.gen_key()
        self.address = HashUtils.get_address(self.publicKey)
        # if os.path.exists(self.chain_file):
        #     self.load_chain()

        self.node_subscribtions = []

    def subscribe(self, node):
        if node in self.node_subscribtions:
            return
        self.node_subscribtions.append(node)
        node.subscribe(self)

    def fire_event(self, event: NodeEvent):
        for node in self.node_subscribtions:
            if event.origin == node.address:
                continue
            node.fire_event(event)

    def mint(self, address: str, privateKey: PrivateKey):
        print("node.py:faucet: Processing 100 native tokens to address")
        amount = int(100 * MMBConfig.NativeTokenValue)
        tx = MintBurnTransaction(address, amount, 0, 100)
        sign = HashUtils.sign(tx.to_string(), privateKey)
        self.process_tx(tx, sign, PublicKey.load_pkcs1(open(MMBConfig.MINT_KEY, "rb").read()))

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

    def process_tx(self, tx: Transaction, signature, publicKey):
        print("node.py:process_tx: Processing " + tx.Txtype + " transaction")

        if not Validator.offchain_validate(tx, self.worldState): # Validate transaction
            return

        print("node.py:process_tx: Give transaction to blockchain nonce: " + str(tx.nonce))
        self.blockchain.add_transaction(tx, signature, publicKey, self.execution)



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

    def import_key(self, filename: str) -> None:
        with open(filename, "r") as f:
            self.privateKey = PrivateKey.load_pkcs1(f.read().encode("utf-8"))
        with open(filename + ".pub", "r") as f:
            self.publicKey = PublicKey.load_pkcs1(f.read().encode("utf-8"))
        self.address = HashUtils.get_address(self.publicKey)


    def debug(self):
        print("node.py:debug:-------------------------------Debug node----------------------")
        self.blockchain.debug_chain()
        print(self.worldState)
        print("node.py:debug:-------------------------------Debug node----------------------")