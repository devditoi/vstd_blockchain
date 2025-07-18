from ecdsa import VerifyingKey, SigningKey, BadSignatureError, SECP256k1
from layer0.utils.crypto.crypto_adapter_interace import ICryptoAdapter
from layer0.utils.hash import HashUtils


class ECDSAAdapter(ICryptoAdapter):

    @staticmethod
    def gen_key() -> tuple[VerifyingKey, SigningKey]:
        return HashUtils.ecdsa_keygen()

    @staticmethod
    def sign(message: str, privateKey: SigningKey) -> str:
        return HashUtils.ecdsa_sign(message, privateKey).hex()

    @staticmethod
    def verify(message: str, signature: str, publicKey: VerifyingKey) -> bool:
        try:
            return HashUtils.ecdsa_verify(message, bytes.fromhex(signature), publicKey)
        except TypeError: # TypeError: fromhex() argument must be str, not ...
            print("TypeError")
            return False
        except BadSignatureError:
            print("BadSignatureError")
            return False
        except ValueError:
            print("ValueError")
            return False

    @staticmethod
    def serialize(publicKey: VerifyingKey) -> str:
        return publicKey.to_string().hex()

    @staticmethod
    def deserialize(serialized: str) -> VerifyingKey:
        return VerifyingKey.from_string(
            bytes.fromhex(serialized),
            curve=SECP256k1,
        )

    @staticmethod
    def save(filename: str, publicKey: VerifyingKey, privateKey: SigningKey) -> None:
        ECDSAAdapter.save_pub(filename, publicKey)
        ECDSAAdapter.save_priv(filename, privateKey)

    @staticmethod
    def save_pub(filename: str, publicKey: VerifyingKey) -> None:
        with open(filename, "w") as f:
            f.write(publicKey.to_string().hex())

    @staticmethod
    def save_priv(filename: str, privateKey: SigningKey) -> None:
        with open(filename + ".priv", "w") as f:
            f.write(privateKey.to_string().hex())
        return ECDSAAdapter.load_pub(filename), ECDSAAdapter.load_priv(filename)

    @staticmethod
    def load_pub(filename: str):
        with open(filename, "r") as f:
            publicKey = VerifyingKey.from_string(
                bytes.fromhex(f.read()),
                curve=SECP256k1,
            )

        return publicKey

    @staticmethod
    def load_priv(filename: str):
        with open(filename + ".priv", "r") as f:
            privateKey = SigningKey.from_string(
                bytes.fromhex(f.read()),
                curve=SECP256k1,
            )

        return privateKey

    @staticmethod
    def address(publicKey: VerifyingKey) -> str:
        return HashUtils.get_address_ecdsa(publicKey)