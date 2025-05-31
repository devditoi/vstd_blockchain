from abc import ABC, abstractmethod

class ICryptoAdapter(ABC):

    @staticmethod
    def gen_key() -> tuple[any, any]:
        pass

    @staticmethod
    def sign(message: str, privateKey: any) -> bytes:
        pass

    @staticmethod
    def verify(message: str, signature: bytes, publicKey: any) -> bool:
        pass

    @staticmethod
    def save(filename: str, publicKey: any, privateKey: any):
        pass

    @staticmethod
    def save_pub(filename: str, publicKey: any):
        pass

    @staticmethod
    def save_priv(filename: str, privateKey: any):
        pass

    @staticmethod
    def load(filename: str):
        pass

    @staticmethod
    def load_pub(filename: str):
        pass

    @staticmethod
    def load_priv(filename: str):
        pass

    @staticmethod
    def address(publicKey) -> str:
        pass