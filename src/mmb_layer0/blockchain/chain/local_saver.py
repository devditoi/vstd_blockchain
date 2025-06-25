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

    @abstractmethod
    def get_block(self, height: int) -> Block:
        pass

    @abstractmethod
    def get_height(self) -> int:
        pass

    @abstractmethod
    def set_block(self, index: int, block: "Block") -> None:
        pass

class NotImplementedSaver(ISaver):
    def get_height(self) -> int:
        pass

    def set_block(self, index: int, block: "Block") -> None:
        pass

    def get_block(self, height: int) -> Block:
        pass

    def save_chain(self, chain: "Chain") -> None:
        # raise NotImplementedError("save_chain not implemented")
        pass

    def load_chain(self) -> "Chain":
        # raise NotImplementedError("load_chain not implemented")
        return Chain()

    def add_block(self, block: "Block") -> None:
        # raise NotImplementedError("add_block not implemented")
        pass