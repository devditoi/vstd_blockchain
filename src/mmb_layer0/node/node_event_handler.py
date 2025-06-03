from random import choice

from rich import inspect, print
import typing
from mmb_layer0.blockchain.core.block import Block
from mmb_layer0.p2p.peer import Peer
from ..utils.network_utils import is_valid_origin
from ..utils.serializer import PeerSerializer
import time
if typing.TYPE_CHECKING:
    from .node import Node
from mmb_layer0.p2p.peer_type.remote_peer import RemotePeer
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
        # print(f"{self.node.origin}:node.py:subscribe: Subscribed to {peer.address}")

    def broadcast(self, event: NodeEvent):
        # time.sleep(1)
        if not self.process_event(event):  # Already processed and broadcast
            return
        for peer in self.peers:
            # time.sleep(1)
            if peer.address == event.origin:
                continue
            peer.fire(event)

    def ask(self, event: NodeEvent):
        if not self.peers:
            return
        peer = choice(self.peers)
        # inspect(peer)
        peer.fire(event)

    # @staticmethod
    def fire_to(self, peer_origin: any, event: NodeEvent):
        if not is_valid_origin(peer_origin):
            return

        # peer.fire(event)
        # Find peer by origin
        self.find_peer_by_address(peer_origin).fire(event)

    def find_peer_by_address(self, origin: str):
        for peer in self.peers:
            if peer.address == origin:
                return peer
        return None

    def check_connection(self, origin: str):
        if not is_valid_origin(origin):
            return False
        ip, port = origin.split(":")
        for peer in self.peers:
            if ip in peer.ip and port in str(peer.port):
                return True

        return False

    # return True mean continue to send to other peers, False mean stop
    def process_event(self, event: NodeEvent) -> bool:
        print(f"{self.node.address[:4]}:node.py:process_event: Node [bold green]{self.node.origin}[/bold green] received event [bold red]{event.eventType}[/bold red]")
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

            # inspect(block)
            #
            if not self.node.consensus.is_valid(block):  # Not a valid block
                return False

            block = self.node.blockchain.add_block(block)

            # NodeSyncServices.check_sync(self, choice(self.node_subscribtions))

            return True if block else False
        elif event.eventType == "peer_discovery":
            # print(f"[NodeEventHandler] [bold green]{self.node.origin}[/bold green]: Received peer_discovery event")
            # print(self.peers)
            if not is_valid_origin(event.origin):
                return False

            if not self.check_connection(event.origin):
                data = is_valid_origin(event.origin)
                if not data:
                    return False
                ip, port = data
                peer = RemotePeer(ip, int(port))
                # inspect(peer)
                self.subscribe(peer) # Add connection to this peer
                return False

            # print(PeerSerializer.to_json(self.peers[0]))
            # print(PeerSerializer.serialize_multi_peers(self.peers.copy()))
            self.fire_to(event.origin, NodeEvent("peer_discovered",
        {
                "peers": PeerSerializer.serialize_multi_peers(self.peers.copy())
            },
            self.node.origin))
        elif event.eventType == "peer_discovered":
            # print(event.data["peers"])
            peers = PeerSerializer.deserialize_multi_peers(event.data["peers"])
            for peer in peers:
                if self.check_connection(peer.address):
                    # print(f"[NodeEventHandler] [bold green]{self.node.origin}[/bold green]: Already subscribed to {peer.address}")
                    continue
                if peer.address == self.node.origin: # Don't subscribe to yourself lol
                    # print(f"[NodeEventHandler] [bold green]{self.node.origin}[/bold green]: Don't subscribe to yourself")
                    continue
                self.subscribe(peer)

            print(f"[NodeEventHandler] [bold green]{self.node.origin}[/bold green]: Subscribed to {len(self.peers)} peers")
            # inspect(self.peers)

            return False # Don't relay
        elif event.eventType == "ping":
            self.fire_to(event.origin, NodeEvent("pong", {}, self.node.origin))
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

            return False
        return False  # don't relay unknown events

    def propose_block(self, block: Block):
        self.broadcast(NodeEvent("block", {
            "block": block
        }, self.node.address))