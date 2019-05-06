from typing import List

import faust
import twitter_client
import aiohttp_cors

from entity_extractor import EntityExtractor
from lagertha import PersonalKnowledge
import relation_extractor
import entity_unifier
import odin
import aragorn
import mongo_test_client
from model.tweet import Tweet
from model.entity import Entity
from model.possible_relation import PossibleRelation
from model.popular_relation import PopularRelation
from model.empty_event import EmptyEvent

entity_extractor = EntityExtractor()
personal_knowledge = PersonalKnowledge()

semantic_enrichment_threshold = 100
semantic_enrichment_time_out = 60

popular_relations_text_length_threshold = 10

semantic_enrichment_popular_selector = 0.06
semantic_enrichment_unusual_selector = 0.016

interesting_entity_types = ['TITLE', 'PERCENT',
                            'MISC', 'PERSON', 'CRIMINAL_CHARGE', 'ORGANIZATION']

app = faust.App(
    'bifrost',
    broker='kafka://localhost:9092',
    value_serializer='raw',
    cors_options={'http://localhost:8000/': aiohttp_cors.ResourceOptions(
        expose_headers="*",
        allow_headers="*")}
)

principal_topic = app.topic('principal', value_type=Tweet)
entity_extraction_topic = app.topic('entity_extraction', value_type=Tweet)
entities_unification_topic = app.topic(
    'entities_unification', value_type=Tweet)
entity_ranking_topic = app.topic('entity_ranking', value_type=Tweet)

possible_relation_extraction_topic = app.topic(
    'possible_relation_extraction', value_type=Tweet)
common_relation_extraction_topic = app.topic(
    'common_relation_extraction', value_type=PossibleRelation)
cluster_relation_extraction_topic = app.topic(
    'cluster_relation_extraction', value_type=PossibleRelation)
popular_relation_extraction_topic = app.topic(
    'popular_relation_extraction', value_type=EmptyEvent)

reset_topic = app.topic('reset_topic', value_type=EmptyEvent)


semantic_relation_topic = app.topic(
    'semantic_relation', value_type=Entity)

thor_table = app.Table(
    name='last_supper', default=list, partitions=1)
visited_entities_key = 'visited_entities'
relations_key = 'relations'
account_resolved_key = 'account_resolved'
entity_counter_key = 'entity_counter'
popular_relations_key = 'popular_relations'


@app.agent(principal_topic, sink=[entity_extraction_topic])
async def start_processing(tweets):
    async for tweet in tweets:
        yield tweet


@app.agent(entity_extraction_topic, sink=[entities_unification_topic])
async def extract_entities(tweets):
    async for tweet in tweets:
        tweet.nee_entities = entity_extractor.extract_entities(tweet.full_text)
        yield tweet


@app.agent(entities_unification_topic, sink=[entity_ranking_topic, possible_relation_extraction_topic])
async def unify_entities(tweets):
    async for tweet in tweets:
        persisted_accounts = thor_table[account_resolved_key]

        if not persisted_accounts:
            persisted_accounts = {}

        tweet = entity_unifier.unify_entities_on_tweet(
            tweet, persisted_accounts)

        thor_table[account_resolved_key] = persisted_accounts
        entity_counter_list = thor_table[entity_counter_key]

        if not entity_counter_list:
            entity_counter_list = []

        for entity in tweet.nee_entities:
            founded = next(
                (x for x in entity_counter_list if x['name'] == entity.text), None)
            if founded:
                filtered_list = [
                    x for x in entity_counter_list if x['name'] != entity.text]
                founded['counter'] += 1
                filtered_list.append(founded)
                entity_counter_list = filtered_list
            else:
                founded = {'name': entity.text,
                           'type': entity.entity_type, 'counter': 1}
                entity_counter_list.append(founded)

        thor_table[entity_counter_key] = entity_counter_list
        yield tweet


@app.agent(entity_ranking_topic, sink=[semantic_relation_topic])
async def rank_entities(tweets_stream):
    async for tweets in tweets_stream.take(semantic_enrichment_threshold, within=semantic_enrichment_time_out):
        print('-----------Threshold for entity ranking reached-----------')
        for entity in personal_knowledge.get_interesting_entities(
                tweets, semantic_enrichment_popular_selector, semantic_enrichment_unusual_selector):
            yield entity


@app.agent(semantic_relation_topic)
async def discover_semantic_relations(entities):
    async for entity in entities:
        visited_entities = thor_table[visited_entities_key]
        saved_relations = set(thor_table[relations_key])
        if not visited_entities:
            visited_entities = []

        if not saved_relations:
            saved_relations = set([])

        if entity in visited_entities:
            continue
        else:
            response, relations = personal_knowledge.discover_semantic_relation(
                entity)
            if response == 'ok':
                visited_entities.append(entity)
                thor_table[visited_entities_key] = visited_entities
                if relations:
                    for relation in relations:
                        saved_relations.add(relation)

        thor_table[relations_key] = list(saved_relations)


@app.agent(possible_relation_extraction_topic, sink=[common_relation_extraction_topic, cluster_relation_extraction_topic])
async def get_possible_relations(processed_tweets):
    async for tweet in processed_tweets:
        posible_relations = relation_extractor.get_possible_relations(tweet)
        for relation in posible_relations:
            yield relation


@app.agent(common_relation_extraction_topic)
async def extract_common_relations(possible_relations_stream):
    async for possible_relation in possible_relations_stream:
        saved_relations = set(thor_table[relations_key])

        if not saved_relations:
            saved_relations = set([])

        relation = odin.seek_common_relations(
            possible_relation, interesting_entity_types)

        if relation:
            saved_relations.add(relation)
            thor_table[relations_key] = list(saved_relations)


@app.agent(cluster_relation_extraction_topic)
async def extract_relations_by_clustering(possible_relations_stream):
    async for possible_relation in possible_relations_stream:

        if possible_relation.clean_relation_text:

            popular_saved_relations = thor_table[popular_relations_key]

            popular = PopularRelation(
                possible_relation.first_entity, possible_relation.second_entity, 3)

            if not popular_saved_relations:
                popular_saved_relations = [{
                    'nodes': popular,
                    'text': [possible_relation.clean_relation_text]
                }]
            else:
                founded = next(
                    (x for x in popular_saved_relations if x['nodes'] == popular), None)
                if founded:
                    filtered_list = [
                        x for x in popular_saved_relations if x['nodes'] != popular]
                    temporal_list = founded['text']
                    temporal_list.append(
                        possible_relation.clean_relation_text)
                    founded['text'] = temporal_list
                    filtered_list.append(founded)
                else:
                    popular_saved_relations.append(
                        {
                            'nodes': popular,
                            'text': [possible_relation.clean_relation_text]
                        })

            thor_table[popular_relations_key] = popular_saved_relations

            await extract_popular_relations.cast(EmptyEvent(1))


@app.agent(popular_relation_extraction_topic)
async def extract_popular_relations(event_stream):
    async for event in event_stream:
        popular_saved_relations = thor_table[popular_relations_key]
        filtered_list = [
            x for x in popular_saved_relations if len(x['text'])
            > popular_relations_text_length_threshold]

        if filtered_list:
            print('-----------Starting popular relations extraction-----------')
            saved_relations = set(thor_table[relations_key])

            if not saved_relations:
                saved_relations = set([])

            retrieved_relations = set(aragorn.find_relations(filtered_list))
            saved_relations.update(retrieved_relations)

            print('aca')
            print(retrieved_relations)

            unprocessed_list = [
                x for x in popular_saved_relations if len(x['text'])
                <= popular_relations_text_length_threshold]

            thor_table[relations_key] = list(saved_relations)
            thor_table[popular_relations_key] = unprocessed_list


@app.agent(reset_topic)
async def reset_query(reset_event_stream):
    async for reset in reset_event_stream:
        print('-----------Deleting persisted relations-----------')
        thor_table[visited_entities_key] = []
        thor_table[relations_key] = []
        thor_table[entity_counter_key] = []
        thor_table[popular_relations_key] = []


@app.page('/relations')
async def get_relations(web, request):
    return web.json({'relations': thor_table[relations_key]},
                    headers={'Access-Control-Allow-Origin': '*'})


@app.page('/entities')
async def get_entities(web, request):
    return web.json({'entities_count': thor_table[entity_counter_key]},
                    headers={'Access-Control-Allow-Origin': '*'})


@app.page('/query/{keyword}')
async def analyze_tweets(self, request, keyword) -> None:
    print('-----------Starting analysis for {}-----------'.format(keyword))
    tweets = twitter_client.request_tweets(keyword)
    for tweet in tweets:
        await start_processing.cast(tweet)
    return self.json({'response': 'query started'}, headers={'Access-Control-Allow-Origin': '*'})

@app.page('/query-test/{keyword}')
async def query_test(self, request, keyword) -> None:
    print('-----------Starting test for {}-----------'.format(keyword))
    tweets = mongo_test_client.request_tweets(keyword)
    for tweet in tweets:
        await start_processing.cast(tweet)
    return self.json({'response': 'query started'}, headers={'Access-Control-Allow-Origin': '*'})

@app.page('/reset')
async def reset_table(self, request):
    print('-----------Deleting previous search-----------')
    await reset_query.cast(EmptyEvent(0))
    return self.json({'response': 'reseted'}, headers={'Access-Control-Allow-Origin': '*'})


@app.page('/test')
async def test(web, request):
    return web.json({'entities_count': thor_table[popular_relations_key]},
                    headers={'Access-Control-Allow-Origin': '*'})
