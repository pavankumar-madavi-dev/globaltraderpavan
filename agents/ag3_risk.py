# ==========================================
# Agent 3 — Risk & Money Management Engine
# GlobalTraderPavan Trading System
# Owner: Pavankumar Madavi
# niDar Marketing And Services
# Sadak Arjuni, Gondia, Maharashtra
# ==========================================

def calculate_risk_parameters(symbol, current_price, direction):
    """Entry Price के आधार पर Stop Loss, Target और Safe Leverage तय करें"""
    try:
        # एक स्टैंडर्ड 1.5% का रिस्क और 3.5% का रिवॉर्ड मानकर चलते हैं (Risk-to-Reward ~ 1:2.3)
        risk_percent = 0.015  # 1.5%
        reward_percent = 0.035 # 3.5%

        if direction == "LONG":
            stop_loss = round(current_price * (1 - risk_percent), 2)
            take_profit = round(current_price * (1 + reward_percent), 2)
        elif direction == "SHORT":
            stop_loss = round(current_price * (1 + risk_percent), 2)
            take_profit = round(current_price * (1 - reward_percent), 2)
        else:
            return {"status": "ignored", "message": "Neutral direction context, no risk mapping needed."}

        # रिस्क-टू-रिवॉर्ड रेशियो चेक करें
        risk_dist = abs(current_price - stop_loss)
        reward_dist = abs(take_profit - current_price)
        rr_ratio = round(reward_dist / risk_dist, 2) if risk_dist > 0 else 0

        # सुरक्षित लेवरेज तय करना (BTC/ETH के लिए 5x-10x, बाकी एल्टकॉइन्स के लिए 3x)
        coin = symbol.replace("USDT", "")
        if coin in ["BTC", "ETH"]:
            recommended_leverage = "5x to 10x"
        else:
            recommended_leverage = "3x"

        return {
            "status": "ok",
            "symbol": symbol,
            "direction": direction,
            "entry_price": current_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "risk_reward_ratio": f"1:{rr_ratio}",
            "recommended_leverage": recommended_leverage,
            "risk_status": "APPROVED ✅" if rr_ratio >= 2.0 else "REJECTED ❌ (Bad R:R)"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def run_agent3(symbol="BTCUSDT", current_price=65000.0, direction="LONG"):
    """Agent 3 का मुख्य एग्जीक्यूशन पॉइंट"""
    return calculate_risk_parameters(symbol, current_price, direction)

# लोकल टेस्टिंग के लिए
if __name__ == "__main__":
    print("🛡️ AG-3 Risk & Money Management Agent Testing...")
    # टेस्ट 1: वैलिड लॉन्ग ट्रेड
    res1 = run_agent3("BTCUSDT", 65000.0, "LONG")
    print(f"\n🪙 Asset: {res1['symbol']} ({res1['direction']})")
    print(f"   Entry Price : ${res1['entry_price']}")
    print(f"   Stop Loss   : ${res1['stop_loss']}")
    print(f"   Take Profit : ${res1['take_profit']}")
    print(f"   R:R Ratio   : {res1['risk_reward_ratio']}")
    print(f"   Leverage    : {res1['recommended_leverage']}")
    print(f"   Risk Status : {res1['risk_status']}")

