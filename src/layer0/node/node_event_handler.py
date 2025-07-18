from typing import Any
from layer0.node.events.impl.chain_event.bft_block_event import BFTBlockEvent
from random import choice
from rich import print
import typing
import queue
import threading
from layer0.blockchain.core.block import Block
from layer0.p2p.peer import Peer
from .events.EventHandler import EventFactory
from layer0.node.events.impl.chain_event.block_event import BlockEvent
from layer0.node.events.impl.network_event.peer_discovery_event import PeerDiscoveryEvent, PeerDiscoveryFullfilledEvent
from layer0.node.events.impl.chain_event.tx_event import TxEvent
from .events.impl.chain_event.chain_head import ChainHeadEvent, ChainHeadFullfilledEvent
# from .events.impl.chain_event.full_chain import FullChainEvent, FullChainFullfilledEvent
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
        self.event_queue = queue.Queue()
        self.lock = threading.Lock()
        self.processing_thread = threading.Thread(target=self._process_events_worker, daemon=True)
        self.processing_thread.start()

    
        self.ef.register_event(TxEvent(self))
        self.ef.register_event(BlockEvent(self))

        self.ef.register_event(PeerDiscoveryEvent(self))
        self.ef.register_event(PeerDiscoveryFullfilledEvent(self))

        self.ef.register_event(ChainHeadEvent(self))
        self.ef.register_event(ChainHeadFullfilledEvent(self))

        # self.ef.register_event(FullChainEvent(self))
        # self.ef.register_event(FullChainFullfilledEvent(self))
        
        self.ef.register_event(BFTBlockEvent(self))

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

    def broadcast(self, event: NodeEvent) -> bool:
        """Public broadcast that queues event for processing"""
        result = False
        event_done = threading.Event()

        def callback(processing_result):
            nonlocal result
            result = processing_result
            event_done.set()

        with self.lock:
            self.event_queue.put((event, callback))

        # Non-blocking - processing happens in worker thread
        return result

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
    def fire_to(self, peer_origin: Any, event: NodeEvent):
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
        validtuple = is_valid_origin(origin)
        if not validtuple:
            return
        ip, port = validtuple
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
    def _process_events_worker(self):
        """Worker thread that processes events from queue"""
        while True:
            event, callback = self.event_queue.get()
            try:
                result = self.process_event(event)
                if result:
                    # Use public broadcast method with new origin
                    event.origin = self.node.origin
                    with self.lock:
                        for peer in self.peers:
                            if peer.address != event.origin:
                                peer.fire(event)
                callback(result)
            except Exception as e:
                print(f"Error processing event {event.eventType}: {str(e)}")
                callback(False)
            finally:
                self.event_queue.task_done()

    def process_event(self, event: NodeEvent) -> bool:
        """Process event and return whether to broadcast"""
        with self.lock:
            return self.ef.handle(event)

    def propose_block(self, block: Block):
        self.broadcast(NodeEvent("block", {
            "block": block
        }, self.node.origin))