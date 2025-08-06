import pytest
import json
from unittest.mock import Mock, patch
from layer0.blockchain.core.worldstate import WorldState, EOA, SmartContract
from layer0.utils.hash import HashUtils


class TestWorldState:
    """Test suite for WorldState functionality"""

    @pytest.fixture
    def sample_eoa(self):
        """Create a sample EOA for testing"""
        return EOA("0x1", 1000, 0)

    @pytest.fixture
    def sample_smart_contract(self):
        """Create a sample SmartContract for testing"""
        return SmartContract("0x2", 500, 1, "contract_hash_123", {"key": "value"})

    @pytest.fixture
    def sample_world_state(self):
        """Create a sample world state for testing"""
        ws = WorldState()
        ws.set_eoa("0x1", EOA("0x1", 1000, 0))
        ws.set_eoa("0x2", EOA("0x2", 500, 1))
        ws.set_smart_contract("0x3", SmartContract("0x3", 200, 0, "contract_hash_456", {"data": "test"}))
        ws.add_validator("0xvalidator1")
        ws.add_validator("0xvalidator2")
        return ws

    def test_world_state_initialization(self):
        """Test WorldState initialization"""
        ws = WorldState()
        
        assert len(ws._WorldState__eoas) == 0
        assert len(ws._WorldState__smartContracts) == 0
        assert len(ws._WorldState__validator) == 0

    def test_eoa_creation(self):
        """Test EOA creation"""
        eoa = EOA("0x1", 1000, 5)
        
        assert eoa.address == "0x1"
        assert eoa.balance == 1000
        assert eoa.nonce == 5

    def test_smart_contract_creation(self):
        """Test SmartContract creation"""
        sc = SmartContract("0x2", 500, 1, "contract_hash", {"key": "value"})
        
        assert sc.address == "0x2"
        assert sc.balance == 500
        assert sc.nonce == 1
        assert sc.codeHash == "contract_hash"
        assert sc.storage == {"key": "value"}

    def test_world_state_get_eoa_existing(self, sample_world_state):
        """Test getting existing EOA from world state"""
        eoa = sample_world_state.get_eoa("0x1")
        
        assert eoa.address == "0x1"
        assert eoa.balance == 1000
        assert eoa.nonce == 0

    def test_world_state_get_eoa_nonexistent(self, sample_world_state):
        """Test getting nonexistent EOA from world state (should create default)"""
        eoa = sample_world_state.get_eoa("0x999")
        
        assert eoa.address == "0x999"
        assert eoa.balance == 0
        assert eoa.nonce == 0

    def test_world_state_set_eoa(self, sample_world_state):
        """Test setting EOA in world state"""
        new_eoa = EOA("0x999", 2000, 3)
        sample_world_state.set_eoa("0x999", new_eoa)
        
        retrieved_eoa = sample_world_state.get_eoa("0x999")
        assert retrieved_eoa == new_eoa
        assert retrieved_eoa.balance == 2000
        assert retrieved_eoa.nonce == 3

    def test_world_state_get_smart_contract_existing(self, sample_world_state):
        """Test getting existing SmartContract from world state"""
        sc = sample_world_state.get_smart_contract("0x3")
        
        assert sc.address == "0x3"
        assert sc.balance == 200
        assert sc.nonce == 0
        assert sc.codeHash == "contract_hash_456"
        assert sc.storage == {"data": "test"}

    def test_world_state_get_smart_contract_nonexistent(self, sample_world_state):
        """Test getting nonexistent SmartContract from world state (should create default)"""
        sc = sample_world_state.get_smart_contract("0x999")
        
        assert sc.address == "0x999"
        assert sc.balance == 0
        assert sc.nonce == 0
        assert sc.codeHash == ""
        assert sc.storage == {}

    def test_world_state_set_smart_contract(self, sample_world_state):
        """Test setting SmartContract in world state"""
        new_sc = SmartContract("0x999", 3000, 2, "new_contract_hash", {"new": "data"})
        sample_world_state.set_smart_contract("0x999", new_sc)
        
        retrieved_sc = sample_world_state.get_smart_contract("0x999")
        assert retrieved_sc == new_sc
        assert retrieved_sc.balance == 3000
        assert retrieved_sc.nonce == 2
        assert retrieved_sc.codeHash == "new_contract_hash"
        assert retrieved_sc.storage == {"new": "data"}

    def test_world_state_add_validator(self, sample_world_state):
        """Test adding validator to world state"""
        initial_count = len(sample_world_state.get_validators())
        sample_world_state.add_validator("0xvalidator3")
        
        validators = sample_world_state.get_validators()
        assert len(validators) == initial_count + 1
        assert "0xvalidator3" in validators

    def test_world_state_get_validators(self, sample_world_state):
        """Test getting validators from world state"""
        validators = sample_world_state.get_validators()
        
        assert len(validators) == 2
        assert "0xvalidator1" in validators
        assert "0xvalidator2" in validators

    def test_world_state_set_eoa_and_smart_contract(self, sample_world_state):
        """Test setting both EOAs and SmartContracts at once"""
        new_eoas = {
            "0x10": EOA("0x10", 100, 0),
            "0x11": EOA("0x11", 200, 1)
        }
        new_smart_contracts = {
            "0x20": SmartContract("0x20", 300, 0, "hash1", {"data": "value1"}),
            "0x21": SmartContract("0x21", 400, 1, "hash2", {"data": "value2"})
        }
        
        sample_world_state.set_eoa_and_smart_contract(new_eoas, new_smart_contracts)
        
        # Check that old data is replaced
        assert len(sample_world_state.get_eoa_full()) == 2
        assert len(sample_world_state.get_smart_contract_full()) == 2
        
        # Check new data
        assert sample_world_state.get_eoa("0x10").balance == 100
        assert sample_world_state.get_eoa("0x11").balance == 200
        assert sample_world_state.get_smart_contract("0x20").balance == 300
        assert sample_world_state.get_smart_contract("0x21").balance == 400

    def test_world_state_get_eoa_full(self, sample_world_state):
        """Test getting full copy of EOAs"""
        eoas = sample_world_state.get_eoa_full()
        
        assert isinstance(eoas, dict)
        assert len(eoas) == 2
        assert "0x1" in eoas
        assert "0x2" in eoas
        assert eoas["0x1"].balance == 1000
        
        # Verify it's a copy (modifications shouldn't affect original)
        eoas["0x1"].balance = 9999
        assert sample_world_state.get_eoa("0x1").balance == 1000

    def test_world_state_get_smart_contract_full(self, sample_world_state):
        """Test getting full copy of SmartContracts"""
        contracts = sample_world_state.get_smart_contract_full()
        
        assert isinstance(contracts, dict)
        assert len(contracts) == 1
        assert "0x3" in contracts
        assert contracts["0x3"].balance == 200
        
        # Verify it's a copy (modifications shouldn't affect original)
        contracts["0x3"].balance = 9999
        assert sample_world_state.get_smart_contract("0x3").balance == 200

    def test_world_state_to_json(self, sample_world_state):
        """Test world state JSON serialization"""
        json_str = sample_world_state.to_json()
        
        assert isinstance(json_str, str)
        assert "eoas" in json_str
        assert "smartContracts" in json_str
        
        # Should be valid JSON
        data = json.loads(json_str)
        assert "eoas" in data
        assert "smartContracts" in data

    def test_world_state_build_worldstate(self, sample_world_state):
        """Test building world state from JSON"""
        # Get original JSON
        original_json = sample_world_state.to_json()
        
        # Create new world state and build from JSON
        new_ws = WorldState()
        new_ws.build_worldstate(original_json)
        
        # Verify the new world state matches the original
        original_eoas = sample_world_state.get_eoa_full()
        new_eoas = new_ws.get_eoa_full()
        
        assert len(original_eoas) == len(new_eoas)
        for addr in original_eoas:
            assert addr in new_eoas
            assert original_eoas[addr].balance == new_eoas[addr].balance
            assert original_eoas[addr].nonce == new_eoas[addr].nonce

    def test_world_state_get_hash(self, sample_world_state):
        """Test world state hash calculation"""
        hash_value = sample_world_state.get_hash()
        
        assert isinstance(hash_value, str)
        assert len(hash_value) > 0
        
        # Same world state should produce same hash
        hash_value2 = sample_world_state.get_hash()
        assert hash_value == hash_value2

    def test_world_state_clone(self, sample_world_state):
        """Test world state cloning"""
        cloned_ws = sample_world_state.clone()
        
        # Verify it's a different object
        assert cloned_ws is not sample_world_state
        
        # Verify data is the same
        original_eoas = sample_world_state.get_eoa_full()
        cloned_eoas = cloned_ws.get_eoa_full()
        
        assert len(original_eoas) == len(cloned_eoas)
        for addr in original_eoas:
            assert addr in cloned_eoas
            assert original_eoas[addr].balance == cloned_eoas[addr].balance
            assert original_eoas[addr].nonce == cloned_eoas[addr].nonce
        
        # Verify validators are copied
        original_validators = sample_world_state.get_validators()
        cloned_validators = cloned_ws.get_validators()
        assert original_validators == cloned_validators

    def test_world_state_clone_independence(self, sample_world_state):
        """Test that cloned world state is independent of original"""
        cloned_ws = sample_world_state.clone()
        
        # Modify original
        original_eoa = sample_world_state.get_eoa("0x1")
        original_eoa.balance = 9999
        sample_world_state.set_eoa("0x1", original_eoa)
        
        # Verify clone is unchanged
        cloned_eoa = cloned_ws.get_eoa("0x1")
        assert cloned_eoa.balance == 1000  # Should still be original value

    def test_world_state_str_representation(self, sample_world_state):
        """Test world state string representation"""
        str_repr = str(sample_world_state)
        
        assert isinstance(str_repr, str)
        assert "WorldState" in str_repr
        assert "eoas" in str_repr
        assert "smartContracts" in str_repr

    def test_eoa_json_dump(self, sample_eoa):
        """Test EOA JSON serialization"""
        json_data = sample_eoa.__jsondump__()
        
        assert isinstance(json_data, dict)
        assert json_data["address"] == "0x1"
        assert json_data["balance"] == 1000
        assert json_data["nonce"] == 0

    def test_smart_contract_json_dump(self, sample_smart_contract):
        """Test SmartContract JSON serialization"""
        json_data = sample_smart_contract.__jsondump__()
        
        assert isinstance(json_data, dict)
        assert json_data["address"] == "0x2"
        assert json_data["balance"] == 500
        assert json_data["nonce"] == 1
        assert json_data["codeHash"] == "contract_hash_123"
        assert json_data["storage"] == {"key": "value"}

    def test_world_state_hash_consistency(self, sample_world_state):
        """Test that world state hash is consistent for same data"""
        hash1 = sample_world_state.get_hash()
        hash2 = sample_world_state.get_hash()
        
        assert hash1 == hash2

    def test_world_state_hash_changes_with_data(self, sample_world_state):
        """Test that world state hash changes when data changes"""
        original_hash = sample_world_state.get_hash()
        
        # Modify data
        eoa = sample_world_state.get_eoa("0x1")
        eoa.balance = 9999
        sample_world_state.set_eoa("0x1", eoa)
        
        new_hash = sample_world_state.get_hash()
        assert original_hash != new_hash

    def test_world_state_empty_state_hash(self):
        """Test hash calculation for empty world state"""
        ws = WorldState()
        hash_value = ws.get_hash()
        
        assert isinstance(hash_value, str)
        assert len(hash_value) > 0

    def test_world_state_large_state_handling(self):
        """Test world state handling with large amounts of data"""
        ws = WorldState()
        
        # Add many EOAs
        for i in range(100):
            addr = f"0x{i:04x}"
            eoa = EOA(addr, i * 100, i)
            ws.set_eoa(addr, eoa)
        
        # Add many smart contracts
        for i in range(50):
            addr = f"0x{i:04x}"
            sc = SmartContract(addr, i * 200, i, f"hash_{i}", {"index": i})
            ws.set_smart_contract(addr, sc)
        
        # Add many validators
        for i in range(10):
            ws.add_validator(f"0xvalidator{i}")
        
        # Should still work correctly
        assert len(ws.get_eoa_full()) == 100
        assert len(ws.get_smart_contract_full()) == 50
        assert len(ws.get_validators()) == 10
        
        # Hash should still work
        hash_value = ws.get_hash()
        assert isinstance(hash_value, str)
        assert len(hash_value) > 0

    def test_world_state_json_serialization_roundtrip(self, sample_world_state):
        """Test JSON serialization and deserialization roundtrip"""
        # Serialize to JSON
        json_str = sample_world_state.to_json()
        
        # Create new world state and deserialize
        new_ws = WorldState()
        new_ws.build_worldstate(json_str)
        
        # Verify all data is preserved
        original_eoas = sample_world_state.get_eoa_full()
        new_eoas = new_ws.get_eoa_full()
        
        assert len(original_eoas) == len(new_eoas)
        for addr in original_eoas:
            assert addr in new_eoas
            assert original_eoas[addr].address == new_eoas[addr].address
            assert original_eoas[addr].balance == new_eoas[addr].balance
            assert original_eoas[addr].nonce == new_eoas[addr].nonce
        
        original_contracts = sample_world_state.get_smart_contract_full()
        new_contracts = new_ws.get_smart_contract_full()
        
        assert len(original_contracts) == len(new_contracts)
        for addr in original_contracts:
            assert addr in new_contracts
            assert original_contracts[addr].address == new_contracts[addr].address
            assert original_contracts[addr].balance == new_contracts[addr].balance
            assert original_contracts[addr].nonce == new_contracts[addr].nonce
            assert original_contracts[addr].codeHash == new_contracts[addr].codeHash
            assert original_contracts[addr].storage == new_contracts[addr].storage

    @pytest.mark.parametrize("address,balance,nonce", [
        ("0x1", 0, 0),
        ("0x2", 1000, 5),
        ("0x3", -1, 0),  # Negative balance (edge case)
        ("0x4", 2**64 - 1, 2**32 - 1),  # Large values
    ])
    def test_eoa_parameterized(self, address, balance, nonce):
        """Test EOA creation with various parameters"""
        eoa = EOA(address, balance, nonce)
        
        assert eoa.address == address
        assert eoa.balance == balance
        assert eoa.nonce == nonce

    @pytest.mark.parametrize("address,balance,nonce,code_hash,storage", [
        ("0x1", 0, 0, "", {}),
        ("0x2", 1000, 5, "hash123", {"key": "value"}),
        ("0x3", -1, 0, "empty", {}),  # Negative balance
        ("0x4", 2**64 - 1, 2**32 - 1, "large_hash", {"large": "data"}),  # Large values
    ])
    def test_smart_contract_parameterized(self, address, balance, nonce, code_hash, storage):
        """Test SmartContract creation with various parameters"""
        sc = SmartContract(address, balance, nonce, code_hash, storage)
        
        assert sc.address == address
        assert sc.balance == balance
        assert sc.nonce == nonce
        assert sc.codeHash == code_hash
        assert sc.storage == storage

    def test_world_state_validator_duplicates(self, sample_world_state):
        """Test adding duplicate validators"""
        initial_count = len(sample_world_state.get_validators())
        
        # Add duplicate validator
        sample_world_state.add_validator("0xvalidator1")  # Already exists
        
        validators = sample_world_state.get_validators()
        assert len(validators) == initial_count  # Should not increase
        assert validators.count("0xvalidator1") == 1  # Should still be unique

    def test_world_state_eoa_overwrite(self, sample_world_state):
        """Test overwriting existing EOA"""
        original_eoa = sample_world_state.get_eoa("0x1")
        assert original_eoa.balance == 1000
        
        # Overwrite with new EOA
        new_eoa = EOA("0x1", 2000, 5)
        sample_world_state.set_eoa("0x1", new_eoa)
        
        retrieved_eoa = sample_world_state.get_eoa("0x1")
        assert retrieved_eoa.balance == 2000
        assert retrieved_eoa.nonce == 5

    def test_world_state_smart_contract_overwrite(self, sample_world_state):
        """Test overwriting existing SmartContract"""
        original_sc = sample_world_state.get_smart_contract("0x3")
        assert original_sc.balance == 200
        
        # Overwrite with new SmartContract
        new_sc = SmartContract("0x3", 3000, 5, "new_hash", {"new": "data"})
        sample_world_state.set_smart_contract("0x3", new_sc)
        
        retrieved_sc = sample_world_state.get_smart_contract("0x3")
        assert retrieved_sc.balance == 3000
        assert retrieved_sc.nonce == 5
        assert retrieved_sc.codeHash == "new_hash"
        assert retrieved_sc.storage == {"new": "data"}