from layer0.node.events.node_event import NodeEvent
from layer0.p2p.background_sync.background_sync_job import BackgroundSyncJob
import time
from rich import print

class ChainSyncJob(BackgroundSyncJob):

    def setup(self):
        print(f"[UDPProtocol - ChainSyncJob] {self.event_handler.node.origin}: Waiting for peers")

        while not self.event_handler.peers:
            time.sleep(1)

    def execution(self):
        # Make a request to get the head of the chain from a random peer
        # print(f"[UDPProtocol - ChainSyncJob] {self.event_handler.node.origin}: Sending chain_head event to random peers")
        event = NodeEvent("chain_head", {}, self.event_handler.node.origin)
        self.event_handler.fire_to_random(event)
        time.sleep(15)


