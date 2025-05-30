import os
import sys
import time

from rich import print
from mmb_layer0.config import MMBConfig
from mmb_layer0.node import Node
from mmb_layer0.wallet import Wallet
import rsa

node = Node()
node.debug()
node2 = Node()
node2.sync(node.to_json())
node.subscribe(node2)
w1 = Wallet(node)

# w2 = Wallet(node)

# print(w1.get_balance())
# print(w1.address)


privateK = rsa.PrivateKey.load_pkcs1(open("private_key.pem", "rb").read())
# # print(privateK)
node.mint(w1.address, privateK)
# node.mint(w1.address, privateK)
# print(f"W1 balance: {w1.get_balance()}")
# # print(w2.address)
# for i in range(10):
#     w1.pay(1 * MMBConfig.NativeTokenValue, w2.address)
# print(w1.get_balance())
# node.debug()
# # time.sleep(3)
#

#
# print("node.py:main: Check sync status with node 2")
# if node.check_sync(node2.to_json()):
#     print("node.py:main: Already synced with node 2")
# else:
#     print("node.py:main: Failed to sync with node 2")