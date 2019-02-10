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
            else:
                print self.text
                print other.text
                tfidf_vectorizer = TfidfVectorizer(analyzer="char")
                tfidf_matrix = tfidf_vectorizer.fit_transform((self.text, other.text))
                cs = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)
                print cs[0][1]
                return cs[0][1] > 0.85
        return False

    def __hash__(self):
        return 1
        # return hash((self.type, self.text))

    __repr__ = __str__
