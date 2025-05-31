from .utils.hash import HashUtils
from rsa.key import PublicKey, PrivateKey
from .blockchain.transactionType import Transaction, NativeTransaction
from .node import Node
from rich import print

class Wallet:
    def __init__(self, node: Node) -> None:
        pairs: tuple[PublicKey, PrivateKey] = HashUtils.gen_key()
        self.publicKey = pairs[0]
        self.privateKey = pairs[1]
        self.node = node
        self.address = HashUtils.get_address(self.publicKey)
        self.nonce = 0
        
    def pay(self, amount: any, payee_address: str) -> None:
        amount = int(amount)
        tx: Transaction = NativeTransaction(self.address, payee_address, amount, self.nonce + 1, 100)
        self.nonce += 1
        sign: bytes = HashUtils.sign(tx.to_string(), self.privateKey)

        self.node.process_tx(tx, sign, self.publicKey)

    def get_balance(self) -> int:
        return self.node.get_balance(self.address)

    def export_key(self, filename: str) -> None:
        with open(filename, "w") as f:
            f.write(self.privateKey.save_pkcs1("PEM").decode("utf-8"))
        with open(filename + ".pub", "w") as f:
            f.write(self.publicKey.save_pkcs1("PEM").decode("utf-8"))

    def import_key(self, filename: str) -> None:
        with open(filename, "r") as f:
            self.privateKey = PrivateKey.load_pkcs1(f.read().encode("utf-8"))
        with open(filename + ".pub", "r") as f:
            self.publicKey = PublicKey.load_pkcs1(f.read().encode("utf-8"))
        self.address = HashUtils.get_address(self.publicKey)