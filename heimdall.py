import faust
from entity_extractor import EntityExtractor
from model.tweet import Tweet

entity_extractor = EntityExtractor()

app = faust.App(
    'bifrost',
    broker='kafka://localhost:9092',
    value_serializer='raw',
)

principal_topic = app.topic('principal',value_type=Tweet)
entity_extraction_topic = app.topic('entity_extraction',value_type=Tweet)
relation_extraction_topic = app.topic('relation_extraction',value_type=Tweet)

@app.agent(principal_topic,sink=[entity_extraction_topic])
async def start_processing(tweets):
    async for tweet in tweets:
        yield tweet


@app.agent(entity_extraction_topic,sink=[relation_extraction_topic])
async def extract_entities(tweets):
    async for tweet in tweets:
        tweet.nee_entities = entity_extractor.extract_entities(tweet.full_text)
        yield tweet

