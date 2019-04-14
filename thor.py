import asyncio

import twitter_client
from heimdall import start_processing
from model.tweet import Tweet
import time


async def analyze_tweets() -> None:
    tweets = twitter_client.request_tweets('Uribe')
    for tweet in tweets:
        await start_processing.cast(tweet)