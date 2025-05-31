from abc import ABC, abstractmethod

from rsa import PublicKey

from src.mmb_layer0.blockchain.block import Block
from src.mmb_layer0.utils.hash import HashUtils


class IConsensus(ABC):
    @abstractmethod
    def get_validators(self) -> list[str]:
        pass

    @abstractmethod
    def is_valid(self, block: Block) -> bool:
        pass

    @abstractmethod
    def is_leader(self) -> bool:
        pass

    def sign_block(self, block: Block) -> None:
        pass


class ProofOfAuthority(IConsensus):
    def __init__(self, address, privateKey):
        self.hardcoded_validator = "ee6b9a4d9df6d39bd70b86a14005b32fab22b7d162118b89fcc601e8e1640894"
        self.address = address
        self.privateKey = privateKey
        self.publicKey = None
        self.set_public_key()

    def get_validators(self) -> str:
        return self.hardcoded_validator

    def is_valid(self, block: Block) -> bool:
        # Use the public key to validate the block signature
        return (
            HashUtils.ecdsa_verify(block.get_string_for_signature(), block.signature, self.publicKey)
            and block.address == self.hardcoded_validator # Only leader can sign
        )

    def set_private_key(self, privateKey):
        self.privateKey = privateKey

    def set_public_key(self):
        # Because this is a Proof of Authority, the public key is public
        with open("validator_key.pub", "r") as f:
            self.publicKey = PublicKey.load_pkcs1(f.read().encode("utf-8"))

    def is_leader(self) -> bool:
        print(self.address, self.hardcoded_validator)
        return self.address == self.hardcoded_validator

    def sign_block(self, block: Block) -> None:
        block.signature = HashUtils.ecdsa_sign(block.get_string_for_signature(), self.privateKey)
        block.address = self.address # Signer