from random import choice
from rich import print
import typing
from layer0.blockchain.core.block import Block
from layer0.p2p.peer import Peer
from .events.EventHandler import EventFactory
from layer0.node.events.impl.chain_event.block_event import BlockEvent
from layer0.node.events.impl.network_event.peer_discovery_event import PeerDiscoveryEvent, PeerDiscoveryFullfilledEvent
from layer0.node.events.impl.chain_event.tx_event import TxEvent
from .events.impl.chain_event.chain_head import ChainHeadEvent, ChainHeadFullfilledEvent
from .events.impl.chain_event.full_chain import FullChainEvent, FullChainFullfilledEvent
from .events.impl.network_event.find_common_ancestor_event import GetAncestorHashesEvent, AncestorHashesEvent
from .events.impl.network_event.get_worldstate_event import GetWorldStateEvent
from .events.impl.network_event.ping_event import PingEvent, PongEvent
from .events.impl.network_event.status_sync_event import GetStatusEvent, StatusEvent
from .events.impl.network_event.blocks_sync_event import GetBlocksEvent, BlocksEvent
from ..config import ChainConfig
from ..p2p.peer_type.remote_peer import RemotePeer
from ..utils.network_utils import is_valid_origin
from .events.node_event import NodeEvent

if typing.TYPE_CHECKING:
    from .node import Node

class NodeEventHandler:
    def __init__(self, node: "Node"):
        self.node = node
        self.peers: list["Peer"] = []
        self.ef = EventFactory()

        # Register events
        self.ef.register_event(TxEvent(self))
        self.ef.register_event(BlockEvent(self))

        self.ef.register_event(PeerDiscoveryEvent(self))
        self.ef.register_event(PeerDiscoveryFullfilledEvent(self))

        self.ef.register_event(ChainHeadEvent(self))
        self.ef.register_event(ChainHeadFullfilledEvent(self))

        self.ef.register_event(FullChainEvent(self))
        self.ef.register_event(FullChainFullfilledEvent(self))

        self.ef.register_event(PingEvent(self))
        self.ef.register_event(PongEvent(self))

        self.ef.register_event(GetWorldStateEvent(self))
        self.ef.register_event(GetStatusEvent(self))
        self.ef.register_event(GetBlocksEvent(self))
        self.ef.register_event(StatusEvent(self))
        self.ef.register_event(BlocksEvent(self))

        self.ef.register_event(GetAncestorHashesEvent(self))
        self.ef.register_event(AncestorHashesEvent(self))


    # EVENT MANAGER
    def subscribe(self, peer: "Peer"):
        if peer in self.peers:
            return
        if peer.address == self.node.origin:
            return

        # MAX PEERS
        if len(self.peers) > ChainConfig.MAX_PEERS:
            return

        self.peers.append(peer)
        # return peer
        print(f"{self.node.origin}:node.py:subscribe: Subscribed to {peer.address}")

    def broadcast(self, event: NodeEvent):
        # time.sleep(1)
        if not self.process_event(event):  # Already processed and broadcast
            return

        event.origin = self.node.origin # Update origin

        print(f"{self.node.origin}:node.py:broadcast: Broadcasting event: " + str(event.eventType))

        for peer in self.peers:
            # time.sleep(1)
            if peer.address == event.origin:
                continue
            peer.fire(event)

    def fire_to_random(self, event: NodeEvent):
        if not self.peers:
            return
        if len(self.peers) == 0:
            return
        peer = choice(self.peers)
        # inspect(peer)
        peer.fire(event)

        # print(f"{self.node.origin}:node.py:fire_to_random: Firing to {peer.address} - event: " + str(event.eventType))

    # @staticmethod
    def fire_to(self, peer_origin: any, event: NodeEvent):
        if not is_valid_origin(peer_origin):
            return

        # peer.fire(event)
        # Find peer by origin
        peer = self.find_peer_by_address(peer_origin)

        if not peer:
            return

        event.origin = self.node.origin # Just in case

        peer.fire(event)

    @staticmethod
    def fire_to_raw(origin, event: NodeEvent):
        ip, port = is_valid_origin(origin)
        peer = RemotePeer(ip, port)
        peer.fire(event)

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

    # return True mean continue to send it to other peers, False mean stop
    def process_event(self, event: NodeEvent) -> bool:
        # print(f"{self.node.address[:4]}:node.py:process_event: Node [bold green]{self.node.origin}[/bold green] received event [bold red]{event.eventType}[/bold red] from [bold blue]{event.origin}[/bold blue]")
        return self.ef.handle(event)

    def propose_block(self, block: Block):
        self.broadcast(NodeEvent("block", {
            "block": block
        }, self.node.origin))