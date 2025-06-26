# import jsonlight

from .chain_repository_interface import IChainRepository
from layer0.blockchain.core.chain import Chain
from layer0.utils.serializer import ChainSerializer


class JsonChainRepository(IChainRepository):
    #! Warning Depricated
    def __init__(self, filename) -> None:
        self.filename = filename

    def save(self, data: Chain) -> None:
        data = ChainSerializer.serialize_chain(data)
        with open(self.filename, "w") as f:
            f.write(data)

    def load(self) -> Chain:
        chain = Chain()
        with open(self.filename, "r") as f:
            data_raw = f.read()

        return ChainSerializer.deserialize_chain(data_raw)