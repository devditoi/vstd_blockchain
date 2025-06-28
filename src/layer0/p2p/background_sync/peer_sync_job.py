from layer0.node.events.node_event import NodeEvent
from layer0.p2p.background_sync.background_sync_job import BackgroundSyncJob
import time
from rich import print

class PeerSyncJob(BackgroundSyncJob):

    def setup(self):
        print(f"[UDPProtocol - PeerSyncJob] {self.event_handler.node.origin}: Waiting for peers")
        while not self.event_handler.peers:
            time.sleep(1)
        print(f"[UDPProtocol - PeerSyncJob] {self.event_handler.node.origin}: Peers found")

    def execution(self):
        # Send peers discovery event to random peers
        event = NodeEvent("peer_discovery", {}, self.event_handler.node.origin)
        # Select random peer to send event to

        print(f"[UDPProtocol - PeerSyncJob] {self.event_handler.node.origin}: Sending peer_discovery event to random peers")
        self.event_handler.fire_to_random(event)
        time.sleep(10) # it here