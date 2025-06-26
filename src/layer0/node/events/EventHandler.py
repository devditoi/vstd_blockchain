from abc import abstractmethod, ABC
import typing
if typing.TYPE_CHECKING:
    from ..node_event_handler import NodeEventHandler
from layer0.node.events.node_event import NodeEvent
from layer0.utils.network_utils import is_valid_origin


class EventHandler(ABC):
    def __init__(self, node_event_handler: "NodeEventHandler"):
        self.neh = node_event_handler # Neh :)

    @staticmethod
    @abstractmethod
    def event_name() -> str:
        return "not_implemented"

    @abstractmethod
    def handle(self, event: "NodeEvent") -> bool:
        return False

    @staticmethod
    @abstractmethod
    def require_field(self) -> list[str]:
        return ""

class EventFactory:
    def __init__(self) -> None:
        self.handlers : dict[str, EventHandler] = {}

    def register_event(self, handler: EventHandler):
        self.handlers[handler.event_name()] = handler

    def handle(self, event: "NodeEvent") -> bool:
        handler = self.handlers.get(event.eventType)

        if handler:
            if not is_valid_origin(event.origin):
                print("[EventFactory] Invalid origin:", event.origin)
                return False

            if len(handler.require_field()) > 0:
                if any([k not in event.data for k in handler.require_field()]):
                    print("[EventFactory] Not enough data for event type:", event.eventType)
                    # Find the missing field
                    for k in handler.require_field():
                        if k not in event.data:
                            print("[EventFactory] Missing field:", k)
                        else:
                            print("[EventFactory] Found field:", k, " with value:", event.data[k])
                    return False # Not enough data
            return handler.handle(event)

        print(f"No handler registered for event type: {event.eventType}")
        return False
