from lagertha import PersonalKnowledge
import relation_extractor
import entity_unifier
import odin
from model.tweet import Tweet
from model.entity import Entity
from model.processed_tweets import ProcessedTweets
from model.possible_relation import PossibleRelation
from model.empty_event import EmptyEvent

personal_knowledge = PersonalKnowledge()


def discover_semantic_relations():
    entity = Entity('PERSON', 'iván Duque márquez', 0)
    response, relations = personal_knowledge.discover_semantic_relation(
        entity)
    print(relations)

discover_semantic_relations()
