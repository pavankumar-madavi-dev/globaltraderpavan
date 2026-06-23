# ==========================================
# Agent 7 — Fundamental Analytics Engine
# GlobalTraderPavan Trading System
# Owner: Pavankumar Madavi
# niDar Marketing And Services
# Sadak Arjuni, Gondia, Maharashtra
# ==========================================

import requests

def analyze_fundamentals(symbol="BTCUSDT"):
    """Binance Global Ticker से कॉइन का वॉल्यूम/मार्केट कैप हेल्थ और फंडामेंटल स्कोर निकालें"""
    try:
        coin = symbol.replace("USDT", "")
        
        # बाइनेंस से 24 घंटे का स्टेटिस्टिक्स डेटा लें
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        res = requests.get(url, timeout=10).json()
        
        if "volume" not in res or "quoteVolume" not in res:
            return {"status": "error", "message": "Invalid API data", "fundamental_bias": "NEUTRAL ⚪"}

        volume_usd = float(res["quoteVolume"]) # 24 घंटे का टोटल USD वॉल्यूम
        
        # फंडामेंटल सेफ्टी स्कोर कैलकुलेशन (0 से 100)
        # बेस स्कोर 50 से शुरू करते हैं
        safety_score = 50 
        
        # 1. लिक्विडिटी चेक (USD वॉल्यूम के आधार पर स्थिरता)
        if volume_usd > 50000000: # $50M से ज़्यादा वॉल्यूम = हाई लिक्विडिटी (सेफ)
            safety_score += 25
        elif volume_usd > 10000000: # $10M से $50M = मीडियम रिस्क
            safety_score += 15
        else: # बहुत कम वॉल्यूम = हाई रिस्क (आसानी से डंप हो सकता है)
            safety_score -= 20

        # 2. एसेट स्टेबिलिटी बोनस (टॉप टियर एसेट्स को एक्स्ट्रा सेफ्टी पॉइंट)
        if coin in ["BTC", "ETH"]:
            safety_score += 25
        elif coin in ["BNB", "SOL", "XRP", "ADA"]:
            safety_score += 15
        else:
            safety_score += 5 # न्यू कमर एल्टकॉइन्स

        # स्कोर की सीमा 0 से 100 के बीच सेट करें
        safety_score = max(0, min(100, safety_score))

        # डिसीजन लॉजिक
        if safety_score >= 70:
            bias = "BULLISH 🟢"
            status = "Strong Fundamentals (Safe Asset) ✅"
        elif safety_score >= 45:
            bias = "NEUTRAL ⚪"
            status = "Moderate Risk Asset ⏳"
        else:
            bias = "BEARISH 🔴"
            status = "High Risk / Low Liquidity Asset ⚠️"

        return {
            "status": "ok",
            "symbol": symbol,
            "asset_class": "Tier 1" if coin in ["BTC", "ETH"] else "Altcoin",
            "24h_usd_volume": round(volume_usd, 2),
            "safety_score": safety_score,
            "fundamental_bias": bias,
            "asset_status": status
        }

    except Exception as e:
        return {"status": "error", "message": str(e), "fundamental_bias": "NEUTRAL ⚪"}

def run_agent7(symbol="BTCUSDT"):
    """Agent 7 का मुख्य एग्जीक्यूशन पॉइंट"""
    return analyze_fundamentals(symbol)

# लोकल TESTING के लिए
if __name__ == "__main__":
    print("🏗️ AG-7 Fundamental Analytics Agent Testing...")
    for test_coin in ["BTCUSDT", "SOLUSDT"]:
        res = run_agent7(test_coin)
        if res['status'] == 'ok':
            print(f"\n🪙 Asset: {res['symbol']} ({res['asset_class']})")
            print(f"   24h Volume  : ${res['24h_usd_volume']:,}")
            print(f"   Safety Score: {res['safety_score']}/100")
            print(f"   Bias        : {res['fundamental_bias']}")
            print(f"   Status      : {res['asset_status']}")
        else:
            print(f"❌ Error: {res['message']}")

