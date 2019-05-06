import requests

relation_url = 'http://localhost:6066/relations'
entities_url = 'http://localhost:6066/entities'


def analyze_relations():
    r = requests.get(relation_url)
    relations = r.json()['relations']
    print('# Relations ' + str(len(relations)))
    semantic_relations = [
        relation for relation in relations if relation['relation_type'] == 1]
    static_relations = [
        relation for relation in relations if relation['relation_type'] == 2]
    popular_relations = [
        relation for relation in relations if relation['relation_type'] == 3]

    print('# Semantic Relations ' + str(len(semantic_relations)))
    print('# Static Relations ' + str(len(static_relations)))
    print('# Popular Relations ' + str(len(popular_relations)))


def analyze_entities():
    r = requests.get(entities_url)
    entities = r.json()['entities_count']
    print('# Entities ' + str(len(entities)))


analyze_relations()
analyze_entities()
