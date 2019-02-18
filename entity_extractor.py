import json
import ner
import requests
from model.entity import Entity
import re


class EntityExtractor:

    vision_model = ner.SocketNER(host='localhost', port=9191)
    standfor_model_url = 'http://localhost:9000/'

    stanford_properties_map = {'annotators': 'ner', 'outputFormat': 'json'}
    stanford_params_map = {'properties': json.dumps(
        stanford_properties_map), 'pipelineLanguage': 'es'}

    def extract_entities(self, text):
        stanford_entities = self._extract_entities_with_standford(text)
        vision_entities = self._extract_entities_with_vision(text)
        unified_entities = self._unify_entities(
            stanford_entities, vision_entities)
        return self._order_entities(unified_entities, text)

    def _extract_entities_with_vision(self, text):
        result = self.vision_model.get_entities(text)
        entities = []
        for key in result:
            for entity in result[key]:
                e = Entity(key, entity, 0)
                entities.append(e)
        return entities

    def _extract_entities_with_standford(self, text):
        r = requests.post(self.standfor_model_url,
                          params=self.stanford_params_map, data=text.encode('utf-8'))
        result = r.json()['sentences'][0]['entitymentions']
        return [Entity(entity['ner'], entity['text'], 0) for entity in result]

    def _unify_entities(self, stanford_entities, vision_entities):
        if not stanford_entities:
            return vision_entities
        return set(stanford_entities + vision_entities)

    def _order_entities(self, unified_entities, text):
        # remove duplicated entities
        unique_entities = set(unified_entities)
        for entity in unique_entities:
            entity.index = [m.start() for m in re.finditer(entity.text, text)]
        entities_with_index_normalized = []
        for entity_indexed in unique_entities:
            if len(entity_indexed.index) > 0:
                for index in entity_indexed.index:
                    entities_with_index_normalized.append(
                        Entity(entity_indexed.entity_type, entity_indexed.text, index))
        entities_with_index_normalized.sort(key=lambda x: x.position)
        return entities_with_index_normalized
