import hashlib
import rsa
from rsa.key import PublicKey, PrivateKey
# print(hashlib.sha256(b"Nobody inspects the spammish repetition").hexdigest())

class HashUtils:
    @staticmethod
    def sha256(data):
        return hashlib.sha256(data.encode('utf8')).hexdigest()

    @staticmethod
    def sha256_nonencode(data):
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def get_address(publicKey: PublicKey) -> str:
        return HashUtils.sha256_nonencode(publicKey.save_pkcs1())

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