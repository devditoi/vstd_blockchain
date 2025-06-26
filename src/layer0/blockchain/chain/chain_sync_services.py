from layer0.blockchain.core.chain import Chain


class ChainSyncServices:
    #! Depricated
    pass
    # @staticmethod
    # def check_sync(chain1: Chain, chain2: Chain):
    #     if chain1.get_height() != chain2.get_height():
    #         print("chain.py:check_sync: Chain heights do not match")
    #         return False
    #
    #     # Check block hashes
    #     for block in chain2.chain:
    #         if block.hash != chain1.get_block(block.index).hash:
    #             print("chain.py:check_sync: Block hashes do not match")
    #             return False
    #
    #     return chain1.get_height() == chain2.get_height()

    # @staticmethod
    # def sync_chain(chain1: Chain, chain2: Chain, executionFunction: callable):
    #
    #     # print("try to sync chain")
    #
    #     if chain1.get_height() > chain2.get_height():
    #     # print(self.get_height(), other.get_height())
    #         return # chain1 is longer (probrally stronger))
    #
    #     # # Clear the blockchain
    #     # chain1.reset_chain()
    #
    #     # Find nearest common block
    #     highest_common_block = 0
    #     for i in range(chain1.get_height()):
    #         if chain1.get_block(i).hash == chain2.get_block(i).hash:
    #             highest_common_block = i
    #
    #     if highest_common_block == 0:
    #         print("chain.py:sync_chain: No common block found")
    #
    #         chain1.reset_chain()
    #         for block in chain2.chain[1:]:
    #             print("chain.py:sync_chain: Syncing block", block.index)
    #             chain1.add_block(block, initially=True)
    #             executionFunction(block)
    #
    #         return
    #
    #     print("Sync from block", highest_common_block + 1)
    #
    #     # Sync blocks
    #     for block in chain2.chain[highest_common_block:]: # Actually the data when send here (aka the chain) hasn't has genesis block?
    #         print("chain.py:sync_chain: Syncing block", block.index)
    #         chain1.add_block(block, initially=True)
    #         # time.sleep(0.1)
    #         executionFunction(block)
