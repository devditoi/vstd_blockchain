from src.mmb_layer0.config import MMBConfig
from src.mmb_layer0.node import Node
from src.mmb_layer0.node_sync_services import NodeSyncServices
from src.mmb_layer0.utils.crypto.signer import SignerFactory
from src.mmb_layer0.utils.serializer import NodeSerializer
from src.mmb_layer0.wallet.wallet import Wallet
import rsa
from rich import print
import time


# Test 1
# node = Node()
# node.debug()
# node2 = Node()
# # node2.sync(NodeSerializer.to_json(node))
# node.subscribe(node2)
# w1 = Wallet(node)
# privateK = rsa.PrivateKey.load_pkcs1(open("private_key.pem", "rb").read())
# # # # print(privateK)
# node.mint(w1.address, privateK)
# node.mint(w1.address, privateK)
#
# print(NodeSyncServices.check_sync(node2, node))
# node.debug()
# node2.debug()


# Test 2
node = Node()
node.debug()

leader = Node()
leader.import_key("validator_key")

node.subscribe(leader) # and backwards

wallet = Wallet(node)
wallet2 = Wallet(leader)
pmint_key, mint_key = SignerFactory().get_signer().load("mint_key")
node.mint(wallet.address, mint_key, pmint_key)

node.debug()
leader.debug()

i = 0
# Leader block creation in the background
while i < 15:
    time.sleep(2)
    # NodeSyncServices.check_sync(node, leader)
    if wallet.get_balance() > int(0.01 * MMBConfig.NativeTokenValue):
        wallet.pay(int(0.01 * MMBConfig.NativeTokenValue), wallet2.address)
    print(wallet2.get_balance())
    i += 1

node.debug()
leader.debug()
print(wallet.get_balance())
print(wallet2.get_balance())
