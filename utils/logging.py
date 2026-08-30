import os
import csv
import pandas as pd


def append_trade(path, row: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    header = ['timestamp','step','price','position','cash','nav','reward']
    file_exists = os.path.exists(path)
    with open(path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if not file_exists:
            writer.writeheader()
        writer.writerow({k: row.get(k, '') for k in header})
