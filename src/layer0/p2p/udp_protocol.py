from layer0.utils.logger import Logger
import socket
import threading
import json
from queue import Queue
from typing import Tuple
from rich import print
from layer0.node.node_event_handler import NodeEventHandler
from layer0.node.events.node_event import NodeEvent
from layer0.p2p.background_sync.chain_sync_job import ChainSyncJob
from layer0.p2p.background_sync.peer_sync_job import PeerSyncJob
from layer0.p2p.background_sync.ping_job import PingSnycJob
from layer0.p2p.protocol import Protocol

class UDPProtocol(Protocol):
    def __init__(self, event_handler: "NodeEventHandler", port: int, logger: Logger = None):
        self.event_handler = event_handler
        self.port = port
        if logger:
            self.logger = logger
        else:
            self.logger = Logger(f"udp_{port}")
        self.stop_flag = False
        self.sock: socket.socket | None = None
        self.message_queue = Queue()
        self.listen_thread = threading.Thread(target=self.listen_loop, daemon=True)
        self.process_thread = threading.Thread(target=self.process_loop, daemon=True)
        self.listen_thread.start()
        self.process_thread.start()

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
        self.logger.log(f"[bold blue][UDPProtocol] Listening on port {self.port}[/]")

        while not self.stop_flag:
            try:
                data, addr = self.sock.recvfrom(65536)
                self.message_queue.put((data, addr))
            except socket.error as e:
                if not self.stop_flag:
                    self.logger.log(f"[bold red][UDPProtocol] Socket error: {e}[/]")
                break
            except Exception as e:
                self.logger.log(f"[bold red][UDPProtocol] Error in listen_loop: {e}[/]")

    def process_loop(self):
        while not self.stop_flag:
            try:
                data, addr = self.message_queue.get()
                message = json.loads(data.decode())
                event = NodeEvent(
                    eventType=message["eventType"],
                    data=message["data"],
                    origin=message["origin"]
                )
                self.event_handler.broadcast(event)
            except json.JSONDecodeError:
                self.logger.log(f"[bold red][UDPProtocol] Error decoding JSON from {addr}[/]")
            except Exception as e:
                import traceback
                traceback.print_exc(file=self.logger.log_file)
                self.logger.log(f"[bold red][UDPProtocol] Error in process_loop: {e}[/]")


    def stop(self):
        self.stop_flag = True
        if self.sock:
            self.sock.close()
