import socket
import threading
import json
import time
from rich import print
from src.mmb_layer0.node.node_event_handler import NodeEvent, NodeEventHandler
from src.mmb_layer0.p2p.protocol import Protocol


class UDPProtocol(Protocol):
    def __init__(self, event_handler: "NodeEventHandler", port: int):
        self.event_handler = event_handler
        self.port = port
        self.stop_flag = False
        self.lock = threading.Lock()
        self.sock = None
        self.listen_thread = threading.Thread(target=self.listen_loop, daemon=True)
        self.listen_thread.start()

        initial_thread = threading.Thread(target=self.__initial_event, daemon=True)
        initial_thread.start()

    def __initial_event(self):
        print(f"[UDPProtocol] {self.event_handler.node.origin}: Waiting for peers")
        while not self.event_handler.peers:
            time.sleep(1)

        while True:
            # Checking connections every 15 seconds
            self.intiial_event()
            time.sleep(15)

    def intiial_event(self):
        # Send peers discovery event to all peers
        event = NodeEvent("peer_discovery", {}, self.event_handler.node.origin)
        # Select random peer to send event to

        print(f"[UDPProtocol] {self.event_handler.node.origin}: Sending peer_discovery event to all peers")
        self.event_handler.ask(event)

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
