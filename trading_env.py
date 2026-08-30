# Minimal Gym trading environment
import gym
from gym import spaces
import numpy as np
import pandas as pd

class TradingEnv(gym.Env):
    """
    Simple single-asset trading environment.
    Observation: window of closes + position + cash_norm
    Action: continuous in [-1,1] meaning target position as fraction of max_position
    Reward: change in portfolio value (NAV) between steps
    """
    metadata = {"render.modes": ["human"]}

    def __init__(self, df: pd.DataFrame, window_size=20, initial_cash=10000.0, max_position=1.0, transaction_cost_pct=0.001):
        super().__init__()
        self.df = df.reset_index(drop=True)
        self.window_size = int(window_size)
        self.initial_cash = float(initial_cash)
        self.max_position = float(max_position)
        self.transaction_cost_pct = float(transaction_cost_pct)

        # continuous action: target position fraction [-1,1]
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(1,), dtype=np.float32)
        # observation: window_size closes normalized + position + cash_norm
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(self.window_size + 2,), dtype=np.float32)

        self._reset_state()

    def _reset_state(self):
        # start at a random point that has enough history
        self.current_step = self.window_size
        self.position = 0.0  # units held
        self.cash = float(self.initial_cash)
        self.done = False

    def reset(self):
        self._reset_state()
        return self._get_obs()

    def _get_obs(self):
        start = self.current_step - self.window_size
        window = self.df.loc[start:self.current_step - 1, 'Close'].values
        # normalize prices by dividing by the first in window
        norm = window / (window[0] + 1e-9) - 1.0
        pos = np.array([self.position / (self.max_position + 1e-9)])
        cash_norm = np.array([self.cash / (self.initial_cash * 10.0)])
        return np.concatenate([norm.astype(np.float32), pos.astype(np.float32), cash_norm.astype(np.float32)])

    def step(self, action):
        if self.done:
            return self._get_obs(), 0.0, True, {}

        # clamp action to [-1,1]
        target_frac = float(np.clip(action[0], -1.0, 1.0))
        price = float(self.df.loc[self.current_step, 'Close'])

        prev_nav = self._nav(price)

        # compute target position in units
        target_units = target_frac * self.max_position
        trade_units = target_units - self.position

        # transaction cost
        cost = abs(trade_units) * price * self.transaction_cost_pct

        # execute trade
        self.cash -= trade_units * price + cost
        self.position = target_units

        # advance
        self.current_step += 1
        if self.current_step >= len(self.df):
            self.done = True
            self.current_step = len(self.df) - 1

        new_price = float(self.df.loc[self.current_step, 'Close'])
        curr_nav = self._nav(new_price)

        reward = curr_nav - prev_nav

        # safety: if cash extremely negative, end
        if self.cash < -1e9:
            self.done = True
            reward -= 1000

        obs = self._get_obs()
        info = {"nav": curr_nav, "price": new_price}
        return obs, float(reward), self.done, info

    def _nav(self, price):
        return self.cash + self.position * price

    def render(self, mode='human'):
        price = float(self.df.loc[self.current_step, 'Close'])
        print(f"Step: {self.current_step}, Price: {price:.2f}, Position: {self.position:.4f}, Cash: {self.cash:.2f}, NAV: {self._nav(price):.2f}")
