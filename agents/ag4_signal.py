# ==========================================
# Agent 4 — Telegram Signal Sender
# GlobalTraderPavan Trading System
# Owner: Pavankumar Madavi
# niDar Marketing And Services
# Sadak Arjuni, Gondia, Maharashtra
# ==========================================

import requests
import os
from datetime import datetime

TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_signal(data):
    """Telegram pe signal bhejo"""

    symbol    = data.get("symbol", "BTCUSDT")
    direction = data.get("direction", "NEUTRAL")
    price     = data.get("price", 0)
    rsi       = data.get("rsi", 0)
    funding   = data.get("funding_rate", 0)
    oi        = data.get("open_interest", 0)
    strength  = data.get("strength", "")
    confidence= data.get("confidence", 0)
    sl        = data.get("stop_loss", 0)
    t1        = data.get("target1", 0)
    t2        = data.get("target2", 0)

    if direction == "LONG":
        emoji  = "🟢"
        side   = "📈"
    elif direction == "SHORT":
        emoji  = "🔴"
        side   = "📉"
    else:
        emoji  = "⚪"
        side   = "➡️"

    now = datetime.now().strftime("%d %b %Y, %I:%M %p IST")

    message = f"""
📊 *SIGNAL ALERT — GlobalTraderPavan*
━━━━━━━━━━━━━━━━━━━━━

{emoji} *{symbol} — {direction}* {side}

💰 *Live Price:* ${price:,.2f} ({data.get('change', 0):+.2f}%)
📍 *Entry Zone:* ${price*0.998:,.0f} – ${price*1.002:,.0f}
🎯 *Target 1:* ${t1:,.0f}
🎯 *Target 2:* ${t2:,.0f}
🛑 *Stop Loss:* ${sl:,.0f}

━━━━━━━━━━━━━━━━━━━━━
📈 *Market Analysis:*
• RSI: {rsi}
• Funding Rate: {funding}%
• Open Interest: {oi:,.0f}
• Signal Strength: {strength}

━━━━━━━━━━━━━━━━━━━━━
⭐ *Confidence: {confidence}%*
⏰ {now}
⚡ Strategy: SMC Analysis
⚠️ Risk: 2% max per trade

🔗 [Binance Join करो](https://www.binance.com/activity/referral-entry/CPA?ref=CPA_009BQG4BOM)

📲 Telegram:
https://t.me/GlobalTraderPavan
━━━━━━━━━━━━━━━━━━━━━
"""

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ TELEGRAM_TOKEN or TELEGRAM_CHAT_ID missing from environment!")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id":                TELEGRAM_CHAT_ID,
        "text":                   message,
        "parse_mode":             "Markdown",
        "disable_web_page_preview": True
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        result = r.json()
        if result.get("ok"):
            print(f"✅ Signal sent: {symbol} {direction}")
            return True
        else:
            print(f"❌ Telegram error (send_signal): {result}")
            return False
    except Exception as e:
        print(f"❌ Send error: {e}")
        return False


def send_no_signal(reason="Market neutral"):
    """Jab signal nahi hai"""

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ TELEGRAM_TOKEN or TELEGRAM_CHAT_ID missing from environment!")
        return False

    now = datetime.now().strftime("%d %b %Y, %I:%M %p IST")
    message = f"""
⚪ *Market Update — GlobalTraderPavan*
━━━━━━━━━━━━━━━━━━━━━
📊 Market abhi neutral hai.
⏳ Koi confirmed signal nahi.
🛡️ Safe rahein — wait karein.

📝 Reason: {reason}
⏰ {now}
📲 @GlobalTraderPavan
━━━━━━━━━━━━━━━━━━━━━
"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id":    TELEGRAM_CHAT_ID,
        "text":       message,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        result = r.json()
        if result.get("ok"):
            print("⚪ No signal update sent")
            return True
        else:
            print(f"❌ Telegram error (send_no_signal): {result}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("AG-4 Signal Sender Testing...")
    test_data = {
        "symbol":       "BTCUSDT",
        "direction":    "LONG",
        "price":        64000,
        "change":       1.5,
        "rsi":          35,
        "funding_rate": -0.01,
        "open_interest":15000,
        "strength":     "Strong",
        "confidence":   85,
        "stop_loss":    62800,
        "target1":      65500,
        "target2":      67000
    }
    send_signal(test_data)
