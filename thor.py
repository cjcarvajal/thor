# -*- coding: utf-8 -*-
from entity_extractor import EntityExtractor
import tweet_retreiver
import relation_extractor

entity_extractor = EntityExtractor()

tweets = tweet_retreiver.request_tweets('Hidroituango')

for tweet in tweets:
    tweet.nee_entities = entity_extractor.extract_entities(tweet.full_text)

#print tweets

clusters = relation_extractor.discover_relations(tweets)
#print clusters
