import pytest

from mmb_layer0.blockchain.core.transaction_type import NativeTransaction
from mmb_layer0.blockchain.core.validator import Validator
from mmb_layer0.blockchain.core.worldstate import WorldState, EOAs
from mmb_layer0.config import MMBConfig
from mmb_layer0.utils.crypto.signer import SignerFactory
from mmb_layer0.wallet.wallet import Wallet
from mmb_layer0.node.node import Node


@pytest.fixture
def data():
    node = Node()
    wallet_1 = Wallet(node)

    tx2, tx2_sign = wallet_1.create_tx(100, "0x1")

    print(tx2_sign)

    # print(SignerFactory().get_signer().verify(tx2.to_verifiable_string(), tx2_sign, wallet_1.publicKey))

    data = {
        "tx2": tx2,
        "tx2_sign": tx2_sign,
        "publicKey": wallet_1.publicKey
    }
    return data

def test_sig_valid(data):
    # Test fail before. Reason: Signature generate from Wallet using to_string() function to convert transaction where
    # in the verify function, the to_verifiable_string() function is used. Cause mismatch
    assert SignerFactory().get_signer().verify(data["tx2"].to_verifiable_string(), data["tx2_sign"], data["publicKey"]), "Signature check failed"