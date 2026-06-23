# ==========================================
# MASTER ORCHESTRATOR
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
from agents.ag1_market import run_agent1
from agents.ag4_signal import send_signal, send_no_signal


def calculate_targets(price, direction):
    """SL aur Targets calculate karo"""
    if direction == "LONG":
        stop_loss = round(price * 0.985, 2)
        target1   = round(price * 1.02, 2)
        target2   = round(price * 1.035, 2)
    elif direction == "SHORT":
        stop_loss = round(price * 1.015, 2)
        target1   = round(price * 0.98, 2)
        target2   = round(price * 0.965, 2)
    else:
        stop_loss = price
        target1   = price
        target2   = price
    return stop_loss, target1, target2


def calculate_confidence(data):
    """Confidence % calculate karo"""
    score = 0

    # RSI
    if data['rsi'] < 30 or data['rsi'] > 70:
        score += 35
    elif data['rsi'] < 40 or data['rsi'] > 60:
        score += 20

    # Volume
    if data['volume_ratio'] > 150:
        score += 25
    elif data['volume_ratio'] > 120:
        score += 10

    # Funding Rate
    if abs(data['funding_rate']) > 0.05:
        score += 25
    elif abs(data['funding_rate']) > 0.01:
        score += 15

    # Direction
    if data['direction'] != "NEUTRAL":
        if data['strength'] == "Strong":
            score += 15
        else:
            score += 5

    return min(score, 100)


def run_system():
    """Main system loop"""
    if not TRADING_ACTIVE:
        print("⏹️ Trading band hai")
        return

    print("\n" + "="*50)
    print("🚀 GlobalTraderPavan System Check")
    print("="*50)

    signal_sent = False

    for coin in COINS:
        print(f"\n📊 {coin} analyze ho raha hai...")

        # Agent 1
        market = run_agent1(coin)

        if market['status'] == 'error':
            print(f"❌ {coin}: {market['message']}")
            continue

        # Confidence
        confidence = calculate_confidence(market)
        market['confidence'] = confidence

        # Targets
        sl, t1, t2 = calculate_targets(
            market['price'],
            market['direction']
        )
        market['stop_loss']   = sl
        market['target1']     = t1
        market['target2']     = t2
        market['min_fund']    = MIN_FUND_USDT
        market['max_fund']    = MAX_FUND_USDT

        print(f"✅ {coin}:")
        print(f"   Price      : ${market['price']:,}")
        print(f"   RSI        : {market['rsi']}")
        print(f"   Direction  : {market['direction']}")
        print(f"   Strength   : {market['strength']}")
        print(f"   Confidence : {confidence}%")

        # Signal decision
        if (confidence >= CONFIDENCE_MINIMUM and
                market['direction'] != "NEUTRAL"):
            print(f"📤 Signal bhej raha hoon!")
            send_signal(market)
            signal_sent = True
            time.sleep(2)
        else:
            print(f"⏳ Confidence kam: {confidence}%")

    if not signal_sent:
        send_no_signal("Koi confirmed signal nahi mila")

    print("\n✅ Check complete!")


if __name__ == "__main__":
    print("=" * 50)
    print("🌍 GlobalTraderPavan Master System")
    print("👤 Owner: Pavankumar Madavi")
    print("🏢 niDar Marketing And Services")
    print("📍 Sadak Arjuni, Gondia, Maharashtra")
    print("=" * 50)

    # Pehle turant chalao
    run_system()

    # Har 5 minute me chalao
    schedule.every(5).minutes.do(run_system)

    print("\n⏰ System scheduled - har 5 min me check")

    while True:
        schedule.run_pending()
        time.sleep(1)