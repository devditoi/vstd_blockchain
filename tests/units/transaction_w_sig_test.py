import pytest

from layer0.blockchain.core.transaction_type import NativeTransaction
from layer0.blockchain.core.validator import Validator
from layer0.blockchain.core.worldstate import WorldState, EOAs
from layer0.config import ChainConfig
from layer0.utils.crypto.signer import SignerFactory
from layer0.wallet.wallet import Wallet
from layer0.node.node import Node


@pytest.fixture
def data():

    node = Node()

    ws = node.worldState

    ws.set_eoa("0x0", EOAs("0x0", int(1 * ChainConfig.NativeTokenValue), 0))
    ws.set_eoa("0x2", EOAs("0x0", int(99), 0))

    wallet_1 = Wallet(node)

    tx1 = NativeTransaction("0x0", "0x1", 100, 0, 100, 100) # Invalid (No sig)

    tx2, tx2_sign = wallet_1.create_tx(100, "0x1")

    print(tx2_sign)

    # print(SignerFactory().get_signer().verify(tx2.to_verifiable_string(), tx2_sign, wallet_1.publicKey))

    data = {
        "world_state": ws,
        "wallet_1": wallet_1,
        "tx1": tx1,
        "tx1_sign": None,
        "tx2": tx2,
        "tx2_sign": tx2_sign
    }

    return data



def test_sig_transfer(data):
    ws = data["world_state"]

    assert not Validator.validate_transaction_with_signature(data["tx1"], data["tx1_sign"], None), "Invalid signature"
    assert Validator.validate_transaction_with_signature(data["tx2"], data["tx2_sign"], data["wallet_1"].publicKey), "Valid signature"