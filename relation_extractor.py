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

interesting_entity_types = ['TITLE', 'PERCENT',
                            'MISC', 'PERSON', 'CRIMINAL_CHARGE', 'ORGANIZATION']

predefined_relations = ['y', 'responde por', 'cuando dices q',
                        'pintaron de negro', 'debe estar q se revienta de la ira, porq el']

spanish_stopwords = stopwords.words('spanish')

non_words = list(punctuation)
non_words.extend(['¿', '¡'])
non_words.extend(map(str, range(10)))

stemmer = SnowballStemmer('spanish')


def tokenize(text):
    text = ''.join([c for c in text if c not in non_words])
    tokens = word_tokenize(text)

    try:
        stems = stem_tokens(tokens, stemmer)
    except Exception as e:
        print(e)
        print(text)
        stems = ['']
    return stems


def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed


vectorizer = TfidfVectorizer(
    analyzer='word',
    tokenizer=tokenize,
    lowercase=True,
    stop_words=spanish_stopwords)


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


def discover_relations(tweets):
    possible_relations = get_possible_relations(tweets)
    grouped_relations = group_relations_by_type(possible_relations)

    fixed_relations = seek_common_relations(grouped_relations)
    relations_by_clusters = create_clusters(grouped_relations)

    return possible_relations, fixed_relations, relations_by_clusters


def get_possible_relations(tweets):
    possible_relations = []
    for tweet in tweets:
        entities_for_relations = tweet.nee_entities
        if entities_for_relations:
            for first, second in zip(entities_for_relations, entities_for_relations[1:]):
                try:
                    text_in_between = tweet.full_text[(tweet.full_text.index(first.text) + len(
                        first.text)):tweet.full_text.index(second.text)]
                    cleaned_text = remove_stop_words(text_in_between)
                    cleaned_text = remove_punctuation(cleaned_text)
                    possible_relations.append(PossibleRelation(
                        text_in_between.strip(), cleaned_text, first, second, tweet))
                except Exception as e:
                    print(e)
    return possible_relations


def group_relations_by_type(possible_relations):
    groups = {}
    for relation in possible_relations:
        first = relation.first_entity
        second = relation.second_entity
        if (is_interesting_entity(first) and is_interesting_entity(second)):
            group_key = get_cluster_type(first, second)
            if group_key:
                if group_key in groups:
                    groups.get(group_key).append(relation)
                else:
                    groups[group_key] = [relation]
    return groups


def seek_common_relations(grouped_relations):
    fixed_relations = []
    for key, value in grouped_relations.items():
        for relation in value:
            if relation.full_relation_text in predefined_relations:
                fixed_relations.append(Relation(
                    relation.first_entity, relation.second_entity, relation.full_relation_text, [relation.tweet]))
    return fixed_relations

def create_clusters(grouped_relations):
    relations = []
    for key, value in grouped_relations.items():
        corpus = [o.clean_relation_text for o in value if o.clean_relation_text]
        if not corpus or len(corpus) < 2:
            print('Empty corpus')
            continue
        X = vectorizer.fit_transform(corpus)
        Z = linkage(X.toarray(), 'single', 'cosine')
        k = 20000
        discovered_clusters = fcluster(Z, k, criterion='maxclust')
        relations.append(getRelationsFromClusters(value, discovered_clusters))
    return relations


def getRelationsFromClusters(grouped_relations, clusters_by_element):

    relations = []
    clusters_content = {}
    for index, element in enumerate(clusters_by_element):
        if element in clusters_content:
            clusters_content[element] += ' ' + \
                grouped_relations[index].clean_relation_text
        else:
            clusters_content[element] = grouped_relations[index].clean_relation_text

    for key in clusters_content:
        counter = Counter(clusters_content[key].split())
        clusters_content[key] = counter.most_common(10)

    for index, element in enumerate(clusters_by_element):
        posible_relation = grouped_relations[index]
        relation_words = ' '.join(v[0] for v in clusters_content[element])
        relations.append(Relation(posible_relation.first_entity,
                                  posible_relation.second_entity, relation_words, posible_relation.tweet))
    return relations


def get_cluster_type(first, second):
    if first.entity_type == 'PERSON' and second.entity_type == 'PERSON':
        return 'person_person_cluster'
    if first.entity_type == 'PERSON' and second.entity_type == 'ORGANIZATION':
        return 'person_organization_cluster'
    if first.entity_type == 'ORGANIZATION' and second.entity_type == 'PERSON':
        return 'organization_person_cluster'
    if first.entity_type == 'ORGANIZATION' and second.entity_type == 'ORGANIZATION':
        return 'organization_organization_cluster'
    if first.entity_type == 'PERSON' and second.entity_type == 'TITLE':
        return 'person_title_cluster'
    if first.entity_type == 'TITLE' and second.entity_type == 'PERSON':
        return 'title_person_cluster'
    if first.entity_type == 'PERSON' and second.entity_type == 'CRIMINAL_CHARGE':
        return 'person_criminal_charge_cluster'
    if first.entity_type == 'PERSON' and second.entity_type == 'MISC':
        return 'person_misc_cluster'
    if first.entity_type == 'MISC' and second.entity_type == 'PERSON':
        return 'misc_person'
    if first.entity_type == 'MISC' and second.entity_type == 'ORGANIZATION':
        return 'misc_organization_cluster'
    if first.entity_type == 'ORGANIZATION' and second.entity_type == 'MISC':
        return 'organization_misc_cluster'
    if first.entity_type == 'MISC' and second.entity_type == 'MISC':
        return 'misc_misc_cluster'


def is_interesting_entity(entity):
    return entity.entity_type in interesting_entity_types
