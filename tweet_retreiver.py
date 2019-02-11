import requests
import json
from model.tweet import Tweet

token = 'Bearer AAAAAAAAAAAAAAAAAAAAACgz0AAAAAAAPET1dlYoHEGiafh6mvMeY7uUde0%3Dz1KrBPMxcukclc0U6TgkFzmmb7Up4FlARaYwsOqHpjkgWxQvkd'
base_url = 'https://api.twitter.com/1.1/search/tweets.json'


def request_tweets(subject):
    params_map = {'q': subject, 'tweet_mode': 'extended', 'count': 100}
    headers = {'Authorization': token}
    r = requests.get(base_url, params=params_map, headers=headers)
    result = r.json()
    return [Tweet(tweet['retweeted_status']['full_text']) if 'retweeted_status' in tweet
            else Tweet(tweet['full_text']) for tweet in result['statuses']]
