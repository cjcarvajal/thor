import json
import ner
import requests


class EntityExtractor:

    vision_model = ner.SocketNER(host='localhost', port=9191)
    standfor_model_url = 'http://localhost:9000/'

    stanford_properties_map = {'annotators': 'ner', 'outputFormat': 'json'}
    stanford_params_map = {'properties': json.dumps(
        stanford_properties_map), 'pipelineLanguage': 'es'}

    def extract_entities(self, text):
        stanford_entities = self._extract_entities_with_standford(text)
        vision_entities = self._extract_entities_with_vision(text)
        return self.unify_entities(stanford_entities, vision_entities)

    def _extract_entities_with_standford(self, text):
        result = self.vision_model.get_entities(text)
        entities = []
        for key in result:
            for entity in result[key]:
                entities.append({'type': key, 'text': entity})
        return entities

    def _extract_entities_with_vision(self, text):
        r = requests.post(self.standfor_model_url,
                          params=self.stanford_params_map, data=text)
        result = r.json()['sentences'][0]['entitymentions']
        return [{'type': entity['ner'], 'text':entity['text']} for entity in result]

    def _unify_entities(self, stanford_entities, vision_entities):
        largest_list = []
        shortest_list = []

        if len(stanford_entities) > len(vision_entities):
            largest_list = stanford_entities
            shortest_list = vision_entities
        else:
            largest_list = vision_entities
            shortest_list = stanford_entities
