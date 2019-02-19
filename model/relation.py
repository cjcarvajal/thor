class Relation:
    def __init__(self, entity_origin, entity_end, relation,tweets):
        self.entity_origin = entity_origin
        self.entity_end = entity_end
        self.relation = relation
        self.tweets = tweets

    def __str__(self):
        separator = u'\n-----------------------------------------------------------------\n'
        origin = str(self.entity_origin)
        end = str(self.entity_end)
        description = u'Origin [' + origin + u'] Relation[{self.relation}]'.format(self=self) + u' End [' + end + u']'
        return separator + description + separator

    def __eq__(self, other):
        return self.entity_origin == other.entity_origin and self.entity_end == other.entity_end and self.relation == other.relation

    def __hash__(self):
        return hash((self.entity_origin, self.entity_end, self.relation))

    __repr__ = __str__
