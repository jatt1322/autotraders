import argparse
import pandas as pd
import numpy as np
from trading_env import TradingEnv
from stable_baselines3 import PPO


def load_data(ticker, start, end):
    import yfinance as yf
    df = yf.download(ticker, start=start, end=end, progress=False)
    return df[['Open','High','Low','Close','Volume']].copy()


def evaluate(model_path, ticker, start, end):
    df = load_data(ticker, start, end)
    env = TradingEnv(df)
    model = PPO.load(model_path, env=env)

    obs = env.reset()
    navs = [env._nav(float(df.loc[env.current_step, 'Close']))]

    done = False
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action)
        navs.append(info.get('nav', navs[-1]))

    returns = np.array(navs) / navs[0] - 1.0
    total_return = returns[-1]
    peak = np.maximum.accumulate(navs)
    drawdown = (peak - navs) / peak
    max_dd = drawdown.max()

    print(f"Total return: {total_return:.4f}, Max drawdown: {max_dd:.4f}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='models/ppo_latest.zip')
    parser.add_argument('--ticker', default='AAPL')
    parser.add_argument('--start', default='2022-01-01')
    parser.add_argument('--end', default='2023-01-01')
    args = parser.parse_args()

    evaluate(args.model, args.ticker, args.start, args.end)
