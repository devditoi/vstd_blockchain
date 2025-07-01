from abc import ABC, abstractmethod
from typing import Any

class ICryptoAdapter(ABC):

    @staticmethod
    def gen_key() -> tuple[Any, Any]:
        return NotImplemented

    @staticmethod
    def sign(message: str, privateKey: object) -> str:
        return NotImplemented

    @staticmethod
    def verify(message: str, signature: str, publicKey: object) -> bool:
        return NotImplemented

    @staticmethod
    def save(filename: str, publicKey: object, privateKey: object):
        return NotImplemented

    @staticmethod
    def save_pub(filename: str, publicKey: object):
        return NotImplemented

    @staticmethod
    def save_priv(filename: str, privateKey: object):
        return NotImplemented

    def load(self, filename: str):
        return self.load_pub(filename), self.load_priv(filename) 

    @staticmethod
    def load_pub(filename: str):
        return NotImplemented

    @staticmethod
    def load_priv(filename: str):
        return NotImplemented

    @staticmethod
    def address(publicKey: object) -> str:
        return NotImplemented

    @staticmethod
    def serialize(publicKey: object) -> str:
        return NotImplemented

    @staticmethod
    def deserialize(serialized) -> object:
        return NotImplemented