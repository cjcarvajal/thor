import pymongo
import json
import os
from model.tweet import Tweet

client = pymongo.MongoClient()
db = client.activism_test_data


def request_tweets(term):
    tweets = db.tweets.find()
    filtered_list = []

    for tweet in tweets:
        text = ''
        if 'retweeted_status' in tweet:
            text = tweet['retweeted_status']['full_text']
        else:
            text = tweet['full_text']
        if term in text:
            filtered_list.append(text)

    return [Tweet(text, []) for text in filtered_list]


request_tweets('Petro')
