# ==========================================
# app.py — Flask Web Dashboard
# GlobalTraderPavan Trading System
# Owner: Pavankumar Madavi
# niDar Marketing And Services
# Sadak Arjuni, Gondia, Maharashtra
# ==========================================

from flask import Flask, jsonify
import os
import requests

app = Flask(__name__)

# ==========================================
# PRICE FETCH
# ==========================================

def get_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        r = requests.get(url, timeout=10).json()
        return {
            "symbol":  symbol.replace("USDT", ""),
            "price":   float(r["lastPrice"]),
            "change":  float(r["priceChangePercent"]),
            "high":    float(r["highPrice"]),
            "low":     float(r["lowPrice"]),
            "volume":  float(r["volume"])
        }
    except:
        return None


def get_rsi(symbol):
    try:
        url = (f"https://api.binance.com/api/v3/klines"
               f"?symbol={symbol}&interval=1h&limit=15")
        data = requests.get(url, timeout=10).json()
        closes = [float(c[4]) for c in data]

        gains, losses = [], []
        for i in range(1, len(closes)):
            diff = closes[i] - closes[i-1]
            gains.append(max(diff, 0))
            losses.append(max(-diff, 0))

        avg_gain = sum(gains[-14:]) / 14
        avg_loss = sum(losses[-14:]) / 14

        if avg_loss == 0:
            return 100
        rs  = avg_gain / avg_loss
        rsi = round(100 - (100 / (1 + rs)), 2)
        return rsi
    except:
        return 50


# ==========================================
# ROUTES
# ==========================================

@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>GlobalTraderPavan — Dashboard</title>
  <style>
    :root {
      --gold: #F5A623;
      --bg: #0A0A0F;
      --surface: #12121A;
      --border: #2A2A3A;
      --text: #E8E8F0;
      --muted: #6B6B80;
      --green: #00C896;
      --red: #FF4D6D;
    }
    * { margin:0; padding:0; box-sizing:border-box; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'Inter', sans-serif;
      padding: 20px;
    }
    .header {
      text-align: center;
      padding: 30px 0;
      border-bottom: 1px solid var(--border);
      margin-bottom: 30px;
    }
    .header h1 {
      color: var(--gold);
      font-size: 24px;
      margin-bottom: 8px;
    }
    .header p {
      color: var(--muted);
      font-size: 13px;
    }
    .status-badge {
      display: inline-block;
      background: rgba(0,200,150,0.1);
      border: 1px solid var(--green);
      color: var(--green);
      padding: 6px 16px;
      border-radius: 20px;
      font-size: 12px;
      margin-top: 10px;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
      margin-bottom: 30px;
    }
    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 20px;
    }
    .card-title {
      font-size: 18px;
      font-weight: 700;
      color: var(--gold);
      margin-bottom: 16px;
    }
    .row {
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid var(--border);
      font-size: 13px;
    }
    .row:last-child { border-bottom: none; }
    .label { color: var(--muted); }
    .value { font-weight: 600; }
    .up { color: var(--green); }
    .down { color: var(--red); }
    .gold { color: var(--gold); }
    .system-info {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 20px;
      text-align: center;
      margin-bottom: 20px;
    }
    .system-info h3 {
      color: var(--gold);
      margin-bottom: 10px;
    }
    .system-info p {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.8;
    }
    footer {
      text-align: center;
      padding: 20px;
      color: var(--muted);
      font-size: 11px;
      border-top: 1px solid var(--border);
    }
    .loading {
      color: var(--muted);
      text-align: center;
      padding: 40px;
    }
  </style>
</head>
<body>

<div class="header">
  <h1>🌍 GlobalTraderPavan</h1>
  <p>Master Trading System — Live Dashboard</p>
  <div class="status-badge">● SYSTEM ACTIVE</div>
</div>

<div class="system-info">
  <h3>🤖 7-Agent System</h3>
  <p>
    Owner: Pavankumar Madavi<br/>
    niDar Marketing And Services<br/>
    Sadak Arjuni, Gondia, Maharashtra<br/>
    Telegram: @GlobalTraderPavan
  </p>
</div>

<div class="grid" id="prices">
  <div class="loading">⏳ Live prices load ho rahi hain...</div>
</div>

<footer>
  © 2026 Pavankumar Madavi |
  niDar Marketing And Services |
  <a href="https://t.me/GlobalTraderPavan"
     style="color:#F5A623;">
    @GlobalTraderPavan
  </a>
</footer>

<script>
async function loadPrices() {
  try {
    const r = await fetch('/api/prices');
    const data = await r.json();
    const grid = document.getElementById('prices');
    grid.innerHTML = '';

    data.forEach(coin => {
      const isUp = coin.change >= 0;
      const rsiColor = coin.rsi < 30
        ? '#00C896'
        : coin.rsi > 70
        ? '#FF4D6D'
        : '#F5A623';
      const signal = coin.rsi < 30
        ? 'LONG 🟢'
        : coin.rsi > 70
        ? 'SHORT 🔴'
        : 'WAIT ⚪';

      grid.innerHTML += `
        <div class="card">
          <div class="card-title">
            ${coin.symbol}/USDT
          </div>
          <div class="row">
            <span class="label">Price</span>
            <span class="value gold">
              $${coin.price.toLocaleString()}
            </span>
          </div>
          <div class="row">
            <span class="label">Change</span>
            <span class="value
              ${isUp ? 'up' : 'down'}">
              ${isUp ? '▲' : '▼'}
              ${Math.abs(coin.change).toFixed(2)}%
            </span>
          </div>
          <div class="row">
            <span class="label">High</span>
            <span class="value">
              $${coin.high.toLocaleString()}
            </span>
          </div>
          <div class="row">
            <span class="label">Low</span>
            <span class="value">
              $${coin.low.toLocaleString()}
            </span>
          </div>
          <div class="row">
            <span class="label">RSI</span>
            <span class="value"
              style="color:${rsiColor}">
              ${coin.rsi}
            </span>
          </div>
          <div class="row">
            <span class="label">Signal</span>
            <span class="value">${signal}</span>
          </div>
        </div>`;
    });
  } catch(e) {
    document.getElementById('prices').innerHTML =
      '<div class="loading">❌ Data load nahi hua</div>';
  }
}

loadPrices();
setInterval(loadPrices, 30000);
</script>
</body>
</html>
"""


@app.route("/api/prices")
def api_prices():
    coins = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
    result = []
    for coin in coins:
        data = get_price(coin)
        if data:
            data['rsi'] = get_rsi(coin)
            result.append(data)
    return jsonify(result)


@app.route("/health")
def health():
    return jsonify({
        "status":  "ok",
        "system":  "GlobalTraderPavan",
        "owner":   "Pavankumar Madavi",
        "company": "niDar Marketing And Services"
    })


# ==========================================
# START
# ==========================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=" * 50)
    print("GlobalTraderPavan Web Dashboard")
    print("Owner: Pavankumar Madavi")
    print("niDar Marketing And Services")
    print(f"Port: {port}")
    print("=" * 50)
    app.run(host="0.0.0.0", port=port, debug=False)