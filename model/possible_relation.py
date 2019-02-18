class PossibleRelation:

    def __init__(self,full_relation_text,clean_relation_text,first_entity,second_entity,tweet):
        self.full_relation_text = full_relation_text
        self.clean_relation_text = clean_relation_text
        self.first_entity = first_entity
        self.second_entity = second_entity
        self.tweet = tweet

    def __str__(self):
        separator = u'\n-----------------------------------------------------------------\n'
        description = u'Full Relation Text [{self.full_relation_text}] First Entity [{self.first_entity} Second entity [{self.second_entity}]'.format(self=self)
        return separator + description + separator
    
    __repr__ = __str__