from layer0.node.node import Node

validator = Node()
validator.debug()
validator.export_key("mint_key")

leader = Node()
leader.debug()
leader.export_key("validator_key")