class Entity:
    def __init__(self, entity_type, text, index):
        self.type = entity_type
        self.text = text
        self.index = index

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return u'type: {self.type}, text: {self.text}, index: {self.index}'.format(self=self)

    def __eq__(self, other):
        if self.type == other.type:
            if self.text == other.text:
                return True
        return False

    def __hash__(self):
        return hash((self.type, self.text))

    __repr__ = __str__
