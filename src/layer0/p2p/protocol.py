from abc import abstractmethod, ABC
from layer0.node.node import Node

class Protocol(ABC):
    @abstractmethod
    def __init__(self, node: "Node", port: int):
        pass
    @abstractmethod
    def listen_loop(self):
        pass
    @abstractmethod
    def stop(self):
        pass