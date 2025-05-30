from mmb_layer0.node import Node
from mmb_layer0.node_sync_services import NodeSyncServices
from mmb_layer0.utils.serializer import NodeSerializer
from mmb_layer0.wallet import Wallet
import rsa
from rich import print

node = Node()
node.debug()
node2 = Node()
# node2.sync(NodeSerializer.to_json(node))

# node.subscribe(node2)
w1 = Wallet(node)
#
#
privateK = rsa.PrivateKey.load_pkcs1(open("private_key.pem", "rb").read())
# # # print(privateK)
node.mint(w1.address, privateK)
node.mint(w1.address, privateK)

print(NodeSyncServices.check_sync(node2, node))

NodeSyncServices.sync(node2, node)

print(NodeSyncServices.check_sync(node2, node))
