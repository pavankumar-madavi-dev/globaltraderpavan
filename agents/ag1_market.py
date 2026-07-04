# ==========================================
# Agent 1 — Market Data Fetcher (Improved)
# GlobalTraderPavan Trading System
# CoinGecko fallback + dedicated API key +
# throttling + retry-on-429 + real confidence.
# ==========================================

import requests
import time
import os

COINGECKO_IDS = {
    "BTCUSDT": "bitcoin",
    "ETHUSDT": "ethereum",
    "BNBUSDT": "binancecoin",
    "SOLUSDT": "solana",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0 Safari/537.36"
}

COINGECKO_API_KEY = os.environ.get("COINGECKO_API_KEY", "")

CG_HEADERS = dict(HEADERS)
if COINGECKO_API_KEY:
    CG_HEADERS["x-cg-demo-api-key"] = COINGECKO_API_KEY

_CACHE = {}
_CACHE_TTL = 90
_LAST_CG_CALL = {"time": 0}
_MIN_GAP = 8


def _throttle_coingecko():
    elapsed = time.time() - _LAST_CG_CALL["time"]
    if elapsed < _MIN_GAP:
        time.sleep(_MIN_GAP - elapsed)
    _LAST_CG_CALL["time"] = time.time()


def _get_cached(key):
    entry = _CACHE.get(key)
    if entry and (time.time() - entry["time"]) < _CACHE_TTL:
        return entry["data"]
    return None


def _set_cache(key, data):
    _CACHE[key] = {"data": data, "time": time.time()}


def _calc_rsi(closes):
    gains = []
    losses = []

    for i in range(1, len(closes)):
        diff = closes[i] - closes[i - 1]

        if diff > 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(diff))

    avg_gain = sum(gains[-14:]) / 14
    avg_loss = sum(losses[-14:]) / 14

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def _get_from_binance(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    resp = requests.get(url, headers=HEADERS, timeout=10)

    if resp.status_code != 200:
        raise Exception(
            f"Binance HTTP {resp.status_code}: {resp.text[:200]}"
        )

    r = resp.json()

    if "lastPrice" not in r:
        raise Exception(f"Binance blocked/unexpected response: {r}")

    price = float(r["lastPrice"])
    change = float(r["priceChangePercent"])
    volume = float(r["volume"])
    high = float(r["highPrice"])
    low = float(r["lowPrice"])

    kresp = requests.get(
        f"https://api.binance.com/api/v3/klines"
        f"?symbol={symbol}&interval=1h&limit=15",
        headers=HEADERS,
        timeout=10
    )

    if kresp.status_code != 200:
        raise Exception(
            f"Binance klines HTTP {kresp.status_code}: {kresp.text[:200]}"
        )

    klines = kresp.json()
    closes = [float(x[4]) for x in klines]
    rsi = _calc_rsi(closes)

    return {
        "status": "ok",
        "symbol": symbol,
        "price": round(price, 2),
        "change": round(change, 2),
        "volume": round(volume, 2),
        "high": round(high, 2),
        "low": round(low, 2),
        "rsi": rsi,
        "source": "binance"
    }


def _get_from_coingecko(symbol):
    cache_key = f"cg_{symbol}"
    cached = _get_cached(cache_key)
    if cached:
        return cached

    coin_id = COINGECKO_IDS.get(symbol)

    if not coin_id:
        raise Exception(f"No CoinGecko mapping for {symbol}")

    price_url = (
        f"https://api.coingecko.com/api/v3/simple/price"
        f"?ids={coin_id}&vs_currencies=usd"
        f"&include_24hr_change=true&include_24hr_vol=true"
    )

    _throttle_coingecko()
    resp = requests.get(price_url, headers=CG_HEADERS, timeout=10)

    if resp.status_code == 429:
        time.sleep(10)
        _throttle_coingecko()
        resp = requests.get(price_url, headers=CG_HEADERS, timeout=10)

    if resp.status_code != 200:
        raise Exception(
            f"CoinGecko HTTP {resp.status_code}: {resp.text[:200]}"
        )

    data = resp.json()[coin_id]

    price = float(data["usd"])
    change = float(data.get("usd_24h_change", 0.0))
    volume = float(data.get("usd_24h_vol", 0.0))

    chart_url = (
        f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        f"/market_chart?vs_currency=usd&days=1"
    )

    _throttle_coingecko()
    cresp = requests.get(chart_url, headers=CG_HEADERS, timeout=10)

    if cresp.status_code == 429:
        time.sleep(10)
        _throttle_coingecko()
        cresp = requests.get(chart_url, headers=CG_HEADERS, timeout=10)

    if cresp.status_code != 200:
        raise Exception(
            f"CoinGecko chart HTTP {cresp.status_code}: {cresp.text[:200]}"
        )

    prices = cresp.json().get("prices", [])
    closes = [p[1] for p in prices]

    rsi = _calc_rsi(closes) if len(closes) > 14 else 50.0

    result = {
        "status": "ok",
        "symbol": symbol,
        "price": round(price, 2),
        "change": round(change, 2),
        "volume": round(volume, 2),
        "high": round(max(closes), 2) if closes else price,
        "low": round(min(closes), 2) if closes else price,
        "rsi": rsi,
        "source": "coingecko"
    }

    _set_cache(cache_key, result)
    return result


def get_price_and_rsi(symbol="BTCUSDT"):
    try:
        return _get_from_binance(symbol)

    except Exception as binance_error:

        try:
            result = _get_from_coingecko(symbol)
            print(
                f"⚠️ {symbol}: Binance failed "
                f"({binance_error}), used CoinGecko fallback"
            )
            return result

        except Exception as coingecko_error:
            return {
                "status": "error",
                "symbol": symbol,
                "message": (
                    f"Binance: {binance_error} | "
                    f"CoinGecko: {coingecko_error}"
                )
            }


def get_funding_rate(symbol="BTCUSDT"):
    try:
        url = (
            f"https://fapi.binance.com/fapi/v1/fundingRate"
            f"?symbol={symbol}&limit=1"
        )

        data = requests.get(url, headers=HEADERS, timeout=10).json()

        return round(float(data[0]["fundingRate"]) * 100, 4)

    except Exception:
        return 0.0


def get_open_interest(symbol="BTCUSDT"):
    try:
        url = f"https://fapi.binance.com/fapi/v1/openInterest?symbol={symbol}"

        data = requests.get(url, headers=HEADERS, timeout=10).json()

        return round(float(data["openInterest"]), 2)

    except Exception:
        return 0.0


def get_market_direction(rsi, change, funding):

    score = 0

    if rsi >= 65:
        score += 3

    elif rsi >= 55:
        score += 1

    elif rsi <= 35:
        score -= 3

    elif rsi <= 45:
        score -= 1

    if change >= 2:
        score += 2

    elif change >= 1:
        score += 1

    elif change <= -2:
        score -= 2

    elif change <= -1:
        score -= 1

    if funding > 0.01:
        score += 1

    elif funding < -0.01:
        score -= 1

    if score >= 4:
        return "LONG", "Strong", score

    elif score >= 2:
        return "LONG", "Moderate", score

    elif score <= -4:
        return "SHORT", "Strong", score

    elif score <= -2:
        return "SHORT", "Moderate", score

    else:
        return "NEUTRAL", "Weak", score


def run_agent1(symbol="BTCUSDT"):

    market = get_price_and_rsi(symbol)

    if market["status"] != "ok":
        return market

    funding = get_funding_rate(symbol)
    oi = get_open_interest(symbol)

    direction, strength, score = get_market_direction(
        market["rsi"],
        market["change"],
        funding
    )

    confidence = round(min(abs(score) / 6 * 100, 100), 1)

    avg_volume = market["volume"] * 0.8 if market["volume"] else 1
    volume_ratio = round(
        (market["volume"] / avg_volume) * 100,
        2
    )

    return {
        "status": "ok",
        "symbol": market["symbol"],
        "price": market["price"],
        "change": market["change"],
        "high": market["high"],
        "low": market["low"],
        "volume": market["volume"],
        "volume_ratio": volume_ratio,
        "rsi": market["rsi"],
        "funding_rate": funding,
        "open_interest": oi,
        "direction": direction,
        "strength": strength,
        "confidence": confidence,
        "source": market.get("source", "unknown")
    }


if __name__ == "__main__":

    print("AG-1 Market Data Agent Testing...")

    for coin in [
        "BTCUSDT",
        "ETHUSDT",
        "BNBUSDT",
        "SOLUSDT"
    ]:

        result = run_agent1(coin)

        if result["status"] == "ok":

            print(f"""
{result['symbol']} (source: {result['source']}):

  Price     : ${result['price']:,}
  Change    : {result['change']}%
  RSI       : {result['rsi']}
  Direction : {result['direction']} ({result['strength']})
  Funding   : {result['funding_rate']}%
  OI        : {result['open_interest']:,}
""")

        else:

            print(
                f"{coin} Error: "
                f"{result['message']}"
            )
