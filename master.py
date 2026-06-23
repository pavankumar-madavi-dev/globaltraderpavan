# ==========================================
# MASTER ORCHESTRATOR — 7-Agent Integrated System
# GlobalTraderPavan Trading System
# Owner: Pavankumar Madavi
# niDar Marketing And Services
# Sadak Arjuni, Gondia, Maharashtra
# ==========================================

import time
import schedule
from config import (
    TRADING_ACTIVE,
    CONFIDENCE_MINIMUM,
    COINS,
    MIN_FUND_USDT,
    MAX_FUND_USDT
)

# सातों एजेंट्स के फ़ंक्शन्स इम्पोर्ट करें
from agents.ag1_market import run_agent1
from agents.ag2_options import run_agent2
from agents.ag3_risk import run_agent3
from agents.ag4_signal import send_signal, send_no_signal
from agents.ag5_news import run_agent5
from agents.ag6_orderflow import run_agent6
from agents.ag7_fundamentals import run_agent7

def calculate_7agent_confidence(ag1, ag2, ag5, ag6, ag7):
    """सातों एजेंट्स के बायस को मिलाकर वैज्ञानिक रूप से 100% में से स्कोर निकालें"""
    score = 0
    
    # 1. AG-1 Technical Direction (Max: 30 Points)
    if ag1.get('direction') != "NEUTRAL":
        score += 30 if ag1.get('strength') == "Strong" else 15
        
    # 2. AG-2 Options Bias (Max: 15 Points)
    if ag2.get('options_bias') == ag1.get('direction'):
        score += 15
        
    # 3. AG-5 News Sentiment (Max: 20 Points)
    if ag5.get('market_bias') == ag1.get('direction'):
        score += 20
    elif ag5.get('market_bias') == "NEUTRAL ⚪":
        score += 10 # न्यूट्रल न्यूज़ पर पार्शियल स्कोर बोनस
        
    # 4. AG-6 Order Flow Whales (Max: 20 Points)
    if ag6.get('order_flow_bias') == ag1.get('direction'):
        score += 20
        
    # 5. AG-7 Fundamental Safety (Max: 15 Points)
    if ag7.get('safety_score', 0) >= 70:
        score += 15
    elif ag7.get('safety_score', 0) >= 45:
        score += 8

    return min(score, 100)

def run_system():
    """Main system engine loop"""
    if not TRADING_ACTIVE:
        print("⏹️ Trading active flag is OFF in config.")
        return

    print("\n" + "="*60)
    print("🚀 GlobalTraderPavan — 7-Agent Parallel Processing Check")
    print("="*60)

    signal_sent = False

    for coin in COINS:
        print(f"\n📊 {coin} पर सातों एजेंट्स एक्टिवेट हो रहे हैं...")

        # Layer 1: मार्केट डेटा फ़ेचर
        market_data = run_agent1(coin)
        if market_data.get('status') == 'error':
            print(f"❌ {coin} AG-1 Error: {market_data.get('message')}")
            continue

        direction = market_data.get('direction', 'NEUTRAL')
        if direction == "NEUTRAL":
            print(f"⏳ {coin} मार्केट अभी न्यूट्रल है, फ़िल्टर प्रोसेस रोकी गई।")
            continue

        # Layer 2 & 3: पैरेलल प्रोसेसिंग (सभी एजेंट्स एक साथ काम पर)
        options_data = run_agent2(coin)
        news_data = run_agent5(coin)
        orderflow_data = run_agent6(coin)
        fundamental_data = run_agent7(coin)

        # Layer 4: अल्टीमेट कॉन्फिडेंस गेट (70%+)
        confidence = calculate_7agent_confidence(
            market_data, options_data, news_data, orderflow_data, fundamental_data
        )

        # AG-3: रिस्क पैरामीटर्स कैलकुलेशन (सटीक SL/TP के लिए)
        risk_data = run_agent3(coin, market_data['price'], direction)

        if risk_data.get('status') == 'error' or risk_data.get('risk_status') == 'REJECTED ❌ (Bad R:R)':
            print(f"🛑 {coin} रिस्क मैनेजर ने ट्रेड ब्लॉक किया: {risk_data.get('message', 'Bad Risk-to-Reward')}")
            continue

        # टेलीग्राम पैकेट के लिए डेटा बंडल तैयार करना
        signal_packet = {
            "symbol":        coin,
            "direction":     direction,
            "price":         market_data['price'],
            "change":        market_data['change'],
            "rsi":           market_data['rsi'],
            "funding_rate":  market_data['funding_rate'],
            "open_interest": market_data['open_interest'],
            "strength":      market_data['strength'],
            "confidence":   confidence,
            "stop_loss":    risk_data['stop_loss'],
            "target1":      risk_data['take_profit'],
            "target2":      round(risk_data['take_profit'] * 1.01, 2) # एक्स्ट्रा सेफ टारगेट 2
        }

        print(f"🎯 विश्लेषण पूरा हुआ:")
        print(f"   RSI: {signal_packet['rsi']} | Direction: {direction} ({market_data['strength']})")
        print(f"   News Bias: {news_data['market_bias']} | OrderFlow: {orderflow_data['order_flow_bias']}")
        print(f"   🔒 Final Confidence: {confidence}% (Minimum Required: {CONFIDENCE_MINIMUM}%)")

        # सिग्नल एक्जीक्यूशन डिसीजन
        if confidence >= CONFIDENCE_MINIMUM:
            print(f"📤 बेहतरीन सेटअप! टेलीग्राम पर सिग्नल डिलीवर किया जा रहा है...")
            send_signal(signal_packet)
            signal_sent = True
            time.sleep(2)
        else:
            print(f"⏳ सिग्नल ख़ारिज: कॉन्फिडेंस स्कोर ({confidence}%) लिमिट से कम है।")

    if not signal_sent:
        send_no_signal("सभी 7 फ़िल्टर्स पार करने वाला कोई ठोस सिग्नल नहीं मिला।")

    print("\n✅ सभी एसेट्स का चक्र पूरा हुआ!")

if __name__ == "__main__":
    print("=" * 50)
    print("🌍 GlobalTraderPavan Integrated Orchestrator")
    print("👤 Owner: Pavankumar Madavi")
    print("🏢 niDar Marketing And Services")
    print("=" * 50)

    # तुरंत पहली जांच करें
    run_system()

    # हर 5 मिनट के लूप पर सेट करें
    schedule.every(5).minutes.do(run_system)
    print("\n⏰ इंजन बैकग्राउंड में एक्टिव है — हर 5 मिनट में 7-लेयर स्कैन होगा।")

    while True:
        schedule.run_pending()
        time.sleep(1)
