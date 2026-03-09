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
