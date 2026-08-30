import json
import os
from typing import Dict, Any

class SimulatedExchange:
    """A very small simulated exchange to track cash and positions persistently.

    State is stored in data/exchange_state.json so deposits/withdrawals persist across runs.
    Designed for a single-asset demo (key 'DEFAULT').
    """

    def __init__(self, state_path: str = 'data/exchange_state.json'):
        self.state_path = state_path
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
        if os.path.exists(self.state_path):
            self._load()
        else:
            self.state = {
                'cash': 10000.0,
                'positions': {'DEFAULT': 0.0},
                'meta': {}
            }
            self._save()

    def _load(self):
        with open(self.state_path, 'r') as f:
            self.state = json.load(f)

    def _save(self):
        with open(self.state_path, 'w') as f:
            json.dump(self.state, f, indent=2)

    def get_cash(self) -> float:
        return float(self.state.get('cash', 0.0))

    def get_positions(self) -> Dict[str, float]:
        return {k: float(v) for k, v in self.state.get('positions', {}).items()}

    def get_balance(self, price: float = None, symbol: str = 'DEFAULT') -> float:
        """Return NAV = cash + position * price. If price is None, only returns cash + position (assumes price=1)
        """
        cash = self.get_cash()
        pos = float(self.state.get('positions', {}).get(symbol, 0.0))
        price = 1.0 if price is None else float(price)
        return cash + pos * price

    def deposit(self, amount: float) -> Dict[str, Any]:
        amount = float(amount)
        if amount <= 0:
            raise ValueError('Deposit amount must be positive')
        self.state['cash'] = float(self.get_cash()) + amount
        self._save()
        return {'cash': self.get_cash(), 'positions': self.get_positions()}

    def withdraw(self, amount: float) -> Dict[str, Any]:
        amount = float(amount)
        if amount <= 0:
            raise ValueError('Withdraw amount must be positive')
        if amount > self.get_cash():
            raise ValueError('Insufficient cash for withdrawal')
        self.state['cash'] = float(self.get_cash()) - amount
        self._save()
        return {'cash': self.get_cash(), 'positions': self.get_positions()}

    def set_position(self, units: float, symbol: str = 'DEFAULT') -> None:
        self.state.setdefault('positions', {})
        self.state['positions'][symbol] = float(units)
        self._save()

    def adjust_position(self, delta_units: float, symbol: str = 'DEFAULT') -> None:
        self.state.setdefault('positions', {})
        cur = float(self.state['positions'].get(symbol, 0.0))
        self.state['positions'][symbol] = cur + float(delta_units)
        self._save()

    def export_state(self) -> Dict[str, Any]:
        return self.state.copy()
