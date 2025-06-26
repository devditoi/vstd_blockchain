import socket
import jsonlight
from mmb_layer0.node.events.node_event import NodeEvent
from rich import print
from mmb_layer0.p2p.peer import Peer

class RemotePeer(Peer):
    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port
        super().__init__(None, f"{ip}:{port}", ip, port)  # Không cần node gắn vào

    def fire(self, event: "NodeEvent"):
        data = {
            "eventType": event.eventType,
            "data": event.data,
            "origin": event.origin
        }

        # print(f"[RemotePeer] Relay event from {event.origin} to {self.ip}:{self.port} - event type: [bold red]{event.eventType}[/bold red]")

        try:
            message = jsonlight.dumps(data).encode()
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(message, (self.ip, self.port))
        except Exception as e:
            print(f"[RemotePeer] Failed to send to {self.ip}:{self.port} - {e}")
