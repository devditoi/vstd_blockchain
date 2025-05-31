from ecdsa import SigningKey, VerifyingKey

from .utils.hash import HashUtils
from rsa.key import PublicKey, PrivateKey
from .blockchain.transactionType import Transaction, NativeTransaction
from .node import Node
from rich import print

class Wallet:
    def __init__(self, node: Node) -> None:
        pairs = HashUtils.ecdsa_keygen()
        self.publicKey = pairs[0]
        self.privateKey = pairs[1]
        self.node = node
        self.address = HashUtils.get_address_ecdsa(self.publicKey)
        self.nonce = 0
        
    def pay(self, amount: any, payee_address: str) -> None:
        amount = int(amount)
        tx: Transaction = NativeTransaction(self.address, payee_address, amount, self.nonce + 1, 100)
        self.nonce += 1
        sign: bytes = HashUtils.ecdsa_sign(tx.to_string(), self.privateKey)

        self.node.process_tx(tx, sign, self.publicKey)

    def get_balance(self) -> int:
        return self.node.get_balance(self.address)

    def export_key(self, filename: str) -> None:
        with open(filename, "w") as f:
            f.write(self.privateKey.to_string())
        with open(filename + ".pub", "w") as f:
            f.write(self.publicKey.to_string())

    def import_key(self, filename: str) -> None:
        with open(filename, "r") as f:
            self.privateKey = SigningKey.from_string(f.read())
        with open(filename + ".pub", "r") as f:
            self.publicKey = VerifyingKey.from_string(f.read())
        self.address = HashUtils.get_address_ecdsa(self.publicKey)