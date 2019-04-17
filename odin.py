from model.relation import Relation
from unified_relations import final_relations
from difflib import SequenceMatcher
import unidecode


def seek_common_relations(possible_relation, interesting_entity_types):

    if (possible_relation.first_entity.entity_type in interesting_entity_types and
            possible_relation.second_entity.entity_type in interesting_entity_types):

        possible_relation_normalized = normalize_text(
            possible_relation.full_relation_text)

        possible_unified_list = []
        for relation in final_relations:
            for nick in relation['relation_nicknames']:
                similarity = calculate_similitude(
                    possible_relation_normalized, normalize_text(nick))
                if(similarity) >= 0.8:
                    possible_unified_list.append(
                        {'relation': relation['relation_name'], 'score': similarity})

        if possible_unified_list:
            possible_unified_list.sort(key=lambda x: x['score'], reverse=True)
            return Relation(
                possible_relation.first_entity, possible_relation.second_entity,
                possible_unified_list[0]['relation'], 2, [possible_relation.tweet])
    return None


def normalize_text(text):
    return unidecode.unidecode(text).lower()


def calculate_similitude(text_one, text_two):
    return SequenceMatcher(None, text_one, text_two, False).ratio()
