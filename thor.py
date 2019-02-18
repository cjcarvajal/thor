import asyncio

import tweet_retreiver
from heimdall import start_processing
from model.tweet import Tweet

async def analyze_tweets() -> None:
    tweets = tweet_retreiver.request_tweets('Hidroituango')
    for tweet in tweets:
        await start_processing.cast(tweet)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(analyze_tweets())
