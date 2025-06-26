import pytest

from layer0.blockchain.core.transaction_type import NativeTransaction
from layer0.blockchain.core.validator import Validator
from layer0.blockchain.core.worldstate import WorldState, EOAs
from layer0.blockchain.processor.transaction_processor import TransactionProcessor
from layer0.config import ChainConfig


@pytest.fixture
def data():

    ws = WorldState()

    ws.set_eoa("0x0", EOAs("0x0", int(1 * ChainConfig.NativeTokenValue), 0))
    ws.set_eoa("0x2", EOAs("0x0", int(99), 0))

    data = {
        "world_state": ws,
        # "native_invalid_1": NativeTransaction("0x0", "0x1", 100, 0, 0), # Invalid gas
        # Now the chain accept zero fee transaction so this suck
        "native_invalid_2": NativeTransaction("0x1", "0x0", 100, 0, 100), # Insufficient balance
        "native_invalid_3": NativeTransaction("0x2", "0x0", 0, 0, 100), # Invalid amount
        "native_invalid_4": NativeTransaction("0x2", "0x0", -100, 0, 100), # Invalid amount
        "native_invalid_5": NativeTransaction("0x0", "0x0", -100, 0, 100),  # Invalid amount
        "native_valid": NativeTransaction("0x0", "0x1", 100, 0, 100),
    }

    return data


def test_transaction_serialization_roundtrip():
    """
    Test that a transaction can be serialized and deserialized without data loss
    """
    # Setup
    tx = NativeTransaction("0x0", "0x1", 100, 0, 100)  # Helper function to create a test transaction

    # Action
    serialized = tx.to_string()
    deserialized = TransactionProcessor.cast_transaction(serialized)

    # Assert
    assert tx.to_string() == deserialized.to_string()
    assert tx.hash == deserialized.hash


def test_invalid_transaction_signature():
    """
    Test that transactions with invalid signatures are rejected
    """
    # Setup
    tx = NativeTransaction("0x0", "0x1", 100, 0, 100)  # Helper function to create a test transaction
    tx.signature = "invalid_signature"

    # Action & Assert
    # with pytest.raises(ValueError, match="Invalid signature"):
    assert Validator.validate_transaction_raw(tx) is False


def test_gas_check_transfer(data):
    ws = data["world_state"]

    # Transaction now can be gas-free!
    # assert not Validator.validate_transaction_with_worldstate(data["native_invalid_1"], ws), "Invalid gas"
    assert not Validator.validate_transaction_with_worldstate(data["native_invalid_2"], ws), "Insufficient balance"
    assert not Validator.validate_transaction_with_worldstate(data["native_invalid_3"], ws), "Invalid amount"
    assert not Validator.validate_transaction_with_worldstate(data["native_invalid_4"], ws), "Invalid amount"
    assert not Validator.validate_transaction_with_worldstate(data["native_invalid_5"], ws), "Invalid amount"
    assert Validator.validate_transaction_with_worldstate(data["native_valid"], ws), "Valid transaction"
