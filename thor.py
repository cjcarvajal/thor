import asyncio

import twitter_client
from heimdall import start_processing
from model.tweet import Tweet
import time


async def analyze_tweets() -> None:
    tweets = twitter_client.request_tweets('bancolombia')
    for tweet in tweets:
        await start_processing.cast(tweet)

if __name__ == '__main__':
    for i in range(1,2):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(analyze_tweets())
        print('go')
        time.sleep(60)
