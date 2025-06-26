from rich import inspect

from layer0.utils.crypto.ECDSA_adapter import ECDSAAdapter
from layer0.utils.crypto.crypto_adapter_interace import ICryptoAdapter
from layer0.utils.crypto.rsa_adapter import RSAAdapter

class SignerFactory(object):
    signer_type = None
    signer: ICryptoAdapter = None

    @staticmethod
    def __get_signer(signer_type) -> ICryptoAdapter:
        if signer_type == "rsa":
            return RSAAdapter()
        elif signer_type == "ecdsa":
            return ECDSAAdapter()
        else:
            raise Exception("Signer type not supported")

    def get_signer(self) -> ICryptoAdapter:
        return self.signer

    def __new__(cls, signer_type: str | None = None):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SignerFactory, cls).__new__(cls)
            cls.instance.signer_type = signer_type
            cls.instance.signer = SignerFactory.__get_signer(signer_type)
        return cls.instance

signer = SignerFactory("ecdsa")
# inspect(signer)