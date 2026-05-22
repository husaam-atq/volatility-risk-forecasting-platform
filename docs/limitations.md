# Limitations

## Free/Public Data

Free public data can have missing values, adjusted-close revisions, delayed updates and occasional ticker-specific issues. The downloader caches raw files so data changes are visible.

## Daily Data

Daily bars miss intraday volatility, overnight liquidity shocks and execution constraints. Intraday realised volatility would improve the target proxy.

## Model Risk

Volatility models can perform well in one regime and poorly in another. The platform reports asset-level metrics to avoid hiding weak segments.

## GARCH Instability

GARCH-family calibration can fail or produce near-integrated parameters during stressed samples. The wrapper handles failures and records challenger models rather than stopping the full pipeline.

## Machine-Learning Overfitting

Tree models can overfit historical stress patterns. The split design and validation-only calibration reduce, but do not eliminate, that risk.

## VaR And ES

VaR is not a complete tail-risk measure. Expected Shortfall diagnostics help, but both measures depend on residual calibration and the representativeness of validation data.

## SQL Benchmark Hardware Dependency

Query timings depend on CPU, memory, storage, DuckDB version and cache state. Benchmark numbers should be regenerated before being quoted externally.
