from rsa import PublicKey

import typing

if typing.TYPE_CHECKING:
    from mmb_layer0.blockchain.consensus.consensus import IConsensus
    from mmb_layer0.blockchain.consensus.consensus_processor import ConsensusProcessor
    from mmb_layer0.blockchain.core.chain import Chain
from mmb_layer0.blockchain.core.transaction_type import Transaction
from mmb_layer0.blockchain.core.worldstate import WorldState
from mmb_layer0.config import MMBConfig
from mmb_layer0.utils.crypto.signer import SignerFactory
from mmb_layer0.utils.hash import HashUtils
from rich import print, inspect
from mmb_layer0.blockchain.core.block import Block

class Validator:
    @staticmethod
    def onchain_validate(tx: Transaction, signature: bytes, publicKey: any) -> bool:
        if not SignerFactory().get_signer().verify(tx.to_verifiable_string(), signature, publicKey):
            print("validator.py:onchain_validate: Transaction signature is invalid")
            # raise Exception("Transaction signature is invalid")
            return False

        if not SignerFactory().get_signer().address(publicKey) == tx.sender and tx.Txtype != "mintburn":
            print("validator.py:onchain_validate: Transaction sender is invalid")
            # raise Exception("Transaction sender is invalid")
            return False

        # TODO REALLY NEED TO FIX HERE TOO, WE NEED A FACTORY FOR KEYS
        tx.signature = signature
        tx.publicKey = publicKey.to_string().hex()

        return True


    @staticmethod
    def offchain_validate(tx: Transaction, worldState: WorldState) -> bool:
        # TODO For debug
        # if tx.gasPrice < MMBConfig.MinimumGasPrice:
        #     print("Validator.py:offchain_validate: Transaction gasPrice is below minimum")
        #     return False

        if worldState.get_eoa(tx.sender).balance < tx.gasPrice and tx.Txtype != "mintburn":
            print("Validator.py:offchain_validate: Transaction sender does not have enough balance")
            return False

        return True

    @staticmethod
    def validate_transaction(tx, pre_nonce_check = None):
        if tx.Txtype == "mintburn":
            # privileged transaction
            return True
        if not SignerFactory().get_signer().verify(tx.to_verifiable_string(), tx.signature, tx.publicKey):
            print("chain.py:process_block: Transaction signature is invalid")
            return False

        if not SignerFactory().get_signer().address(tx.publicKey) == tx.sender:
            print("chain.py:process_block: Transaction sender is invalid")
            return False

        if pre_nonce_check:
            if tx.sender in pre_nonce_check and tx.nonce != pre_nonce_check[tx.sender] + 1:
                print("chain.py:process_block: Transaction nonce is not valid")
                return False

        return True
    @staticmethod
    def preblock_validate(mempool: list[Transaction]) -> bool:
        pre_nonce_check = {}
        for tx in mempool:
            if not Validator.validate_transaction(tx):
                return False

            # if tx.sender not in pre_nonce_check:
            pre_nonce_check[tx.sender] = tx.nonce

        return True

    @staticmethod
    def validate_block(block: Block, chain, initially=False) -> bool:
        if block.index != chain.get_height() and not initially:
            print("chain.py:add_block: Block index does not match chain length of " + str(chain.length))
            print(chain.chain)
            return False

        if block.previous_hash != chain.get_last_block().hash:
            print("chain.py:add_block: Block previous hash does not match last block hash")
            return False

        if block.hash == chain.get_last_block().hash:
            print("chain.py:add_block: Block hash already exists")
            return False

        return True

    @staticmethod
    def validate_block_offchain(block: Block, prev_hash):

        if prev_hash == "0":
            if block.index != 0:
                return False
            return True

        if block.previous_hash != prev_hash:
            return False

        if block.hash == prev_hash:
            return False

        if block.hash != HashUtils.sha256(
                str(block.index) + str(block.previous_hash) + str(block.timestamp) + str(block.data)):
            return False


        for tx in block.data:
            # inspect(tx)
            if not Validator.validate_transaction(tx):
                return False

        return True

    @staticmethod
    def validate_full_chain(chain: "Chain", consensus: "IConsensus"):
        prev_hash = "0"
        for i in range(len(chain.chain)):
            block = chain.chain[i]

            if not Validator.validate_block_offchain(block, prev_hash):
                return False

            if i != 0 and block.timestamp < chain.chain[i - 1].timestamp:
                return False

            if i != 0 and not consensus.is_valid(block): # don't check first block
                return False

            prev_hash = block.hash

        return True