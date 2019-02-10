import json
import ner
import requests
from model.entity import Entity

class EntityExtractor:

    vision_model = ner.SocketNER(host='localhost', port=9191)
    standfor_model_url = 'http://localhost:9000/'

    stanford_properties_map = {'annotators': 'ner', 'outputFormat': 'json'}
    stanford_params_map = {'properties': json.dumps(
        stanford_properties_map), 'pipelineLanguage': 'es'}

    def extract_entities(self, text):
        stanford_entities = self._extract_entities_with_standford(text)
        vision_entities = self._extract_entities_with_vision(text)
        print stanford_entities
        print vision_entities
        print self._unify_entities(stanford_entities, vision_entities)

    def _extract_entities_with_standford(self, text):
        result = self.vision_model.get_entities(text)
        entities = []
        for key in result:
            for entity in result[key]:
                e = Entity(key, entity)
                entities.append(e)
        return entities

    def _extract_entities_with_vision(self, text):
        r = requests.post(self.standfor_model_url,
                          params=self.stanford_params_map, data=text)
        result = r.json()['sentences'][0]['entitymentions']
        return [Entity(entity['ner'], entity['text']) for entity in result]

    def _unify_entities(self, stanford_entities, vision_entities):
        return set(stanford_entities + vision_entities)
