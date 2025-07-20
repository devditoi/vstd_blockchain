from layer0.node.node import Node

validator = Node()
validator.log_state()
validator.export_key("mint_key")

leader = Node()
leader.log_state()
leader.export_key("validator_key")