from .chain import Chain

class ChainSyncServices:
    @staticmethod
    def check_sync(chain1: Chain, chain2: Chain):
        for block in chain2.chain:
            if block.hash != chain1.get_block(block.index).hash:
                # print("chain.py:check_sync: Block hashes do not match")
                return False

        # print(self.get_height(), other.get_height())
        return chain1.get_height() == chain2.get_height()