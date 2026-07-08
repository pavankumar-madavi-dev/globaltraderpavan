
import time
import schedule

from config import (
    TRADING_ACTIVE,
    CONFIDENCE_MINIMUM,
    COINS
)

from agents.ag1_market import run_agent1
from agents.ag2_options import run_agent2
from agents.ag3_risk import run_agent3
from agents.ag4_signal import send_signal, send_no_signal
from agents.ag5_news import run_agent5
from agents.ag6_orderflow import run_agent6
from agents.ag7_fundamentals import run_agent7


def normalize_bias(value):
    """
    LONG / SHORT / BULLISH / BEARISH
    ko ek common format me convert kare
    """
    value = str(value).upper()

    if "LONG" in value or "BULLISH" in value:
        return "LONG"

    if "SHORT" in value or "BEARISH" in value:
        return "SHORT"

    return "NEUTRAL"


def calculate_7agent_confidence(ag1, ag2, ag5, ag6, ag7):

    score = 0

    ag1_bias = normalize_bias(ag1.get("direction"))
    ag2_bias = normalize_bias(ag2.get("options_bias"))
    ag5_bias = normalize_bias(ag5.get("market_bias"))
    ag6_bias = normalize_bias(ag6.get("order_flow_bias"))

    # AG1 Technical
    if ag1_bias != "NEUTRAL":
        score += 30 if ag1.get("strength") == "Strong" else 15

    # AG2 Options
    if ag2_bias == ag1_bias:
        score += 15

    # AG5 News
    if ag5_bias == ag1_bias:
        score += 20
    elif ag5_bias == "NEUTRAL":
        score += 10

    # AG6 Order Flow
    if ag6_bias == ag1_bias:
        score += 20

    # AG7 Fundamentals
    safety = ag7.get("safety_score", 0)

    if safety >= 70:
        score += 15
    elif safety >= 45:
        score += 8

    return min(score, 100)


def run_system():

    if not TRADING_ACTIVE:
        print("⏹ Trading Disabled")
        return

    print("\n" + "=" * 60)
    print("🚀 GlobalTraderPavan — 7-Agent Scan")
    print("=" * 60)

    signal_sent = False

    for coin in COINS:

        print(f"\n📊 {coin} scan started...")

        ag1 = run_agent1(coin)

        if ag1.get("status") != "ok":
            print(f"❌ AG1 Error: {ag1}")
            continue

        direction = normalize_bias(ag1.get("direction"))

        if direction == "NEUTRAL":
            print("⏳ Neutral Market")
            continue

        ag2 = run_agent2(coin)
        ag5 = run_agent5(coin)
        ag6 = run_agent6(coin)
        ag7 = run_agent7(coin)

        confidence = calculate_7agent_confidence(
            ag1,
            ag2,
            ag5,
            ag6,
            ag7
        )

        risk = run_agent3(
            coin,
            ag1["price"],
            direction
        )

        if risk.get("status") != "ok":
            print("❌ Risk Agent Failed")
            continue

        print("\n🎯 Analysis Complete")
        print(f"RSI: {ag1['rsi']}")
        print(f"Direction: {direction}")
        print(f"News: {ag5.get('market_bias')}")
        print(f"OrderFlow: {ag6.get('order_flow_bias')}")
        print(f"Confidence: {confidence}%")

        packet = {
            "symbol": coin,
            "direction": direction,
            "price": ag1["price"],
            "change": ag1["change"],
            "rsi": ag1["rsi"],
            "funding_rate": ag1["funding_rate"],
            "open_interest": ag1["open_interest"],
            "strength": ag1["strength"],
            "confidence": confidence,
            "stop_loss": risk["stop_loss"],
            "target1": risk["take_profit"],
            "target2": round(
    risk["take_profit"] * (1.01 if direction == "LONG" else 0.99),
    2
)
}

        if confidence >= CONFIDENCE_MINIMUM:

            print("🚀 SIGNAL FOUND")
            send_signal(packet)
            signal_sent = True

        else:

            print(
                f"⏳ Rejected ({confidence}% < {CONFIDENCE_MINIMUM}%)"
            )

    # Neutral market message disabled
    # if not signal_sent:
    # send_no_signal("All filters not aligned")
    

    print("\n✅ Scan Complete")


if __name__ == "__main__":

    print("=" * 50)
    print("🌍 GlobalTraderPavan")
    print("=" * 50)

    run_system()

    schedule.every(5).minutes.do(run_system)

    while True:
        schedule.run_pending()
        time.sleep(1)
