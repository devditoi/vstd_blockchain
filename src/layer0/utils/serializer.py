from layer0.blockchain.core.worldstate import SmartContract
from layer0.blockchain.core.worldstate import EOA
import jsonlight
import json
import typing
from typing import Any

# from layer0.blockchain.core.chain import Chain
from layer0.p2p.peer_type.remote_peer import RemotePeer

if typing.TYPE_CHECKING:
    pass
from layer0.blockchain.core.worldstate import WorldState


class ChainSerializer:
    pass
    #! DeprecationWarning
    # @staticmethod
    # def serialize_chain(chain: Chain, exclude_genesis=False) -> str:
    #     return jsonlight.dumps({
    #         "chain": chain.chain[1:] if exclude_genesis else chain.chain,
    #         "length": chain.height,
    #         "mempool": chain.mempool,
    #         "max_block_size": chain.max_block_size
    #     })
    #
    # @staticmethod
    # def deserialize_chain(chain_json: str) -> Chain:
    #     # Building chain
    #     chain = Chain()
    #     data = json.loads(chain_json)
    #     chain.max_block_size = data["max_block_size"]
    #     for block in data["chain"][1:]:
    #         chain.add_block(BlockProcessor.cast_block(block), initially=True)
    #     return chain


class WorldStateSerializer:
    @staticmethod
    def serialize_world_state(world_state: WorldState) -> str:
        """
        Serializes a WorldState object into a JSON string.

        Args:
            world_state (WorldState): The WorldState object to serialize.

        Returns:
            str: A JSON string representation of the world state, including EOA and smart contracts.
        """
        return jsonlight.dumps({
            "eoas": jsonlight.dumps(world_state.get_eoa_full()),
            "smartContracts": jsonlight.dumps(world_state.get_smart_contract_full())
        })

    @staticmethod
    def deserialize_world_state(world_state_json: str) -> WorldState:
        """
        Deserialize a JSON string representation of a world state into a WorldState object.

        Args:
            world_state_json (str): The JSON string representing the world state.

        Returns:
            WorldState: A WorldState object constructed from the given JSON string.
        """
        data: Any = json.loads(world_state_json)
        return WorldStateSerializer.build_world_state(data)

    @staticmethod
    def build_world_state(data: Any) -> WorldState:
        """
        Builds a WorldState object from a JSON string or a dictionary.

        Args:
            data (any): A JSON string or a dictionary containing the EOA and smart contracts as keys "eoas" and "smartContracts" respectively.

        Returns:
            WorldState: A WorldState object constructed from the given data.
        """
        world_state: WorldState = WorldState()
        raw_eoas_dict: dict[str, dict] = json.loads(data["eoas"])
        raw_smart_contracts_dict: dict[str, dict] = json.loads(data["smartContracts"])
        
        converted_eoas: dict[str, EOA] = {}
        for address, eoa_data_dict in raw_eoas_dict.items():
            converted_eoas[address] = EOA(**eoa_data_dict) # Unpack dict to dataclass

        # Convert smart contracts
        converted_smart_contracts: dict[str, SmartContract] = {}
        for address, sc_data_dict in raw_smart_contracts_dict.items():
            converted_smart_contracts[address] = SmartContract(**sc_data_dict) # Unpack dict to dataclass
        
        world_state.set_eoa_and_smart_contract(converted_eoas, converted_smart_contracts)
        # inspect(world_state)
        return world_state


# class NodeSerializer:
#     @staticmethod
#     def to_json(node: "Node"):
#         """
#         Serialize a Node object to a JSON string.

#         Args:
#             node (Node): The Node object to serialize.

#         Returns:
#             str: A JSON string representation of the given Node object.
#         """
#         return jsonlight.dumps({
#             "blockchain": ChainSerializer.serialize_chain(node.blockchain),
#             "worldstate": node.worldState.to_json(),
#             "version": node.version,
#             "address": node.address,
#             "publicKey": node.publicKey.to_string().hex()
#         })

#     @staticmethod
#     def deserialize_node(node_json: str) -> "Node":
#         """
#         Deserialize a JSON string representation of a Node object into a Node object.

#         Args:
#             node_json (str): The JSON string representing the Node object.

#         Returns:
#             Node: A Node object constructed from the given JSON string.
#         """
#         data = json.loads(node_json)
#         print(data["publicKey"])
#         node = Node()
#         node.blockchain = ChainSerializer.deserialize_chain(data["blockchain"])
#         node.worldState = WorldStateSerializer.deserialize_world_state(data["worldstate"])
#         node.version = data["version"]
#         node.address = data["address"]
#         node.publicKey = data["publicKey"]
#         return node

class PeerSerializer:
    @staticmethod
    def to_json(peer):
        return json.dumps({
            "ip": peer.ip,
            "port": peer.port
        })
    @staticmethod
    def deserialize_peer(peer_json):
        # print(peer_json)
        data = json.loads(peer_json)
        peer = RemotePeer(data["ip"], data["port"])
        return peer

    @staticmethod
    def serialize_multi_peers(peers):
        return json.dumps([PeerSerializer.to_json(peer) for peer in peers])

    @staticmethod
    def deserialize_multi_peers(peers_json):
        peers_data = json.loads(peers_json)
        return [PeerSerializer.deserialize_peer(peer) for peer in peers_data]