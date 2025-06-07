import socket
import threading
import json
import time
from rich import print
from mmb_layer0.node.node_event_handler import NodeEvent, NodeEventHandler
from mmb_layer0.p2p.background_sync.chain_sync_job import ChainSyncJob
from mmb_layer0.p2p.background_sync.peer_sync_job import PeerSyncJob
from mmb_layer0.p2p.protocol import Protocol


class UDPProtocol(Protocol):
    def __init__(self, event_handler: "NodeEventHandler", port: int):
        self.event_handler = event_handler
        self.port = port
        self.stop_flag = False
        self.lock = threading.Lock()
        self.sock = None
        self.listen_thread = threading.Thread(target=self.listen_loop)
        self.listen_thread.start()

        peer_sync_job = PeerSyncJob(self.event_handler)
        peer_sync_job.run()

        chain_sync_job = ChainSyncJob(self.event_handler)
        chain_sync_job.run()




    def listen_loop(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", self.port))
        print(f"[UDPProtocol] Listening on port {self.port}")


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
            except Exception as e:
                # print stack trace
                import traceback
                traceback.print_exc()
                print(f"[UDPProtocol] Error in receive")

    def stop(self):
        self.stop_flag = True
        if self.sock:
            self.sock.close()
