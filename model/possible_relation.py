import faust
from model.entity import Entity
from model.tweet import Tweet


class PossibleRelation(faust.Record, serializer='json'):
    full_relation_text: str
    clean_relation_text: str
    first_entity: Entity
    second_entity: Entity
    tweet: Tweet

    def __str__(self):
        separator = u'\n-----------------------------------------------------------------\n'
        description = u'Full Relation Text [{self.full_relation_text}] First Entity [{self.first_entity} Second entity [{self.second_entity}]'.format(
            self=self)
        return separator + description + separator

    __repr__ = __str__
