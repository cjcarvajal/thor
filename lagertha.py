from string import punctuation
from unidecode import unidecode
from SPARQLWrapper import SPARQLWrapper, JSON
from gems import *
from model.relation import Relation
from model.entity import Entity

endpoint_url = "https://query.wikidata.org/sparql"


class PersonalKnowledge:

    non_words = list(punctuation)
    non_words.extend(['¿', '¡'])

    interesting_entity_types = [
        'CRIMINAL_CHARGE', 'LOCATION', 'MISC', 'ORGANIZATION', 'PERSON']

    def get_interesting_entities(self, tweets, popular_boundary, unusual_boundary):

        entities_to_search = []
        for tweet in tweets:
            entities_to_search.extend(
                [entity for entity in tweet.nee_entities if entity.entity_type in self.interesting_entity_types])

        processed_entities = self.__get_tf(entities_to_search)

        filtered_list = [
            e for e in processed_entities if e['score'] >= popular_boundary or e['score'] < unusual_boundary]
        filtered_list.sort(key=lambda e: e['score'], reverse=True)
        return [e['entity'] for e in filtered_list]

    def discover_semantic_relation(self, ranked_entity):
        try:
            return self.__query_info(ranked_entity)
        except Exception as e:
            print(e)
        return None

    def __get_tf(self, entities_to_search):
        tf_map = {}
        for entity in entities_to_search:
            if entity.text in tf_map:
                scored_entity = tf_map[entity.text]
                scored_entity['score'] += 1
                tf_map[entity.text] = scored_entity
            else:
                tf_map[entity.text] = {'entity': entity, 'score': 1}

        normalized_entity_list = []
        for key, value in tf_map.items():
            normalized_entity_list.append({'entity': value['entity'],
                                           'score': value['score']/len(entities_to_search)})
        return normalized_entity_list

    def __clean_text(self, text):
        cleaned_text = text.lower()
        cleaned_text = ''.join(
            [c for c in cleaned_text if c not in self.non_words])
        return cleaned_text

    def __query_info(self, entity):
        cleaned_text = self.__clean_text(entity.text)
        print(cleaned_text)
        if entity.entity_type == 'PERSON':
            return self.__get_semantic_relations_for_person(cleaned_text)
        return []

    def __get_semantic_relations_for_person(self, entity):
        relation_list = []
        results = self.__get_results(spouse_query.format(entity))
        relation_list.extend(self.__relation_list_builder(
            results, entity, 'conyugue de', 'PERSON', 'PERSON'))

        results = self.__get_results(political_party_query.format(entity))
        relation_list.extend(self.__relation_list_builder(
            results, entity, 'ha sido miembro de', 'PERSON', 'ORGANIZATION'))

        results = self.__get_results(education_query.format(entity))
        relation_list.extend(self.__relation_list_builder(
            results, entity, 'educado/a en', 'PERSON', 'ORGANIZATION'))

        results = self.__get_results(place_of_birth_query.format(entity))
        relation_list.extend(self.__relation_list_builder(
            results, entity, 'nació en', 'PERSON', 'LOCATION'))

        results = self.__get_results(positions_held_query.format(entity))
        relation_list.extend(self.__relation_list_builder(
            results, entity, 'ha sido', 'PERSON', 'TITLE'))

        return relation_list

    def __get_results(self, query):
        sparql = SPARQLWrapper(endpoint_url)
        sparql.setTimeout(2)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        return sparql.query().convert()

    def __relation_list_builder(self, query_results, entity_text, relation_text, first_entity_type, second_entity_type):
        relation_list = []
        for result in query_results['results']['bindings']:
            relation_list.append(
                Relation(Entity(first_entity_type, entity_text, -1), Entity(second_entity_type, result['info']['value'], -1), relation_text, []))
        return relation_list
