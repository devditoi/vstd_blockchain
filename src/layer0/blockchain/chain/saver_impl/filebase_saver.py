from ..local_saver import ISaver
import json
import os
import typing
from layer0.blockchain.core.transaction_type import Transaction
from ...processor.block_processor import BlockProcessor
from ...processor.transaction_processor import TransactionProcessor
if typing.TYPE_CHECKING:
    from layer0.blockchain.core.block import Block
    from layer0.blockchain.core.chain import Chain


class FilebaseDatabase:
    def __init__(self, blockchain_dir: str = "blockchain", transactions_dir: str = "transactions"):
        self.blockchain_dir = blockchain_dir
        self.transactions_dir = transactions_dir

        # Create directories if they don't exist
        os.makedirs(self.blockchain_dir, exist_ok=True)
        os.makedirs(self.transactions_dir, exist_ok=True)
        self.height = 0

    def get_and_sort_filelist(self) -> list[str]:
        file_list = os.listdir(self.blockchain_dir)
        # Sort by the number after #, default sort is error
        file_list.sort(key=lambda x: int(x.split("#")[1][:-5]))
        return file_list

    def load_height(self):
        self.height = len(self.get_and_sort_filelist())

    def save_block(self, block: "Block") -> None:
        """Save a block to the blockchain directory"""
        # First we going to check the height
        if block.index + 1 >= self.height:
            self.height = block.index + 1
        else:
            raise Exception("Block index is lower than current height") # Bruh
        block_path = os.path.join(self.blockchain_dir, f"Block#{block.index}.json")
        with open(block_path, "w") as f:
            f.write(block.to_string())

        # Save transaction too!!!
        if block.index != 0:
            for tx in block.data:
                tx_path = os.path.join(self.transactions_dir, f"{tx.hash}.json")
                with open(tx_path, "w") as f:
                    f.write(tx.to_string_with_status())

    def load_block(self, block_height: int) -> str | None:
        """Load a block from the blockchain directory"""
        block_path = os.path.join(self.blockchain_dir, f"Block#{block_height}.json")
        if not os.path.exists(block_path):
            # raise FileNotFoundError(f"Block {block_height} not found")
            return None
        with open(block_path, "r") as f:
            return f.read()

    def load_tx(self, tx_hash):
        tx_path = os.path.join(self.transactions_dir, f"{tx_hash}.json")
        if os.path.exists(tx_path):
            with open(tx_path, "r") as f:
                return f.read()
        else:
            return None

    # def save_transaction(self, tx: "Transaction") -> None:
    #     """Save a transaction to the transactions directory"""
    #     tx_path = os.path.join(self.transactions_dir, f"{tx.hash}.json")
    #     with open(tx_path, "w") as f:
    #         # json.dump(tx_data, f, indent=4)
    #         f.write(tx.to_string())

    def load_block_all(self):
        block_datas = []
        for filename in self.get_and_sort_filelist():
            if filename.endswith(".json"):
                with open(os.path.join(self.blockchain_dir, filename), "r") as f:
                    block_datas.append(f.read())
        return block_datas

    def remove_last_block(self):
        os.remove(os.path.join(self.blockchain_dir, f"Block#{self.height-1}.json"))
        self.height -= 1

    def clear(self) -> None:
        for filename in self.get_and_sort_filelist():
            os.remove(os.path.join(self.blockchain_dir, filename))

    # def load_transaction(self, tx_id: str) -> Optional[Dict]:
    #     """Load a transaction from the transactions directory"""
    #     tx_path = os.path.join(self.transactions_dir, f"{tx_id}.json")
    #     if not os.path.exists(tx_path):
    #         return None
    #     with open(tx_path, "r") as f:
    #         return json.load(f)


class FilebaseSaver(ISaver):
    def __init__(self, database: FilebaseDatabase):
        self.database = database
        self.delayed = []

    def get_tx(self, tx_hash) -> "Transaction | None":
        tx_data = self.database.load_tx(tx_hash)
        if tx_data is None:
            return None
        tx = TransactionProcessor.cast_transaction(tx_data)

        # Cast special tx status
        tx_json = json.loads(tx_data)
        tx.status = tx_json["status"]

        return tx

    def flush(self):
        for block in self.delayed:
            self.add_block(block)
        self.delayed = []

    def remote_block(self):
        # Purge the last block
        self.database.remove_last_block()

    def clear(self) -> None:
        self.database.clear()

    def get_chain_hashes(self) -> list[str]:
        hashes = []
        # TODO: Need to implement some kind of index for hashes of it would cost a huge amount of I/O
        for i in range(self.database.height):
            block = self.get_block(i)
            if not block:
                continue
            hashes.append({
                "height": i,
                "hash": block.hash
            })

        return hashes

    def add_block(self, block: "Block", delay_flush = False) -> None:
        """
        Add a new block to the blockchain.
        Returns the block hash.
        """
        if not delay_flush:
            self.database.save_block(block)
        else:
            self.delayed.append(block)

    def get_block(self, height: int) -> "Block | None":
        """
        Retrieve a block from the blockchain at a given height.

        Args:
            height (int): The height of the block to retrieve.

        Returns:
            Block: The Block object corresponding to the specified height.

        Raises:
            FileNotFoundError: If the block at the specified height does not exist.
        """
        # print("[FilebaseSaver] get_block " + str(height))
        block_data = self.database.load_block(height) # TODO: Hmm fine
        if block_data is None:
            return None
        return BlockProcessor.cast_block(block_data)

    def get_height(self) -> int:
        return self.database.height

    def save_chain(self, chain: "Chain") -> None:
        for block in chain.chain:
            self.add_block(block)

    def load_chain(self) -> "None":
        #! Depricated
        # TODO: Need to change this to apply every block to worldstate, not to return the chain
        pass
        # block_datas = self.database.load_block_all()
        # chain = Chain()
        # is_genesis = True
        # for block_data in block_datas:
        #     if is_genesis:
        #         is_genesis = False
        #         continue
        #     block = BlockProcessor.cast_block(block_data)
        #     chain.add_block(block, initially=True)
        # return chain


    # def get_block(self, block_height: int) -> Dict:
    #     """
    #     Retrieve a block by height with full transaction data.
    #     """
    #     block_data = self.database.load_block(block_height)
    #
    #     # Load full transaction data
    #     for tx_id in block_data["transactions"]:
    #         tx_data = self.database.load_transaction(tx_id)
    #         if tx_data:
    #             block_data["transactions"] = [tx for tx in block_data["transactions"] if tx != tx_id]
    #             block_data["transactions"].append(tx_data)
    #
    #     return block_data
    #
    # def get_full_chain(self) -> List[Dict]:
    #     """
    #     Retrieve the full blockchain chain in order.
    #     """
    #     full_chain = []
    #     for height in range(1, self.current_height + 1):
    #         block = self.get_block(height)
    #         full_chain.append(block)
    #     return full_chain
    #
    # def search_transaction(self, tx_hash: str) -> Optional[Dict]:
    #     """
    #     Search for a transaction by its hash.
    #     """
    #     for filename in os.listdir(self.database.transactions_dir):
    #         tx_id = os.path.splitext(filename)[0]
    #         tx_data = self.database.load_transaction(tx_id)
    #         if tx_data and tx_data.get("tx_id") == tx_hash:
    #             return tx_data
    #     return None


# # Example usage:
# if __name__ == "__main__":
#     # Initialize the database and blockchain
#     database = Database()
#     blockchain = Blockchain(database)
#
#     # Add sample blocks with transactions
#     # Block 1
#     transactions1 = [
#         {
#             "sender": "A",
#             "receiver": "B",
#             "amount": 1.0,
#             "data": "Sample transaction 1"
#         },
#         {
#             "sender": "B",
#             "receiver": "C",
#             "amount": 0.5,
#             "data": "Sample transaction 2"
#         }
#     ]
#
#     previous_hash = "genesis_block_hash"
#     block_hash1 = blockchain.add_block(previous_hash, transactions1)
#     print(f"Block 1 added with hash: {block_hash1}")
#
#     # Block 2
#     transactions2 = [
#         {
#             "sender": "C",
#             "receiver": "D",
#             "amount": 0.75,
#             "data": "Sample transaction 3"
#         }
#     ]
#
#     previous_hash = block_hash1
#     block_hash2 = blockchain.add_block(previous_hash, transactions2)
#     print(f"Block 2 added with hash: {block_hash2}")
#
#     # Get full chain
#     full_chain = blockchain.get_full_chain()
#     print("\nFull Blockchain Chain:")
#     print(json.dumps(full_chain, indent=2))
#
#     # Get specific block
#     block2 = blockchain.get_block(2)
#     print("\nBlock 2 data:")
#     print(json.dumps(block2, indent=2))
#
#     # Search for a transaction
#     tx_hash = block2["transactions"][0]["tx_id"]
#     tx_data = blockchain.search_transaction(tx_hash)
#     print("\nFound transaction data:")
#     print(json.dumps(tx_data, indent=2))