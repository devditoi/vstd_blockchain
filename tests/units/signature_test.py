import pytest

from layer0.blockchain.core.transaction_type import NativeTransaction
from layer0.blockchain.core.validator import Validator
from layer0.blockchain.core.worldstate import WorldState, EOA
from layer0.config import ChainConfig
from layer0.utils.crypto.signer import SignerFactory
from layer0.wallet.wallet import Wallet
from layer0.node.node import Node


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


def test_valid_signature_verification():
    """
    Test that a properly signed transaction is verified correctly
    """
    # Setup
    signer = SignerFactory().get_signer()
    public_key, private_key = signer.gen_key()
    message = "test message"

    # Action
    signature = signer.sign(message, private_key)
    is_verified = signer.verify(message, signature, public_key)

    # Assert
    assert is_verified is True


def test_tampered_message_verification():
    """
    Test that tampered messages fail verification
    """
    # Setup
    signer = SignerFactory().get_signer()
    public_key, private_key = signer.gen_key()
    original_message = "original message"
    tampered_message = "tampered message"

    # Action
    signature = signer.sign(original_message, private_key)
    is_verified = signer.verify(tampered_message, signature, public_key)

    # Assert
    assert is_verified is False


def test_invalid_signature_format():
    """
    Test that malformed signatures are handled gracefully
    """
    # Setup
    signer = SignerFactory().get_signer()
    public_key, _ = signer.gen_key()

    # Action & Assert
    assert signer.verify("test", "Suspicious signature".encode("utf-8"), public_key) is False


def test_sig_valid(data):
    # Test fail before. Reason: Signature generates from Wallet using to_string() function to convert transaction where
    # in the verify function, the to_verifiable_string() function is used. Cause mismatch
    assert SignerFactory().get_signer().verify(data["tx2"].to_verifiable_string(), data["tx2_sign"], data["publicKey"]), "Signature check failed"