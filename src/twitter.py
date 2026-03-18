import os
import tweepy
from dotenv import load_dotenv

load_dotenv()


def get_client():
    return tweepy.Client(
        consumer_key=os.getenv("twitter_api_key"),
        consumer_secret=os.getenv("twitter_api_secret"),
        access_token=os.getenv("twitter_access_token"),
        access_token_secret=os.getenv("twitter_access_token_secret"),
    )


def create_tweet(text: str):
    client = get_client()
    response = client.create_tweet(text=text)
    return {"id": response.data["id"], "text": response.data["text"]}
