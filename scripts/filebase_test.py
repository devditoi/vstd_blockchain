from mmb_layer0.blockchain.chain.saver_impl.filebase_saver import FilebaseSaver, FilebaseDatabase
from mmb_layer0.node.node import Node
from mmb_layer0.wallet.wallet import Wallet
from mmb_layer0.blockchain.core.block import Block

saver = FilebaseSaver(FilebaseDatabase())

node = Node(True)

wallet = Wallet(node)

tx, sign = wallet.create_tx(100, "0x1234")

block = Block(0, 0, 0, node.worldState.get_hash(), [tx])

saver.add_block(block)
