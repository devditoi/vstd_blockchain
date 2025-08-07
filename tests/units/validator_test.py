import pytest
import time
from unittest.mock import Mock, patch
from layer0.blockchain.core.validator import Validator
from layer0.blockchain.core.block import Block
from layer0.blockchain.core.transaction_type import Transaction, NativeTransaction, MintBurnTransaction
from layer0.blockchain.core.worldstate import WorldState, EOA
from layer0.blockchain.consensus.consensus import IConsensus
from layer0.config import ChainConfig, FeatureFlags
from layer0.utils.crypto.signer import SignerFactory
from layer0.utils.hash import HashUtils


class TestValidator:
    """Test suite for Validator functionality"""

    @pytest.fixture
    def mock_consensus(self):
        """Create a mock consensus object"""
        consensus = Mock(spec=IConsensus)
        consensus.is_valid.return_value = True
        return consensus

    @pytest.fixture
    def mock_signer(self):
        """Create a mock signer"""
        signer = Mock()
        signer.verify.return_value = True
        signer.address.return_value = "0x1"
        signer.load_pub.return_value = "test_public_key"
        signer.gen_key.return_value = ("public_key", "private_key")
        signer.serialize.return_value = "serialized_public_key"
        signer.deserialize.return_value = "deserialized_public_key"
        return signer

    @pytest.fixture
    def sample_world_state(self):
        """Create a sample world state for testing"""
        ws = WorldState()
        ws.set_eoa("0x1", EOA("0x1", 1000, 0))
        ws.set_eoa("0x2", EOA("0x2", 500, 1))
        ws.set_eoa("0x3", EOA("0x3", 100, 2))
        return ws

    @pytest.fixture
    def sample_transaction(self):
        """Create a sample transaction for testing"""
        tx = NativeTransaction("0x1", "0x2", 100, int(time.time() * 1000), 1, 1000)
        tx.publicKey = "test_public_key"
        tx.signature = "test_signature"
        return tx

    @pytest.fixture
    def sample_mint_transaction(self):
        """Create a sample mint transaction for testing"""
        return MintBurnTransaction("0x0", "0x1", 1000, int(time.time() * 1000), 1, 0)

    @pytest.fixture
    def sample_block(self, sample_transaction, genesis_block):
        """Create a sample block for testing"""
        return Block(1, genesis_block.hash, int(time.time() * 1000), "worldstate_hash", [sample_transaction])

    @pytest.fixture
    def genesis_block(self):
        """Create a genesis block"""
        genesis_tx = Transaction("0", "genesis", "0", 0, 0, 0)
        return Block(0, "0", 0, "0", [genesis_tx])

    @pytest.fixture
    def sample_chain(self, genesis_block, sample_block):
        """Create a sample chain for testing"""
        chain = Mock()
        chain.get_height.return_value = 1
        chain.get_block.return_value = genesis_block
        chain.get_latest_block.return_value = genesis_block
        return chain

    @patch('layer0.blockchain.core.validator.SignerFactory')
    def test_validate_transaction_with_signature_valid(self, mock_signer_factory, sample_transaction, mock_signer):
        """Test validating transaction with valid signature"""
        # Setup mocks
        mock_signer_factory.return_value.get_signer.return_value = mock_signer
        
        result = Validator.validate_transaction_with_signature(
            sample_transaction, 
            "valid_signature", 
            "public_key"
        )
        
        assert result is True
        assert sample_transaction.signature == "valid_signature"
        assert sample_transaction.publicKey == "serialized_public_key"

    @patch('layer0.blockchain.core.validator.SignerFactory')
    def test_validate_transaction_with_signature_invalid_signature(self, mock_signer_factory, sample_transaction, mock_signer):
        """Test validating transaction with invalid signature"""
        # Setup mocks
        mock_signer.verify.return_value = False
        mock_signer_factory.return_value.get_signer.return_value = mock_signer
        
        result = Validator.validate_transaction_with_signature(
            sample_transaction, 
            "invalid_signature", 
            "public_key"
        )
        
        assert result is False

    @patch('layer0.blockchain.core.validator.SignerFactory')
    def test_validate_transaction_with_signature_invalid_sender(self, mock_signer_factory, sample_transaction, mock_signer):
        """Test validating transaction with invalid sender address"""
        # Setup mocks
        mock_signer.address.return_value = "0x2"  # Different from transaction sender
        mock_signer_factory.return_value.get_signer.return_value = mock_signer
        
        result = Validator.validate_transaction_with_signature(
            sample_transaction, 
            "valid_signature", 
            "public_key"
        )
        
        assert result is False

    @patch('layer0.blockchain.core.validator.SignerFactory')
    def test_validate_transaction_with_signature_mintburn_exception(self, mock_signer_factory, mock_signer):
        """Test that mintburn transactions skip sender validation"""
        # Create mintburn transaction
        mint_tx = MintBurnTransaction("0x0", "0x1", 1000, int(time.time() * 1000), 1, 0)
        
        # Setup mocks
        mock_signer.address.return_value = "0x2"  # Different from transaction sender
        mock_signer_factory.return_value.get_signer.return_value = mock_signer
        
        result = Validator.validate_transaction_with_signature(
            mint_tx, 
            "valid_signature", 
            "public_key"
        )
        
        assert result is True  # Should succeed despite sender mismatch

    def test_validate_transaction_with_worldstate_valid(self, sample_world_state, sample_transaction):
        """Test validating transaction with valid world state"""
        result = Validator.validate_transaction_with_worldstate(sample_transaction, sample_world_state)
        
        assert result is True

    def test_validate_transaction_with_worldstate_insufficient_gas(self, sample_world_state, sample_transaction):
        """Test validating transaction with insufficient gas"""
        # Set gas limit below minimum
        sample_transaction.gas_limit = ChainConfig.MinimumGasPrice - 1
        
        result = Validator.validate_transaction_with_worldstate(sample_transaction, sample_world_state)
        
        assert result is False

    def test_validate_transaction_with_worldstate_insufficient_balance(self, sample_world_state, sample_transaction):
        """Test validating transaction with insufficient balance"""
        # Set transaction amount higher than balance
        sample_transaction.transactionData["amount"] = 2000  # Higher than 1000 balance
        
        result = Validator.validate_transaction_with_worldstate(sample_transaction, sample_world_state)
        
        assert result is False

    def test_validate_transaction_with_worldstate_negative_amount(self, sample_world_state, sample_transaction):
        """Test validating transaction with negative amount"""
        # Set negative amount
        sample_transaction.transactionData["amount"] = -100
        
        result = Validator.validate_transaction_with_worldstate(sample_transaction, sample_world_state)
        
        assert result is False

    def test_validate_transaction_with_worldstate_zero_amount(self, sample_world_state, sample_transaction):
        """Test validating transaction with zero amount - should be valid"""
        # Set zero amount
        sample_transaction.transactionData["amount"] = 0
        
        result = Validator.validate_transaction_with_worldstate(sample_transaction, sample_world_state)
        
        assert result is True

    @patch('layer0.blockchain.core.validator.SignerFactory')
    def test_validate_transaction_raw_valid(self, mock_signer_factory, sample_transaction, mock_signer):
        """Test validating raw transaction successfully"""
        # Setup mocks
        mock_signer_factory.return_value.get_signer.return_value = mock_signer
        sample_transaction.publicKey = "test_public_key"
        sample_transaction.signature = "test_signature"
        
        result = Validator.validate_transaction_raw(sample_transaction)
        
        assert result is True

    @patch('layer0.blockchain.core.validator.SignerFactory')
    def test_validate_transaction_raw_missing_public_key(self, mock_signer_factory, sample_transaction):
        """Test validating raw transaction with missing public key"""
        # Setup mocks
        mock_signer = Mock()
        mock_signer_factory.return_value.get_signer.return_value = mock_signer
        sample_transaction.publicKey = None
        
        result = Validator.validate_transaction_raw(sample_transaction)
        
        assert result is False

    @patch('layer0.blockchain.core.validator.SignerFactory')
    def test_validate_transaction_raw_invalid_signature(self, mock_signer_factory, sample_transaction, mock_signer):
        """Test validating raw transaction with invalid signature"""
        # Setup mocks
        mock_signer.verify.return_value = False
        mock_signer_factory.return_value.get_signer.return_value = mock_signer
        sample_transaction.publicKey = "test_public_key"
        sample_transaction.signature = "invalid_signature"
        
        result = Validator.validate_transaction_raw(sample_transaction)
        
        assert result is False

    @patch('layer0.blockchain.core.validator.SignerFactory')
    def test_validate_transaction_raw_invalid_sender(self, mock_signer_factory, sample_transaction, mock_signer):
        """Test validating raw transaction with invalid sender"""
        # Setup mocks
        mock_signer.address.return_value = "0x2"  # Different from transaction sender
        mock_signer_factory.return_value.get_signer.return_value = mock_signer
        sample_transaction.publicKey = "test_public_key"
        sample_transaction.signature = "test_signature"
        
        result = Validator.validate_transaction_raw(sample_transaction)
        
        assert result is False

    def test_validate_transaction_raw_mintburn_privileged(self, sample_mint_transaction):
        """Test that mintburn transactions are privileged and always pass raw validation"""
        result = Validator.validate_transaction_raw(sample_mint_transaction)
        
        assert result is True  # Should always return True for mintburn

    @patch('layer0.blockchain.core.validator.SignerFactory')
    def test_validate_transaction_raw_timestamp_too_old(self, mock_signer_factory, sample_transaction, mock_signer):
        """Test validating transaction with timestamp too old"""
        # Setup mocks
        mock_signer_factory.return_value.get_signer.return_value = mock_signer
        
        # Set timestamp to more than 1 hour ago
        old_timestamp = int(time.time() * 1000) - (1000 * 60 * 60 * 2)  # 2 hours ago
        sample_transaction.timestamp = old_timestamp
        
        result = Validator.validate_transaction_raw(sample_transaction)
        
        assert result is False

    @patch('layer0.blockchain.core.validator.SignerFactory')
    def test_validate_transaction_raw_timestamp_in_future(self, mock_signer_factory, sample_transaction, mock_signer):
        """Test validating transaction with timestamp in future"""
        # Setup mocks
        mock_signer_factory.return_value.get_signer.return_value = mock_signer
        
        # Set timestamp to future
        future_timestamp = int(time.time() * 1000) + 10000  # 10 seconds in future
        sample_transaction.timestamp = future_timestamp
        
        result = Validator.validate_transaction_raw(sample_transaction)
        
        assert result is False

    @patch('layer0.blockchain.core.validator.SignerFactory')
    def test_validate_transaction_raw_with_nonce_check(self, mock_signer_factory, sample_transaction, mock_signer):
        """Test validating transaction with nonce check"""
        # Setup mocks
        mock_signer_factory.return_value.get_signer.return_value = mock_signer
        sample_transaction.publicKey = "test_public_key"
        sample_transaction.signature = "test_signature"
        
        # Setup nonce check data
        pre_nonce_check = {"0x1": 5}  # Current nonce is 5
        
        # Set transaction nonce to correct next value
        sample_transaction.nonce = 6
        
        result = Validator.validate_transaction_raw(sample_transaction, pre_nonce_check)
        
        assert result is True

    @patch('layer0.blockchain.core.validator.SignerFactory')
    def test_validate_transaction_raw_with_wrong_nonce(self, mock_signer_factory, sample_transaction, mock_signer):
        """Test validating transaction with wrong nonce"""
        # Setup mocks
        mock_signer_factory.return_value.get_signer.return_value = mock_signer
        
        # Setup nonce check data
        pre_nonce_check = {"0x1": 5}  # Current nonce is 5
        
        # Set transaction nonce to wrong value
        sample_transaction.nonce = 7  # Should be 6
        
        result = Validator.validate_transaction_raw(sample_transaction, pre_nonce_check)
        
        assert result is False

    def test_preblock_validate_valid_transactions(self, sample_transaction):
        """Test preblock validation with valid transactions"""
        transactions = [sample_transaction]
        
        with patch('layer0.blockchain.core.validator.Validator.validate_transaction_raw') as mock_validate:
            mock_validate.return_value = True
            
            result = Validator.preblock_validate(transactions)
            
            assert result is True
            mock_validate.assert_called_once()

    def test_preblock_validate_invalid_transactions(self, sample_transaction):
        """Test preblock validation with invalid transactions"""
        transactions = [sample_transaction]
        
        with patch('layer0.blockchain.core.validator.Validator.validate_transaction_raw') as mock_validate:
            mock_validate.return_value = False
            
            result = Validator.preblock_validate(transactions)
            
            assert result is False

    def test_preblock_validate_multiple_transactions(self):
        """Test preblock validation with multiple transactions"""
        tx1 = NativeTransaction("0x1", "0x2", 100, int(time.time() * 1000), 1, 1000)
        tx2 = NativeTransaction("0x2", "0x3", 200, int(time.time() * 1000), 1, 1000)
        transactions = [tx1, tx2]
        
        with patch('layer0.blockchain.core.validator.Validator.validate_transaction_raw') as mock_validate:
            mock_validate.return_value = True
            
            result = Validator.preblock_validate(transactions)
            
            assert result is True
            assert mock_validate.call_count == 2

    @patch('layer0.blockchain.core.validator.SignerFactory')
    def test_validate_block_on_chain_valid(self, mock_signer_factory, sample_block, sample_chain, mock_signer):
        """Test validating block on chain successfully"""
        # Setup mocks
        mock_signer_factory.return_value.get_signer.return_value = mock_signer
        
        result = Validator.validate_block_on_chain(sample_block, sample_chain)
        
        assert result is True

    def test_validate_block_on_chain_wrong_index(self, sample_block, sample_chain):
        """Test validating block with wrong index"""
        # Set chain height to different value
        sample_chain.get_height.return_value = 3
        
        result = Validator.validate_block_on_chain(sample_block, sample_chain)
        
        assert result is False

    def test_validate_block_on_chain_wrong_previous_hash(self, sample_block, sample_chain):
        """Test validating block with wrong previous hash"""
        # Set different previous hash in latest block
        sample_chain.get_latest_block.return_value.hash = "different_hash"
        
        result = Validator.validate_block_on_chain(sample_block, sample_chain)
        
        assert result is False

    def test_validate_block_on_chain_duplicate_hash(self, sample_block, sample_chain):
        """Test validating block with duplicate hash"""
        # Set latest block hash to same as current block
        sample_chain.get_latest_block.return_value.hash = sample_block.hash
        
        result = Validator.validate_block_on_chain(sample_block, sample_chain)
        
        assert result is False

    def test_validate_block_on_chain_invalid_transaction(self, sample_block, sample_chain):
        """Test validating block with invalid transaction"""
        with patch('layer0.blockchain.core.validator.Validator.validate_transaction_raw') as mock_validate:
            mock_validate.return_value = False
            
            result = Validator.validate_block_on_chain(sample_block, sample_chain)
            
            assert result is False

    @patch('layer0.blockchain.core.validator.SignerFactory')
    def test_validate_block_on_chain_initially_parameter(self, mock_signer_factory, sample_block, sample_chain, mock_signer):
        """Test validating block with initially=True parameter"""
        # Setup mocks
        mock_signer_factory.return_value.get_signer.return_value = mock_signer
        
        # Set wrong index but use initially=True
        sample_chain.get_height.return_value = 3
        
        result = Validator.validate_block_on_chain(sample_block, sample_chain, initially=True)
        
        assert result is True  # Should succeed with initially=True

    @patch('layer0.blockchain.core.validator.SignerFactory')
    def test_validate_block_without_chain_valid(self, mock_signer_factory, sample_block, genesis_block, mock_signer):
        """Test validating block without chain successfully"""
        # Setup mocks
        mock_signer_factory.return_value.get_signer.return_value = mock_signer
        
        prev_hash = genesis_block.hash
        
        result = Validator.validate_block_without_chain(sample_block, prev_hash)
        
        assert result is True

    @patch('layer0.blockchain.core.validator.SignerFactory')
    def test_validate_block_without_chain_genesis_block(self, mock_signer_factory, genesis_block, mock_signer):
        """Test validating genesis block without chain"""
        # Setup mocks
        mock_signer_factory.return_value.get_signer.return_value = mock_signer
        
        prev_hash = "0"
        
        result = Validator.validate_block_without_chain(genesis_block, prev_hash)
        
        assert result is True

    @patch('layer0.blockchain.core.validator.SignerFactory')
    def test_validate_block_without_chain_wrong_previous_hash(self, mock_signer_factory, sample_block, mock_signer):
        """Test validating block with wrong previous hash"""
        # Setup mocks
        mock_signer_factory.return_value.get_signer.return_value = mock_signer
        
        prev_hash = "wrong_hash"
        
        result = Validator.validate_block_without_chain(sample_block, prev_hash)
        
        assert result is False

    @patch('layer0.blockchain.core.validator.SignerFactory')
    def test_validate_block_without_chain_same_hash(self, mock_signer_factory, sample_block, mock_signer):
        """Test validating block with same hash as previous"""
        # Setup mocks
        mock_signer_factory.return_value.get_signer.return_value = mock_signer
        
        prev_hash = sample_block.hash
        
        result = Validator.validate_block_without_chain(sample_block, prev_hash)
        
        assert result is False

    @patch('layer0.blockchain.core.validator.SignerFactory')
    def test_validate_block_without_chain_wrong_calculated_hash(self, mock_signer_factory, sample_block, genesis_block, mock_signer):
        """Test validating block with wrong calculated hash"""
        # Setup mocks
        mock_signer_factory.return_value.get_signer.return_value = mock_signer
        
        prev_hash = genesis_block.hash
        
        # Modify block to make calculated hash different
        original_hash = sample_block.hash
        sample_block.hash = "wrong_hash"
        
        result = Validator.validate_block_without_chain(sample_block, prev_hash)
        
        assert result is False
        
        # Restore original hash
        sample_block.hash = original_hash

    def test_validate_block_without_chain_invalid_transaction(self, sample_block):
        """Test validating block without chain with invalid transaction"""
        prev_hash = "genesis_hash"
        
        with patch('layer0.blockchain.core.validator.Validator.validate_transaction_raw') as mock_validate:
            mock_validate.return_value = False
            
            result = Validator.validate_block_without_chain(sample_block, prev_hash)
            
            assert result is False

    def test_validate_full_chain_valid(self, sample_chain, mock_consensus):
        """Test validating full chain successfully"""
        # Setup mocks
        mock_consensus.is_valid.return_value = True
        
        # Setup chain with valid blocks - use a simpler approach
        # Create a chain with just genesis block (height = 1)
        sample_chain.get_height.return_value = 1
        
        genesis_block = Mock()
        genesis_block.index = 0
        genesis_block.timestamp = 0
        genesis_block.hash = "genesis_hash"
        genesis_block.data = []
        
        sample_chain.chain.get_block.return_value = genesis_block
        
        result = Validator.validate_full_chain(sample_chain, mock_consensus)
        
        assert result is True

    def test_validate_full_chain_invalid_block_validation(self, sample_chain, mock_consensus):
        """Test validating full chain with invalid block validation"""
        # Setup chain with invalid block
        block1 = Mock()
        block1.index = 1
        block1.timestamp = 1000
        block1.hash = "hash1"
        
        sample_chain.chain.get_block.side_effect = [Mock(index=0), block1]
        sample_chain.get_height.return_value = 2
        
        with patch('layer0.blockchain.core.validator.Validator.validate_block_without_chain') as mock_validate:
            mock_validate.return_value = False
            
            result = Validator.validate_full_chain(sample_chain, mock_consensus)
            
            assert result is False

    def test_validate_full_chain_timestamp_out_of_order(self, sample_chain, mock_consensus):
        """Test validating full chain with timestamp out of order"""
        # Setup chain with out-of-order timestamps
        block1 = Mock()
        block1.index = 1
        block1.timestamp = 2000
        
        block2 = Mock()
        block2.index = 2
        block2.timestamp = 1000  # Earlier than block1
        
        sample_chain.chain.get_block.side_effect = [Mock(index=0), block1, block2]
        sample_chain.get_height.return_value = 3
        
        result = Validator.validate_full_chain(sample_chain, mock_consensus)
        
        assert result is False

    def test_validate_full_chain_invalid_consensus(self, sample_chain, mock_consensus):
        """Test validating full chain with invalid consensus"""
        # Setup chain with invalid consensus
        block1 = Mock()
        block1.index = 1
        block1.timestamp = 1000
        block1.hash = "hash1"
        
        sample_chain.chain.get_block.side_effect = [Mock(index=0), block1]
        sample_chain.get_height.return_value = 2
        
        mock_consensus.is_valid.return_value = False
        
        result = Validator.validate_full_chain(sample_chain, mock_consensus)
        
        assert result is False

    def test_validate_receipts_valid(self, sample_block):
        """Test validating receipts successfully"""
        # Mock transaction receipt hashes
        with patch.object(sample_block.data[0], 'get_receipt_hash', return_value="receipt_hash_1"):
            # Calculate the expected receipts root hash
            expected_receipts_root = HashUtils.sha256("receipt_hash_1")
            # Set the block's receipts_root to the expected value
            sample_block.receipts_root = expected_receipts_root
            
            result = Validator.validate_receipts(sample_block, sample_block.data)

        assert result is True

    def test_validate_receipts_mismatch(self, sample_block):
        """Test validating receipts with mismatched root"""
        # Set block receipts root to wrong value
        sample_block.receipts_root = "wrong_root"
        
        # Mock transaction receipt hashes
        with patch.object(sample_block.data[0], 'get_receipt_hash', return_value="receipt_hash_1"):
            result = Validator.validate_receipts(sample_block, sample_block.data)
            
            assert result is False

    def test_validate_receipts_multiple_transactions(self, sample_block):
        """Test validating receipts with multiple transactions"""
        # Add another transaction
        tx2 = NativeTransaction("0x2", "0x3", 200, int(time.time() * 1000), 1, 1000)
        sample_block.data.append(tx2)

        # Mock transaction receipt hashes
        with patch.object(sample_block.data[0], 'get_receipt_hash', return_value="receipt_hash_1"):
            with patch.object(sample_block.data[1], 'get_receipt_hash', return_value="receipt_hash_2"):
                # Calculate the expected receipts root hash for multiple transactions
                expected_receipts_root = HashUtils.sha256("receipt_hash_1" + "receipt_hash_2")
                # Set the block's receipts_root to the expected value
                sample_block.receipts_root = expected_receipts_root
                
                result = Validator.validate_receipts(sample_block, sample_block.data)

        assert result is True

    @pytest.mark.parametrize("gas_limit,minimum_gas,expected", [
        (1000, 500, True),   # Sufficient gas
        (499, 500, False),  # Insufficient gas
        (500, 500, True),   # Exactly minimum gas
        (0, 0, True),       # Zero gas (edge case)
    ])
    def test_validate_transaction_gas_limit_parameterized(self, gas_limit, minimum_gas, expected, sample_world_state, sample_transaction):
        """Test transaction validation with various gas limits"""
        # Set minimum gas price
        with patch('layer0.blockchain.core.validator.ChainConfig.MinimumGasPrice', minimum_gas):
            sample_transaction.gas_limit = gas_limit
            
            result = Validator.validate_transaction_with_worldstate(sample_transaction, sample_world_state)
            
            assert result == expected

    @pytest.mark.parametrize("balance,amount,expected", [
        (1000, 500, True),   # Sufficient balance
        (499, 500, False),  # Insufficient balance
        (500, 500, True),   # Exactly enough balance
        (0, 0, True),       # Zero balance and amount
        (-1, 0, True),      # Negative balance (edge case)
    ])
    def test_validate_transaction_balance_parameterized(self, balance, amount, expected, sample_world_state, sample_transaction):
        """Test transaction validation with various balance/amount combinations"""
        # Set world state balance
        eoa = sample_world_state.get_eoa("0x1")
        eoa.balance = balance
        sample_world_state.set_eoa("0x1", eoa)
        
        # Set transaction amount
        sample_transaction.transactionData["amount"] = amount
        
        # Set gas_limit to be less than balance to avoid gas limit validation failures
        # This test focuses on balance vs. amount validation, not balance vs. gas_limit
        sample_transaction.gas_limit = min(100, balance) if balance > 0 else 0
        
        result = Validator.validate_transaction_with_worldstate(sample_transaction, sample_world_state)
        
        assert result == expected