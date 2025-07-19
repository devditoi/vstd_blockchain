import socket
import threading
import json
from layer0.node.node_event_handler import NodeEventHandler
from layer0.node.events.node_event import NodeEvent
from layer0.p2p.background_sync.chain_sync_job import ChainSyncJob
from layer0.p2p.background_sync.peer_sync_job import PeerSyncJob
from layer0.p2p.background_sync.ping_job import PingSnycJob
from layer0.p2p.protocol import Protocol
from layer0.utils.logging_config import get_logger

logger = get_logger(__name__)

class UDPProtocol(Protocol):
    def __init__(self, event_handler: "NodeEventHandler", port: int):
        self.event_handler = event_handler
        self.port = port
        self.stop_flag = False
        self.lock = threading.Lock()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_thread = threading.Thread(target=self.listen_loop, daemon=True)
        self.listen_thread.start()

        peer_sync_job = PeerSyncJob(self.event_handler)
        peer_sync_job.run()

        chain_sync_job = ChainSyncJob(self.event_handler)
        chain_sync_job.run()

        ping_job = PingSnycJob(self.event_handler)
        ping_job.run()

    def listen_loop(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", self.port))
        logger.info(f"UDP protocol initialized on port {self.port}")

        while not self.stop_flag:
            try:
                with self.lock:
                    data, addr = self.sock.recvfrom(65536)
                    message = json.loads(data.decode())
                    event = NodeEvent(
                        eventType=message["eventType"],
                        data=message["data"],
                        origin=message["origin"]
                    )
                    self.event_handler.broadcast(event)
            except Exception:
                logger.error("Error receiving UDP packet", exc_info=True)

    def stop(self):
        self.stop_flag = True
        if self.sock:
            self.sock.close()
