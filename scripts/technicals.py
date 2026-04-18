#!/usr/bin/env python3
"""
technicals-desk — live technical-indicator puller via yfinance history.

Pattern: parallel to price-desk + fundamentals-desk.
Kills stale-web-data bug for technicals (MAs, RSI, ADX, 52w range, etc).

Usage:
  python3 technicals.py                     → menu
  python3 technicals.py TICKER              → full technicals
  python3 technicals.py TICKER1 TICKER2 ... → batch
  python3 technicals.py watchlist           → read waypoint-capital/watchlist.md
  python3 technicals.py log [N]             → recent pulls
"""
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

try:
    import yfinance as yf
    import pandas as pd
except ImportError:
    print(json.dumps({"error": "yfinance + pandas required. Run: pip install yfinance pandas"}))
    sys.exit(2)

LOG_FILE = Path(__file__).parent.parent / "data" / "technicals-log.jsonl"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

MENU = """
📈 TECHNICALS DESK — Technical Analyst
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What do you want to pull?

1. 📊 Single / batch technicals
     .technicals NVDA
     .technicals NVDA AMD MU            (batch)

2. 👀 Pull the watchlist
     .technicals watchlist              (reads waypoint-capital/watchlist.md)

3. 📜 Show recent pulls
     .technicals log [N]                (last N from technicals-log.jsonl)

4. ❓ This menu
     .technicals                        (no args = this)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Source: yfinance history (daily OHLCV, 1-year lookback)
Indicators: 50/100/200 MA · RSI(14) · ADX · 52w range · volume trend
            golden/death cross · ATR · Fibonacci retracements
Logged: data/technicals-log.jsonl every pull
"""


def log_pull(record):
    try:
        with LOG_FILE.open("a") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass


def compute_rsi(prices, period=14):
    """Standard 14-day RSI."""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None


def compute_adx(high, low, close, period=14):
    """Standard 14-day ADX (trend strength, not direction)."""
    plus_dm = high.diff()
    minus_dm = low.diff() * -1
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)

    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs(),
    ], axis=1).max(axis=1)

    atr = tr.rolling(window=period).mean()
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    adx = dx.rolling(window=period).mean()
    return float(adx.iloc[-1]) if not pd.isna(adx.iloc[-1]) else None


def compute_atr(high, low, close, period=14):
    """Average True Range — used for stop-loss sizing."""
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs(),
    ], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return float(atr.iloc[-1]) if not pd.isna(atr.iloc[-1]) else None


def compute_fib_levels(swing_high, swing_low):
    """Fibonacci retracements from swing high → swing low."""
    diff = swing_high - swing_low
    return {
        "0": round(swing_high, 2),
        "23.6": round(swing_high - diff * 0.236, 2),
        "38.2": round(swing_high - diff * 0.382, 2),
        "50.0": round(swing_high - diff * 0.500, 2),
        "61.8": round(swing_high - diff * 0.618, 2),
        "100": round(swing_low, 2),
    }


def get_technicals(ticker):
    """Full technical snapshot."""
    pulled_at = datetime.now(timezone.utc).isoformat()

    try:
        tkr = yf.Ticker(ticker)
        hist = tkr.history(period="1y")

        if len(hist) < 50:
            record = {
                "ticker": ticker.upper(),
                "status": "ERROR",
                "error": "Insufficient history (need 50+ days for MAs)",
                "source": "yfinance",
                "pulled_at": pulled_at,
            }
            log_pull(record)
            return record

        close = hist["Close"]
        high = hist["High"]
        low = hist["Low"]
        volume = hist["Volume"]

        current = float(close.iloc[-1])

        # Moving averages
        ma50 = float(close.rolling(window=50).mean().iloc[-1]) if len(close) >= 50 else None
        ma100 = float(close.rolling(window=100).mean().iloc[-1]) if len(close) >= 100 else None
        ma200 = float(close.rolling(window=200).mean().iloc[-1]) if len(close) >= 200 else None

        # 52-week range
        high_52w = float(high.max())
        low_52w = float(low.min())
        pct_from_52w_high = round((current - high_52w) / high_52w * 100, 2)
        pct_from_52w_low = round((current - low_52w) / low_52w * 100, 2)

        # Indicators
        rsi = compute_rsi(close)
        adx = compute_adx(high, low, close)
        atr = compute_atr(high, low, close)

        # Volume trend
        vol_30d_avg = float(volume.rolling(window=30).mean().iloc[-1])
        vol_today = float(volume.iloc[-1])
        vol_vs_30d_pct = round((vol_today - vol_30d_avg) / vol_30d_avg * 100, 2)

        # Trend signals
        above_200dma = ma200 is not None and current > ma200
        above_50dma = ma50 is not None and current > ma50
        golden_cross = (ma50 is not None and ma200 is not None and ma50 > ma200)
        death_cross = (ma50 is not None and ma200 is not None and ma50 < ma200)

        # Fibonacci from 52-week high → low
        fib_levels = compute_fib_levels(high_52w, low_52w)

        record = {
            "ticker": ticker.upper(),
            "status": "OK",
            "current_price": round(current, 2),
            "moving_averages": {
                "ma_50": round(ma50, 2) if ma50 else None,
                "ma_100": round(ma100, 2) if ma100 else None,
                "ma_200": round(ma200, 2) if ma200 else None,
                "above_200dma": above_200dma,
                "above_50dma": above_50dma,
                "golden_cross": golden_cross,
                "death_cross": death_cross,
            },
            "momentum": {
                "rsi_14": round(rsi, 2) if rsi else None,
                "adx_14": round(adx, 2) if adx else None,
                "atr_14": round(atr, 2) if atr else None,
            },
            "range_52w": {
                "high": round(high_52w, 2),
                "low": round(low_52w, 2),
                "pct_from_high": pct_from_52w_high,
                "pct_from_low": pct_from_52w_low,
            },
            "volume": {
                "today": int(vol_today),
                "avg_30d": int(vol_30d_avg),
                "vs_30d_pct": vol_vs_30d_pct,
            },
            "fibonacci_52w": fib_levels,
            "source": "yfinance history(1y)",
            "pulled_at": pulled_at,
        }
        log_pull(record)
        return record

    except Exception as e:
        record = {
            "ticker": ticker.upper(),
            "status": "ERROR",
            "error": f"{type(e).__name__}: {str(e)}",
            "source": "yfinance",
            "pulled_at": pulled_at,
        }
        log_pull(record)
        return record


def read_watchlist():
    path = Path.home() / "Desktop/CLAUDE CODE/waypoint-capital/watchlist.md"
    if not path.exists():
        return None, f"No watchlist at {path}"
    tickers = []
    try:
        with path.open() as f:
            for line in f:
                line = line.strip()
                if line.startswith("|") and "|---|" not in line and "Ticker" not in line:
                    parts = [p.strip() for p in line.split("|")]
                    for p in parts:
                        if p and p.isupper() and 1 <= len(p) <= 6 and p.isalpha():
                            if p not in tickers:
                                tickers.append(p)
                            break
    except Exception as e:
        return None, f"Could not parse watchlist: {e}"
    return tickers or None, None if tickers else "No tickers found"


def show_log(n=10):
    if not LOG_FILE.exists():
        print("No technicals log yet.")
        return
    lines = LOG_FILE.read_text().strip().split("\n")
    recent = lines[-n:] if len(lines) > n else lines
    print(f"📜 Last {len(recent)} technicals pulls:\n")
    for line in recent:
        try:
            r = json.loads(line)
            ts = r.get("pulled_at", "—")[:19]
            ticker = r.get("ticker", "—")
            status = r.get("status", "?")
            ma200 = r.get("moving_averages", {}).get("ma_200", "—") if status == "OK" else "—"
            rsi = r.get("momentum", {}).get("rsi_14", "—") if status == "OK" else "—"
            print(f"  {ts}  {ticker:>6}  {status:>6}  200DMA: {ma200}  RSI: {rsi}")
        except Exception:
            continue


def main():
    args = sys.argv[1:]

    if not args:
        print(MENU)
        sys.exit(0)

    if args[0] == "watchlist":
        tickers, err = read_watchlist()
        if err:
            print(f"❌ {err}")
            sys.exit(1)
        print(f"📈 Pulling technicals for {len(tickers)} watchlist tickers: {' '.join(tickers)}\n")
        results = [get_technicals(t) for t in tickers]
        print(json.dumps(results, indent=2))
        sys.exit(0 if all(r["status"] == "OK" for r in results) else 1)

    if args[0] == "log":
        n = 10
        if len(args) > 1:
            try:
                n = int(args[1])
            except ValueError:
                pass
        show_log(n)
        sys.exit(0)

    results = [get_technicals(t) for t in args]
    print(json.dumps(results, indent=2))
    sys.exit(0 if all(r["status"] == "OK" for r in results) else 1)


if __name__ == "__main__":
    main()
