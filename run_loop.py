import argparse
import os
import pandas as pd
import numpy as np
import time
from trading_env import TradingEnv
from stable_baselines3 import PPO
from utils.logging import append_trade
from exchange.simulated_exchange import SimulatedExchange

# Simple run loop that simulates streaming through historical data and fine-tunes the model after K trades


def load_data(ticker, start, end):
    import yfinance as yf
    df = yf.download(ticker, start=start, end=end, progress=False)
    if df.empty:
        raise ValueError("No data downloaded")
    return df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()


def run_simulation(model_path, ticker, start, end, out_trades='logs/trades.csv', fine_tune_every=50, fine_tune_steps=500, deposit=None, withdraw=None):
    if not os.path.exists('models'):
        os.makedirs('models')
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # init exchange simulator
    ex = SimulatedExchange()

    # optional deposit/withdraw before starting
    if deposit is not None:
        ex.deposit(deposit)
    if withdraw is not None:
        try:
            ex.withdraw(withdraw)
        except Exception as e:
            print("Withdraw failed before run:", e)

    df = load_data(ticker, start, end)
    env = TradingEnv(df)

    # sync env cash/position from exchange
    env.cash = ex.get_cash()
    env.position = ex.get_positions().get('DEFAULT', 0.0)

    model = PPO.load(model_path, env=env)

    obs = env.reset()
    trades_since_tune = 0
    step = 0

    while True:
        action, _ = model.predict(obs, deterministic=False)
        prev_nav = env._nav(float(df.loc[env.current_step, 'Close']))
        obs2, reward, done, info = env.step(action)
        new_nav = info.get('nav', prev_nav)

        # persist exchange state to follow env
        ex.state['cash'] = float(env.cash)
        ex.set_position(float(env.position), symbol='DEFAULT')

        # if a trade occurred (position changed), log it
        row = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'step': step,
            'price': float(df.loc[env.current_step, 'Close']),
            'position': env.position,
            'cash': env.cash,
            'nav': new_nav,
            'reward': reward
        }
        append_trade(out_trades, row)
        step += 1

        # simple fine-tune trigger: every N logged steps
        trades_since_tune += 1
        if trades_since_tune >= fine_tune_every:
            print(f"Fine-tuning model for {fine_tune_steps} steps using recent data...")
            # perform short fine-tune
            try:
                model.set_env(env)
                model.learn(total_timesteps=fine_tune_steps)
                timestamp = int(time.time())
                save_path = f"models/ppo_finetuned_{timestamp}.zip"
                model.save(save_path)
                print("Saved fine-tuned model to", save_path)
            except Exception as e:
                print("Fine-tune failed:", e)
            trades_since_tune = 0

        # save exchange state after each step
        ex._save()

        if done:
            print("Simulation finished after steps:", step)
            break

        obs = obs2


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='models/ppo_latest.zip')
    parser.add_argument('--ticker', default='AAPL')
    parser.add_argument('--start', default='2021-01-01')
    parser.add_argument('--end', default='2022-01-01')
    parser.add_argument('--deposit', type=float, default=None, help='Optional deposit to apply before starting')
    parser.add_argument('--withdraw', type=float, default=None, help='Optional withdraw to apply before starting')
    parser.add_argument('--fine_tune_every', type=int, default=50)
    parser.add_argument('--fine_tune_steps', type=int, default=500)
    args = parser.parse_args()

    run_simulation(args.model, args.ticker, args.start, args.end, fine_tune_every=args.fine_tune_every, fine_tune_steps=args.fine_tune_steps, deposit=args.deposit, withdraw=args.withdraw)
