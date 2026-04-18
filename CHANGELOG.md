# CHANGELOG — Technicals Desk

## [2026-04-18] — v0.1.0 — Initial ship

**Trigger:** User caught that royal-rumble still cited technical levels (200DMA, RSI, Fib) from web search — the last stale-data hole. Verified: yesterday's NOW rumble cited 200DMA $110, actual is $155.25 (41% error). Shipped immediately.

### Shipped
- `scripts/technicals.py` — yfinance history wrapper, full indicator computation
- `scripts/install.sh` — sync to `~/.claude/skills/technicals-desk/`
- 4 commands: menu, TICKER pull, watchlist, log
- Every pull logs to `data/technicals-log.jsonl`

### Indicators computed
- Moving averages: 50, 100, 200-day + above/below flags + golden/death cross
- Momentum: RSI(14), ADX(14), ATR(14)
- 52-week range: high, low, % from each
- Volume: today vs 30-day average, % deviation
- Fibonacci retracements: 0/23.6/38.2/50/61.8/100

### Validation — NOW on 2026-04-18
```
Current price:     $96.66
200DMA:            $155.25   (yesterday's rumble cited $110 — WRONG)
Death cross:       TRUE
RSI(14):           46.91
ADX(14):           53.52     (STRONG trend — rumble called it "weak")
52w high/low:      $211.48 / $81.24
% from 52w high:   -54.3%    (rumble cited -46% YTD — close but different timeframe)
```

### Architectural completion
With this skill, every NUMBER in a rumble comes from a clean source:

```
📊 price-desk        → current prices
📐 fundamentals-desk → quarterly fundamentals
📈 technicals-desk   → daily technical indicators  ← NEW
⚠️ web search        → only narrative / news / sector story
```

Data-layer triangle complete.
