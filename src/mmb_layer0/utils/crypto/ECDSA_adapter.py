from ecdsa import VerifyingKey, SigningKey

from mmb_layer0.utils.crypto.crypto_adapter_interace import ICryptoAdapter
from mmb_layer0.utils.hash import HashUtils


class ECDSAAdapter(ICryptoAdapter):

    @staticmethod
    def gen_key() -> tuple[any, any]:
        return HashUtils.ecdsa_keygen()

    @staticmethod
    def sign(message: str, privateKey) -> hex:
        return HashUtils.ecdsa_sign(message, privateKey).hex()

    @staticmethod
    def verify(message: str, signature: hex, publicKey) -> bool:
        return HashUtils.ecdsa_verify(message, bytes.fromhex(signature), publicKey)

    @staticmethod
    def save(filename: str, publicKey: any, privateKey: any):
        ECDSAAdapter.save_pub(filename, publicKey)
        ECDSAAdapter.save_priv(filename, privateKey)

    @staticmethod
    def save_pub(filename: str, publicKey: any):
        with open(filename, "wb") as f:
            f.write(publicKey.to_string())

    @staticmethod
    def save_priv(filename: str, privateKey: any):
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
    def address(publicKey: any) -> str:
        return HashUtils.get_address_ecdsa(publicKey)