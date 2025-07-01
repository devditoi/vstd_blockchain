from layer0.config import FeatureFlags
import hashlib
import rsa
from ecdsa import VerifyingKey, SigningKey, SECP256k1
from rsa.key import PublicKey, PrivateKey
import ecdsa
# print(hashlib.sha256(b"Nobody inspects the spammish repetition").hexdigest())

class HashUtils:
    @staticmethod
    def sha256(data) -> str:
        return hashlib.sha256(data.encode('utf8')).hexdigest()

    @staticmethod
    def sha256_nonencode(data) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def get_address(publicKey: PublicKey) -> str:
        return HashUtils.sha256_nonencode(publicKey.save_pkcs1())

    @staticmethod
    def get_address_ecdsa(publicKey: VerifyingKey) -> str:
        if FeatureFlags.DEBUG:
            print(publicKey.to_string())
            print(publicKey.to_string().hex())
        return HashUtils.sha256(publicKey.to_string().hex())

    @staticmethod
    def gen_key() -> tuple[PublicKey, PrivateKey]:
        return rsa.newkeys(512)
    
    @staticmethod
    def sign(data: str, privateKey: PrivateKey) -> bytes:
        encoded_data: bytes = data.encode('utf8')
        return rsa.sign(encoded_data, privateKey, 'SHA-256')

    @staticmethod
    def verify(data: str, signature: bytes, publicKey: PublicKey) -> bool:
        encoded_data: bytes = data.encode('utf8')
        return True if rsa.verify(encoded_data, signature, publicKey) else False

    @staticmethod
    def ecdsa_keygen() -> tuple[VerifyingKey, SigningKey]:
        sk = ecdsa.SigningKey.generate(curve=SECP256k1)
        vk = sk.get_verifying_key()
        return vk, sk

    @staticmethod
    def ecdsa_sign(data: str, sk: ecdsa.SigningKey) -> bytes:
        return sk.sign(data.encode('utf8'))

    @staticmethod
    def ecdsa_verify(data: str, signature: bytes, vk: ecdsa.VerifyingKey):
        return vk.verify(signature, data.encode('utf8'))
