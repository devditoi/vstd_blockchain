import typing
if typing.TYPE_CHECKING:
    pass

class NodeSyncServices:
    pass
    # ! Depricated
    # @staticmethod
    # def check_sync(node1: "Node", node2: "Node") -> bool:
    #     other_chain = node2.blockchain
    #     # chain_synced = ChainSyncServices.check_sync(node1.blockchain, other_chain)
    #     worldstate_synced = WorldStateSyncServices.check_sync(node1.worldState, node2.worldState)
    #     if not chain_synced:
    #         print("node_sync_services.py:check_sync: Syncing chain")
    #         # ChainSyncServices.sync_chain(node1.blockchain, other_chain, node1.execution)
    #     if not worldstate_synced:
    #         print("node_sync_services.py:check_sync: Syncing worldstate")
    #         nworldstate = WorldStateSyncServices.merge_worldstates(node1.worldState, node2.worldState)
    #         node1.worldState = nworldstate
    #         # node2 is not reachable here
    #     # chain_synced = ChainSyncServices.check_sync(node1.blockchain, other_chain) # Recheck
    #     worldstate_synced = WorldStateSyncServices.check_sync(node1.worldState, node2.worldState) # Recheck
    #     print(f"node_sync_services.py:check_sync: Chain synced: {chain_synced}, Worldstate synced: {worldstate_synced}")
    #     return chain_synced and worldstate_synced

    # @staticmethod
    # def sync(node1: "Node", node2: "Node") -> None:
    #     print("node_sync_services.py:sync: Syncing " + node1.address + " from " + node2.address)
    #     # ChainSyncServices.sync_chain(node1.blockchain, node2.blockchain, node1.execution)
    #
