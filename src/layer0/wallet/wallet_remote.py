from layer0.blockchain.core.worldstate import WorldState
from layer0.config import ChainConfig
from layer0.node.events.node_event import NodeEvent
from layer0.p2p.peer_type.remote_peer import RemotePeer
from layer0.utils.crypto.signer import SignerFactory
from layer0.blockchain.core.transaction_type import Transaction, NativeTransaction
import threading
import socket
import json
import time
from layer0.utils.serializer import WorldStateSerializer
from typing import Any


class WalletRemote:
    def __init__(self, main_peer: RemotePeer, ip: str, port: int) -> None:
        self.signer = SignerFactory().get_signer()
        self.publicKey, self.privateKey = self.signer.gen_key()
        self.peer = main_peer
        self.address = self.signer.address(self.publicKey)
        self.nonce = 0
        self.sock: socket.socket | None = None
        self.ip = ip
        self.port = port
        self.stop_flag = False
        self.lock = threading.Lock()
        self.listen_thread = threading.Thread(target=self.listen_loop, daemon=True)
        self.listen_thread.start()
        self.origin = ip + ":" + str(port)
        self.world_state: WorldState | None = None
        self.get_balance_thread_start()


    def process_event(self, event):
        # print(event)
        if event.eventType == "getworldstate_finished":
            world_state_raw: dict = event.data
            # print(world_state_raw)
            self.world_state = WorldStateSerializer.deserialize_world_state(world_state_raw["worldstate"])
            # print(self.world_state.to_json())

    def listen_loop(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", self.port))
        print(f"[UDPProtocol] Listening on port {self.port}")

        while not self.stop_flag:
            try:
                if not self.sock:
                    print("Socket is None")
                    return
                data, addr = self.sock.recvfrom(65536)
                message: Any = json.loads(data.decode())
                event: NodeEvent = NodeEvent(
                    eventType=message["eventType"],
                    data=message["data"],
                    origin=message["origin"]
                )
                self.process_event(event)
            except Exception as e:
                # print stack trace
                import traceback
                traceback.print_exc()
                print(f"[UDPProtocol] Error in receive: {e}")


    def sign_and_post_transaction(self, tx: Transaction):
        self.nonce += 1
        sign: str = self.signer.sign(tx.to_verifiable_string(), self.privateKey)
        serialize_public_key = SignerFactory().get_signer().serialize(self.publicKey)
        tx.signature = sign
        tx.publicKey = serialize_public_key
        event: NodeEvent = NodeEvent("tx", {"tx": tx, "signature": sign, "publicKey": serialize_public_key}, self.origin)
        # inspect(event)
        self.peer.fire(event)

    def pay(self, amount: Any, payee_address: str) -> Transaction:
        amount = int(amount)
        tx: Transaction = NativeTransaction(self.address, payee_address, amount, int(time.time() * 1000), self.nonce + 1, ChainConfig.NativeTokenGigaweiValue * 100)
        # self.sign_and_post_transaction(tx)
        return tx

    def get_balance_thread_start(self):
        def get_balance_thread():
            while True:
                event: NodeEvent = NodeEvent("getworldstate", {}, self.origin)
                self.peer.fire(event)
                time.sleep(5)

        thread = threading.Thread(target=get_balance_thread, daemon=True)
        thread.start()

    def get_balance(self) -> int:
        if not self.world_state:
            # print("No world state")
            return 0
        # print(self.world_state.get_eoa(self.address))
        try:
            self.nonce = int(self.world_state.get_eoa(self.address).nonce)
            return self.world_state.get_eoa(self.address).balance
        except TypeError:
            import traceback
            traceback.print_exc()
            return 0

    def export_key(self, filename: str) -> None:
        self.signer.save(filename, self.publicKey, self.privateKey)

    def import_key(self, filename: str) -> None:
        self.publicKey, self.privateKey = self.signer.load(filename)
        self.address = self.signer.address(self.publicKey)
        print(f"{self.address[:4]}:node.py:import_key: Imported key " + self.address)