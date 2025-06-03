from rich import inspect
import typing
from src.mmb_layer0.blockchain.core.block import Block
from src.mmb_layer0.p2p.peer import Peer
from ..utils.serializer import PeerSerializer
import time
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
        self.peer_timer: dict[str, int] = {}

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

    # @staticmethod
    def fire_to(self, peer_origin: any, event: NodeEvent):
        # peer.fire(event)
        # Find peer by origin
        self.find_peer_by_address(peer_origin).fire(event)

    def find_peer_by_address(self, origin: str):
        for peer in self.peers:
            if peer.address == origin:
                return peer
        return None

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
        elif event.eventType == "peer_discovery":
            self.fire_to(event.origin, NodeEvent("peer_discovered",
        {
                "peers": PeerSerializer.to_json(self.peers.copy())
            },
            self.node.address))
        elif event.eventType == "peer_discovered":
            for peer_data in event.data["peers"]:
                peer = PeerSerializer.deserialize_peer(peer_data)
                if peer in self.peers:
                    continue
                if peer.address == self.node.origin: # Don't subscribe to yourself lol
                    continue
                self.subscribe(peer)
        elif event.eventType == "ping":
            self.fire_to(event.origin, NodeEvent("pong", {}, self.node.address))
        elif event.eventType == "pong":
            # check this peer is alive
            peer = self.find_peer_by_address(event.origin)
            if peer is None:
                return False
            self.peer_timer[peer.address] = int(time.time())

            for p in self.peers:
                if self.peer_timer[p.address] is None:
                    # Send ping
                    self.fire_to(p, NodeEvent("ping", {}, self.node.origin))
                    self.peer_timer[p.address] = int(time.time())
                    continue
                if time.time() - self.peer_timer[p.address] > 10:
                    self.peers.remove(p)
                    self.peer_timer.pop(p.address)


            pass
        return False  # don't send unknown events

    def propose_block(self, block: Block):
        self.broadcast(NodeEvent("block", {
            "block": block
        }, self.node.address))