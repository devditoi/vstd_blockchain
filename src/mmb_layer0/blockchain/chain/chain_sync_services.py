from src.mmb_layer0.blockchain.core.chain import Chain

class ChainSyncServices:
    @staticmethod
    def check_sync(chain1: Chain, chain2: Chain):
        if chain1.get_height() != chain2.get_height():
            print("chain.py:check_sync: Chain heights do not match")
            return False

        # Check block hashes
        for block in chain2.chain:
            if block.hash != chain1.get_block(block.index).hash:
                print("chain.py:check_sync: Block hashes do not match")
                return False

        # print(self.get_height(), other.get_height())
        return chain1.get_height() == chain2.get_height()

    @staticmethod
    def sync_chain(chain1: Chain, chain2: Chain, executionFunction: callable):
        if chain1.get_height() > chain2.get_height():
            return # chain1 is longer (probrally stronger))

        # Sync blocks
        for block in chain2.chain[1:]:
            print("chain.py:sync_chain: Syncing block", block.index)
            chain1.add_block(block, initially=True)
            executionFunction(block)