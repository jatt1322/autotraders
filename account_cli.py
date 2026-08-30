import argparse
from exchange.simulated_exchange import SimulatedExchange


def print_status(ex: SimulatedExchange, price: float = None):
    cash = ex.get_cash()
    positions = ex.get_positions()
    balance = ex.get_balance(price=price)
    print("Account status:")
    print(f"  Cash: {cash:.2f}")
    print(f"  Positions: {positions}")
    if price is not None:
        print(f"  NAV (using price={price}): {balance:.2f}")
    else:
        print(f"  Approx NAV (price unknown): {balance:.2f}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Account CLI: check status, deposit, withdraw (simulated)')
    parser.add_argument('--status', action='store_true', help='Print account status')
    parser.add_argument('--deposit', type=float, help='Deposit amount to account')
    parser.add_argument('--withdraw', type=float, help='Withdraw amount from account')
    parser.add_argument('--price', type=float, default=None, help='Optional price to compute NAV')

    args = parser.parse_args()
    ex = SimulatedExchange()

    if args.deposit is not None:
        try:
            res = ex.deposit(args.deposit)
            print(f"Deposited {args.deposit:.2f}. New cash: {res['cash']:.2f}")
        except Exception as e:
            print("Deposit failed:", e)

    if args.withdraw is not None:
        try:
            res = ex.withdraw(args.withdraw)
            print(f"Withdrew {args.withdraw:.2f}. New cash: {res['cash']:.2f}")
        except Exception as e:
            print("Withdraw failed:", e)

    if args.status or (args.deposit is None and args.withdraw is None):
        print_status(ex, price=args.price)
