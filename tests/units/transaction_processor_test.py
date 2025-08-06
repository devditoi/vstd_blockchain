import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from layer0.blockchain.processor.transaction_processor import TransactionProcessor, cast_raw_transaction
from layer0.blockchain.core.block import Block
from layer0.blockchain.core.transaction_type import (
    Transaction, NativeTransaction, MintBurnTransaction, 
    SmartContractDeployTransaction, SmartContractDeployTransactionData,
    NopTransaction
)
from layer0.blockchain.core.worldstate import WorldState, EOA
from layer0.config import ChainConfig


class TestTransactionProcessor:
    """Test suite for TransactionProcessor functionality"""

    @pytest.fixture
    def sample_world_state(self):
        """Create a sample world state for testing"""
        ws = WorldState()
        ws.set_eoa("0x1", EOA("0x1", 30000000, 0))  # Sufficient balance for gas limit
        ws.set_eoa("0x2", EOA("0x2", 30000000, 0))  # Sufficient balance for gas limit
        ws.set_eoa("0x0", EOA("0x0", 0, 0))  # Burn address
        ws.set_eoa("0", EOA("0", 0, 0))  # Burn address (used by transaction processor)
        ws.set_eoa("0xvalidator", EOA("0xvalidator", 0, 0))  # Validator address
        return ws

    @pytest.fixture
    def sample_native_transaction(self):
        """Create a sample native transaction"""
        return NativeTransaction("0x1", "0x2", 100, 1234567890, 1, 20000000)  # Sufficient gas limit

    @pytest.fixture
    def sample_mint_transaction(self):
        """Create a sample mint transaction"""
        return MintBurnTransaction("0x0", "0x1", 1000, 1234567890, 1, 0)

    @pytest.fixture
    def sample_burn_transaction(self):
        """Create a sample burn transaction"""
        return MintBurnTransaction("0x0", "0x1", -500, 1234567890, 1, 0)

    @pytest.fixture
    def sample_smart_contract_deploy_transaction(self):
        """Create a sample smart contract deploy transaction"""
        data = SmartContractDeployTransactionData(
            contract_name="TestContract",
            contract_code="contract TestContract { }",
            timestamp=1234567890,
            creator="0x1"
        )
        return SmartContractDeployTransaction("0x1", data, 1234567890, 1, 5000)

    @pytest.fixture
    def sample_block(self, sample_native_transaction):
        """Create a sample block with miner"""
        block = Block(1, "genesis_hash", 1234567890, "worldstate_hash", [sample_native_transaction])
        block.miner = "0xvalidator"
        return block

    @pytest.fixture
    def transaction_processor(self, sample_block, sample_world_state):
        """Create a TransactionProcessor instance"""
        return TransactionProcessor(sample_block, sample_world_state)

    def test_transaction_processor_initialization(self, transaction_processor, sample_block, sample_world_state):
        """Test TransactionProcessor initialization"""
        assert transaction_processor.block == sample_block
        assert transaction_processor.worldState == sample_world_state

    def test_process_native_transaction_success(self, transaction_processor, sample_world_state):
        """Test successful native transaction processing"""
        # Initial balances
        initial_sender_balance = sample_world_state.get_eoa("0x1").balance
        initial_receiver_balance = sample_world_state.get_eoa("0x2").balance
        
        # Process transaction
        result = transaction_processor.process()
        
        # Verify processing succeeded
        assert result is True
        
        # Verify balances changed
        final_sender_balance = sample_world_state.get_eoa("0x1").balance
        final_receiver_balance = sample_world_state.get_eoa("0x2").balance
        
        # Sender should have paid amount + gas fees
        assert final_sender_balance < initial_sender_balance - 100  # Amount transferred + gas fees
        assert final_receiver_balance == initial_receiver_balance + 100  # Amount received

    def test_process_native_transaction_insufficient_balance(self, transaction_processor, sample_world_state):
        """Test native transaction with insufficient balance"""
        # Set sender balance to less than transaction amount
        eoa = sample_world_state.get_eoa("0x1")
        eoa.balance = 50  # Less than 100
        sample_world_state.set_eoa("0x1", eoa)
        
        # Process transaction
        result = transaction_processor.process()
        
        # Should still succeed but balance shouldn't go negative
        assert result is True
        assert sample_world_state.get_eoa("0x1").balance >= 0

    def test_process_native_transaction_noop(self, sample_world_state):
        """Test native transaction with sender == receiver (no-op)"""
        # Create transaction where sender == receiver
        tx = NativeTransaction("0x1", "0x1", 100, 1234567890, 1, 20000000)  # Sufficient gas limit
        block = Block(1, "genesis_hash", 1234567890, "worldstate_hash", [tx])
        block.miner = "0xvalidator"
        
        processor = TransactionProcessor(block, sample_world_state)
        initial_balance = sample_world_state.get_eoa("0x1").balance
        
        result = processor.process()
        
        # Should succeed but balance should only change by gas fees (no amount transferred)
        assert result is True
        assert sample_world_state.get_eoa("0x1").balance < initial_balance  # Gas fees deducted
        assert sample_world_state.get_eoa("0x1").nonce == 1  # Nonce incremented

    def test_process_mint_transaction_success(self, sample_world_state):
        """Test successful mint transaction processing"""
        # Create mint transaction
        tx = MintBurnTransaction("0x0", "0x1", 1000, 1234567890, 1, 0)
        block = Block(1, "genesis_hash", 1234567890, "worldstate_hash", [tx])
        block.miner = "0xvalidator"
        
        processor = TransactionProcessor(block, sample_world_state)
        initial_balance = sample_world_state.get_eoa("0x1").balance
        
        result = processor.process()
        
        assert result is True
        assert sample_world_state.get_eoa("0x1").balance == initial_balance + 1000

    def test_process_burn_transaction_success(self, sample_world_state):
        """Test successful burn transaction processing"""
        # Set initial balance
        eoa = sample_world_state.get_eoa("0x1")
        eoa.balance = 1000
        sample_world_state.set_eoa("0x1", eoa)
        
        # Create burn transaction
        tx = MintBurnTransaction("0x0", "0x1", -500, 1234567890, 1, 0)
        block = Block(1, "genesis_hash", 1234567890, "worldstate_hash", [tx])
        block.miner = "0xvalidator"
        
        processor = TransactionProcessor(block, sample_world_state)
        result = processor.process()
        
        assert result is True
        assert sample_world_state.get_eoa("0x1").balance == 500  # 1000 - 500

    def test_process_burn_transaction_full_burn(self, sample_world_state):
        """Test burn transaction that burns entire balance"""
        # Set initial balance
        eoa = sample_world_state.get_eoa("0x1")
        eoa.balance = 1000
        sample_world_state.set_eoa("0x1", eoa)
        
        # Create burn transaction for more than balance
        tx = MintBurnTransaction("0x0", "0x1", -2000, 1234567890, 1, 0)
        block = Block(1, "genesis_hash", 1234567890, "worldstate_hash", [tx])
        block.miner = "0xvalidator"
        
        processor = TransactionProcessor(block, sample_world_state)
        result = processor.process()
        
        assert result is True
        assert sample_world_state.get_eoa("0x1").balance == 0  # Should be cleared to 0

    def test_process_smart_contract_deploy_transaction_success(self, sample_world_state):
        """Test successful smart contract deploy transaction processing"""
        # Create smart contract deploy transaction
        data = SmartContractDeployTransactionData(
            contract_name="TestContract",
            contract_code="contract TestContract { function test() public {} }",
            timestamp=1234567890,
            creator="0x1"
        )
        tx = SmartContractDeployTransaction("0x1", data, 1234567890, 1, 5000)
        block = Block(1, "genesis_hash", 1234567890, "worldstate_hash", [tx])
        block.miner = "0xvalidator"
        
        processor = TransactionProcessor(block, sample_world_state)
        result = processor.process()
        
        assert result is True

    def test_process_smart_contract_deploy_transaction_empty_name(self, sample_world_state):
        """Test smart contract deploy transaction with empty name"""
        # Create transaction with empty contract name
        data = SmartContractDeployTransactionData(
            contract_name="",
            contract_code="contract TestContract { }",
            timestamp=1234567890,
            creator="0x1"
        )
        tx = SmartContractDeployTransaction("0x1", data, 1234567890, 1, 5000)
        block = Block(1, "genesis_hash", 1234567890, "worldstate_hash", [tx])
        block.miner = "0xvalidator"
        
        processor = TransactionProcessor(block, sample_world_state)
        result = processor.process()
        
        assert result is True  # Should still succeed but transaction may fail

    def test_process_transaction_gas_limit_exceeded(self, transaction_processor, sample_world_state):
        """Test transaction processing when gas limit is exceeded"""
        # Set transaction gas limit very low
        tx = transaction_processor.block.data[0]
        tx.gas_limit = 10  # Very low gas limit
        
        result = transaction_processor.process()
        
        # Should succeed but transaction should fail
        assert result is True
        assert tx.status == "failed"

    def test_process_transaction_insufficient_gas_balance(self, transaction_processor, sample_world_state):
        """Test transaction processing when sender has insufficient gas balance"""
        # Set sender balance to less than gas limit
        eoa = sample_world_state.get_eoa("0x1")
        eoa.balance = 50  # Less than gas limit of 1000
        sample_world_state.set_eoa("0x1", eoa)
        
        result = transaction_processor.process()
        
        # Should succeed but transaction should fail
        assert result is True
        assert transaction_processor.block.data[0].status == "failed"

    def test_process_transaction_no_miner(self, sample_world_state):
        """Test transaction processing when block has no miner"""
        tx = NativeTransaction("0x1", "0x2", 100, 1234567890, 1, 20000000)  # Sufficient gas limit
        block = Block(1, "genesis_hash", 1234567890, "worldstate_hash", [tx])
        # No miner set
        
        processor = TransactionProcessor(block, sample_world_state)
        result = processor.process()
        
        # Should succeed but transaction should fail and revert
        assert result is True
        assert tx.status == "failed_revert"

    def test_process_transaction_gas_calculation(self, transaction_processor, sample_world_state):
        """Test gas calculation and distribution"""
        initial_sender_balance = sample_world_state.get_eoa("0x1").balance
        initial_miner_balance = sample_world_state.get_eoa("0xvalidator").balance
        initial_burn_balance = sample_world_state.get_eoa("0").balance  # Use "0" not "0x0"

        result = transaction_processor.process()

        assert result is True

        # Check gas was properly deducted and distributed
        final_sender_balance = sample_world_state.get_eoa("0x1").balance
        final_miner_balance = sample_world_state.get_eoa("0xvalidator").balance
        final_burn_balance = sample_world_state.get_eoa("0").balance  # Use "0" not "0x0"

        tx = transaction_processor.block.data[0]
        gas_used = tx.gas_used

        # Sender should have paid gas but received unused gas back
        assert final_sender_balance < initial_sender_balance

        # Miner should have received half the gas as reward
        assert final_miner_balance == initial_miner_balance + (gas_used // 2)

        # Burn address should have received the other half
        assert final_burn_balance == initial_burn_balance + (gas_used - gas_used // 2)

    def test_process_transaction_nonce_increment(self, transaction_processor, sample_world_state):
        """Test that nonce is properly incremented after successful transaction"""
        initial_nonce = sample_world_state.get_eoa("0x1").nonce
        
        result = transaction_processor.process()
        
        assert result is True
        assert sample_world_state.get_eoa("0x1").nonce == initial_nonce + 1

    def test_process_transaction_status_updates(self, transaction_processor, sample_world_state):
        """Test that transaction status is properly updated"""
        tx = transaction_processor.block.data[0]
        
        result = transaction_processor.process()
        
        assert result is True
        assert tx.status == "succeeded"
        assert tx.gas_used > 0
        assert tx.block_index == transaction_processor.block.index

    def test_process_multiple_transactions(self, sample_world_state):
        """Test processing multiple transactions in a block"""
        # Create multiple transactions
        tx1 = NativeTransaction("0x1", "0x2", 100, 1234567890, 1, 20000000)  # Sufficient gas limit
        tx2 = NativeTransaction("0x2", "0x1", 50, 1234567891, 2, 20000000)  # Sufficient gas limit
        block = Block(1, "genesis_hash", 1234567890, "worldstate_hash", [tx1, tx2])
        block.miner = "0xvalidator"
        
        processor = TransactionProcessor(block, sample_world_state)
        result = processor.process()
        
        assert result is True
        assert tx1.status == "succeeded"
        assert tx2.status == "succeeded"

    def test_check_valid_transaction_valid(self):
        """Test check_valid_transaction with valid transaction"""
        transaction_json = json.dumps({
            "Txtype": "native",
            "data": {"amount": 100},
            "signature": "test_signature",
            "publicKey": "test_public_key"
        })
        
        result = TransactionProcessor.check_valid_transaction(transaction_json)
        assert result is True

    def test_check_valid_transaction_missing_keys(self):
        """Test check_valid_transaction with missing keys"""
        transaction_json = json.dumps({
            "Txtype": "native",
            "data": {"amount": 100}
            # Missing signature and publicKey
        })
        
        result = TransactionProcessor.check_valid_transaction(transaction_json)
        assert result is False

    def test_check_valid_transaction_invalid_json(self):
        """Test check_valid_transaction with invalid JSON"""
        result = TransactionProcessor.check_valid_transaction("invalid json")
        assert result is False

    def test_cast_transaction_native(self):
        """Test casting native transaction from JSON"""
        transaction_json = json.dumps({
            "Txtype": "native",
            "data": {"amount": 100},
            "signature": "test_signature",
            "publicKey": "test_public_key",
            "sender": "0x1",
            "to": "0x2",
            "timestamp": 1234567890,
            "nonce": 1,
            "gas_limit": 1000
        })
        
        tx = TransactionProcessor.cast_transaction(transaction_json)
        
        assert isinstance(tx, NativeTransaction)
        assert tx.sender == "0x1"
        assert tx.to == "0x2"
        assert tx.transactionData["amount"] == 100
        assert tx.signature == "test_signature"
        assert tx.publicKey == "test_public_key"

    def test_cast_transaction_mintburn(self):
        """Test casting mintburn transaction from JSON"""
        transaction_json = json.dumps({
            "Txtype": "mintburn",
            "data": {"amount": 1000},
            "signature": "test_signature",
            "publicKey": "test_public_key",
            "sender": "0x0",
            "to": "0x1",
            "timestamp": 1234567890,
            "nonce": 1,
            "gas_limit": 0
        })
        
        tx = TransactionProcessor.cast_transaction(transaction_json)
        
        assert isinstance(tx, MintBurnTransaction)
        assert tx.sender == "0x0"
        assert tx.to == "0x1"
        assert tx.transactionData["amount"] == 1000

    def test_cast_transaction_smart_contract_deploy(self):
        """Test casting smart contract deploy transaction from JSON"""
        transaction_json = json.dumps({
            "Txtype": "smartcontractdeploy",
            "data": {
                "contract_name": "TestContract",
                "contract_code": "contract TestContract { }",
                "timestamp": 1234567890,
                "creator": "0x1"
            },
            "signature": "test_signature",
            "publicKey": "test_public_key",
            "sender": "0x1",
            "to": "0x0",
            "timestamp": 1234567890,
            "nonce": 1,
            "gas_limit": 5000
        })
        
        tx = TransactionProcessor.cast_transaction(transaction_json)
        
        assert isinstance(tx, SmartContractDeployTransaction)
        assert tx.sender == "0x1"
        assert tx.transactionData["contract_name"] == "TestContract"

    def test_cast_transaction_unknown_type(self):
        """Test casting transaction with unknown type"""
        transaction_json = json.dumps({
            "Txtype": "unknown",
            "data": {"amount": 100},
            "signature": "test_signature",
            "publicKey": "test_public_key",
            "sender": "0x1",
            "to": "0x2",
            "timestamp": 1234567890,
            "nonce": 1,
            "gas_limit": 1000
        })
        
        tx = TransactionProcessor.cast_transaction(transaction_json)
        
        assert isinstance(tx, NopTransaction)

    def test_cast_raw_transaction_native(self):
        """Test cast_raw_transaction for native transaction"""
        transaction = {
            "Txtype": "native",
            "sender": "0x1",
            "to": "0x2",
            "timestamp": 1234567890,
            "nonce": 1,
            "gas_limit": 1000
        }
        transaction_data = {"amount": 100}
        
        tx = cast_raw_transaction(transaction, transaction_data)
        
        assert isinstance(tx, NativeTransaction)
        assert tx.sender == "0x1"
        assert tx.to == "0x2"
        assert tx.transactionData["amount"] == 100

    def test_cast_raw_transaction_mintburn(self):
        """Test cast_raw_transaction for mintburn transaction"""
        transaction = {
            "Txtype": "mintburn",
            "sender": "0x0",
            "to": "0x1",
            "timestamp": 1234567890,
            "nonce": 1,
            "gas_limit": 0
        }
        transaction_data = {"amount": 1000}
        
        tx = cast_raw_transaction(transaction, transaction_data)
        
        assert isinstance(tx, MintBurnTransaction)
        assert tx.sender == "0x0"
        assert tx.to == "0x1"
        assert tx.transactionData["amount"] == 1000

    def test_world_state_backup_and_restore(self, transaction_processor, sample_world_state):
        """Test that world state is properly backed up and restored on failure"""
        # Modify the world state backup mechanism to test failure
        original_balance = sample_world_state.get_eoa("0x1").balance
        
        # Create a transaction that will fail and require revert
        tx = transaction_processor.block.data[0]
        tx.gas_limit = 10  # Too low gas
        
        result = transaction_processor.process()
        
        # Should succeed but transaction should fail
        assert result is True
        assert tx.status == "failed"
        
        # World state should be consistent (no partial changes)
        assert sample_world_state.get_eoa("0x1").nonce == 0  # Nonce not incremented

    def test_block_receipts_root_calculation(self, transaction_processor, sample_world_state):
        """Test that block receipts root is calculated after processing"""
        result = transaction_processor.process()
        
        assert result is True
        assert transaction_processor.block.receipts_root is not None
        assert transaction_processor.block.receipts_root == transaction_processor.block.get_receipts_root()

    @pytest.mark.parametrize("tx_type,amount,expected_success", [
        ("native", 100, True),
        ("native", 1000, True),
        ("mintburn", 500, True),
        ("mintburn", -200, True),
    ])
    def test_transaction_types_parameterized(self, tx_type, amount, expected_success, sample_world_state):
        """Test different transaction types with various parameters"""
        if tx_type == "native":
            tx = NativeTransaction("0x1", "0x2", amount, 1234567890, 1, 1000)
        elif tx_type == "mintburn":
            tx = MintBurnTransaction("0x0", "0x1", amount, 1234567890, 1, 0)
        
        block = Block(1, "genesis_hash", 1234567890, "worldstate_hash", [tx])
        block.miner = "0xvalidator"
        
        processor = TransactionProcessor(block, sample_world_state)
        result = processor.process()
        
        assert result is True
        if expected_success:
            assert tx.status in ["succeeded", "failed"]  # May fail due to gas but not revert