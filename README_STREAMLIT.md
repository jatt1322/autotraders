## Streamlit Dashboard

A small Streamlit dashboard to inspect the simulated account, deposit/withdraw funds, and view recent logged steps and NAV curve.

Run locally:

1. Activate your virtual environment (see README).
2. Install streamlit (if not already):
   pip install -r requirements.txt
   pip install -r requirements-additional.txt

3. Start the dashboard:
   streamlit run streamlit_app.py

Notes:
- The dashboard reads/writes the same simulated exchange state file at data/exchange_state.json.
- The NAV/plot uses logs/trades.csv produced by run_loop.py.
- If you deposit/withdraw using the dashboard, the run-loop (if running simultaneously) will see the updated state (no concurrency locking implemented).
