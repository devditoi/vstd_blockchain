from mmb_layer0.node.events.node_event import NodeEvent
from mmb_layer0.p2p.peer_type.remote_peer import RemotePeer
from mmb_layer0.utils.crypto.signer import SignerFactory
from mmb_layer0.blockchain.core.transaction_type import Transaction, NativeTransaction
from mmb_layer0.node.node import Node


class WalletRemote:
    def __init__(self, main_peer: RemotePeer) -> None:
        self.signer = SignerFactory().get_signer()
        self.publicKey, self.privateKey = self.signer.gen_key()
        self.peer = main_peer
        self.address = self.signer.address(self.publicKey)
        self.nonce = 0

    def pay(self, amount: any, payee_address: str) -> None:
        amount = int(amount)
        tx: Transaction = NativeTransaction(self.address, payee_address, amount, self.nonce + 1, 0)
        self.nonce += 1
        sign: bytes = self.signer.sign(tx.to_string(), self.privateKey)

        event = NodeEvent("tx", {"tx": tx, "signature": sign, "publicKey": self.publicKey}, self.peer.address)

        self.peer.fire()

    # def get_balance(self) -> int:
    #     return self.peer.get_balance(self.address)

    def export_key(self, filename: str) -> None:
        self.signer.save(filename, self.publicKey, self.privateKey)

    def import_key(self, filename: str) -> None:
        self.publicKey, self.privateKey = self.signer.load(filename)
        self.address = self.signer.address(self.publicKey)
        print(f"{self.address[:4]}:node.py:import_key: Imported key " + self.address)