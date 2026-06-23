# ==========================================
# Agent 6 — Order Flow Intelligence Engine
# GlobalTraderPavan Trading System
# Owner: Pavankumar Madavi
# niDar Marketing And Services
# Sadak Arjuni, Gondia, Maharashtra
# ==========================================

import requests

def analyze_order_flow(symbol="BTCUSDT"):
    """Binance Order Book (Depth) चेक करके Whales का लाइव बाइंग/सेलिंग प्रेशर निकालें"""
    try:
        # बाइनेंस स्पॉट या फ्यूचर्स की टॉप 100 ऑर्डर बुक लेयर्स मंगाएं
        url = f"https://api.binance.com/api/v3/depth?symbol={symbol}&limit=100"
        res = requests.get(url, timeout=10).json()
        
        if "bids" not in res or "asks" not in res:
            return {"status": "error", "message": "Invalid API response", "order_flow_bias": "NEUTRAL ⚪"}

        # टोटल बाइंग वॉल्यूम (Bids) और टोटल सेलिंग वॉल्यूम (Asks) कैलकुलेट करें
        total_bid_volume = sum(float(bid[1]) for bid in res["bids"])
        total_ask_volume = sum(float(ask[1]) for ask in res["asks"])

        # ऑर्डर बुक रेशियो निकालें (Bids / Asks)
        if total_ask_volume == 0:
            ratio = 1.0
        else:
            ratio = round(total_bid_volume / total_ask_volume, 2)

        # डिसीजन लॉजिक:
        # अगर रेशियो 1.15 या ज्यादा है = 15% ज्यादा बाइंग ऑर्डर्स लगे हैं (Whales Support)
        # अगर रेशियो 0.85 या कम है = 15% ज्यादा सेलिंग ऑर्डर्स लगे हैं (Whales Resistance)
        if ratio >= 1.15:
            bias = "BULLISH 🟢"
            activity = "Whales Buying Wall Active 🔥"
        elif ratio <= 0.85:
            bias = "BEARISH 🔴"
            activity = "Whales Selling Wall Active ⚠️"
        else:
            bias = "NEUTRAL ⚪"
            activity = "Balanced Liquidity"

        return {
            "status": "ok",
            "symbol": symbol,
            "bid_volume": round(total_bid_volume, 2),
            "ask_volume": round(total_ask_volume, 2),
            "order_book_ratio": ratio,
            "order_flow_bias": bias,
            "whale_activity": activity
        }

    except Exception as e:
        return {"status": "error", "message": str(e), "order_flow_bias": "NEUTRAL ⚪"}

def run_agent6(symbol="BTCUSDT"):
    """Agent 6 का मुख्य एग्जीक्यूशन पॉइंट"""
    return analyze_order_flow(symbol)

# लोकल टेस्टिंग के लिए
if __name__ == "__main__":
    print("🌊 AG-6 Order Flow Intelligence Agent Testing...")
    for test_coin in ["BTCUSDT", "ETHUSDT"]:
        res = run_agent6(test_coin)
        if res['status'] == 'ok':
            print(f"\n🪙 Asset: {res['symbol']}")
            print(f"   Bid Volume (Buys) : {res['bid_volume']}")
            print(f"   Ask Volume (Sells): {res['ask_volume']}")
            print(f"   Orderbook Ratio   : {res['order_book_ratio']}")
            print(f"   Order Flow Bias   : {res['order_flow_bias']}")
            print(f"   Whale Activity    : {res['whale_activity']}")
        else:
            print(f"❌ Error: {res['message']}")

