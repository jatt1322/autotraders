import streamlit as st
import pandas as pd
import os
import io
import time
from datetime import datetime, date
from exchange.simulated_exchange import SimulatedExchange

st.set_page_config(page_title="Autotraders — Trades Viewer", layout="wide")
st.title("Autotraders — Trades & Account Viewer")

TRADES_PATH = "logs/trades.csv"

# Initialize exchange and read state
ex = SimulatedExchange()

# Sidebar controls
st.sidebar.header("Controls")
auto_refresh = st.sidebar.checkbox("Auto-refresh (5s)", value=False)
rows_per_page = st.sidebar.number_input("Rows per page", min_value=10, max_value=5000, value=200, step=10)
show_only_trades = st.sidebar.checkbox("Show only rows with position changes", value=False)

st.sidebar.markdown("---")
st.sidebar.header("Account")
st.sidebar.write(f"Cash: ${ex.get_cash():,.2f}")
positions = ex.get_positions()
for sym, units in positions.items():
    st.sidebar.write(f"{sym}: {units}")

st.sidebar.markdown("---")
if st.sidebar.button("Refresh now"):
    st.experimental_rerun()

# Main layout
col1, col2 = st.columns([3, 1])

with col1:
    st.header("Trades Log")

    if not os.path.exists(TRADES_PATH):
        st.info("No trades log found at logs/trades.csv. Run the simulator (run_loop.py) to generate trades.")
    else:
        # Load trades
        try:
            df = pd.read_csv(TRADES_PATH, parse_dates=["timestamp"])
        except Exception as e:
            st.error(f"Failed to read trades CSV: {e}")
            df = None

        if df is not None and not df.empty:
            # Ensure timestamp dtype
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            else:
                # create a synthetic timestamp index if missing
                df['timestamp'] = pd.to_datetime(df.index, unit='s')

            # derive useful columns
            if 'nav' in df.columns:
                df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
                df['pnl'] = df['nav'].diff().fillna(0.0)
            else:
                df['pnl'] = pd.to_numeric(df.get('reward', 0.0))

            # Filters: date range
            min_date = df['timestamp'].min().date()
            max_date = df['timestamp'].max().date()
            start_date, end_date = st.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
            # ensure single date selection becomes tuple
            if isinstance(start_date, date) and isinstance(end_date, date):
                start_dt = datetime.combine(start_date, datetime.min.time())
                end_dt = datetime.combine(end_date, datetime.max.time())
            else:
                start_dt = df['timestamp'].min()
                end_dt = df['timestamp'].max()

            filtered = df[(df['timestamp'] >= start_dt) & (df['timestamp'] <= end_dt)].copy()

            # Optional: show only rows where position changed compared to previous row
            if show_only_trades and 'position' in filtered.columns:
                filtered['position'] = pd.to_numeric(filtered['position'], errors='coerce').fillna(0.0)
                filtered['position_prev'] = filtered['position'].shift(1).fillna(filtered['position'])
                filtered = filtered[filtered['position'] != filtered['position_prev']].copy()
                filtered.drop(columns=['position_prev'], inplace=True)

            # Quick metrics
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            with metrics_col1:
                if 'nav' in filtered.columns:
                    first_nav = filtered['nav'].iloc[0]
                    last_nav = filtered['nav'].iloc[-1]
                    total_return = (last_nav / first_nav - 1.0) if first_nav != 0 else 0.0
                    st.metric("Total return (selected)", f"{total_return:.2%}")
                else:
                    st.metric("Rows (selected)", f"{len(filtered)}")
            with metrics_col2:
                avg_pnl = filtered['pnl'].mean()
                st.metric("Avg PnL per step", f"{avg_pnl:.4f}")
            with metrics_col3:
                trades_count = len(filtered)
                st.metric("Rows (selected)", f"{trades_count}")

            # Charts
            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                if 'nav' in filtered.columns:
                    nav_series = filtered[['timestamp', 'nav']].set_index('timestamp').sort_index()
                    st.line_chart(nav_series)
                else:
                    st.info("NAV column not found; run simulation to produce nav values.")
            with chart_col2:
                if 'pnl' in filtered.columns:
                    pnl_series = filtered[['timestamp', 'pnl']].set_index('timestamp').sort_index()
                    st.bar_chart(pnl_series.tail(200))

            # Table with pagination
            total_rows = len(filtered)
            page = st.number_input("Page", min_value=1, max_value=max(1, (total_rows - 1) // rows_per_page + 1), value=1)
            start_idx = (page - 1) * rows_per_page
            end_idx = start_idx + rows_per_page
            page_df = filtered.iloc[start_idx:end_idx]

            st.markdown(f"Showing rows {start_idx + 1} — {min(end_idx, total_rows)} of {total_rows}")
            st.dataframe(page_df.reset_index(drop=True))

            # Download filtered data
            csv = filtered.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download filtered CSV", data=csv, file_name="trades_filtered.csv", mime='text/csv')

            # Select a trade to view details
            st.markdown("---")
            st.subheader("Inspect a trade")
            idx_options = list(filtered.index.astype(str))
            if idx_options:
                selected = st.selectbox("Select trade index", options=idx_options)
                sel_idx = int(selected)
                sel_row = filtered.loc[sel_idx]
                st.json(sel_row.to_dict())
            else:
                st.info("No trades in selection to inspect.")

        else:
            st.info("Trades CSV is empty or failed to parse.")

with col2:
    st.header("Account & Controls")
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

    st.markdown("---")
    st.write("Streamlit last refresh:")
    st.write(datetime.now().isoformat())

# Auto-refresh handling
if auto_refresh:
    time.sleep(5)
    st.experimental_rerun()
