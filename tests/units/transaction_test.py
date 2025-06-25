import pytest

from mmb_layer0.blockchain.core.transaction_type import NativeTransaction
from mmb_layer0.blockchain.core.validator import Validator
from mmb_layer0.blockchain.core.worldstate import WorldState, EOAs
from mmb_layer0.config import ChainConfig


@pytest.fixture
def data():

    ws = WorldState()

    ws.set_eoa("0x0", EOAs("0x0", int(1 * ChainConfig.NativeTokenValue), 0))
    ws.set_eoa("0x2", EOAs("0x0", int(99), 0))

    data = {
        "world_state": ws,
        "native_invalid_1": NativeTransaction("0x0", "0x1", 100, 0, 0), # Invalid gas
        "native_invalid_2": NativeTransaction("0x1", "0x0", 100, 0, 100), # Insufficient balance
        "native_invalid_3": NativeTransaction("0x2", "0x0", 0, 0, 100), # Invalid amount
        "native_invalid_4": NativeTransaction("0x2", "0x0", -100, 0, 100), # Invalid amount
        "native_invalid_5": NativeTransaction("0x0", "0x0", -100, 0, 100),  # Invalid amount
        "native_valid": NativeTransaction("0x0", "0x1", 100, 0, 100),
    }

    return data



def test_gas_check_transfer(data):
    ws = data["world_state"]

    assert not Validator.validate_transaction_with_worldstate(data["native_invalid_1"], ws), "Invalid gas"
    assert not Validator.validate_transaction_with_worldstate(data["native_invalid_2"], ws), "Insufficient balance"
    assert not Validator.validate_transaction_with_worldstate(data["native_invalid_3"], ws), "Invalid amount"
    assert not Validator.validate_transaction_with_worldstate(data["native_invalid_4"], ws), "Invalid amount"
    assert not Validator.validate_transaction_with_worldstate(data["native_invalid_5"], ws), "Invalid amount"
    assert Validator.validate_transaction_with_worldstate(data["native_valid"], ws), "Valid transaction"
