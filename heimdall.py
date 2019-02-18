from typing import List

import faust

from entity_extractor import EntityExtractor
import relation_extractor
from model.tweet import Tweet
from model.processed_tweets import ProcessedTweets

entity_extractor = EntityExtractor()

relation_seeker_threshold = 100

app = faust.App(
    'bifrost',
    broker='kafka://localhost:9092',
    value_serializer='raw'
)

principal_topic = app.topic('principal',value_type=Tweet)
entity_extraction_topic = app.topic('entity_extraction',value_type=Tweet)
relation_extraction_topic = app.topic('relation_extraction',value_type=ProcessedTweets)

processed_tweets_table = app.Table(name='processed_tweets_table',default=list,partitions=1)
tweets_with_entities_key = 'tweets_with_entities'

@app.agent(principal_topic,sink=[entity_extraction_topic])
async def start_processing(tweets):
    async for tweet in tweets:
        yield tweet


@app.agent(entity_extraction_topic)
async def extract_entities(tweets):
    async for tweet in tweets:
        tweet.nee_entities = entity_extractor.extract_entities(tweet.full_text)
        
        print ('Processed tweet ' + str(len(processed_tweets_table[tweets_with_entities_key])))
        if (len(processed_tweets_table[tweets_with_entities_key])) > relation_seeker_threshold:
            print ('Threshold for clustering reached')
            tweets_with_entities = processed_tweets_table[tweets_with_entities_key]
            processed_tweets_table[tweets_with_entities_key]=[]
            await extract_relations.send(value=ProcessedTweets(tweets_with_entities))
        tweets_with_entities = processed_tweets_table[tweets_with_entities_key]
        tweets_with_entities.append(tweet)
        processed_tweets_table[tweets_with_entities_key] = tweets_with_entities
        yield tweet

@app.agent(relation_extraction_topic)
async def extract_relations(processed_tweets):
    async for group in processed_tweets:
        posible,fixed = relation_extractor.discover_relations(group.tweets)
        print (posible)
        print ('***********************************')
        print (fixed)
