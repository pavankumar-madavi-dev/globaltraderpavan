# ==========================================
# Agent 1 — Market Data Fetcher
# GlobalTraderPavan Trading System
# Owner: Pavankumar Madavi
# niDar Marketing And Services
# Sadak Arjuni, Gondia, Maharashtra
# ==========================================

import requests
import os

def get_price_and_rsi(symbol="BTCUSDT"):
    """Price + RSI calculate karo"""
    try:
        # Live price
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        r = requests.get(url, timeout=10).json()
        price  = float(r["lastPrice"])
        change = float(r["priceChangePercent"])
        volume = float(r["volume"])
        high   = float(r["highPrice"])
        low    = float(r["lowPrice"])

        # RSI calculation
        klines = requests.get(
            f"https://api.binance.com/api/v3/klines"
            f"?symbol={symbol}&interval=1h&limit=15",
            timeout=10
        ).json()
        closes = [float(c[4]) for c in klines]

        gains, losses = [], []
        for i in range(1, len(closes)):
            diff = closes[i] - closes[i-1]
            gains.append(max(diff, 0))
            losses.append(max(-diff, 0))

        avg_gain = sum(gains[-14:]) / 14
        avg_loss = sum(losses[-14:]) / 14

        if avg_loss == 0:
            rsi = 100
        else:
            rs  = avg_gain / avg_loss
            rsi = round(100 - (100 / (1 + rs)), 2)

        return {
            "symbol": symbol,
            "price":  round(price, 2),
            "change": round(change, 2),
            "volume": round(volume, 2),
            "high":   round(high, 2),
            "low":    round(low, 2),
            "rsi":    rsi,
            "status": "ok"
        }

    except Exception as e:
        return {"symbol": symbol, "status": "error", "message": str(e)}


def get_funding_rate(symbol="BTCUSDT"):
    """Funding rate fetch karo"""
    try:
        url = (
            f"https://fapi.binance.com/fapi/v1/fundingRate"
            f"?symbol={symbol}&limit=1"
        )
        data = requests.get(url, timeout=10).json()
        return round(float(data[0]['fundingRate']) * 100, 4)
    except:
        return 0.0


def get_open_interest(symbol="BTCUSDT"):
    """Open Interest fetch karo"""
    try:
        url = f"https://fapi.binance.com/fapi/v1/openInterest?symbol={symbol}"
        data = requests.get(url, timeout=10).json()
        return round(float(data['openInterest']), 2)
    except:
        return 0.0


def get_market_direction(rsi, change, funding):
    """Market direction decide karo"""
    score = 0

    # RSI score
    if rsi < 30:
        score += 2   # Strong buy
    elif rsi < 45:
        score += 1   # Weak buy
    elif rsi > 70:
        score -= 2   # Strong sell
    elif rsi > 55:
        score -= 1   # Weak sell

    # Price change score
    if change > 2:
        score += 1
    elif change < -2:
        score -= 1

    # Funding rate score
    if funding < -0.01:
        score += 1   # Negative funding = long friendly
    elif funding > 0.01:
        score -= 1   # Positive funding = short friendly

    # Final direction
    if score >= 2:
        return "LONG", "Strong"
    elif score == 1:
        return "LONG", "Moderate"
    elif score <= -2:
        return "SHORT", "Strong"
    elif score == -1:
        return "SHORT", "Moderate"
    else:
        return "NEUTRAL", "Weak"


def run_agent1(symbol="BTCUSDT"):
    """Agent 1 — Complete market data"""

    # Data fetch
    market  = get_price_and_rsi(symbol)
    if market['status'] == 'error':
        return market

    funding = get_funding_rate(symbol)
    oi      = get_open_interest(symbol)

    # Direction decide
    direction, strength = get_market_direction(
        market['rsi'],
        market['change'],
        funding
    )

    # Volume ratio
    avg_volume   = market['volume'] * 0.8
    volume_ratio = round((market['volume'] / avg_volume) * 100, 2)

    return {
        "symbol":        market['symbol'],
        "price":         market['price'],
        "change":        market['change'],
        "high":          market['high'],
        "low":           market['low'],
        "volume":        market['volume'],
        "volume_ratio":  volume_ratio,
        "rsi":           market['rsi'],
        "funding_rate":  funding,
        "open_interest": oi,
        "direction":     direction,
        "strength":      strength,
        "status":        "ok"
    }


# Test
if __name__ == "__main__":
    print("AG-1 Market Data Agent Testing...")
    for coin in ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]:
        result = run_agent1(coin)
        if result['status'] == 'ok':
            print(f"""
{result['symbol']}:
  Price     : ${result['price']:,}
  Change    : {result['change']}%
  RSI       : {result['rsi']}
  Direction : {result['direction']} ({result['strength']})
  Funding   : {result['funding_rate']}%
  OI        : {result['open_interest']:,}
""")
        else:
            print(f"{coin} Error: {result['message']}")