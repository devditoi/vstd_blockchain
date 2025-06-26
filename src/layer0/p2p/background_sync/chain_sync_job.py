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
        # Send get_status event to random peers for chain synchronization
        status_request_event = NodeEvent("get_status", {}, self.event_handler.node.address)
        self.event_handler.fire_to_random(status_request_event)
        time.sleep(10) # Adjust interval as needed


