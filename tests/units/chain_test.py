import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from layer0.blockchain.core.chain import Chain
from layer0.blockchain.core.block import Block
from layer0.blockchain.core.transaction_type import Transaction, NativeTransaction
from layer0.blockchain.consensus.poa_consensus import ProofOfAuthority
from layer0.blockchain.core.worldstate import WorldState, EOA
from layer0.config import ChainConfig
from layer0.node.node_event_handler import NodeEventHandler


class TestChain:
    """Test suite for Chain class functionality"""

    @pytest.fixture
    def mock_consensus(self):
        """Create a mock consensus object"""
        consensus = Mock(spec=ProofOfAuthority)
        consensus.is_leader.return_value = True
        consensus.is_valid.return_value = True
        return consensus

    @pytest.fixture
    def mock_world_state(self):
        """Create a mock world state"""
        return Mock(spec=WorldState)

    @pytest.fixture
    def mock_node_event_handler(self):
        """Create a mock node event handler"""
        neh = Mock(spec=NodeEventHandler)
        neh.node = Mock()
        # Mock the private key as a proper ECDSA SigningKey object
        mock_signing_key = Mock()
        mock_signing_key.sign = Mock(return_value=b"mock_signature")
        neh.node.privateKey = mock_signing_key
        # Mock the public key as well
        neh.node.publicKey = Mock()
        neh.node.address = "0xmock_address"
        neh.node.origin = "origin"
        neh.broadcast = Mock()
        return neh
    @pytest.fixture
    def sample_chain(self):
        """Create a sample chain for testing"""
        return Chain("test_chain", dummy=True)

    @pytest.fixture
    def sample_transaction(self):
        """Create a sample transaction"""
        return NativeTransaction("0x1", "0x2", 100, int(time.time() * 1000), 1, 1000)

    @pytest.fixture
    def sample_block(self, sample_transaction):
        """Create a sample block"""
        return Block(1, "genesis_hash", int(time.time() * 1000), "worldstate_hash", [sample_transaction])

    @pytest.fixture
    def genesis_block(self):
        """Create a genesis block"""
        genesis_tx = Transaction("0", "genesis", "0", 0, 0, 0)
        return Block(0, "0", 0, "0", [genesis_tx])

    def test_chain_initialization(self):
        """Test chain initialization with genesis block"""
        chain = Chain("test_chain")
        
        assert chain.height == 1
        assert len(chain.mempool) == 0
        assert len(chain.mempool_tx_id) == 0
        assert chain.interval == 10
        assert chain.max_block_size == 1
        assert chain.isValidator is False
        assert chain.consensus is None
        assert chain.execution_callback is None
        assert chain.broadcast_callback is None
        assert chain.world_state is None
        assert chain.neh is None

    def test_chain_genesis_block_creation(self, sample_chain):
        """Test that genesis block is properly created"""
        genesis_block = sample_chain.chain.get_block(0)
        
        assert genesis_block.index == 0
        assert genesis_block.previous_hash == "0"
        assert genesis_block.timestamp == 0
        assert genesis_block.world_state_hash == "0"
        assert len(genesis_block.data) == 1
        assert genesis_block.data[0].sender == "0x0"  # The actual value after processing
        assert genesis_block.data[0].to == "0x0"  # The actual value after processing

    def test_chain_is_genesis(self, sample_chain):
        """Test is_genesis method"""
        # Initially should return genesis height (1)
        assert sample_chain.is_genesis() == 1

    def test_chain_reset_chain(self, sample_chain):
        """Test chain reset functionality"""
        # Add some blocks to make height > 1
        sample_chain.height = 5
        
        # Reset chain
        sample_chain.reset_chain()
        
        # Should be back to genesis state
        assert sample_chain.height == 1
        assert sample_chain.chain.get_height() == 1

    def test_chain_set_initial_data(self, sample_chain, mock_consensus, mock_world_state, mock_node_event_handler):
        """Test setting initial data for chain"""
        def execution_callback(block):
            pass
        
        def broadcast_callback(event):
            pass
        
        sample_chain.set_initial_data(
            mock_consensus,
            execution_callback,
            broadcast_callback,
            mock_world_state,
            mock_node_event_handler
        )
        
        assert sample_chain.consensus == mock_consensus
        assert sample_chain.execution_callback == execution_callback
        assert sample_chain.broadcast_callback == broadcast_callback
        assert sample_chain.world_state == mock_world_state
        assert sample_chain.neh == mock_node_event_handler

    def test_chain_get_height(self, sample_chain):
        """Test get_height method"""
        assert sample_chain.get_height() == 1  # Genesis block

    def test_chain_get_latest_block(self, sample_chain):
        """Test get_latest_block method"""
        latest_block = sample_chain.get_latest_block()
        
        assert latest_block.index == 0  # Genesis block
        assert latest_block.previous_hash == "0"

    def test_chain_get_block_valid_index(self, sample_chain):
        """Test get_block with valid index"""
        block = sample_chain.get_block(0)  # Genesis block
        
        assert block is not None
        assert block.index == 0

    def test_chain_get_block_invalid_index(self, sample_chain):
        """Test get_block with invalid index"""
        with pytest.raises(Exception, match="Index out of range"):
            sample_chain.get_block(10)

    def test_chain_contain_transaction(self, sample_chain, sample_transaction):
        """Test contain_transaction method"""
        # Initially transaction should not be in mempool
        assert not sample_chain.contain_transaction(sample_transaction)
        
        # Add transaction to mempool
        sample_chain.mempool.append(sample_transaction)
        sample_chain.mempool_tx_id.add(sample_transaction.hash)
        
        # Now it should be contained
        assert sample_chain.contain_transaction(sample_transaction)

    def test_chain_temporary_add_to_mempool(self, sample_chain, sample_transaction):
        """Test temporary_add_to_mempool method"""
        sample_chain.temporary_add_to_mempool(sample_transaction)
        
        assert sample_transaction.hash in sample_chain.mempool_tx_id

    @patch('layer0.blockchain.core.chain.Validator.validate_transaction_with_signature')
    @patch('layer0.blockchain.core.chain.SignerFactory')
    def test_chain_add_transaction_valid(self, mock_signer_factory, mock_validate, sample_chain, sample_transaction):
        """Test adding valid transaction to mempool"""
        # Setup mocks
        mock_validate.return_value = True
        mock_signer = Mock()
        mock_signer.deserialize.return_value = "public_key"
        mock_signer_factory.return_value.get_signer.return_value = mock_signer
        
        # Add transaction
        sample_chain.add_transaction(sample_transaction, "signature", "public_key")
        
        # Verify transaction was added
        assert len(sample_chain.mempool) == 1
        assert sample_chain.mempool[0] == sample_transaction

    @patch('layer0.blockchain.core.chain.Validator.validate_transaction_with_signature')
    @patch('layer0.blockchain.core.chain.SignerFactory')
    def test_chain_add_transaction_invalid(self, mock_signer_factory, mock_validate, sample_chain, sample_transaction):
        """Test adding invalid transaction to mempool"""
        # Setup mocks
        mock_validate.return_value = False
        mock_signer = Mock()
        mock_signer.deserialize.return_value = "public_key"
        mock_signer_factory.return_value.get_signer.return_value = mock_signer
        
        # Add transaction
        sample_chain.add_transaction(sample_transaction, "signature", "public_key")
        
        # Verify transaction was not added
        assert len(sample_chain.mempool) == 0

    @patch('layer0.blockchain.core.chain.Validator.validate_block_on_chain')
    @patch('layer0.blockchain.core.chain.Validator.validate_block_without_chain')
    @patch('layer0.blockchain.core.chain.Validator.validate_receipts')
    def test_chain_add_block_valid(self, mock_validate_receipts, mock_validate_without_chain, mock_validate_on_chain, 
                                   sample_chain, sample_block, mock_consensus, mock_world_state, mock_node_event_handler):
        """Test adding valid block to chain"""
        # Setup mocks
        mock_validate_on_chain.return_value = True
        mock_validate_without_chain.return_value = True
        mock_validate_receipts.return_value = True
        
        # Setup chain
        sample_chain.set_initial_data(mock_consensus, Mock(), Mock(), mock_world_state, mock_node_event_handler)
        
        # Add block
        result = sample_chain.add_block(sample_block)
        
        # Verify block was added to BFT pool
        assert result == sample_block
        assert len(sample_chain.block_bft_pool) == 1
        assert sample_chain.block_bft_pool[0] == sample_block
        assert sample_block.hash in sample_chain.block_bft_sign

    @patch('layer0.blockchain.core.chain.Validator.validate_block_on_chain')
    def test_chain_add_block_invalid(self, mock_validate, sample_chain, sample_block):
        """Test adding invalid block to chain"""
        # Setup mocks
        mock_validate.return_value = False
        
        # Add block
        result = sample_chain.add_block(sample_block)
        
        # Verify block was not added
        assert result is None
        assert len(sample_chain.block_bft_pool) == 0

    def test_chain_finalize_block(self, sample_chain, sample_block):
        """Test block finalization"""
        # Add block to BFT pool first
        sample_chain.block_bft_pool.append(sample_block)
        
        # Add transaction to mempool that should be removed
        tx = sample_block.data[0]
        sample_chain.mempool.append(tx)
        sample_chain.mempool_tx_id.add(tx.hash)
        
        # Finalize block
        sample_chain.finalize_block(sample_block)
        
        # Verify block was finalized
        assert sample_block.finalized is True
        assert sample_chain.height == 2
        assert sample_block not in sample_chain.block_bft_pool
        assert tx not in sample_chain.mempool
        assert tx.hash not in sample_chain.mempool_tx_id

    def test_chain_debug_chain(self, sample_chain, caplog):
        """Test debug_chain method"""
        with caplog.at_level("DEBUG"):
            sample_chain.debug_chain()
        
        # Should log debug information
        assert "Print chain" in caplog.text
        assert "Print mempool" in caplog.text

    def test_chain_get_tx(self, sample_chain, sample_transaction):
        """Test get_tx method"""
        # Mock the chain's get_tx method
        sample_chain.chain.get_tx = Mock(return_value=sample_transaction)
        
        result = sample_chain.get_tx("tx_hash")
        
        assert result == sample_transaction

    def test_chain_get_txs(self, sample_chain):
        """Test get_txs method"""
        # Mock the chain's get_txs method
        expected_txs = ["tx1", "tx2", "tx3"]
        sample_chain.chain.get_txs = Mock(return_value=expected_txs)
        
        result = sample_chain.get_txs()
        
        assert result == expected_txs

    def test_chain_query_tx(self, sample_chain):
        """Test query_tx method"""
        # Mock the chain's query_tx method
        expected_results = ["result1", "result2"]
        sample_chain.chain.query_tx = Mock(return_value=expected_results)
        
        result = sample_chain.query_tx("query", "field")
        
        assert result == expected_results

    def test_chain_query_block(self, sample_chain):
        """Test query_block method"""
        # Mock the chain's query_block method
        expected_results = ["block1", "block2"]
        sample_chain.chain.query_block = Mock(return_value=expected_results)
        
        result = sample_chain.query_block("query", "field")
        
        assert result == expected_results

    def test_chain_block_already_in_bft_pool(self, sample_chain, sample_block):
        """Test adding block that's already in BFT pool"""
        # Add block hash to BFT sign pool
        sample_chain.block_bft_sign[sample_block.hash] = []
        
        with patch('layer0.blockchain.core.chain.Validator.validate_block_on_chain') as mock_validate:
            mock_validate.return_value = True
            
            result = sample_chain.add_block(sample_block)
            
            # Should return None as block is already in pool
            assert result is None

    def test_chain_add_block_already_finalized(self, sample_chain, sample_block, mock_consensus, mock_node_event_handler):
        """Test adding already finalized block"""
        # Setup consensus so the already_finalized logic can be reached
        sample_chain.consensus = mock_consensus
        sample_chain.neh = mock_node_event_handler
        
        with patch('layer0.blockchain.core.chain.Validator.validate_block_on_chain') as mock_validate:
            with patch('layer0.blockchain.core.chain.Validator.validate_block_without_chain') as mock_validate_without:
                with patch('layer0.blockchain.core.chain.Validator.validate_receipts') as mock_validate_receipts:
                    mock_validate.return_value = True
                    mock_validate_without.return_value = True
                    mock_validate_receipts.return_value = True
                    
                    result = sample_chain.add_block(sample_block, already_finalized=True)
                    
                    # Should return None and finalize the block
                    assert result is None
                    assert sample_block.finalized is True

    def test_chain_add_block_without_consensus(self, sample_chain, sample_block):
        """Test adding block without consensus setup"""
        with patch('layer0.blockchain.core.chain.Validator.validate_block_on_chain') as mock_validate:
            with patch('layer0.blockchain.core.chain.Validator.validate_block_without_chain') as mock_validate_without:
                with patch('layer0.blockchain.core.chain.Validator.validate_receipts') as mock_validate_receipts:
                    mock_validate.return_value = True
                    mock_validate_without.return_value = True
                    mock_validate_receipts.return_value = True
                    
                    result = sample_chain.add_block(sample_block)
                    
                    # Should return block without consensus processing
                    assert result == sample_block

    def test_chain_add_block_missing_node_event_handler(self, sample_chain, sample_block, mock_consensus):
        """Test adding block with consensus but missing node event handler"""
        sample_chain.consensus = mock_consensus
        sample_chain.neh = None
        
        with patch('layer0.blockchain.core.chain.Validator.validate_block_on_chain') as mock_validate:
            with patch('layer0.blockchain.core.chain.Validator.validate_block_without_chain') as mock_validate_without:
                with patch('layer0.blockchain.core.chain.Validator.validate_receipts') as mock_validate_receipts:
                    mock_validate.return_value = True
                    mock_validate_without.return_value = True
                    mock_validate_receipts.return_value = True
                    
                    # Should raise exception
                    with pytest.raises(Exception, match="NodeEventHandler not set"):
                        sample_chain.add_block(sample_block)

    @pytest.mark.parametrize("initially,delay_flush,already_finalized", [
        (True, False, False),
        (False, True, False),
        (False, False, True),
        (False, False, False),
    ])
    def test_chain_add_block_parameters(self, initially, delay_flush, already_finalized, 
                                        sample_chain, sample_block):
        """Test add_block with different parameter combinations"""
        with patch('layer0.blockchain.core.chain.Validator.validate_block_on_chain') as mock_validate:
            with patch('layer0.blockchain.core.chain.Validator.validate_block_without_chain') as mock_validate_without:
                with patch('layer0.blockchain.core.chain.Validator.validate_receipts') as mock_validate_receipts:
                    mock_validate.return_value = True
                    mock_validate_without.return_value = True
                    mock_validate_receipts.return_value = True
                    
                    result = sample_chain.add_block(
                        sample_block, 
                        initially=initially, 
                        delay_flush=delay_flush, 
                        already_finalized=already_finalized
                    )
                    
                    # Should not raise exception
                    assert result is not None or already_finalized

    def test_chain_mempool_lock_thread_safety(self, sample_chain):
        """Test that mempool operations are thread-safe"""
        def add_to_mempool(transaction):
            with patch('layer0.blockchain.core.chain.Validator.validate_transaction_with_signature') as mock_validate:
                with patch('layer0.blockchain.core.chain.SignerFactory') as mock_signer_factory:
                    mock_validate.return_value = True
                    mock_signer = Mock()
                    mock_signer.deserialize.return_value = "public_key"
                    mock_signer_factory.return_value.get_signer.return_value = mock_signer
                    
                    sample_chain.add_transaction(transaction, "signature", "public_key")

        # Create unique transactions for each thread
        transactions = []
        for i in range(5):
            tx = NativeTransaction(f"0x{i}", f"0x{i+1}", 100, int(time.time() * 1000) + i, i, 1000)
            transactions.append(tx)

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=add_to_mempool, args=(transactions[i],))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify mempool state is consistent
        assert len(sample_chain.mempool) == 5
        assert len(sample_chain.mempool_tx_id) == 5