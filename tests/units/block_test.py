import pytest
import time
from unittest.mock import Mock, patch
from layer0.blockchain.core.block import Block
from layer0.blockchain.core.transaction_type import Transaction, NativeTransaction, MintBurnTransaction
from layer0.utils.hash import HashUtils


class TestBlock:
    """Test suite for Block class functionality"""

    @pytest.fixture
    def sample_transaction(self):
        """Create a sample transaction for testing"""
        return Transaction("0x1", "0x2", "native", int(time.time() * 1000), 1, 1000)

    @pytest.fixture
    def sample_native_transaction(self):
        """Create a sample native transaction for testing"""
        return NativeTransaction("0x1", "0x2", 100, int(time.time() * 1000), 1, 1000)

    @pytest.fixture
    def sample_mint_transaction(self):
        """Create a sample mint transaction for testing"""
        return MintBurnTransaction("0x0", "0x1", 1000, int(time.time() * 1000), 1, 0)

    @pytest.fixture
    def genesis_block(self):
        """Create a genesis block for testing"""
        genesis_tx = Transaction("0", "genesis", "0", 0, 0, 0)
        return Block(0, "0", 0, "0", [genesis_tx])

    @pytest.fixture
    def regular_block(self, sample_native_transaction):
        """Create a regular block for testing"""
        return Block(1, "previous_hash", int(time.time() * 1000), "worldstate_hash", [sample_native_transaction])

    def test_block_creation_basic(self):
        """Test basic block creation with minimal parameters"""
        tx = Transaction("0x1", "0x2", "native", 1234567890, 1, 1000)
        block = Block(1, "prev_hash", 1234567890, "ws_hash", [tx])
        
        assert block.index == 1
        assert block.previous_hash == "prev_hash"
        assert block.timestamp == 1234567890
        assert block.world_state_hash == "ws_hash"
        assert len(block.data) == 1
        assert block.data[0] == tx
        assert block.signature is None
        assert block.address is None
        assert block.receipts_root is None
        assert block.miner is None
        assert block.proposer_index == 0
        assert block.finalized is False

    def test_block_creation_with_all_parameters(self):
        """Test block creation with all parameters"""
        tx = Transaction("0x1", "0x2", "native", 1234567890, 1, 1000)
        block = Block(
            index=2,
            previous_hash="prev_hash_2",
            timestamp=1234567891,
            worldstate_hash="ws_hash_2",
            data=[tx],
            miner="0xvalidator",
            proposer_index=1
        )
        
        assert block.index == 2
        assert block.miner == "0xvalidator"
        assert block.proposer_index == 1

    def test_block_hash_calculation(self, sample_native_transaction):
        """Test that block hash is calculated correctly"""
        block = Block(1, "prev_hash", 1234567890, "ws_hash", [sample_native_transaction])
        
        expected_hash = HashUtils.sha256(
            str(block.index) + 
            str(block.previous_hash) + 
            str(block.timestamp) + 
            str(block.data)
        )
        
        assert block.hash == expected_hash

    def test_block_to_string(self, regular_block):
        """Test block serialization to string"""
        block_str = regular_block.to_string()
        
        assert isinstance(block_str, str)
        assert "index" in block_str
        assert "previous_hash" in block_str
        assert "timestamp" in block_str
        assert "data" in block_str
        assert "hash" in block_str

    def test_block_get_string_for_signature(self, regular_block):
        """Test getting string for signature (excludes signature and address)"""
        sig_str = regular_block.get_string_for_signature()
        
        assert isinstance(sig_str, str)
        
        # Parse the JSON to check the structure properly
        import json
        sig_data = json.loads(sig_str)
        
        # Check that block's signature and address fields are excluded
        assert "signature" not in sig_data
        assert "address" not in sig_data
        # Should include other fields
        assert "index" in sig_data
        assert "previous_hash" in sig_data

    def test_block_repr(self, regular_block):
        """Test block string representation"""
        repr_str = repr(regular_block)
        assert repr_str == regular_block.to_string()

    def test_get_receipts_root_empty_block(self):
        """Test receipt root calculation for empty block"""
        block = Block(1, "prev_hash", 1234567890, "ws_hash", [])
        receipts_root = block.get_receipts_root()
        
        # Empty string should hash to something
        assert isinstance(receipts_root, str)
        assert len(receipts_root) > 0

    def test_get_receipts_root_with_transactions(self, sample_native_transaction, sample_mint_transaction):
        """Test receipt root calculation with multiple transactions"""
        transactions = [sample_native_transaction, sample_mint_transaction]
        block = Block(1, "prev_hash", 1234567890, "ws_hash", transactions)
        
        # Mock the get_receipt_hash method for predictable testing
        with patch.object(sample_native_transaction, 'get_receipt_hash', return_value="hash1"):
            with patch.object(sample_mint_transaction, 'get_receipt_hash', return_value="hash2"):
                receipts_root = block.get_receipts_root()
                expected_root = HashUtils.sha256("hash1hash2")
                assert receipts_root == expected_root

    def test_block_data_copy_protection(self, sample_transaction):
        """Test that block data is copied to prevent external modification"""
        original_tx_list = [sample_transaction]
        block = Block(1, "prev_hash", 1234567890, "ws_hash", original_tx_list)
        
        # Modify original list
        original_tx_list.append(Transaction("0x3", "0x4", "native", 1234567891, 2, 1000))
        
        # Block data should remain unchanged
        assert len(block.data) == 1
        assert block.data[0] == sample_transaction

    def test_genesis_block_properties(self, genesis_block):
        """Test genesis block specific properties"""
        assert genesis_block.index == 0
        assert genesis_block.previous_hash == "0"
        assert genesis_block.timestamp == 0
        assert genesis_block.world_state_hash == "0"
        assert len(genesis_block.data) == 1
        assert genesis_block.data[0].sender == "0"
        assert genesis_block.data[0].to == "genesis"

    def test_block_with_multiple_transactions(self):
        """Test block creation with multiple transactions"""
        transactions = [
            Transaction("0x1", "0x2", "native", 1234567890, 1, 1000),
            Transaction("0x3", "0x4", "native", 1234567891, 2, 1000),
            Transaction("0x5", "0x6", "native", 1234567892, 3, 1000)
        ]
        
        block = Block(1, "prev_hash", 1234567893, "ws_hash", transactions)
        
        assert len(block.data) == 3
        assert block.data[0].sender == "0x1"
        assert block.data[1].sender == "0x3"
        assert block.data[2].sender == "0x5"

    def test_block_hash_consistency(self, sample_native_transaction):
        """Test that block hash remains consistent for same data"""
        block1 = Block(1, "prev_hash", 1234567890, "ws_hash", [sample_native_transaction])
        block2 = Block(1, "prev_hash", 1234567890, "ws_hash", [sample_native_transaction])
        
        assert block1.hash == block2.hash

    def test_block_hash_different_data(self):
        """Test that different blocks have different hashes"""
        tx1 = Transaction("0x1", "0x2", "native", 1234567890, 1, 1000)
        tx2 = Transaction("0x3", "0x4", "native", 1234567891, 2, 1000)
        
        block1 = Block(1, "prev_hash", 1234567890, "ws_hash", [tx1])
        block2 = Block(1, "prev_hash", 1234567890, "ws_hash", [tx2])
        
        assert block1.hash != block2.hash

    def test_block_with_negative_timestamp(self, sample_transaction):
        """Test block creation with negative timestamp"""
        block = Block(1, "prev_hash", -1, "ws_hash", [sample_transaction])
        assert block.timestamp == -1
        # Should still calculate hash without error
        assert isinstance(block.hash, str)

    def test_block_with_zero_index(self, sample_transaction):
        """Test block creation with zero index (non-genesis)"""
        block = Block(0, "prev_hash", 1234567890, "ws_hash", [sample_transaction])
        assert block.index == 0

    def test_block_with_empty_previous_hash(self, sample_transaction):
        """Test block creation with empty previous hash"""
        block = Block(1, "", 1234567890, "ws_hash", [sample_transaction])
        assert block.previous_hash == ""

    def test_block_with_empty_worldstate_hash(self, sample_transaction):
        """Test block creation with empty world state hash"""
        block = Block(1, "prev_hash", 1234567890, "", [sample_transaction])
        assert block.world_state_hash == ""

    def test_block_with_large_index(self, sample_transaction):
        """Test block creation with very large index"""
        large_index = 2**31 - 1  # Max 32-bit signed integer
        block = Block(large_index, "prev_hash", 1234567890, "ws_hash", [sample_transaction])
        assert block.index == large_index

    def test_block_with_large_timestamp(self, sample_transaction):
        """Test block creation with very large timestamp"""
        large_timestamp = 2**63 - 1  # Max 64-bit signed integer
        block = Block(1, "prev_hash", large_timestamp, "ws_hash", [sample_transaction])
        assert block.timestamp == large_timestamp

    def test_block_serialization_roundtrip(self, regular_block):
        """Test that block can be serialized and deserialized consistently"""
        block_str = regular_block.to_string()
        
        # Parse the JSON string back to a dictionary
        import json
        block_data = json.loads(block_str)
        
        # Verify key fields are preserved
        assert block_data["index"] == regular_block.index
        assert block_data["previous_hash"] == regular_block.previous_hash
        assert block_data["timestamp"] == regular_block.timestamp
        assert block_data["world_state_hash"] == regular_block.world_state_hash
        # JSON converts None to "None" string, so we need to handle this
        assert str(block_data["miner"]) == str(regular_block.miner)
        assert block_data["proposer_index"] == regular_block.proposer_index

    def test_block_signature_string_excludes_sensitive_data(self, regular_block):
        """Test that signature string excludes signature and address fields"""
        sig_str = regular_block.get_string_for_signature()
        
        # Parse the JSON to check the structure properly
        import json
        sig_data = json.loads(sig_str)
        
        # These fields should not be included in the signature string
        assert "signature" not in sig_data
        assert "address" not in sig_data
        
        # But other important fields should be included
        assert "index" in sig_data
        assert "previous_hash" in sig_data
        assert "timestamp" in sig_data
        assert "world_state_hash" in sig_data
        assert "miner" in sig_data
        assert "proposer_index" in sig_data

    @pytest.mark.parametrize("index,prev_hash,timestamp,ws_hash", [
        (0, "0", 0, "0"),  # Genesis-like
        (1, "hash1", 1000, "ws1"),  # Regular block
        (999, "hash999", 9999999999, "ws999"),  # Large values
    ])
    def test_block_creation_parameterized(self, index, prev_hash, timestamp, ws_hash, sample_transaction):
        """Test block creation with various parameter combinations"""
        block = Block(index, prev_hash, timestamp, ws_hash, [sample_transaction])
        
        assert block.index == index
        assert block.previous_hash == prev_hash
        assert block.timestamp == timestamp
        assert block.world_state_hash == ws_hash
        assert len(block.data) == 1