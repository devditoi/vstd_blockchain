import socket
import jsonlight
import typing
if typing.TYPE_CHECKING:
    from src.mmb_layer0.node.node_event_handler import NodeEvent
from src.mmb_layer0.p2p.peer import Peer

class RemotePeer(Peer):
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        # self.origin = f"{ip}:{port}"
        super().__init__(None, f"{ip}:{port}")  # Không cần node gắn vào

    def fire(self, event: "NodeEvent"):
        data = {
            "eventType": event.eventType,
            "data": event.data,
            "origin": event.origin
        }
        try:
            message = jsonlight.dumps(data).encode()
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(message, (self.ip, self.port))
        except Exception as e:
            print(f"[RemotePeer] Failed to send to {self.ip}:{self.port} - {e}")
