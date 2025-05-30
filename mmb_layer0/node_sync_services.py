from .blockchain.chain.chain_sync_services import ChainSyncServices
from .node import Node
from .utils.serializer import NodeSerializer, ChainSerializer


class NodeSyncServices:
    @staticmethod
    def check_sync(node1: Node, node2: Node) -> bool:
        other_chain = node2.blockchain
        return ChainSyncServices.check_sync(node1.blockchain, other_chain)

    @staticmethod
    def sync(node1: Node, node2: Node) -> None:
        print("node_sync_services.py:sync: Syncing " + node1.address + " from " + node2.address)
        ChainSyncServices.sync_chain(node1.blockchain, node2.blockchain, node1.execution)

