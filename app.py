# ==========================================
# app.py — Flask Web Dashboard
# GlobalTraderPavan Trading System
# Owner: Pavankumar Madavi
# niDar Marketing And Services
# Sadak Arjuni, Gondia, Maharashtra
# ==========================================

from flask import Flask, jsonify
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agents"))

from ag1_market import run_agent1

app = Flask(__name__)

# ==========================================
# EXCHANGE REFERRAL LINKS
# ==========================================
EXCHANGES = [
    {
        "name": "Binance",
        "color": "#F0B90B",
        "url": "https://www.binance.com/referral/earn-together/refer2earn-usdc/claim?hl=en&ref=GRO_28502_2UOCJ&utm_source=referral_entrance",
        "tag": "World's #1 Exchange"
    },
    {
        "name": "Delta India",
        "color": "#00D897",
        "url": "https://www.delta.exchange/?code=DBQGEA",
        "tag": "Options Trading"
    },
    {
        "name": "CoinDCX",
        "color": "#4B7BFF",
        "url": "https://invite.coindcx.com/65522468",
        "tag": "India's Trusted"
    },
    {
        "name": "CoinSwitch",
        "color": "#6C5CE7",
        "url": "https://coinswitch.co/in/refer?tag=MuyP&pro=true",
        "tag": "Easy for Beginners"
    }
]

COINS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]


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
<title>GlobalTraderPavan — Trading Command Center</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;600;700;800&display=swap" rel="stylesheet"/>
<style>
  :root {
    --gold: #F5A623;
    --gold-dim: #B87D1A;
    --bg: #07090e;
    --glass-bg: rgba(24, 26, 32, 0.7);
    --glass-border: rgba(243, 186, 47, 0.15);
    --text: #E8E8F0;
    --muted: #929ba6;
    --green: #0ecb81;
    --red: #ea4335;
    --mono: 'Space Mono', monospace;
    --sans: 'Inter', sans-serif;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--sans);
    padding-bottom: 100px;
  }

  .lang-bar { display:flex; gap:6px; padding:12px 16px; overflow-x:auto; border-bottom:1px solid var(--glass-border); }
  .lang-btn { background:transparent; border:1px solid var(--glass-border); color:var(--text); padding:6px 14px; border-radius:20px; font-size:12px; white-space:nowrap; cursor:pointer; }
  .lang-btn.active { background:var(--gold); border-color:var(--gold); color:#000; font-weight:700; }

  .header { text-align:center; padding:28px 20px; border-bottom:1px solid var(--glass-border); }
  .header h1 { font-family:var(--mono); color:var(--gold); font-size:22px; font-weight:800; letter-spacing:.02em; }
  .header p { color:var(--muted); font-size:12.5px; margin-top:6px; }
  .status-badge { display:inline-flex; align-items:center; gap:6px; background:rgba(14,203,129,0.1); border:1px solid var(--green); color:var(--green); padding:6px 16px; border-radius:20px; font-size:11.5px; font-weight:700; margin-top:12px; }
  .status-dot { width:7px; height:7px; background:var(--green); border-radius:50%; animation:pulse 1.5s infinite; }
  @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.4;transform:scale(1.3)} }

  .agent-strip { padding:20px 16px; border-bottom:1px solid var(--glass-border); }
  .agent-strip-title { font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:.08em; margin-bottom:14px; font-family:var(--mono); }
  .agent-nodes { display:flex; gap:8px; overflow-x:auto; padding-bottom:4px; }
  .agent-node { flex-shrink:0; width:78px; background:var(--glass-bg); border:1px solid var(--glass-border); border-radius:12px; padding:12px 8px; text-align:center; backdrop-filter:blur(12px); -webkit-backdrop-filter:blur(12px); }
  .agent-node .icon { font-size:20px; }
  .agent-node .id { font-family:var(--mono); font-size:11px; color:var(--gold); font-weight:700; margin-top:4px; }
  .agent-node .name { font-size:8.5px; color:var(--muted); margin-top:2px; line-height:1.3; }
  .agent-node .dot { width:6px; height:6px; background:var(--green); border-radius:50%; margin:6px auto 0; animation:pulse 2s infinite; }

  .section { padding:24px 16px; }
  .section-title { font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:.08em; margin-bottom:14px; font-family:var(--mono); }

  .exchange-rail { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
  .exchange-card { display:block; text-decoration:none; background:var(--glass-bg); border:1px solid var(--glass-border); border-radius:14px; padding:16px; position:relative; overflow:hidden; backdrop-filter:blur(12px); -webkit-backdrop-filter:blur(12px); }
  .exchange-card::before { content:''; position:absolute; top:0; left:0; width:4px; height:100%; background:var(--accent-color); }
  .exchange-name { font-weight:800; font-size:14px; color:var(--text); }
  .exchange-tag { font-size:10.5px; color:var(--muted); margin-top:3px; }
  .exchange-cta { font-size:11px; color:var(--accent-color); font-weight:700; margin-top:10px; }

  .signal-grid { display:grid; grid-template-columns:1fr; gap:12px; }
  .signal-card { background:var(--glass-bg); border:1px solid var(--glass-border); border-radius:16px; overflow:hidden; backdrop-filter:blur(12px); -webkit-backdrop-filter:blur(12px); }
  .signal-head { display:flex; justify-content:space-between; align-items:center; padding:14px 16px; background:rgba(243,186,47,0.06); border-bottom:1px solid var(--glass-border); }
  .signal-symbol { font-family:var(--mono); font-weight:800; font-size:15px; color:var(--gold); }
  .signal-source { font-size:9.5px; padding:3px 8px; border-radius:10px; font-weight:700; }
  .src-binance { background:rgba(240,185,11,0.15); color:#F0B90B; }
  .src-coingecko { background:rgba(140,197,63,0.15); color:#8cc53f; }
  .signal-body { padding:16px; }
  .signal-main-row { display:flex; justify-content:space-between; align-items:baseline; margin-bottom:14px; }
  .signal-price { font-family:var(--mono); font-size:22px; font-weight:700; }
  .signal-change { font-family:var(--mono); font-size:13px; font-weight:700; }
  .up { color:var(--green); } .down { color:var(--red); }
  .direction-badge { display:inline-flex; align-items:center; gap:6px; padding:8px 14px; border-radius:10px; font-weight:800; font-size:13px; margin-bottom:12px; }
  .dir-long { background:rgba(14,203,129,0.12); color:var(--green); border:1px solid rgba(14,203,129,0.3); }
  .dir-short { background:rgba(234,67,53,0.12); color:var(--red); border:1px solid rgba(234,67,53,0.3); }
  .dir-neutral { background:rgba(146,155,166,0.12); color:var(--muted); border:1px solid rgba(146,155,166,0.3); }
  .signal-stats { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; }
  .stat-box { background:rgba(0,0,0,0.2); border-radius:8px; padding:8px; text-align:center; }
  .stat-box .label { font-size:9px; color:var(--muted); text-transform:uppercase; }
  .stat-box .val { font-family:var(--mono); font-size:13px; font-weight:700; margin-top:3px; }
  .confidence-bar-wrap { margin-top:12px; }
  .confidence-label { display:flex; justify-content:space-between; font-size:10.5px; color:var(--muted); margin-bottom:5px; }
  .confidence-track { height:6px; background:rgba(255,255,255,0.08); border-radius:4px; overflow:hidden; }
  .confidence-fill { height:100%; background:linear-gradient(90deg, var(--gold-dim), var(--gold)); border-radius:4px; }

  .tg-float { position:fixed; bottom:24px; right:20px; background:linear-gradient(135deg,#0088cc,#006699); color:#fff; padding:14px 20px; border-radius:50px; font-size:13px; font-weight:700; text-decoration:none; display:flex; align-items:center; gap:8px; box-shadow:0 8px 24px rgba(34,158,217,.4); z-index:99; }
  .wa-float { position:fixed; bottom:92px; right:20px; background:linear-gradient(135deg,#25D366,#1ebd57); color:#fff; width:52px; height:52px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:24px; text-decoration:none; box-shadow:0 6px 20px rgba(37,211,102,.4); z-index:99; }

  footer { text-align:center; padding:24px 16px; color:var(--muted); font-size:11px; font-family:var(--mono); border-top:1px solid var(--glass-border); margin-top:20px; }
  footer a { color:var(--gold); text-decoration:none; font-weight:700; }
  .loading { text-align:center; padding:40px; color:var(--muted); }

  @media(min-width:600px){ .exchange-rail{grid-template-columns:repeat(4,1fr);} .signal-grid{grid-template-columns:1fr 1fr;} }
</style>
</head>
<body>

<div class="lang-bar">
  <button class="lang-btn active" data-lang="hi">🇮🇳 हिंदी</button>
  <button class="lang-btn" data-lang="en">🇬🇧 English</button>
  <button class="lang-btn" data-lang="mr">🇮🇳 मराठी</button>
</div>

<div class="header">
  <h1>🌍 GlobalTraderPavan</h1>
  <p id="hdr-sub">Master Trading System — Live Command Center</p>
  <div class="status-badge"><div class="status-dot"></div><span id="hdr-status">SYSTEM ACTIVE</span></div>
</div>

<div class="agent-strip">
  <div class="agent-strip-title" id="agent-strip-title">// 7-AGENT SYSTEM STATUS</div>
  <div class="agent-nodes" id="agents-grid">
    <div class="loading">Loading...</div>
  </div>
</div>

<div class="section">
  <div class="section-title" id="exchange-title">// EXCHANGES PER JOIN KAREIN</div>
  <div class="exchange-rail" id="exchange-rail"></div>
</div>

<div class="section">
  <div class="section-title" id="signal-title">// LIVE SIGNALS — REAL-TIME AGENT ANALYSIS</div>
  <div class="signal-grid" id="prices">
    <div class="loading">⏳ Live signals load ho rahe hain...</div>
  </div>
</div>

<footer>
  © 2026 Pavankumar Madavi | niDar Marketing And Services<br/>
  Sadak Arjuni, Gondia, Maharashtra<br/>
  <a href="https://t.me/GlobalTraderPavan">@GlobalTraderPavan</a>
</footer>

<a class="tg-float" href="https://t.me/GlobalTraderPavan" target="_blank">📲 Telegram</a>
<a class="wa-float" href="https://wa.me/918956681474" target="_blank">💬</a>

<script>
const EXCHANGES = __EXCHANGES_JSON__;

const I18N = {
  hi: { sub: "Master Trading System — Live Command Center", status: "सिस्टम एक्टिव", agentTitle: "// 7-एजेंट सिस्टम स्टेटस", exTitle: "// एक्सचेंज पर जॉइन करें", sigTitle: "// लाइव सिग्नल्स — रियल-टाइम एजेंट एनालिसिस", loadingSignal: "⏳ लाइव सिग्नल्स लोड हो रहे हैं...", errSignal: "❌ डेटा लोड नहीं हुआ" },
  en: { sub: "Master Trading System — Live Command Center", status: "SYSTEM ACTIVE", agentTitle: "// 7-AGENT SYSTEM STATUS", exTitle: "// JOIN EXCHANGES", sigTitle: "// LIVE SIGNALS — REAL-TIME AGENT ANALYSIS", loadingSignal: "⏳ Loading live signals...", errSignal: "❌ Failed to load data" },
  mr: { sub: "मास्टर ट्रेडिंग सिस्टम — लाइव्ह कमांड सेंटर", status: "सिस्टम सक्रिय", agentTitle: "// 7-एजंट सिस्टम स्थिती", exTitle: "// एक्सचेंजवर जॉईन करा", sigTitle: "// लाइव्ह सिग्नल्स — रिअल-टाइम एजंट अ‍ॅनालिसिस", loadingSignal: "⏳ लाइव्ह सिग्नल्स लोड होत आहेत...", errSignal: "❌ डेटा लोड झाला नाही" }
};

function setLang(lang) {
  const t = I18N[lang];
  document.getElementById('hdr-sub').textContent = t.sub;
  document.getElementById('hdr-status').textContent = t.status;
  document.getElementById('agent-strip-title').textContent = t.agentTitle;
  document.getElementById('exchange-title').textContent = t.exTitle;
  document.getElementById('signal-title').textContent = t.sigTitle;
  document.querySelectorAll('.lang-btn').forEach(b => b.classList.toggle('active', b.dataset.lang === lang));
  localStorage.setItem('gtp_lang', lang);
}
document.querySelectorAll('.lang-btn').forEach(b => b.addEventListener('click', () => setLang(b.dataset.lang)));

function renderExchanges() {
  const rail = document.getElementById('exchange-rail');
  rail.innerHTML = EXCHANGES.map(ex => `
    <a class="exchange-card" style="--accent-color:${ex.color}" href="${ex.url}" target="_blank" rel="noopener">
      <div class="exchange-name">${ex.name}</div>
      <div class="exchange-tag">${ex.tag}</div>
      <div class="exchange-cta">Join Free →</div>
    </a>
  `).join('');
}

async function loadPrices() {
  try {
    const r = await fetch('/api/prices');
    const data = await r.json();
    const grid = document.getElementById('prices');
    grid.innerHTML = '';
    data.forEach(coin => {
      const isUp = coin.change >= 0;
      const dirClass = coin.direction === 'LONG' ? 'dir-long' : coin.direction === 'SHORT' ? 'dir-short' : 'dir-neutral';
      const dirIcon = coin.direction === 'LONG' ? '🟢' : coin.direction === 'SHORT' ? '🔴' : '⚪';
      const srcClass = coin.source === 'binance' ? 'src-binance' : 'src-coingecko';

      grid.innerHTML += `
        <div class="signal-card">
          <div class="signal-head">
            <span class="signal-symbol">${coin.symbol}/USDT</span>
            <span class="signal-source ${srcClass}">${coin.source.toUpperCase()}</span>
          </div>
          <div class="signal-body">
            <div class="signal-main-row">
              <span class="signal-price">$${coin.price.toLocaleString()}</span>
              <span class="signal-change ${isUp ? 'up' : 'down'}">${isUp ? '▲' : '▼'} ${Math.abs(coin.change).toFixed(2)}%</span>
            </div>
            <div class="direction-badge ${dirClass}">${dirIcon} ${coin.direction} · ${coin.strength}</div>
            <div class="signal-stats">
              <div class="stat-box"><div class="label">RSI</div><div class="val">${coin.rsi}</div></div>
              <div class="stat-box"><div class="label">High</div><div class="val">$${coin.high.toLocaleString()}</div></div>
              <div class="stat-box"><div class="label">Low</div><div class="val">$${coin.low.toLocaleString()}</div></div>
            </div>
            <div class="confidence-bar-wrap">
              <div class="confidence-label"><span>Confidence</span><span>${coin.confidence}%</span></div>
              <div class="confidence-track"><div class="confidence-fill" style="width:${coin.confidence}%"></div></div>
            </div>
          </div>
        </div>`;
    });
  } catch(e) {
    document.getElementById('prices').innerHTML = `<div class="loading">${I18N[localStorage.getItem('gtp_lang') || 'hi'].errSignal}</div>`;
  }
}

async function loadAgents() {
  try {
    const r = await fetch('/api/agents');
    const data = await r.json();
    const grid = document.getElementById('agents-grid');
    grid.innerHTML = '';
    data.forEach(ag => {
      grid.innerHTML += `
        <div class="agent-node">
          <div class="icon">${ag.icon}</div>
          <div class="id">${ag.id}</div>
          <div class="name">${ag.name}</div>
          <div class="dot"></div>
        </div>`;
    });
  } catch(e) { console.log("Agents error:", e); }
}

renderExchanges();
loadPrices();
loadAgents();
setInterval(loadPrices, 30000);
setInterval(loadAgents, 60000);
setLang(localStorage.getItem('gtp_lang') || 'hi');
</script>
</body>
</html>
""".replace("__EXCHANGES_JSON__", json.dumps(EXCHANGES))


@app.route("/api/prices")
def api_prices():
    result = []
    for coin in COINS:
        data = run_agent1(coin)
        if data.get("status") == "ok":
            result.append(data)
    return jsonify(result)


@app.route("/api/agents")
def api_agents():
    return jsonify([
        {"id": "AG1", "name": "Market Analysis", "status": "active", "icon": "📊"},
        {"id": "AG2", "name": "Options Flow", "status": "active", "icon": "📈"},
        {"id": "AG3", "name": "Risk Manager", "status": "active", "icon": "🛡️"},
        {"id": "AG4", "name": "Signal Sender", "status": "active", "icon": "📡"},
        {"id": "AG5", "name": "News Engine", "status": "active", "icon": "📰"},
        {"id": "AG6", "name": "Order Flow", "status": "active", "icon": "🔄"},
        {"id": "AG7", "name": "Fundamentals", "status": "active", "icon": "🧠"}
    ])


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "system": "GlobalTraderPavan",
        "owner": "Pavankumar Madavi",
        "company": "niDar Marketing And Services"
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
