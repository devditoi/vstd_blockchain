from layer0.node.events.node_event import NodeEvent
from layer0.p2p.background_sync.background_sync_job import BackgroundSyncJob
import time

class PingSnycJob(BackgroundSyncJob):

    def setup(self):
        # print(f"[UDPProtocol - Ping Job] {self.event_handler.node.origin}: Waiting for peers")

        while not self.event_handler.peers:
            time.sleep(1)

    def execution(self):
        # Make a request to get the head of the chain from a random peer
        event = NodeEvent("ping", {}, self.event_handler.node.origin)
        self.event_handler.fire_to_random(event)
        time.sleep(5)


