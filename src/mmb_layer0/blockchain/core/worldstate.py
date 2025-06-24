from dataclasses import dataclass, field
import jsonlight
import json

from mmb_layer0.utils.hash import HashUtils


# This is a single unit of the world state that only contains the data
@dataclass
class EOAs:
    address: str
    balance: int
    nonce: int

    def __jsondump__(self):
        return {
            "address": self.address,
            "balance": self.balance,
            "nonce": self.nonce
        }
    # def __str__(self) -> str:
    #     return f"EOAs(address={self.address}, balance={self.balance}, nonce={self.nonce})"

@dataclass
class SmartContract:
    address: str
    balance: int
    nonce: int
    codeHash: str
    storage: dict

    def __jsondump__(self):
        return {
            "address": self.address,
            "balance": self.balance,
            "nonce": self.nonce,
            "codeHash": self.codeHash,
            "storage": self.storage
        }

    # def __str__(self) -> str:
    #     return f"SmartContract(address={self.address}, balance={self.balance}, nonce={self.nonce}, codeHash={self.codeHash}, storage={self.storage})"

@dataclass
class WorldState:
    __eoas: dict[str, EOAs]
    __smartContracts: dict[str, SmartContract]

    def __init__(self):
        self.__eoas = {}
        self.__smartContracts = {}

    def set_eoa_and_smart_contract(self, eoas: dict[str, EOAs], smartContracts: dict[str, SmartContract]):
        self.__eoas = eoas
        self.__smartContracts = smartContracts

    def __str__(self) -> str:
        return f"WorldState(eoas={self.__eoas}, smartContracts={self.__smartContracts})"

    def get_eoa(self, address: str) -> EOAs:
        if address not in self.__eoas:
            self.__eoas[address] = EOAs(address, 0, 0)
        return self.__eoas[address]

    def set_eoa(self, address: str, eoa: EOAs):
        self.__eoas[address] = eoa

    def get_smart_contract(self, address: str) -> SmartContract:
        if address not in self.__smartContracts:
            self.__smartContracts[address] = SmartContract(address, 0, 0, "", {})
        return self.__smartContracts[address]

    def set_smart_contract(self, address: str, smartContract: SmartContract):
        self.__smartContracts[address] = smartContract

    def to_json(self):
        return jsonlight.dumps({
            "eoas": jsonlight.dumps(self.__eoas),
            "smartContracts": jsonlight.dumps(self.__smartContracts)
        })

    def build_worldstate(self, json_string: str):
        data = json.loads(json_string)
        self.__eoas = json.loads(data["eoas"])
        self.__smartContracts = json.loads(data["smartContracts"])
        print("worldstate.py:build_worldstate: built worldstate")

    def get_eoa_full(self):
        return self.__eoas.copy()

    def get_smart_contract_full(self):
        return self.__smartContracts.copy()

    def get_hash(self):
        return HashUtils.sha256(self.to_json())

    def clone(self):
        copy = WorldState()
        copy.set_eoa_and_smart_contract(self.get_eoa_full(), self.get_smart_contract_full())
        return copy
