from model.relation import Relation
from unified_relations import final_relations
import unidecode


def seek_common_relations(possible_relation, interesting_entity_types):

    if (possible_relation.first_entity.entity_type in interesting_entity_types and
            possible_relation.second_entity.entity_type in interesting_entity_types):

        possible_unified_list = [
            x for x in final_relations if normalize_text(possible_relation.full_relation_text) in
            [normalize_text(nick) for nick in x['relation_nicknames']] + [x['relation_name']]]

        if possible_unified_list:
            return Relation(
                possible_relation.first_entity, possible_relation.second_entity,
                possible_unified_list[0]['relation_name'], [possible_relation.tweet])
    return None


def normalize_text(text):
    return unidecode.unidecode(text).lower()
