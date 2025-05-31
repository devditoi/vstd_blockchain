from rsa import PublicKey
from src.mmb_layer0.blockchain.core.transactionType import Transaction
from src.mmb_layer0.blockchain.core.worldstate import WorldState
from src.mmb_layer0.config import MMBConfig
from src.mmb_layer0.utils.crypto.signer import SignerFactory
from src.mmb_layer0.utils.hash import HashUtils
from rich import print
from src.mmb_layer0.blockchain.core.block import Block

class Validator:
    @staticmethod
    def onchain_validate(tx: Transaction, signature: bytes, publicKey: PublicKey) -> bool:
        if not HashUtils.ecdsa_verify(tx.to_string(), signature, publicKey):
            print("validator.py:onchain_validate: Transaction signature is invalid")
            # raise Exception("Transaction signature is invalid")
            return False

        if not SignerFactory().get_signer().address(publicKey) == tx.sender and tx.Txtype != "mintburn":
            print("validator.py:onchain_validate: Transaction sender is invalid")
            # raise Exception("Transaction sender is invalid")
            return False

        tx.signature = signature
        tx.publicKey = publicKey

        return True


    @staticmethod
    def offchain_validate(tx: Transaction, worldState: WorldState) -> bool:
        if tx.gasPrice < MMBConfig.MinimumGasPrice:
            print("Validator.py:offchain_validate: Transaction gasPrice is below minimum")
            return False

        if worldState.get_eoa(tx.sender).balance < tx.gasPrice and tx.Txtype != "mintburn":
            print("Validator.py:offchain_validate: Transaction sender does not have enough balance")
            return False

        # if tx.nonce != worldState.get_eoa(tx.sender).nonce + 1 and tx.Txtype != "mintburn":
        #     print("Validator.py:offchain_validate: Transaction nonce is not valid")
        #     print(tx)
        #     print(worldState.get_eoa(tx.sender))
        #     return False

        return True

    @staticmethod
    def preblock_validate(mempool: list[Transaction]) -> bool:
        pre_nonce_check = {}
        for tx in mempool:
            if tx.Txtype == "mintburn":
                # privileged transaction
                continue
            if not SignerFactory().get_signer().verify(tx.to_string(), tx.signature, tx.publicKey):
                print("chain.py:process_block: Transaction signature is invalid")
                return False

            if not SignerFactory().get_signer().address(tx.publicKey) == tx.sender:
                print("chain.py:process_block: Transaction sender is invalid")
                return False

            if tx.sender in pre_nonce_check and tx.nonce != pre_nonce_check[tx.sender] + 1:
                print("chain.py:process_block: Transaction nonce is not valid")
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
