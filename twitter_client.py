import requests
import json
from model.tweet import Tweet

token = '{your twitter token}'
tweets_search_url = 'https://api.twitter.com/1.1/search/tweets.json'
user_search_url = 'https://api.twitter.com/1.1/users/lookup.json'

puerto_lopez_geocode = '4.0913971,-72.9734281'
colombian_radius = '800km'
geocode_param = puerto_lopez_geocode + ',' + colombian_radius


def request_tweets(subject):
    params_map = {'q': subject, 'tweet_mode': 'extended',
                  'count': 100, 'geocode': geocode_param}
    headers = {'Authorization': token}
    r = requests.get(tweets_search_url, params=params_map, headers=headers)
    result = r.json()
    return [Tweet(tweet['retweeted_status']['full_text'], []) if 'retweeted_status' in tweet
            else Tweet(tweet['full_text'], []) for tweet in result['statuses']]


def get_user_by_handle(subject):
    params_map = {'screen_name': subject}
    headers = {'Authorization': token}
    r = requests.get(user_search_url, params=params_map, headers=headers)
    result = r.json()
    return result
