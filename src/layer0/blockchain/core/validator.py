from rsa import PublicKey

import typing

if typing.TYPE_CHECKING:
    from layer0.blockchain.consensus.consensus import IConsensus
    from layer0.blockchain.consensus.consensus_processor import ConsensusProcessor
    from layer0.blockchain.core.chain import Chain
from layer0.blockchain.core.transaction_type import Transaction
from layer0.blockchain.core.worldstate import WorldState
from layer0.config import ChainConfig
from layer0.utils.crypto.signer import SignerFactory
from layer0.utils.hash import HashUtils
from rich import print, inspect
from layer0.blockchain.core.block import Block
import time

MAX_TRANSACTION_WAITING_TIME = 1000 * 60 * 60 # 1 Hours

class Validator:
    @staticmethod
    def validate_transaction_with_signature(tx: Transaction, signature: bytes, publicKey: any) -> bool:
        print(tx.to_verifiable_string())
        print(signature)
        print(publicKey)
        if not SignerFactory().get_signer().verify(tx.to_verifiable_string(), signature, publicKey):
            print("validator.py:validate_transaction_with_signature: Transaction signature is invalid")
            # raise Exception("Transaction signature is invalid")
            return False

        if not SignerFactory().get_signer().address(publicKey) == tx.sender and tx.Txtype != "mintburn":
            print("validator.py:validate_transaction_with_signature: Transaction sender is invalid")
            # raise Exception("Transaction sender is invalid")
            return False

        tx.signature = signature
        # tx.publicKey = publicKey.to_string().hex()
        tx.publicKey = SignerFactory().get_signer().serialize(publicKey)

        return True


    @staticmethod
    def validate_transaction_with_worldstate(tx: Transaction, worldState: WorldState) -> bool:

        if tx.gas_limit < ChainConfig.MinimumGasPrice:
            print("Validator.py:offchain_validate: Transaction gasPrice is below minimum")
            return False

        if worldState.get_eoa(tx.sender).balance < tx.gas_limit and tx.Txtype != "mintburn":
            print("Validator.py:offchain_validate: Transaction sender does not have enough balance")
            return False

        if tx.transactionData["amount"] <= 0:
            print("Validator.py:offchain_validate: Transaction amount is negative")
            return False

        return True

    @staticmethod
    def validate_transaction_raw(tx, pre_nonce_check = None):
        if tx.Txtype == "mintburn":
            # privileged transaction
            return True

        # Public key are in hex format -> need to convert back

        # Yeah wtf?
        if not tx.publicKey:
            print("chain.py:process_block: Transaction public key is missing")
            return False

        temp_public_key = SignerFactory().get_signer().deserialize(tx.publicKey)

        if not SignerFactory().get_signer().verify(tx.to_verifiable_string(), tx.signature, temp_public_key):
            print("chain.py:process_block: Transaction signature is invalid")
            return False

        if not SignerFactory().get_signer().address(temp_public_key) == tx.sender:
            print("chain.py:process_block: Transaction sender is invalid")
            return False

        # Check if transaction aren't too old or in the futures
        if tx.timestamp < (time.time() * 1000 - MAX_TRANSACTION_WAITING_TIME) or tx.timestamp > time.time() * 1000:
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
            if not Validator.validate_transaction_raw(tx):
                return False

            # if tx.sender not in pre_nonce_check:
            pre_nonce_check[tx.sender] = tx.nonce

        return True

    @staticmethod
    def validate_block_on_chain(block: Block, chain, initially=False) -> bool:
        if block.index != chain.get_height() and not initially:
            print("chain.py:add_block: Block index does not match chain length of " + str(chain.get_height()))
            print(block.index, chain.get_height())
            return False

        if block.previous_hash != chain.get_latest_block().hash:
            print("chain.py:add_block: Block previous hash does not match last block hash")
            return False

        if block.hash == chain.get_latest_block().hash:
            print("chain.py:add_block: Block hash already exists")
            return False

        for tx in block.data:
            # inspect(tx)
            if not Validator.validate_transaction_raw(tx):
                return False

        return True

    @staticmethod
    def validate_block_without_chain(block: Block, prev_hash):

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
            if not Validator.validate_transaction_raw(tx):
                return False

        return True

    @staticmethod
    def validate_full_chain(chain: "Chain", consensus: "IConsensus"):
        prev_hash = "0"
        for i in range(chain.get_height()):
            block = chain.chain.get_block(i)

            if i != 0 and not Validator.validate_block_without_chain(block, prev_hash):
                return False

            if i != 0 and block.timestamp < chain.chain.get_block(i - 1).timestamp:
                return False

            if i != 0 and not consensus.is_valid(block): # don't check the first block
                return False

            prev_hash = block.hash
        return True