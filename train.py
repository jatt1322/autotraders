import argparse
import pandas as pd
import yfinance as yf
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from trading_env import TradingEnv


def download_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end, progress=False)
    if df.empty:
        raise ValueError("No data downloaded. Check ticker/date range.")
    return df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()


def make_env(df):
    def _init():
        return TradingEnv(df)
    return DummyVecEnv([_init])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", default="AAPL")
    parser.add_argument("--start", default="2016-01-01")
    parser.add_argument("--end", default="2021-01-01")
    parser.add_argument("--timesteps", type=int, default=50000)
    parser.add_argument("--out", default="models/ppo_latest.zip")
    args = parser.parse_args()

    print("Downloading data for", args.ticker)
    df = download_data(args.ticker, args.start, args.end)
    env = make_env(df)
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=args.timesteps)
    model.save(args.out)
    print("Saved model to", args.out)


if __name__ == '__main__':
    main()
