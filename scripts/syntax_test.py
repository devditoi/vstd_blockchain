# This is just the syntax and usage of smart contract, not a smart contract itself

# First a smart contract need a storage

# Implent of the storage:

from transformers.utils.import_utils import export
from scipy._lib.decorator import __init__

class Storage:
    def __init__(self, parent: StorageConstructor):
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

class StorageConstructor:
    def __init__(self, storage = None):
        self.storages: dict[str, Storage] = {}
        
        self.get("default") # Create default storage
        
        if storage:
            self.import_(storage)
        
    def get(self, name: str) -> Storage:
        if name in self.storages:
            return self.storages[name]
        
        storage = Storage(self)
        self.storages[name] = storage
        
        return storage
    
    def event(self, name: str, data):
        # Log
        print(f"Event: {name}")
        print(data)
    
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
        
# Example (Smart contract code will import this storage as default storage)

# storage.get("key")
# storage.set("key", "value")
# storage.delete("key")

class VSTD_TOKEN: # This is the default token contract
    def __init__(self, storage: StorageConstructor, msg):
        self._msg = msg
        self.storage = storage.get("default")
        self.totalSupply = self.storage.get("total_supply")
        self.balance = storage.get("balance")
        self._allowance = storage.get("allowance")
        
        
    def name(self) -> str:
        return "VSTD"
    
    def symbol(self) -> str:
        return "VSTD"
        
    def totalSupply(self) -> int:
        return self.total_supply
    
    def allowance(self, owner, spender) -> int:
        return self._allowance.get((owner, spender))
    
    def approve(self, spender, amount):
        self._allowance.set((self._msg.sender, spender), amount)
        # self.storage.set(self._msg.sender, )
        
    def _approveFor(self, owner, spender, amount):
        self._allowance.set((owner, spender), amount)
        
    def balanceOf(self, address) -> int:
        return self.storage.get(address)
    
    def transfer(self, to_address, amount):
        if self.balanceOf(self._msg.sender) < amount:
            return False
            
        self.storage.set(self._msg.sender, self.balanceOf(self._msg.sender) - amount)
        self.storage.set(to_address, self.balanceOf(to_address) + amount)
        return True
    
    def transferFrom(self, from_address, to_address, amount):
        if self.allowance(from_address, self._msg.sender) < amount:
            return False
        
        allow = self.allowance(from_address, self._msg.sender)
        self._approveFor(from_address, self._msg.sender, allow - amount)
        self.storage.set(from_address, self.balanceOf(from_address) - amount)
        self.storage.set(to_address, self.balanceOf(to_address) + amount)
        return True