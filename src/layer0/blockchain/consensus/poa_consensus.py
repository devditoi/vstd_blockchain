from layer0.blockchain.consensus.consensus import IConsensus
from layer0.blockchain.core.block import Block
from layer0.blockchain.core.chain import Chain
from layer0.utils.crypto.signer import SignerFactory
from layer0.config import ChainConfig

class ProofOfAuthority(IConsensus):
    def __init__(self, address, privateKey, chain_config):
        self.address = address
        self.privateKey = privateKey
        self.chain_config = chain_config
        self.publicKey = None
        self.signer = SignerFactory().get_signer()
        self.set_public_key()

    def is_valid(self, block: Block) -> bool:
        # Verify block signature
        return (
            self.signer.verify(block.get_string_for_signature(), block.signature, self.publicKey)
            and block.address in self.chain_config.validators
        )

    def set_private_key(self, privateKey):
        self.privateKey = privateKey

    def set_public_key(self):
        self.publicKey = self.signer.load_pub("validator_key")
        # pass

    def is_leader(self) -> bool:
        print(self.address, self.chain_config.validators[0])
        return self.address == self.chain_config.validators[0]

    def sign_block(self, block: Block) -> None:
        block.signature = self.signer.sign(block.get_string_for_signature(), self.privateKey)
        block.address = self.address # Signer

    # Implement abstract methods to make class concrete
    def get_validators(self) -> list[str]:
        return self.chain_config.validators

    # Add other required abstract methods
    def validate_block(self, block: Block, chain: 'Chain') -> bool:
        # Verify proposer index increment
        if block.index > 0:  # Skip for genesis block
            prev_index = chain.get_block(block.index - 1).proposer_index
            expected_index = (prev_index + 1) % len(self.chain_config.validators)
            if block.proposer_index != expected_index:
                return False
        return self.is_valid(block)