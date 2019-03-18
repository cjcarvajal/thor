from typing import List

import faust

from entity_extractor import EntityExtractor
from lagertha import PersonalKnowledge
import relation_extractor
import entity_unifier
from model.tweet import Tweet
from model.entity import Entity
from model.processed_tweets import ProcessedTweets

entity_extractor = EntityExtractor()
personal_knowledge = PersonalKnowledge()

relation_seeker_threshold = 100

semantic_enrichment_threshold = 100
semantic_enrichment_time_out = 60

semantic_enrichment_popular_selector = 0.06
semantic_enrichment_unusual_selector = 0.016

app = faust.App(
    'bifrost',
    broker='kafka://localhost:9092',
    value_serializer='raw'
)

principal_topic = app.topic('principal', value_type=Tweet)
entity_extraction_topic = app.topic('entity_extraction', value_type=Tweet)
entities_unification_topic = app.topic(
    'entities_unification', value_type=Tweet)
entity_ranking_topic = app.topic('entity_ranking', value_type=Tweet)
relation_extraction_topic = app.topic(
    'relation_extraction', value_type=ProcessedTweets)
semantic_relation_topic = app.topic(
    'semantic_relation', value_type=Entity)
processed_tweets_table = app.Table(
    name='processed_tweets_table', default=list, partitions=1)

tweets_with_entities_key = 'tweets_with_entities'


@app.agent(principal_topic, sink=[entity_extraction_topic])
async def start_processing(tweets):
    async for tweet in tweets:
        yield tweet


@app.agent(entity_extraction_topic, sink=[entities_unification_topic])
async def extract_entities(tweets):
    async for tweet in tweets:
        tweet.nee_entities = entity_extractor.extract_entities(tweet.full_text)
        yield tweet


@app.agent(entities_unification_topic, sink=[entity_ranking_topic])
async def unify_entities(tweets):
    async for tweet in tweets:
        tweet = entity_unifier.unify_entities_on_tweet(tweet)
        yield tweet


@app.agent(entity_ranking_topic, sink=[semantic_relation_topic])
async def rank_entities(tweets_stream):
    async for tweets in tweets_stream.take(semantic_enrichment_threshold, within=semantic_enrichment_time_out):
        print('Threshold for semantic enrichment reached')
        print('Discovering interesting entities')
        for entity in personal_knowledge.get_interesting_entities(
                tweets, semantic_enrichment_popular_selector, semantic_enrichment_unusual_selector):
            yield entity


@app.agent(semantic_relation_topic)
async def discover_semantic_relations(entities):
    async for entity in entities:
        relations = personal_knowledge.discover_semantic_relation(entity)
        if relations:
            for relation in relations:
                print(relation)


@app.agent(relation_extraction_topic)
async def extract_relations(processed_tweets):
    async for group in processed_tweets:
        posible, fixed, clusters = relation_extractor.discover_relations(
            group.tweets)
        print('***********************************')
        print(clusters)
