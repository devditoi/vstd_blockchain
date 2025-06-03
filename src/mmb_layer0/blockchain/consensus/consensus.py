from abc import ABC, abstractmethod

from mmb_layer0.blockchain.core.block import Block


class IConsensus(ABC):
    @abstractmethod
    def get_validators(self) -> list[str]:
        pass

    @abstractmethod
    def is_valid(self, block: Block) -> bool:
        pass

    @abstractmethod
    def is_leader(self) -> bool:
        pass

    def sign_block(self, block: Block) -> None:
        pass
