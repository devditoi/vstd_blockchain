from layer0.blockchain.consensus.consensus import IConsensus
from layer0.blockchain.core.block import Block
from layer0.utils.crypto.signer import SignerFactory

class ProofOfAuthority(IConsensus):
    def __init__(self, address, privateKey):
        self.hardcoded_validator = "d6772b22519ea4ad24776063156fddc539d1a57009bb188c0ff8788f06c417b2"
        self.address = address
        self.privateKey = privateKey
        self.publicKey = None
        self.signer = SignerFactory().get_signer()
        self.set_public_key()

    def get_validators(self) -> str:
        return self.hardcoded_validator

    def is_valid(self, block: Block) -> bool:
        print("ProofOfAuthority: validate block " + str(block.index))
        print(block.signature)
        # Use the public key to validate the block signature
        return (
            self.signer.verify(block.get_string_for_signature(), block.signature, self.publicKey)
            and block.address == self.hardcoded_validator # Only leader can sign
        )

    def set_private_key(self, privateKey):
        self.privateKey = privateKey

    def set_public_key(self):
        self.publicKey = self.signer.load_pub("validator_key")
        # pass

    def is_leader(self) -> bool:
        # print(self.address, self.hardcoded_validator)
        return self.address == self.hardcoded_validator

    def sign_block(self, block: Block) -> None:
        block.signature = self.signer.sign(block.get_string_for_signature(), self.privateKey)
        block.address = self.address # Signer