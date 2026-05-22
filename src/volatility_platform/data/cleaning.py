from __future__ import annotations

import pandas as pd

PRICE_COLUMNS = ["open", "high", "low", "close", "adj_close"]


def clean_prices(prices: pd.DataFrame) -> pd.DataFrame:
    data = prices.copy()
    data["date"] = pd.to_datetime(data["date"]).dt.normalize()
    data["asset"] = data["asset"].astype(str).str.upper()
    for column in PRICE_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data["volume"] = pd.to_numeric(data.get("volume", 0), errors="coerce").fillna(0).astype("int64")
    data = data.drop_duplicates(["asset", "date"], keep="last")
    data = data.dropna(subset=["asset", "date", *PRICE_COLUMNS])
    for column in PRICE_COLUMNS:
        data = data[data[column] > 0]
    data = data.sort_values(["asset", "date"]).reset_index(drop=True)
    return data[["asset", "date", "open", "high", "low", "close", "adj_close", "volume", "source"]]


def data_quality_checks(raw: pd.DataFrame, clean: pd.DataFrame) -> pd.DataFrame:
    duplicate_keys = raw.duplicated(["asset", "date"]).sum()
    missing_values = raw[PRICE_COLUMNS].isna().sum().sum()
    non_positive = (raw[PRICE_COLUMNS] <= 0).sum().sum()
    coverage = clean.groupby("asset")["date"].nunique()
    min_coverage = int(coverage.min()) if not coverage.empty else 0
    returns = clean.groupby("asset")["adj_close"].pct_change()
    extreme_returns = int((returns.abs() > 0.20).sum())
    rows = [
        (
            "missing_price_values",
            float(missing_values),
            "pass" if missing_values == 0 else "warn",
            "Null OHLC or adjusted-close values in raw data.",
        ),
        (
            "duplicate_asset_date_keys",
            float(duplicate_keys),
            "pass" if duplicate_keys == 0 else "warn",
            "Duplicate raw asset/date records before de-duplication.",
        ),
        (
            "non_positive_prices",
            float(non_positive),
            "pass" if non_positive == 0 else "fail",
            "Non-positive OHLC or adjusted-close values.",
        ),
        (
            "minimum_asset_coverage_days",
            float(min_coverage),
            "pass" if min_coverage >= 500 else "warn",
            "Minimum number of observations across assets.",
        ),
        (
            "extreme_absolute_returns_gt_20pct",
            float(extreme_returns),
            "pass" if extreme_returns <= 5 else "warn",
            "Daily absolute returns above 20%.",
        ),
        (
            "clean_price_rows",
            float(len(clean)),
            "pass" if len(clean) > 0 else "fail",
            "Rows after cleaning.",
        ),
    ]
    return pd.DataFrame(rows, columns=["check_name", "result_value", "status", "details"])
