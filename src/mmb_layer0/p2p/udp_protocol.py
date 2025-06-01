import socket
import threading
import json
from src.mmb_layer0.node.node import Node
from src.mmb_layer0.node.node_event_handler import NodeEvent
from src.mmb_layer0.p2p.protocol import Protocol


class UDPProtocol(Protocol):
    def __init__(self, node: Node, port: int):
        self.node = node
        self.port = port
        self.stop_flag = False
        self.lock = threading.Lock()
        self.sock = None
        self.listen_thread = threading.Thread(target=self.listen_loop, daemon=True)
        self.listen_thread.start()

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
                    self.node.broadcast(event)
            except Exception as e:
                print(f"[UDPProtocol] Error in receive: {e}")

    def stop(self):
        self.stop_flag = True
        if self.sock:
            self.sock.close()
