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

predefined_relations = ['y','responde por', 'cuando dices q',
                        'pintaron de negro', 'debe estar q se revienta de la ira, porq el']

clusters = {
    'person_person_cluster': [],
    'person_organization_cluster': [],
    'organization_person_cluster': [],
    'organization_organization_cluster': [],
    'person_title_cluster': [],
    'title_person_cluster': [],
    'person_criminal_charge_cluster': [],
    'person_misc_cluster': [],
    'misc_person': [],
    'misc_organization_cluster': [],
    'organization_misc_cluster': [],
    'misc_misc_cluster': []
}

relations = []

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
    possible_relations =  get_possible_relations(tweets)
    fixed_relations = seek_common_relations(possible_relations)
    return possible_relations,fixed_relations
    '''
    create_clusters(tweets)
    seek_common_relations()
    for key, value in clusters.items():
        corpus = [o['cleaned_relation_text'] for o in value]
        if not corpus or len(corpus) < 2:
            print ('Empty corpus')
            continue
        X = vectorizer.fit_transform(corpus)
        Z = linkage(X.toarray(), 'single', 'cosine')
        k = 20000
        discovered_clusters = fcluster(Z, k, criterion='maxclust')
        getCommonWordsFromCluster(value, discovered_clusters)
    print (relations)
    return clusters
    '''

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
                    possible_relations.append(PossibleRelation(text_in_between.strip(),cleaned_text,first,second,tweet))
                except Exception as e:
                    print(e)
    return possible_relations


def getCommonWordsFromCluster(segmented_cluster, clusters_by_element):

    clusters_content = {}
    for index, element in enumerate(clusters_by_element):
        if element in clusters_content:
            clusters_content[element] += ' ' + \
                segmented_cluster[index]['cleaned_relation_text']
        else:
            clusters_content[element] = segmented_cluster[index]['cleaned_relation_text']

    for key in clusters_content:
        counter = Counter(clusters_content[key].split())
        clusters_content[key] = counter.most_common(10)

    for index, element in enumerate(clusters_by_element):
        segmented_cluster[index]['cluster'] = clusters_content[element]


def create_clusters(tweets):
    for tweet in tweets:
        entities_for_relations = [
            entity for entity in tweet.nee_entities if is_interesting_entity(entity)]
        if entities_for_relations:
            for first, second in zip(entities_for_relations, entities_for_relations[1:]):
                cluster = clusters.get(get_cluster_type(first, second))
                try:
                    text_in_between = tweet.full_text[(tweet.full_text.index(first.text) + len(
                        first.text)):tweet.full_text.index(second.text)]
                    cleaned_text = remove_stop_words(text_in_between)
                    cleaned_text = remove_punctuation(cleaned_text)
                    if cleaned_text and cleaned_text.strip():
                        cluster.append({'cleaned_relation_text': cleaned_text,
                                        'relation_text': text_in_between.strip(),
                                        'entities': [first, second],
                                        'tweet': tweet
                                        })
                except Exception as e:
                    print(e)


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

def seek_common_relations(possible_relations):
    fixed_relations = []
    for relation in possible_relations:
            if relation.full_relation_text in predefined_relations:
                fixed_relations.append(
                    Relation(relation.first_entity,relation.second_entity,relation.full_relation_text))
    return fixed_relations
