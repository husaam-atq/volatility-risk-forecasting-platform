from __future__ import annotations

import argparse

from volatility_platform.database.build_database import build_database


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--live", action="store_true", help="Try live yfinance data instead of the included sample."
    )
    args = parser.parse_args()
    result = build_database(use_live=args.live)
    print(result)


if __name__ == "__main__":
    main()
