import os
import requests
from dotenv import load_dotenv


class DataFetcher:
    def __init__(self):
        load_dotenv()

        self.api_key = os.getenv("blave_api_key")
        self.secret_key = os.getenv("blave_secret_key")

    def get_latest_alpha(self, indicator, symbol, period="5min", **kwargs):
        url = f"https://api.blave.org/{indicator}/get_alpha"
        headers = {
            "api-key": self.api_key,
            "secret-key": self.secret_key,
        }

        params = {
            "symbol": symbol,
            "period": period,
        }

        # 加入額外參數
        params.update(kwargs)

        result = {}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=60)
            response.raise_for_status()

            data = response.json().get("data", {})

            alpha = data.get("alpha", [])
            if not alpha:
                print("沒有取得 alpha 資料")
                return None

            result["latest_alpha"] = alpha[-1]

            stat = data.get("stat")
            if stat:
                result["analysis_statistics"] = stat
            return result

        except requests.RequestException as e:
            print(f"API 請求失敗: {e}")
            return None
