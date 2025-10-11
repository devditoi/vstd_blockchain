from dataclasses import dataclass
import jsonlight
import json
import copy
from typing import Any
from layer0.utils.hash import HashUtils


# This is a single unit of the world state that only contains the data
@dataclass
class EOA:
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
    #     return f"EOA(address={self.address}, balance={self.balance}, nonce={self.nonce})"

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
    __eoas: dict[str, EOA]
    __smartContracts: dict[str, SmartContract]
    __validator: list[str]

    def __init__(self):
        self.__eoas = {}
        self.__smartContracts = {}
        self.__validator = []
        
    def add_validator(self, validator: str):
        self.__validator.append(validator)
        
    def get_validators(self) -> list[str]:
        return self.__validator

    def set_eoa_and_smart_contract(self, eoas: dict[str, EOA], smartContracts: dict[str, SmartContract]):
        # Create deep copies of the EOA and SmartContract objects to ensure encapsulation
        self.__eoas = copy.deepcopy(eoas)
        self.__smartContracts = copy.deepcopy(smartContracts)

    def __str__(self) -> str:
        return f"WorldState(eoas={self.__eoas}, smartContracts={self.__smartContracts})"

    def get_eoa(self, address: str) -> EOA:
        if address not in self.__eoas:
            self.__eoas[address] = EOA(address, 0, 0)
        return self.__eoas[address]

    def set_eoa(self, address: str, eoa: EOA):
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
        data: Any = json.loads(json_string)
        eoas_data = json.loads(data["eoas"])
        smart_contracts_data = json.loads(data["smartContracts"])
        
        # Reconstruct EOA objects from JSON data
        self.__eoas = {}
        for address, eoa_data in eoas_data.items():
            self.__eoas[address] = EOA(
                address=eoa_data["address"],
                balance=eoa_data["balance"],
                nonce=eoa_data["nonce"]
            )
        
        # Reconstruct SmartContract objects from JSON data
        self.__smartContracts = {}
        for address, sc_data in smart_contracts_data.items():
            self.__smartContracts[address] = SmartContract(
                address=sc_data["address"],
                balance=sc_data["balance"],
                nonce=sc_data["nonce"],
                codeHash=sc_data["codeHash"],
                storage=sc_data["storage"]
            )
        
        print("worldstate.py:build_worldstate: built worldstate")

    def get_eoa_full(self):
        return copy.deepcopy(self.__eoas)

    def get_smart_contract_full(self):
        return copy.deepcopy(self.__smartContracts)

    def get_hash(self):
        return HashUtils.sha256(self.to_json())

    def clone(self):
        copy = WorldState()
        copy.set_eoa_and_smart_contract(self.get_eoa_full(), self.get_smart_contract_full())
        # Copy validators as well
        copy.__validator = copy.deepcopy(self.__validator)
        return copy
