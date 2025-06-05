from ecdsa import VerifyingKey, SigningKey

from mmb_layer0.utils.crypto.crypto_adapter_interace import ICryptoAdapter
from mmb_layer0.utils.hash import HashUtils


class ECDSAAdapter(ICryptoAdapter):

    @staticmethod
    def gen_key() -> tuple[VerifyingKey, SigningKey]:
        return HashUtils.ecdsa_keygen()

    @staticmethod
    def sign(message: str, privateKey: SigningKey) -> hex:
        return HashUtils.ecdsa_sign(message, privateKey).hex()

    @staticmethod
    def verify(message: str, signature: hex, publicKey: VerifyingKey) -> bool:
        return HashUtils.ecdsa_verify(message, bytes.fromhex(signature), publicKey)

    @staticmethod
    def serialize(publicKey: VerifyingKey) -> str:
        return publicKey.to_string().hex()

    @staticmethod
    def deserialize(serialized: str) -> any:
        return VerifyingKey.from_string(bytes.fromhex(serialized))

    @staticmethod
    def save(filename: str, publicKey: VerifyingKey, privateKey: SigningKey):
        ECDSAAdapter.save_pub(filename, publicKey)
        ECDSAAdapter.save_priv(filename, privateKey)

    @staticmethod
    def save_pub(filename: str, publicKey: VerifyingKey):
        with open(filename, "wb") as f:
            f.write(publicKey.to_string())

    @staticmethod
    def save_priv(filename: str, privateKey: SigningKey):
        with open(filename + ".priv", "wb") as f:
            f.write(privateKey.to_string())

    @staticmethod
    def load(filename: str):
        return ECDSAAdapter.load_pub(filename), ECDSAAdapter.load_priv(filename)

    @staticmethod
    def load_pub(filename: str):
        with open(filename, "rb") as f:
            publicKey = VerifyingKey.from_string(f.read())

        return publicKey

    @staticmethod
    def load_priv(filename: str):
        with open(filename + ".priv", "rb") as f:
            privateKey = SigningKey.from_string(f.read())

        return privateKey

    @staticmethod
    def address(publicKey: VerifyingKey) -> str:
        return HashUtils.get_address_ecdsa(publicKey)