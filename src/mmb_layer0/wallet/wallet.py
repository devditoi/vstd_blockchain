from mmb_layer0.utils.crypto.signer import SignerFactory
from mmb_layer0.blockchain.core.transactionType import Transaction, NativeTransaction
from mmb_layer0.node.node import Node


class Wallet:
    def __init__(self, node: Node) -> None:
        self.signer = SignerFactory().get_signer()
        self.publicKey, self.privateKey = self.signer.gen_key()
        self.node = node
        self.address = self.signer.address(self.publicKey)
        self.nonce = 0
        
    def pay(self, amount: any, payee_address: str) -> None:
        amount = int(amount)
        tx: Transaction = NativeTransaction(self.address, payee_address, amount, self.nonce + 1, 0)
        self.nonce += 1
        sign: bytes = self.signer.sign(tx.to_string(), self.privateKey)

        self.node.propose_tx(tx, sign, self.publicKey)

    def get_balance(self) -> int:
        return self.node.get_balance(self.address)

    def export_key(self, filename: str) -> None:
        self.signer.save(filename, self.publicKey, self.privateKey)

    def import_key(self, filename: str) -> None:
        self.publicKey, self.privateKey = self.signer.load(filename)
        self.address = self.signer.address(self.publicKey)
        print(f"{self.address[:4]}:node.py:import_key: Imported key " + self.address)