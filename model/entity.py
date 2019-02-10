from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Entity:
    def __init__(self, entity_type, text):
        self.type = entity_type
        self.text = text

    def __str__(self):
        return 'Type: ' + self.type + ' ' + 'Text: ' + self.text

    def __eq__(self, other):
        if self.type == other.type:
            if self.text == other.text:
                return True
        return False

    def __hash__(self):
        return 1
        # return hash((self.type, self.text))

    __repr__ = __str__
