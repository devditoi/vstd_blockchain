from .blockchain.chain.chain_sync_services import ChainSyncServices
from .node import Node
from .utils.serializer import NodeSerializer


class NodeSyncServices:
    @staticmethod
    def check_sync(node1: Node, node2: Node) -> bool:
        other_chain = node2.blockchain
        return ChainSyncServices.check_sync(node1.blockchain, other_chain)
