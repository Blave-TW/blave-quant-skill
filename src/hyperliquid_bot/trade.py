from hyperliquid.utils import constants
from hyperliquid.exchange import _get_dex
from .utils import setup
from .info import get_current_positions


def market_order(token, is_buy, sz, is_usd_base=True):
    """
    下市價單
    token: str, 交易對
    is_buy: bool, True 買入 False 賣出
    sz: float, 金額(USD) 或 token 數量
    is_usd_base: 是否以 USD 金額下單
    """
    _, info, exchange = setup(base_url=constants.MAINNET_API_URL, skip_ws=True)

    if is_usd_base:
        price = float(info.all_mids(_get_dex(token))[token])
        token_size = round(sz / price, 4)
    else:
        token_size = sz

    # 最小單檢查
    if token_size <= 0:
        return {"error": "token size too small"}

    order_result = exchange.market_open(token, is_buy, token_size)
    return order_result


def adjust_portfolio(target_portfolio, usd_base=True, min_usd_order=10):
    orders = []
    current_positions = get_current_positions()  # {token: USD 或 token 數量}

    # 合併所有 token：目標 + 現有持倉
    all_tokens = set(target_portfolio.keys()).union(current_positions.keys())

    for token in all_tokens:
        target_value = target_portfolio.get(token, 0)  # 如果沒設定目標，視為 0
        current_value = current_positions.get(token, 0)
        diff = target_value - current_value

        # 忽略小額差異
        if abs(diff) < min_usd_order:
            continue

        is_buy = diff > 0
        order_size = abs(diff)

        # 下單
        result = market_order(token, is_buy, order_size, is_usd_base=usd_base)
        orders.append(
            {
                "token": token,
                "action": "buy" if is_buy else "sell",
                "amount": order_size,
                "result": result,
            }
        )
    return orders
