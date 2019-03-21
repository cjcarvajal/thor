# -*- coding: utf-8 -*-

from string import punctuation
from collections import Counter

from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.cluster.hierarchy import fcluster, linkage
from model.relation import Relation
from model.possible_relation import PossibleRelation

predefined_relations = ['y']


def seek_common_relations(possible_relation, interesting_entity_types):

    #print(possible_relation)
    if (possible_relation.first_entity.entity_type in interesting_entity_types and
            possible_relation.second_entity.entity_type in interesting_entity_types):
        if possible_relation.full_relation_text in predefined_relations:
            return Relation(
                possible_relation.first_entity, possible_relation.second_entity,
                possible_relation.full_relation_text, [possible_relation.tweet])
    return None
