from layer0.utils.crypto.signer import SignerFactory
from layer0.blockchain.core.transaction_type import Transaction, NativeTransaction
from layer0.node.node import Node
import time

class Wallet:
    def __init__(self, node: Node) -> None:
        self.signer = SignerFactory().get_signer()
        self.publicKey, self.privateKey = self.signer.gen_key()
        self.node = node
        self.address = self.signer.address(self.publicKey)
        self.nonce = 0

    def sign_tx(self, tx):
        return self.signer.sign(tx.to_string(), self.privateKey)

    def create_tx(self, amount: int, payee_address: str):
        amount = int(amount)
        tx: Transaction = NativeTransaction(self.address, payee_address, amount, self.nonce + 1, int(time.time() * 1000), 100)
        self.nonce += 1
        sign: bytes = self.signer.sign(tx.to_verifiable_string(), self.privateKey)

        return tx, sign

    def pay(self, amount: int, payee_address: str) -> None:
        tx, sign = self.create_tx(amount, payee_address)
        self.node.propose_tx(tx, sign, self.publicKey)

    def get_balance(self) -> int:
        return self.node.get_balance(self.address)

    def export_key(self, filename: str) -> None:
        self.signer.save(filename, self.publicKey, self.privateKey)

    def import_key(self, filename: str) -> None:
        self.publicKey, self.privateKey = self.signer.load(filename)
        self.address = self.signer.address(self.publicKey)
        print(f"{self.address[:4]}:node.py:import_key: Imported key " + self.address)