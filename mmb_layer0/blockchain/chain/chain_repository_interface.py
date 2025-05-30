from abc import ABC, abstractmethod


class IChainRepository(ABC):
    @abstractmethod
    def save(self, data: any) -> None:
        pass

    @abstractmethod
    def load(self) -> any:
        pass
