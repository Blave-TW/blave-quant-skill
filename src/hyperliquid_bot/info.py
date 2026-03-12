import os
from dotenv import load_dotenv
from hyperliquid.info import Info
from hyperliquid.utils import constants


def get_account_value():
    load_dotenv()

    result = {}
    info = Info(constants.MAINNET_API_URL, skip_ws=True)

    # spot
    spot_user_state = info.spot_user_state(os.getenv("arbitrum_address"))
    if spot_user_state:
        result["spot"] = spot_user_state

    # perp
    user_state = info.user_state(os.getenv("arbitrum_address"))
    if user_state:
        result["perp"] = user_state
    return result


def get_current_positions():
    """
    將 get_account_value() 輸出轉成 {token: USD} 格式
    只取 perpetual positions
    """
    positions = {}
    account_value = get_account_value()
    perp_positions = account_value.get("perp", {}).get("assetPositions", [])
    for p in perp_positions:
        token = p["position"]["coin"]
        usd_value = float(p["position"]["positionValue"])
        positions[token] = usd_value
    return positions


if __name__ == "__main__":
    print(get_account_value())
