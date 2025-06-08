class NodeEvent:
    def __init__(self, eventType, data, origin) -> None:
        self.eventType = eventType
        self.data = data
        self.origin = origin