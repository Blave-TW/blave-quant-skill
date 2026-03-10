import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd

load_dotenv()


class ThreadsAPI:
    def __init__(self):
        self.user_id = os.getenv("threads_user_id")
        self.access_token = os.getenv("threads_access_token")
        self.app_secret = os.getenv("threads_secret")
        self.api_url = "https://graph.threads.net/v1.0"
        self.limit = 5
        self.backfill_date_interval = 7

    def get_threads_df(self) -> pd.DataFrame:
        # set up params
        start_date_dt = datetime.now() - timedelta(days=self.backfill_date_interval)

        resp = requests.get(
            f"{self.api_url}/{self.user_id}/threads",
            params={
                "fields": "id,permalink,username,timestamp,text",
                "since": str(start_date_dt.isoformat()),
                "access_token": self.access_token,
                "limit": self.limit if self.limit else 100,
            },
        )
        if resp.status_code != 200:
            raise Exception(resp.json())

        df = pd.DataFrame.from_dict(resp.json().get("data", []))

        return df

    def get_threads_insights_by_id(self, thread_id: str) -> dict:
        insight_metric_list = ["views", "likes", "replies", "reposts", "quotes"]

        resp = requests.get(
            f"{self.api_url}/{thread_id}/insights",
            params={
                "metric": ",".join(insight_metric_list),
                "access_token": self.access_token,
            },
        )

        if resp.status_code != 200:
            raise Exception(resp.json())

        metric_dict = {}

        for data in resp.json().get("data", []):
            metric_dict[data.get("name")] = data.get("values")[0].get("value")
            continue
        return metric_dict

    def arrange_insight_table(self) -> pd.DataFrame:
        INSIGHT_METRIC_LIST = [
            "views",
            "likes",
            "replies",
            "reposts",
            "quotes",
            "followers_count",
            # "follower_demographics",
        ]

        # get threads
        df_threads = self.get_threads_df()

        # get insights
        df_threads["insights"] = df_threads["id"].apply(self.get_threads_insights_by_id)

        # create columns for insights
        for metric in INSIGHT_METRIC_LIST:
            df_threads[metric] = df_threads["insights"].apply(
                lambda dict: dict.get(metric)
            )
            continue

        # drop insights column
        df_threads.drop(columns=["insights"], inplace=True)

        return df_threads

    def create_container(self, text=None, image_url=None, reply_to_id=None):

        params = {
            "access_token": self.access_token,
        }

        if text:
            params["text"] = text
            params["media_type"] = "TEXT"

        if image_url:
            params["image_url"] = image_url
            params["media_type"] = "IMAGE"

        if reply_to_id:
            params["reply_to_id"] = reply_to_id

        resp = requests.post(
            f"{self.api_url}/{self.user_id}/threads",
            params=params,
        )

        if resp.status_code != 200:
            raise Exception(resp.json())

        return resp.json()

    def publish_container(self, creation_id):

        resp = requests.post(
            f"{self.api_url}/{self.user_id}/threads_publish",
            params={
                "creation_id": creation_id,
                "access_token": self.access_token,
            },
        )

        if resp.status_code != 200:
            raise Exception(resp.json())

        return resp.json()

    def create_text_post(self, text: str):

        container = self.create_container(text=text)

        creation_id = container["id"]

        return self.publish_container(creation_id)
