# client/overlay/state_manager.py
import threading
from typing import Optional, List, Dict, Any
from PySide6 import QtCore

class StateSignals(QtCore.QObject):
    # Qt signals to communicate with UI
    token_changed = QtCore.Signal(str)
    contracts_updated = QtCore.Signal(list)  # emits list of contract dicts
    contract_updated = QtCore.Signal(dict)   # emits single contract dict
    ws_message = QtCore.Signal(dict)

class StateManager:
    def __init__(self):
        self._lock = threading.RLock()
        self._jwt_token: Optional[str] = None
        self.contracts: List[Dict[str, Any]] = []
        self.signals = StateSignals()

    def set_token(self, token: str):
        with self._lock:
            self._jwt_token = token
        self.signals.token_changed.emit(token)

    def get_token(self) -> Optional[str]:
        with self._lock:
            return self._jwt_token

    def set_contracts(self, contracts: List[Dict]):
        with self._lock:
            self.contracts = contracts
        self.signals.contracts_updated.emit(contracts)

    def update_contract(self, contract: Dict):
        with self._lock:
            # replace or append
            found = False
            for i, c in enumerate(self.contracts):
                if c.get("id") == contract.get("id"):
                    self.contracts[i] = contract
                    found = True
                    break
            if not found:
                self.contracts.append(contract)
        self.signals.contract_updated.emit(contract)

    def get_contracts(self) -> List[Dict]:
        with self._lock:
            return list(self.contracts)

# Singleton instance to import
state = StateManager()
