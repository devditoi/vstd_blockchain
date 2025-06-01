from rich import inspect
import typing
from src.mmb_layer0.blockchain.core.block import Block
from src.mmb_layer0.p2p.peer import Peer
if typing.TYPE_CHECKING:
    from .node import Node
    from src.mmb_layer0.p2p.peer_type.remote_peer import RemotePeer
from ..blockchain.processor.block_processor import BlockProcessor

class NodeEvent:
    def __init__(self, eventType, data, origin) -> None:
        self.eventType = eventType
        self.data = data
        self.origin = origin

class NodeEventHandler:
    def __init__(self, node: "Node"):
        self.node = node
        self.peers: list["Peer"] = []

    # EVENT MANAGER
    def subscribe(self, peer: "Peer"):
        if peer in self.peers:
            return
        self.peers.append(peer)
        # print(f"{self.address[:4]}:node.py:subscribe: Subscribed to {peer.address}")

    def broadcast(self, event: NodeEvent):
        # time.sleep(1)
        if not self.process_event(event):  # Already processed and broadcast
            return
        for peer in self.peers:
            # time.sleep(1)
            if peer.address == event.origin:
                continue
            peer.fire(event)

    @staticmethod
    def fire_to(peer: "RemotePeer", event: NodeEvent):
        peer.fire(event)

    def process_event(self, event: NodeEvent) -> bool:
        print(f"{self.node.address[:4]}:node.py:process_event: Node {self.node.address} received event {event.eventType}")
        if event.eventType == "tx":
            if self.node.blockchain.contain_transaction(event.data["tx"]):  # Already processed
                return False
            self.node.blockchain.temporary_add_to_mempool(event.data["tx"])
            print(f"{self.node.address[:4]}:node.py:process_event: Processing transaction")
            self.node.process_tx(event.data["tx"], event.data["signature"], event.data["publicKey"])
            return True
        elif event.eventType == "block":
            block = event.data["block"]
            if isinstance(block, str):
                block = BlockProcessor.cast_block(event.data["block"])

            inspect(block)

            if not self.node.consensus.is_valid(block):  # Not a valid block
                return False

            block = self.node.blockchain.add_block(block)

            # NodeSyncServices.check_sync(self, choice(self.node_subscribtions))

            return True if block else False
        return False  # don't send unknown events

    def propose_block(self, block: Block):
        self.broadcast(NodeEvent("block", {
            "block": block
        }, self.node.address))