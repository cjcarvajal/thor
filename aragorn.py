# For Frodo!!!

from model.relation import Relation
from collections import Counter


def find_relations(possible_popular_relations):
    discovered_relations = []
    for relation in possible_popular_relations:
        relation_text = find_key_strings(relation['text'])
        discovered_relations.append(Relation(relation['nodes'].entity_origin,
                                             relation['nodes'].entity_end,
                                             relation_text,
                                             3,
                                             []))
    return discovered_relations


def find_key_strings(text_list):
    counter = Counter(text_list)
    return counter.most_common(1)[0][0]
