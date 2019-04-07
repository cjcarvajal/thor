base_url = 'http://localhost:6066/'
query_url = base_url + 'query/'
relations_url = base_url + 'relations'

let queryTerm = '';

function startAnalysis() {
    queryTerm = document.getElementById('query_term').value
    if (queryTerm) {
        sendQuery()
    }
}

function sendQuery() {
    fetch(query_url + queryTerm).then(data => {
        return data.json()
    }).then(res => console.log(res));
}

function getRelations() {
    fetch(relations_url).then(data => {
        return data.json()
    }).then(res => createGraph(res));
    sendQuery();
}

function createGraph(relations) {
    nodes = [];
    links = [];
    relations.relations.forEach(
        function (element) {
            const entityOriginNode = {
                'type': element.entity_origin.entity_type,
                'text': element.entity_origin.text
            };

            const entityEndNode = {
                'type': element.entity_end.entity_type,
                'text': element.entity_end.text
            }

            const entityRelation = {
                'source': entityOriginNode.text,
                'target': entityEndNode.text,
                'relation': element.relation_text
            }

            if (_.findWhere(nodes, entityOriginNode) == null) {
                nodes.push(entityOriginNode);
            }

            if (_.findWhere(nodes, entityEndNode) == null) {
                nodes.push(entityEndNode);
            }

            if (_.findWhere(links, entityRelation) == null) {
                links.push(entityRelation);
            }
        }
    );
    drawOverviewGraph(nodes, links);
}