class Tweet:
    def __init__(self, text):
        self.full_text = text
        self.nee_entities = []

    def __str__(self):
        entities_text = u''
        for entity in self.nee_entities:
            entities_text += str(entity) + ' | '
        return u'Text {self.full_text}'.format(self=self) + u'\nnee_entities: [' + entities_text + u']' + '\n'
    __repr__ = __str__
