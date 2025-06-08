import json
import os
import typing
from mmb_layer0.blockchain.core.chain import Chain
from mmb_layer0.blockchain.core.block import Block
from abc import ABC, abstractmethod
class ISaver(ABC):
    @abstractmethod
    def save_chain(self, chain: "Chain"):
        pass

    @abstractmethod
    def load_chain(self) -> "Chain":
        pass

    @abstractmethod
    def add_block(self, block: "Block") -> None:
        pass

class NotImplementedSaver(ISaver):
    def save_chain(self, chain: "Chain") -> None:
        # raise NotImplementedError("save_chain not implemented")
        pass

    def load_chain(self) -> "Chain":
        # raise NotImplementedError("load_chain not implemented")
        return Chain()

    def add_block(self, block: "Block") -> None:
        # raise NotImplementedError("add_block not implemented")
        pass