import faust

class Entity(faust.Record,serializer='json'):
    entity_type :str
    text :str
    index :int

    def __str__(self):
        return u'type: {self.entity_type}, text: {self.text}, index: {self.index}'.format(self=self)

    def __eq__(self, other):
        if self.entity_type == other.entity_type:
            if self.text == other.text:
                return True
        return False

    def __hash__(self):
        return hash((self.entity_type, self.text))

    __repr__ = __str__
