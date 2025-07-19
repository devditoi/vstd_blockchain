from layer0.utils.logging_config import get_logger

logger = get_logger(__name__)

class StorageConstructor:
    def __init__(self, storage = None):
        self.storages: dict[str, "Storage"] = {}
        
        self.get("default") # Create default storage
        
        if storage:
            self.import_(storage)
        
    def get(self, name: str) -> "Storage":
        if name in self.storages:
            return self.storages[name]
        
        storage = Storage(self)
        self.storages[name] = storage
        
        return storage
    
    def event(self, name: str, data):
        # Log
        logger.debug(f"Event: {name}")
        logger.debug(data)
    
    def export(self):
        storage = {}
        for name, storage in self.storages.items():
            storage[name] = storage.data
            
        return storage
    
    def import_(self, storage):
        # Clear the storage
        self.storages = {}
        for name, data in storage.items():
            self.storages[name].data = data
        
class Storage:
    def __init__(self, parent: "StorageConstructor"):
        self.data = {}
        self.parent = parent
    
    def get(self, key):
        # Log
        self.parent.event("get", {"key": key})
        return self.data[key]
    
    def set(self, key, value):
        # State change
        self.parent.event("set", {"key": key, "value": value})
        self.data[key] = value
        
    def delete(self, key):
        # State change
        del self.data[key]

class CentralStorageConstructor:
    def __init__(self):
        self.storage_constructors: dict[str, StorageConstructor] = {}
        
    def get(self, contract_address: str) -> StorageConstructor:
        if contract_address in contract_address:
            return self.storage_constructors[contract_address]
        
        storage_constructor = StorageConstructor()
        self.storage_constructors[contract_address] = storage_constructor
        
        return storage_constructor