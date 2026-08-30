import streamlit as st
import pandas as pd
import os
from exchange.simulated_exchange import SimulatedExchange

st.set_page_config(page_title="Autotraders Dashboard", layout="wide")
st.title("Autotraders — Simulated Account Dashboard")

# Initialize exchange
ex = SimulatedExchange()

col1, col2 = st.columns([2, 3])

with col1:
    st.header("Account Status")
    price_input = st.number_input("Optional current price (for NAV)", value=0.0, step=0.01, format="%.2f")
    cash = ex.get_cash()
    positions = ex.get_positions()
    nav = ex.get_balance(price=price_input if price_input > 0 else None)

    st.metric("Cash", f"${cash:,.2f}")
    st.metric("NAV (approx)", f"${nav:,.2f}")
    st.write("Positions:")
    st.json(positions)

    st.markdown("---")
    st.header("Deposit / Withdraw")
    deposit_amt = st.number_input("Deposit amount", min_value=0.0, value=0.0, step=1.0, format="%.2f")
    if st.button("Deposit"):
        try:
            ex.deposit(deposit_amt)
            st.success(f"Deposited ${deposit_amt:.2f}")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Deposit failed: {e}")

    withdraw_amt = st.number_input("Withdraw amount", min_value=0.0, value=0.0, step=1.0, format="%.2f")
    if st.button("Withdraw"):
        try:
            ex.withdraw(withdraw_amt)
            st.success(f"Withdrew ${withdraw_amt:.2f}")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Withdraw failed: {e}")

with col2:
    st.header("Recent Trades & NAV")
    trades_path = "logs/trades.csv"
    if os.path.exists(trades_path):
        df = pd.read_csv(trades_path, parse_dates=["timestamp"])
        st.write(f"Loaded {len(df)} logged steps/trades from {trades_path}")
        st.dataframe(df.tail(50))

        if "nav" in df.columns:
            df_nav = df[['timestamp', 'nav']].dropna()
            df_nav = df_nav.drop_duplicates(subset=['timestamp'])
            df_nav = df_nav.set_index('timestamp').sort_index()
            st.line_chart(df_nav)
        else:
            st.info("No NAV column found in logs; run the simulation to generate logs/trades.csv")
    else:
        st.info("No trades/logs found (logs/trades.csv). Run run_loop.py to generate simulated trades.")

st.markdown("---")
st.write("This dashboard connects to the local simulated exchange (data/exchange_state.json). Use the Deposit/Withdraw controls to change the cash balance. The NAV plot is built from logs/trades.csv created by the simulation run loop.")
