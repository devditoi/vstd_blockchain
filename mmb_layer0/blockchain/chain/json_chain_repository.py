# import jsonlight

from .chain_repository_interface import IChainRepository
from .chain import Chain
import json
from mmb_layer0.utils.serializer import ChainSerializer
from ..block_processor import BlockProcessor


class JsonChainRepository(IChainRepository):
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