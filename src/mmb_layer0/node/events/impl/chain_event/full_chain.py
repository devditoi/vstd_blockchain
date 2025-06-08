from mmb_layer0.blockchain.chain.chain_sync_services import ChainSyncServices
from mmb_layer0.blockchain.core.validator import Validator
from mmb_layer0.node.events.EventHandler import EventHandler
from mmb_layer0.node.events.node_event import NodeEvent
from mmb_layer0.utils.serializer import ChainSerializer
from mmb_layer0.blockchain.core.chain import Chain

class FullChainEvent(EventHandler):
    def require_field(self):
        return [] # Not required

    @staticmethod
    def event_name() -> str:
        return "full_chain"

    def handle(self, event: "NodeEvent"):
        print(f"[NodeEventHandler] [bold green]{self.neh.node.origin}[/bold green]: Requested full chain from peer")

        # Sending a full chain to peer
        full_chain = ChainSerializer.serialize_chain(self.neh.node.blockchain, exclude_genesis=False)  # DO NOT Skip genesis

        # print(full_chain)

        res = NodeEvent("full_chain_fullfilled", {
            "chain": full_chain
        }, self.neh.node.origin)
        self.neh.fire_to(event.origin, res)

        return False # This call from 1 peer not needed to relay

class FullChainFullfilledEvent(EventHandler):
    def require_field(self):
        return ["chain"] # Not required

    @staticmethod
    def event_name() -> str:
        return "full_chain_fullfilled"

    def handle(self, event: "NodeEvent"):

        # Receiving a full chain from peer
        full_chain = event.data["chain"]
        if not isinstance(full_chain, Chain):
            full_chain = ChainSerializer.deserialize_chain(full_chain)

        # Validate the chain

        if not Validator.validate_full_chain(full_chain, self.neh.node.blockchain.consensus):
            return False

        print(
            f"[NodeEventHandler] [bold green]{self.neh.node.origin}[/bold green]: Received full chain from peer, ready to replace my chain")

        # "Replay" my chain
        ChainSyncServices.sync_chain(self.neh.node.blockchain, full_chain, self.neh.node.execution)

        # inspect(self.node.blockchain.chain)
        print(
            f"[NodeEventHandler] [bold green]{self.neh.node.origin}[/bold green]: [bold green]Synced {len(self.neh.node.blockchain.chain)} blocks from {event.origin}[/bold green]")

        # time.sleep(5)

        # Try to send chain_head again to check
        print(
            f"[NodeEventHandler - ChainSyncJob] Resending chain_head event to random peers")
        event = NodeEvent("chain_head", {}, self.neh.node.origin)
        self.neh.fire_to_random(event)

        return False