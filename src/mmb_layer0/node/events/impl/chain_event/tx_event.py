from mmb_layer0.blockchain.core.transaction_type import Transaction
from mmb_layer0.blockchain.processor.transaction_processor import TransactionProcessor
from mmb_layer0.node.events.EventHandler import EventHandler
from mmb_layer0.node.node_event_handler import NodeEventHandler, NodeEvent


class TxEvent(EventHandler):
    def __init__(self, node_event_handler: "NodeEventHandler"):
        super().__init__(node_event_handler)

    @staticmethod
    def event_name() -> str:
        return "tx"

    def require_field(self):
        return ["tx", "signature", "publicKey"]

    def handle(self, event: "NodeEvent"):

        # print(event.data)
        if not isinstance(event.data["tx"], Transaction):
            event.data["tx"] = TransactionProcessor.cast_transaction(event.data["tx"])

        # if not isinstance(event.data["publicKey"], str):
        #     event.data["publicKey"] = event.data["publicKey"].hex()

        if self.neh.node.blockchain.contain_transaction(event.data["tx"]):  # Already processed
            return False

        self.neh.node.blockchain.temporary_add_to_mempool(event.data["tx"])
        print(f"{self.neh.node.address[:4]}:node.py:process_event: Processing transaction")
        # inspect(event.data["tx"])
        self.neh.node.process_tx(event.data["tx"], event.data["signature"], event.data["publicKey"])

        return True