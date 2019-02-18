import faust

from typing import List
from model.tweet import Tweet

class ProcessedTweets(faust.Record,serializer='json'):
    tweets: List[Tweet]