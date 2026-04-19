# 📈 Technicals Desk

> Technical Analyst for Blue Hill Capital. Third data-layer brick after price-desk + fundamentals-desk.

Computes technical indicators directly from yfinance daily OHLCV — zero web-search dependency.

## What it pulls

```
Moving averages:     50, 100, 200-day + above/below + golden/death cross
Momentum:            RSI(14), ADX(14), ATR(14)
52-week range:       high, low, % from each
Volume:              today vs 30-day avg, % deviation
Fibonacci:           0 / 23.6 / 38.2 / 50 / 61.8 / 100 levels
```

## Commands

```
.technicals              → menu
.technicals NVDA         → full indicator snapshot
.technicals NVDA AMD MU  → batch
.technicals watchlist    → every watchlist ticker
.technicals log [N]      → recent pulls
```

## Install

```bash
./scripts/install.sh
```

Requires: `python3` + `yfinance` + `pandas` (auto-installed).

## Why this exists

yesterday's NOW rumble cited 200DMA at $110. Live today: **$155.25** (41% error). Web search returned stale chart data. technicals-desk pulls direct from yfinance daily bars — reliable, deterministic, auditable.

🃏⚔️
