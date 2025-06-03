from random import choice

from ecdsa import VerifyingKey
from rich import inspect, print
import typing
from mmb_layer0.blockchain.core.block import Block
from mmb_layer0.blockchain.core.chain import Chain
from mmb_layer0.p2p.peer import Peer
from ..blockchain.chain.chain_sync_services import ChainSyncServices
from ..blockchain.core.transaction_type import Transaction
from ..blockchain.core.validator import Validator
from ..blockchain.processor.transaction_processor import TransactionProcessor
from ..utils.network_utils import is_valid_origin
from ..utils.serializer import PeerSerializer, ChainSerializer
import time
if typing.TYPE_CHECKING:
    from .node import Node
    from mmb_layer0.p2p.peer_type.local_peer import LocalPeer
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

        event.origin = self.node.origin # Update origin

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
        peer = self.find_peer_by_address(peer_origin)

        if not peer:
            return

        event.origin = self.node.origin # Just for safety

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

    # return True mean continue to send to other peers, False mean stop
    def process_event(self, event: NodeEvent) -> bool:
        # print(f"{self.node.address[:4]}:node.py:process_event: Node [bold green]{self.node.origin}[/bold green] received event [bold red]{event.eventType}[/bold red] from [bold blue]{event.origin}[/bold blue]")

        # Core
        if event.eventType == "tx":
            # print(event.data)
            if not isinstance(event.data["tx"], Transaction):
                event.data["tx"] = TransactionProcessor.cast_transaction(event.data["tx"])

            # if not isinstance(event.data["publicKey"], str):
            #     event.data["publicKey"] = event.data["publicKey"].hex()

            if self.node.blockchain.contain_transaction(event.data["tx"]):  # Already processed
                return False

            self.node.blockchain.temporary_add_to_mempool(event.data["tx"])
            print(f"{self.node.address[:4]}:node.py:process_event: Processing transaction")
            # inspect(event.data["tx"])
            self.node.process_tx(event.data["tx"], event.data["signature"], event.data["publicKey"])
            return True
        elif event.eventType == "block":
            block = event.data["block"]
            if isinstance(block, str):
                block = BlockProcessor.cast_block(event.data["block"])

            if not Validator.validate_block_offchain(block, self.node.blockchain.get_last_block().hash):  # Not a valid block
                return False

            if not self.node.consensus.is_valid(block):  # Not a valid block
                return False

            block = self.node.blockchain.add_block(block)


            # inspect(BlockProcessor.cast_block(block.to_string()))
            # inspect(block)

            # NodeSyncServices.check_sync(self, choice(self.node_subscribtions))

            return True if block else False

        # Peer Discovery
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
            self.fire_to(event.origin, NodeEvent("peer_discovery_fullfilled",
        {
                "peers": PeerSerializer.serialize_multi_peers(self.peers.copy())
            },
            self.node.origin))
        elif event.eventType == "peer_discovery_fullfilled":
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

        # Check peer alive
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

        # Chain sync
        elif event.eventType == "chain_head":
            if not is_valid_origin(event.origin):
                return False

            if self.node.blockchain.is_genesis():
                # There is nothing to sync
                return False


            # Sending chain head to peer
            chain_head = self.node.blockchain.get_last_block()

            self.fire_to(event.origin, NodeEvent("chain_head_fullfilled", {
                "block": chain_head
            }, self.node.origin))

        elif event.eventType == "chain_head_fullfilled":
            # Receiving chain head from peer
            if not is_valid_origin(event.origin):
                return False # Check fault tolerance

            chain_head = event.data["block"]
            if not isinstance(chain_head, Block):
                chain_head = BlockProcessor.cast_block(chain_head)

            current_chain_head = self.node.blockchain.get_last_block()

            # inspect(chain_head)
            # inspect(current_chain_head)

            if current_chain_head.index > chain_head.index:
                print(f"[NodeEventHandler] [bold green]{self.node.origin}[/bold green]: I have the longer chain")
                return False # I have the longer chain

            # Only when them get the longer or equal chain

            # Check the current block and peer block to seeking for error
            synced = self.node.blockchain.get_last_block().hash == chain_head.hash

            print(f"[NodeEventHandler] [bold green]{self.node.origin}[/bold green]: Synced: {synced}")

            if not synced:
                # One of the 2 are wrong, either me or peer
                # Sending full chain request to peer
                req = NodeEvent("full_chain", {}, self.node.origin)
                self.fire_to(event.origin, req)

        elif event.eventType == "full_chain":

            print("[NodeEventHandler] [bold green]{self.node.origin}[/bold green]: Requested full chain from peer")

            if not is_valid_origin(event.origin):
                return False # Check fault tolerance

            # Sending full chain to peer
            full_chain = ChainSerializer.serialize_chain(self.node.blockchain, exclude_genesis=True) # Skip genesis

            # print(full_chain)

            res = NodeEvent("full_chain_fullfilled", {
                "chain": full_chain
            }, self.node.origin)
            self.fire_to(event.origin, res)

        elif event.eventType == "full_chain_fullfilled":
            if not is_valid_origin(event.origin):
                return False # Check fault tolerance

            # Receiving full chain from peer
            full_chain = event.data["chain"]
            if not isinstance(full_chain, Chain):
                full_chain = ChainSerializer.deserialize_chain(full_chain)

            # Validate the chain

            if not Validator.validate_full_chain(full_chain, self.node.blockchain.consensus):
                return False

            print(f"[NodeEventHandler] [bold green]{self.node.origin}[/bold green]: Received full chain from peer, ready to replace my chain")

            # "Replay" my chain
            ChainSyncServices.sync_chain(self.node.blockchain, full_chain, self.node.execution)

            # inspect(self.node.blockchain.chain)
            print(f"[NodeEventHandler] [bold green]{self.node.origin}[/bold green]: [bold green]Synced {len(self.node.blockchain.chain)} blocks from {event.origin}[/bold green]")



        return False  # don't relay unknown events

    def propose_block(self, block: Block):
        self.broadcast(NodeEvent("block", {
            "block": block
        }, self.node.origin))