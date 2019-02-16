import faust
from typing import List
from model.entity import Entity

class Tweet(faust.Record,serializer='json'):
    full_text: str
    nee_entities: List[Entity]

    def __str__(self):
        entities_text = u''
        for entity in self.nee_entities:
            entities_text += str(entity) + ' | '
        return u'Text {self.full_text}'.format(self=self) + u'\nnee_entities: [' + entities_text + u']' + '\n'
    __repr__ = __str__
