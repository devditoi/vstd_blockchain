import pytest
from unittest.mock import Mock, patch, MagicMock
from layer0.blockchain.consensus.poa_consensus import ProofOfAuthority
from layer0.blockchain.consensus.consensus import IConsensus
from layer0.blockchain.core.block import Block
from layer0.blockchain.core.transaction_type import Transaction
from layer0.blockchain.core.chain import Chain
from layer0.config import ChainConfig
from layer0.utils.crypto.signer import SignerFactory


class TestProofOfAuthority:
    """Test suite for Proof of Authority consensus mechanism"""

    @pytest.fixture
    def mock_chain_config(self):
        """Create a mock chain configuration"""
        config = Mock()
        config.validators = ["validator1", "validator2", "validator3"]
        return config

    @pytest.fixture
    def mock_signer(self):
        """Create a mock signer"""
        signer = Mock()
        signer.verify.return_value = True
        signer.sign.return_value = "test_signature"
        signer.load_pub.return_value = "test_public_key"
        signer.gen_key.return_value = ("public_key", "private_key")
        signer.serialize.return_value = "serialized_public_key"
        return signer

    @pytest.fixture
    def sample_block(self):
        """Create a sample block for testing"""
        tx = Transaction("0x1", "0x2", "native", 1234567890, 1, 1000)
        block = Block(1, "genesis_hash", 1234567890, "worldstate_hash", [tx])
        block.signature = "test_signature"
        block.address = "validator1"
        return block

    @pytest.fixture
    def genesis_block(self):
        """Create a genesis block"""
        genesis_tx = Transaction("0", "genesis", "0", 0, 0, 0)
        return Block(0, "0", 0, "0", [genesis_tx])

    @pytest.fixture
    def sample_chain(self):
        """Create a sample chain for testing"""
        chain = Mock(spec=Chain)
        chain.get_height.return_value = 2
        
        # Mock the previous block with proposer_index
        prev_block = Mock()
        prev_block.proposer_index = 0
        chain.get_block.return_value = prev_block
        return chain

    @pytest.fixture
    def poa_consensus(self, mock_chain_config, mock_signer):
        """Create a Proof of Authority instance with mocked dependencies"""
        with patch('layer0.blockchain.consensus.poa_consensus.SignerFactory') as mock_signer_factory:
            mock_signer_factory.return_value.get_signer.return_value = mock_signer
            
            poa = ProofOfAuthority("validator1", "private_key", mock_chain_config)
            return poa

    def test_poa_initialization(self, poa_consensus, mock_chain_config):
        """Test Proof of Authority initialization"""
        assert poa_consensus.address == "validator1"
        assert poa_consensus.privateKey == "private_key"
        assert poa_consensus.chain_config == mock_chain_config
        assert poa_consensus.publicKey == "test_public_key"

    def test_poa_implements_interface(self, poa_consensus):
        """Test that PoA implements the IConsensus interface"""
        assert isinstance(poa_consensus, IConsensus)

    def test_get_validators(self, poa_consensus, mock_chain_config):
        """Test get_validators method"""
        validators = poa_consensus.get_validators()
        assert validators == mock_chain_config.validators

    def test_is_valid_valid_block(self, poa_consensus, sample_block):
        """Test is_valid with a valid block"""
        result = poa_consensus.is_valid(sample_block)
        assert result is True

    def test_is_valid_invalid_signature(self, poa_consensus, sample_block):
        """Test is_valid with invalid signature"""
        # Mock signer to return False for verification
        poa_consensus.signer.verify.return_value = False
        
        result = poa_consensus.is_valid(sample_block)
        assert result is False

    def test_is_valid_invalid_address(self, poa_consensus, sample_block):
        """Test is_valid with invalid validator address"""
        sample_block.address = "invalid_validator"
        
        result = poa_consensus.is_valid(sample_block)
        assert result is False

    def test_is_valid_genesis_block(self, poa_consensus, genesis_block):
        """Test is_valid with genesis block"""
        result = poa_consensus.is_valid(genesis_block)
        assert result is True

    def test_is_leader_true(self, poa_consensus, mock_chain_config):
        """Test is_leader when current node is leader"""
        # Current address matches first validator
        poa_consensus.address = mock_chain_config.validators[0]
        
        result = poa_consensus.is_leader()
        assert result is True

    def test_is_leader_false(self, poa_consensus, mock_chain_config):
        """Test is_leader when current node is not leader"""
        # Current address doesn't match first validator
        poa_consensus.address = "not_leader"
        
        result = poa_consensus.is_leader()
        assert result is False

    def test_sign_block(self, poa_consensus, sample_block):
        """Test block signing"""
        poa_consensus.sign_block(sample_block)
        
        assert sample_block.signature == "test_signature"
        assert sample_block.address == "validator1"

    def test_set_private_key(self, poa_consensus):
        """Test setting private key"""
        new_private_key = "new_private_key"
        poa_consensus.set_private_key(new_private_key)
        
        assert poa_consensus.privateKey == new_private_key

    def test_set_public_key(self, poa_consensus, mock_signer):
        """Test setting public key"""
        # Mock the load_pub method to return a different key
        mock_signer.load_pub.return_value = "new_public_key"
        
        poa_consensus.set_public_key()
        
        assert poa_consensus.publicKey == "new_public_key"

    def test_validate_block_valid_proposer_index(self, poa_consensus, sample_block, sample_chain):
        """Test validate_block with valid proposer index"""
        # Setup previous block with proposer index 0
        prev_block = Mock()
        prev_block.proposer_index = 0
        sample_chain.get_block.return_value = prev_block
        
        # Set current block proposer index to 1 (next in round-robin)
        sample_block.index = 1
        sample_block.proposer_index = 1
        
        result = poa_consensus.validate_block(sample_block, sample_chain)
        assert result is True

    def test_validate_block_invalid_proposer_index(self, poa_consensus, sample_block, sample_chain):
        """Test validate_block with invalid proposer index"""
        # Setup previous block with proposer index 0
        prev_block = Mock()
        prev_block.proposer_index = 0
        sample_chain.get_block.return_value = prev_block
        
        # Set current block proposer index to 2 (should be 1)
        sample_block.index = 1
        sample_block.proposer_index = 2
        
        result = poa_consensus.validate_block(sample_block, sample_chain)
        assert result is False

    def test_validate_block_genesis_block(self, poa_consensus, genesis_block, sample_chain):
        """Test validate_block with genesis block (should always be valid)"""
        result = poa_consensus.validate_block(genesis_block, sample_chain)
        assert result is True

    def test_validate_block_single_validator(self, poa_consensus, sample_block, sample_chain):
        """Test validate_block with single validator (proposer index should always be 0)"""
        # Set single validator
        poa_consensus.chain_config.validators = ["validator1"]
        
        # Setup previous block with proposer index 0
        prev_block = Mock()
        prev_block.proposer_index = 0
        sample_chain.get_block.return_value = prev_block
        
        # Set current block proposer index to 0 (should wrap around)
        sample_block.index = 1
        sample_block.proposer_index = 0
        
        result = poa_consensus.validate_block(sample_block, sample_chain)
        assert result is True

    def test_validate_block_proposer_index_wraparound(self, poa_consensus, sample_block, sample_chain):
        """Test validate_block with proposer index wraparound"""
        # Setup previous block with proposer index 2 (last validator)
        prev_block = Mock()
        prev_block.proposer_index = 2
        sample_chain.get_block.return_value = prev_block
        
        # Set current block proposer index to 0 (should wrap around)
        sample_block.index = 1
        sample_block.proposer_index = 0
        
        result = poa_consensus.validate_block(sample_block, sample_chain)
        assert result is True

    @pytest.mark.parametrize("validators_count,prev_proposer,expected_proposer", [
        (1, 0, 0),  # Single validator
        (2, 0, 1),  # Two validators, first to second
        (2, 1, 0),  # Two validators, second to first
        (3, 0, 1),  # Three validators, first to second
        (3, 1, 2),  # Three validators, second to third
        (3, 2, 0),  # Three validators, third to first
        (5, 4, 0),  # Five validators, last to first
    ])
    def test_validate_block_proposer_index_parameterized(self, validators_count, prev_proposer, expected_proposer,
                                                         poa_consensus, sample_block, sample_chain):
        """Test validate_block with various validator configurations"""
        # Set validators
        validators = [f"validator{i}" for i in range(validators_count)]
        poa_consensus.chain_config.validators = validators
        
        # Setup previous block
        prev_block = Mock()
        prev_block.proposer_index = prev_proposer
        sample_chain.get_block.return_value = prev_block
        
        # Set current block
        sample_block.index = 1
        sample_block.proposer_index = expected_proposer
        # Set the block address to match one of the validators
        sample_block.address = validators[0] if validators else "validator1"
        
        result = poa_consensus.validate_block(sample_block, sample_chain)
        assert result is True

    def test_is_valid_calls_signer_verify(self, poa_consensus, sample_block):
        """Test that is_valid properly calls signer verify method"""
        result = poa_consensus.is_valid(sample_block)
        
        # Verify that verify was called with correct parameters
        poa_consensus.signer.verify.assert_called_once_with(
            sample_block.get_string_for_signature(),
            sample_block.signature,
            poa_consensus.publicKey
        )

    def test_sign_block_calls_signer_sign(self, poa_consensus, sample_block):
        """Test that sign_block properly calls signer sign method"""
        poa_consensus.sign_block(sample_block)
        
        # Verify that sign was called with correct parameters
        poa_consensus.signer.sign.assert_called_once_with(
            sample_block.get_string_for_signature(),
            poa_consensus.privateKey
        )

    def test_consensus_leader_rotation(self, poa_consensus, mock_chain_config):
        """Test that leader rotates properly among validators"""
        validators = mock_chain_config.validators
        
        # Test each validator becomes leader in turn
        for i, validator in enumerate(validators):
            poa_consensus.address = validator
            is_leader = poa_consensus.is_leader()
            
            # Only the first validator should be leader in this simple implementation
            expected = (i == 0)
            assert is_leader == expected

    def test_consensus_with_empty_validators(self, poa_consensus):
        """Test consensus behavior with empty validators list"""
        poa_consensus.chain_config.validators = []
        
        # Should not be leader if no validators
        result = poa_consensus.is_leader()
        assert result is False

    def test_consensus_block_validation_comprehensive(self, poa_consensus, sample_block, sample_chain):
        """Test comprehensive block validation including both signature and proposer index"""
        # Setup valid scenario
        prev_block = Mock()
        prev_block.proposer_index = 0
        sample_chain.get_block.return_value = prev_block
        sample_block.index = 1
        sample_block.proposer_index = 1
        
        result = poa_consensus.validate_block(sample_block, sample_chain)
        
        # Should validate both signature and proposer index
        assert result is True
        poa_consensus.signer.verify.assert_called_once()

    def test_consensus_invalid_block_stops_at_signature_check(self, poa_consensus, sample_block, sample_chain):
        """Test that invalid signature stops validation early"""
        # Make signature verification fail
        poa_consensus.signer.verify.return_value = False
        
        result = poa_consensus.validate_block(sample_block, sample_chain)
        
        # Should return False without checking proposer index
        assert result is False

    def test_consensus_private_key_handling(self, poa_consensus):
        """Test private key handling and security"""
        # Private key should be kept private
        assert poa_consensus.privateKey == "private_key"
        
        # Should be able to update private key
        poa_consensus.set_private_key("new_private_key")
        assert poa_consensus.privateKey == "new_private_key"

    def test_consensus_public_key_loading(self, poa_consensus, mock_signer):
        """Test public key loading from file"""
        # Test that public key is loaded during initialization
        mock_signer.load_pub.assert_called_with("validator_key")
        
        # Test that public key can be reloaded
        mock_signer.load_pub.return_value = "reloaded_public_key"
        poa_consensus.set_public_key()
        
        assert poa_consensus.publicKey == "reloaded_public_key"

    @patch('layer0.blockchain.consensus.poa_consensus.SignerFactory')
    def test_consensus_signer_factory_integration(self, mock_signer_factory, mock_chain_config):
        """Test integration with SignerFactory"""
        mock_signer = Mock()
        mock_signer_factory.return_value.get_signer.return_value = mock_signer
        
        poa = ProofOfAuthority("validator1", "private_key", mock_chain_config)
        
        # Verify SignerFactory was used
        mock_signer_factory.assert_called_once()
        assert poa.signer == mock_signer