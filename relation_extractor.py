# -*- coding: utf-8 -*-

import numpy as np

from string import punctuation
from collections import Counter

from nltk import word_tokenize
from nltk.corpus import stopwords
from model.relation import Relation
from model.possible_relation import PossibleRelation

spanish_stopwords = stopwords.words('spanish')

non_words = list(punctuation)
non_words.extend(['¿', '¡'])
non_words.extend(map(str, range(10)))


def remove_stop_words(dirty_text):
    cleaned_text = ''
    for word in dirty_text.lower().split():
        if word in spanish_stopwords or word in non_words:
            continue
        else:
            cleaned_text += word + ' '
    return cleaned_text


def remove_punctuation(dirty_string):
    for word in non_words:
        dirty_string = dirty_string.replace(word, '')

    return dirty_string


def get_possible_relations(tweet):
    possible_relations = []
    entities_for_relations = tweet.nee_entities
    if entities_for_relations:
        for first, second in zip(entities_for_relations, entities_for_relations[1:]):
            try:
                text_in_between = tweet.full_text[(tweet.full_text.index(first.text) + len(
                    first.text)):tweet.full_text.index(second.text)]
                cleaned_text = remove_punctuation(text_in_between)
                cleaned_text = remove_stop_words(cleaned_text)
                possible_relations.append(PossibleRelation(
                    text_in_between.strip(), cleaned_text.strip(), first, second, tweet))
            except Exception as e:
                # Do nothing, expectable exception if no substring is founded
                pass
    return possible_relations
