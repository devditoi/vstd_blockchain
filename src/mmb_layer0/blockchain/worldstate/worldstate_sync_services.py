from src.mmb_layer0.blockchain.core.worldstate import WorldState


class WorldStateSyncServices:

    @staticmethod
    def check_sync(world1: WorldState, world2: WorldState) -> bool:
        try:
            w1eoas = world1.get_eoa_full()
            w2eoas = world2.get_eoa_full()
            for eoa in w1eoas.keys():
                if w1eoas[eoa].balance != w2eoas[eoa].balance:
                    return False

            w1smartContracts = world1.get_smart_contract_full()
            w2smartContracts = world2.get_smart_contract_full()
            for smartContract in w1smartContracts.keys():
                if w1smartContracts[smartContract].balance != w2smartContracts[smartContract].balance:
                    return False
        except Exception as e:
            print(e)
            return False
        return True

    @staticmethod
    def merge_worldstates(world1: WorldState, world2: WorldState) -> WorldState:
        w1eoas = world1.get_eoa_full()
        w2eoas = world2.get_eoa_full()
        all_keys = set(w1eoas.keys()) | set(w2eoas.keys())

        # Merge
        for key in all_keys:
            if key not in w1eoas:
                w1eoas[key] = w2eoas[key]  # Add missing key to w1eoas
            elif key not in w2eoas:
                w2eoas[key] = w1eoas[key]  # Add missing key to w2eoas

        w1smartContracts = world1.get_smart_contract_full()
        w2smartContracts = world2.get_smart_contract_full()
        all_keys = set(w1smartContracts.keys()) | set(w2smartContracts.keys())

        # Merge
        for key in all_keys:
            if key not in w1smartContracts:
                w1smartContracts[key] = w2smartContracts[key]  # Add missing key to w1smartContracts
            elif key not in w2smartContracts:
                w2smartContracts[key] = w1smartContracts[key]  # Add missing key to     w2smartContracts

        return WorldState(w1eoas, w1smartContracts)
