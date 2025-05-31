from src.mmb_layer0.utils.crypto.crypto_adapter_interace import ICryptoAdapter
from src.mmb_layer0.utils.hash import HashUtils
from rsa import PublicKey, PrivateKey
class RSAAdapter(ICryptoAdapter):
    @staticmethod
    def gen_key() -> tuple[any, any]:
        return HashUtils.gen_key()

    @staticmethod
    def sign(message: str, privateKey: PrivateKey) -> hex:
        return HashUtils.sign(message, privateKey).hex()

    @staticmethod
    def verify(message: str, signature: hex, publicKey: PublicKey) -> bool:
        return HashUtils.verify(message, bytes.fromhex(signature), publicKey)

    @staticmethod
    def save(filename: str, publicKey: any, privateKey: any):
        RSAAdapter.save_pub(filename, publicKey)
        RSAAdapter.save_priv(filename, privateKey)

    @staticmethod
    def save_pub(filename: str, publicKey: any):
        with open(filename, "w") as f:
            f.write(publicKey.save_pkcs1().decode('utf-8'))

    @staticmethod
    def save_priv(filename: str, privateKey: any):
        with open(filename + ".priv", "w") as f:
            f.write(privateKey.save_pkcs1().decode('utf-8'))

    @staticmethod
    def load(filename: str):
        return RSAAdapter.load_pub(filename), RSAAdapter.load_priv(filename)

    @staticmethod
    def load_pub(filename: str):
        with open(filename, "r") as f:
            publicKey = PublicKey.load_pkcs1(f.read().encode('utf-8'))

        return publicKey

    @staticmethod
    def load_priv(filename: str):
        with open(filename + ".priv", "r") as f:
            privateKey = PrivateKey.load_pkcs1(f.read().encode('utf-8'))

        return privateKey

    @staticmethod
    def address(publicKey: any) -> str:
        return HashUtils.get_address(publicKey)