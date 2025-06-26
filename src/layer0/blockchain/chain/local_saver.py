import json
import os
import typing


if typing.TYPE_CHECKING:
    from layer0.blockchain.core.chain import Chain
    from layer0.blockchain.core.block import Block
    from layer0.blockchain.core.transaction_type import Transaction

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
    def get_block(self, height: int) -> "Block":
        pass

    @abstractmethod
    def get_height(self) -> int:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    def get_chain_hashes(self) -> list[str]:
        pass

    @abstractmethod
    def flush(self):
        pass

    @abstractmethod
    def remote_block(self) -> "Block":
        pass

    @abstractmethod
    def get_tx(self, tx_hash) -> "Transaction | None":
        pass


class NotImplementedSaver(ISaver):
    def get_chain_hashes(self) -> list[str]:
        pass

    def remote_block(self) -> "Block":
        pass

    def get_tx(self, tx_hash) -> "Transaction":
        pass

    def get_height(self) -> int:
        pass

    def flush(self):
        pass

    def get_block(self, height: int) -> "Block":
        pass

    def save_chain(self, chain: "Chain") -> None:
        # raise NotImplementedError("save_chain not implemented")
        pass

    def load_chain(self) -> "Chain":
        # raise NotImplementedError("load_chain not implemented")
        pass

    def add_block(self, block: "Block") -> None:
        # raise NotImplementedError("add_block not implemented")
        pass

    def clear(self) -> None:
        pass