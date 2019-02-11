# -*- coding: utf-8 -*-

from string import punctuation
from collections import Counter

from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
import itertools
from scipy.cluster.hierarchy import fcluster, linkage
from model.relation import Relation

interesting_entity_types = ['TITLE', 'PERCENT',
                            'MISC', 'PERSON', 'CRIMINAL_CHARGE', 'ORGANIZATION']

predefined_relations = ['responde por', 'cuando dices q',
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
        dirty_string = dirty_string.replace(word.decode('utf-8'), '')

    return dirty_string


def discover_relations(tweets):
    create_clusters(tweets)
    seek_common_relations()
    for key, value in clusters.iteritems():
        corpus = [o['cleaned_relation_text'] for o in value]
        if not corpus or len(corpus) < 2:
            print 'Empty corpus'
            continue
        X = vectorizer.fit_transform(corpus)
        Z = linkage(X.toarray(), 'single', 'cosine')
        k = 20000
        discovered_clusters = fcluster(Z, k, criterion='maxclust')
        getCommonWordsFromCluster(value, discovered_clusters)
    print relations
    return clusters


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
            for first, second in itertools.izip(entities_for_relations, entities_for_relations[1:]):
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
    if first.type == 'PERSON' and second.type == 'PERSON':
        return 'person_person_cluster'
    if first.type == 'PERSON' and second.type == 'ORGANIZATION':
        return 'person_organization_cluster'
    if first.type == 'ORGANIZATION' and second.type == 'PERSON':
        return 'organization_person_cluster'
    if first.type == 'ORGANIZATION' and second.type == 'ORGANIZATION':
        return 'organization_organization_cluster'
    if first.type == 'PERSON' and second.type == 'TITLE':
        return 'person_title_cluster'
    if first.type == 'TITLE' and second.type == 'PERSON':
        return 'title_person_cluster'
    if first.type == 'PERSON' and second.type == 'CRIMINAL_CHARGE':
        return 'person_criminal_charge_cluster'
    if first.type == 'PERSON' and second.type == 'MISC':
        return 'person_misc_cluster'
    if first.type == 'MISC' and second.type == 'PERSON':
        return 'misc_person'
    if first.type == 'MISC' and second.type == 'ORGANIZATION':
        return 'misc_organization_cluster'
    if first.type == 'ORGANIZATION' and second.type == 'MISC':
        return 'organization_misc_cluster'
    if first.type == 'MISC' and second.type == 'MISC':
        return 'misc_misc_cluster'


def is_interesting_entity(entity):
    return entity.type in interesting_entity_types


def seek_common_relations():
    for key, value in clusters.iteritems():
        for item in value:
            if item['relation_text'] in predefined_relations:
                relations.append(
                    Relation(item['entities'][0], item['entities'][1], item['relation_text']))
