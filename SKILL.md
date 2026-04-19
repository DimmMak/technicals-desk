---
name: technicals-desk
domain: fund
version: 0.1.0
role: Technical Analyst
description: >
  Live technical-indicator single source of truth for Blue Hill Capital. Third
  leg of the data-layer triangle (after price-desk + fundamentals-desk).
  Computes indicators deterministically from yfinance 1-year OHLCV history.
  Replaces web-search-sourced technicals which were frequently stale.
  Commands: .technicals | .technicals TICKER | .technicals watchlist | .technicals log
  NOT for: prices (use price-desk).
  NOT for: fundamentals (use fundamentals-desk).
  NOT for: committee analysis (use .rumble).
capabilities:
  reads:
    - "yfinance API (1y OHLCV history)"
  writes:
    - "technicals-desk/data/technicals-log.jsonl"
  calls: []
  cannot:
    - "write outside own data folder"
    - "modify other skills"
    - "cite web-sourced technicals"
---

# Technicals Desk — The Technical Analyst

Computes technical indicators directly from yfinance daily OHLCV data. No web search. No stale numbers.

## 🎯 COMMANDS

- `.technicals TICKER [TICKER2 ...]` — pull technical snapshot(s)
- `.technicals watchlist` — full watchlist
- `.technicals log [N]` — recent pulls
- `.technicals` — menu

## 📊 WHAT IT COMPUTES

**Moving averages:** 50, 100, 200-day · above/below flags · golden/death cross
**Momentum:** RSI(14), ADX(14), ATR(14)
**52-week range:** high, low, % from each
**Volume:** today vs 30-day average, % deviation
**Fibonacci retracements:** from 52-week high to low (0, 23.6, 38.2, 50, 61.8, 100)

All deterministic. All timestamped. All logged.

## 🚨 THE INVIOLABLE RULE

**No rumble cites a technical level (MA, RSI, ADX, Fib) without calling technicals-desk first.** Kills the stale-web-data bug for technicals, as price-desk killed it for prices.

## 🏛️ INTEGRATION

```
royal-rumble → parent calls technicals-desk → injects into subagent prompt
             → Trend Follower, Simons, Druckenmiller legends get clean inputs
journalist   → pulls technicals before citing any chart level
chief-of-staff → .chief watchlist already combines price + fundamentals;
                 next version adds technicals row

Web search demoted to qualitative only (news, sector story, narrative).
```

## 🎭 HONEST LIMITATIONS

```
✅ Daily EOD indicators (50DMA, 200DMA, RSI etc) — perfect
✅ 52-week range — perfect
✅ Volume analysis — accurate
❌ Intraday indicators — we only pull daily bars
❌ Options-specific technicals (IV skew, max pain) — that's vol-desk territory
```

For swing/position trading, daily indicators are the right tool.

## If no command given

Run `python3 ~/.claude/skills/technicals-desk/scripts/technicals.py` — the script shows the menu.
