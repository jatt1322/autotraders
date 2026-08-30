Autotraders - minimal autonomous trading agent

This repository contains a minimal, working prototype of a continuously-learning trading agent that runs in paper/simulated mode by default.

Quick start (recommended):

1. Clone and install

    git clone https://github.com/jatt1322/autotraders.git
    cd autotraders
    python -m venv venv
    source venv/bin/activate   # Windows: venv\Scripts\activate
    pip install -r requirements.txt

2. Train an initial model (offline, historical data)

    python train.py --ticker AAPL --start 2016-01-01 --end 2021-01-01 --timesteps 50000 --out models/ppo_latest.zip

3. Run the simulation + online fine-tune loop (paper mode)

    python run_loop.py --model models/ppo_latest.zip --ticker AAPL --start 2021-01-01 --end 2022-01-01

   This will simulate streaming through the historical period, log steps to logs/trades.csv, and perform conservative fine-tuning every N steps.

4. Evaluate/backtest

    python backtest.py --model models/ppo_latest.zip --ticker AAPL --start 2022-01-01 --end 2023-01-01

Notes & safety
- This is a research/demo scaffold. Do NOT run with real funds until you've extensively backtested and paper-traded.
- Default mode is paper/simulated; no real exchange orders are placed.
- The online fine-tuning is intentionally conservative. If you plan to use live funds, add strict risk limits and human review.

What to improve
- More realistic execution with slippage/order book modelling
- Use a better feature set (technical indicators, returns, volatility, volume profile)
- Robust replay store (SQLite or Parquet), validation set, and model selection
- Use ensembles or conservative acceptance tests before deploying updated checkpoints

If you want, I can add a Streamlit dashboard to visualize logs and model checkpoints.
