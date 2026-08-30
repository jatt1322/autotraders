"""diagnostics.py
Run this script inside the repo (in your activated venv) to check the main components of the project.
It prints environment info, package import checks, file checks, and attempts to instantiate the env and (optionally) load a model.

Usage:
    source venv/bin/activate   # or activate your venv on Windows
    python diagnostics.py

Copy the full output and paste it back here so I can diagnose any failures.
"""

import sys
import platform
import subprocess
import json
import os
from glob import glob

PRINT_SEPARATOR = '=' * 80


def run_cmd(cmd):
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        return out.strip()
    except Exception as e:
        return f"ERROR running '{cmd}': {e}"


def check_import(pkg, attr=None):
    try:
        m = __import__(pkg)
        version = getattr(m, '__version__', None)
        if attr:
            val = getattr(m, attr)
            return True, f"import OK, version={version}, {attr}={val}"
        return True, f"import OK, version={version}"
    except Exception as e:
        return False, str(e)


def print_section(title):
    print('\n' + PRINT_SEPARATOR)
    print(title)
    print(PRINT_SEPARATOR)


def main():
    print_section('System')
    print('Python executable:', sys.executable)
    print('Python version:', sys.version.replace('\n', ' '))
    print('Platform:', platform.platform())

    print_section('Streamlit / CLI')
    print('streamlit --version ->')
    print(run_cmd('streamlit --version'))
    print('\nwhich streamlit ->')
    print(run_cmd('which streamlit' if os.name != 'nt' else 'where streamlit'))

    print_section('Key package import checks')
    pkgs = ['torch', 'stable_baselines3', 'gym', 'pandas', 'yfinance', 'streamlit', 'numpy']
    for p in pkgs:
        ok, msg = check_import(p)
        print(f"{p}: {ok} - {msg}")

    print_section('Project files')
    print('Repo root:', os.getcwd())
    print('models/*.zip ->')
    for f in glob('models/*.zip'):
        print('  ', f)
    print('logs/trades.csv exists:', os.path.exists('logs/trades.csv'))
    if os.path.exists('logs/trades.csv'):
        print('\nFirst 10 lines of logs/trades.csv:')
        try:
            with open('logs/trades.csv','r', encoding='utf-8') as fh:
                for i, line in enumerate(fh):
                    print(line.strip())
                    if i >= 9:
                        break
        except Exception as e:
            print('  Error reading logs/trades.csv:', e)

    print('\nData exchange state file: data/exchange_state.json exists:', os.path.exists('data/exchange_state.json'))
    if os.path.exists('data/exchange_state.json'):
        try:
            with open('data/exchange_state.json','r', encoding='utf-8') as fh:
                j = json.load(fh)
                print('  sample state:', json.dumps(j, indent=2))
        except Exception as e:
            print('  Error reading exchange_state.json:', e)

    print_section('Try to instantiate TradingEnv')
    try:
        import pandas as pd
        from trading_env import TradingEnv
        # create a tiny fake df
        pdf = pd.DataFrame({
            'Open': [100.0, 101.0, 102.0, 103.0, 104.0, 105.0],
            'High': [100.5, 101.5, 102.5, 103.5, 104.5, 105.5],
            'Low': [99.5, 100.5, 101.5, 102.5, 103.5, 104.5],
            'Close': [100.0, 101.0, 102.0, 103.0, 104.0, 105.0],
            'Volume': [10, 12, 11, 13, 14, 10]
        })
        env = TradingEnv(pdf, window_size=3)
        obs = env.reset()
        print('TradingEnv reset OK. obs shape/type:', type(obs), getattr(obs, 'shape', None))
        action = env.action_space.sample()
        obs2, reward, done, info = env.step(action)
        print('Step OK. reward=', reward, 'done=', done, 'info=', info)
    except Exception as e:
        print('Failed to create/run TradingEnv:', e)

    print_section('Try to load model with Stable-Baselines3 (if model exists)')
    model_files = glob('models/*.zip')
    if model_files:
        print('Found model files:', model_files)
        try:
            from stable_baselines3 import PPO
            mpath = model_files[0]
            print('Loading model', mpath)
            model = PPO.load(mpath)
            print('Model loaded OK (PPO).')
        except Exception as e:
            print('Failed to load model with SB3:', e)
    else:
        print('No model zip files found under models/*.zip')

    print_section('Done')

if __name__ == '__main__':
    main()
