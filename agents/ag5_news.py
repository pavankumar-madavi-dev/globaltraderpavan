# ==========================================
# Agent 5 — News Intelligence Engine
# GlobalTraderPavan Trading System
# Owner: Pavankumar Madavi
# niDar Marketing And Services
# Sadak Arjuni, Gondia, Maharashtra
# ==========================================

import requests
import xml.etree.ElementTree as ET

# बुलिश और बीयरिश कीवर्ड्स की डिक्शनरी (सेंटीमेंट स्कोरिंग के लिए)
BULLISH_WORDS = ["bullish", "pump", "surge", "breakout", "buy", "gain", "growth", "accumulate", "listing", "adopt", "ath", "green"]
BEARISH_WORDS = ["bearish", "dump", "crash", "breakdown", "sell", "loss", "drop", "ban", "hack", "scam", "fud", "red", "liquidate"]

# फेक या पैनिक फैलाने वाले संदिग्ध कीवर्ड्स
FAKE_NEWS_KEYWORDS = ["unconfirmed", "rumor", "anonymous source", "source says", "insider claims", "just in case", "alleged"]

def fetch_crypto_news():
    """CryptoPanic या RSS फ़ीड्स से ताज़ा खबरें निकालें (बिना किसी पेड टोकन के)"""
    news_list = []
    # CoinDesk की ग्लोबल क्रिप्टो RSS फीड का इस्तेमाल
    url = "https://www.coindesk.com/arc/outboundfeeds/rss/"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            for item in root.findall('.//item')[:10]: # टॉप 10 ताज़ा खबरें लें
                title = item.find('title').text if item.find('title') is not None else ""
                desc = item.find('description').text if item.find('description') is not None else ""
                news_list.append({"title": title.lower(), "description": desc.lower()})
    except Exception as e:
        print(f"⚠️ न्यूज़ फेच करने में एरर आया: {e}")
    return news_list

def analyze_news_sentiment(news_data, symbol="BTC"):
    """खबरों का फेक न्यूज़ फ़िल्टर और सेंटीमेंट स्कोर कैलकुलेशन (-1.0 से +1.0)"""
    coin_name = symbol.replace("USDT", "").lower()
    score = 0.0
    total_relevant_news = 0
    fake_news_count = 0

    for news in news_data:
        text = f"{news['title']} {news['description']}"
        
        # सिर्फ उसी कॉइन की खबर चेक करें जिसके लिए सिग्नल बन रहा है
        if coin_name in text or "crypto" in text or "bitcoin" in text:
            total_relevant_news += 1
            
            # 1. फेक न्यूज़ / अफवाह चेक (Rug & FUD Prevention)
            is_fake = any(keyword in text for keyword in FAKE_NEWS_KEYWORDS)
            if is_fake:
                fake_news_count += 1
                continue # संदिग्ध खबर को स्कोर में शामिल न करें
            
            # 2. सेंटीमेंट स्कोरिंग
            bullish_hits = sum(1 for word in BULLISH_WORDS if word in text)
            bearish_hits = sum(1 for word in BEARISH_WORDS if word in text)
            
            score += (bullish_hits - bearish_hits)

    # स्कोर को -1.0 से +1.0 के बीच नॉर्मलाइज़ करें
    if total_relevant_news > 0:
        final_score = round(score / total_relevant_news, 2)
        # लिमिट सेट करना ताकि स्कोर लिमिट से बाहर न जाए
        final_score = max(-1.0, min(1.0, final_score))
    else:
        final_score = 0.0 # न्यूट्रल अगर कोई खबर नहीं मिली

    return {
        "sentiment_score": final_score,
        "relevant_stories": total_relevant_news,
        "filtered_fake_news": fake_news_count,
        "market_bias": "BULLISH 🟢" if final_score > 0.1 else "BEARISH 🔴" if final_score < -0.1 else "NEUTRAL ⚪"
    }

def run_agent5(symbol="BTCUSDT"):
    """Agent 5 का मुख्य एग्जीक्यूशन पॉइंट"""
    raw_news = fetch_crypto_news()
    if not raw_news:
        return {"status": "error", "message": "No news data available", "sentiment_score": 0.0, "market_bias": "NEUTRAL ⚪"}
    
    analysis = analyze_news_sentiment(raw_news, symbol)
    analysis["status"] = "ok"
    return analysis

# लोकल टेस्टिंग के लिए
if __name__ == "__main__":
    print("📰 AG-5 News Intelligence Agent Testing...")
    for test_coin in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
        res = run_agent5(test_coin)
        print(f"\n🪙 Asset: {test_coin}")
        print(f"   Score      : {res['sentiment_score']}")
        print(f"   Bias       : {res['market_bias']}")
        print(f"   Stories    : {res['relevant_stories']} scanned, {res['filtered_fake_news']} fake news blocked.")

