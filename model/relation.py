import faust
from typing import List
from model.entity import Entity
from model.tweet import Tweet


class Relation(faust.Record, serializer='json'):
    entity_origin: Entity
    entity_end: Entity
    relation_text: str
    tweets: List[Tweet]

    def __str__(self):
        separator = u'\n-----------------------------------------------------------------\n'
        origin = str(self.entity_origin)
        end = str(self.entity_end)
        description = u'Origin [' + origin + u'] Relation[{self.relation_text}]'.format(
            self=self) + u' End [' + end + u']'
        return separator + description + separator

    def __eq__(self, other):
        return self.entity_origin == other.entity_origin and self.entity_end == other.entity_end and self.relation_text == other.relation_text

    def __hash__(self):
        return hash((self.entity_origin, self.entity_end, self.relation_text))

    __repr__ = __str__
