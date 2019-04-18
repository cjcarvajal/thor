base_url = 'http://localhost:6066/'
query_url = base_url + 'query/'
relations_url = base_url + 'relations'
entities_url = base_url + 'entities'
reset_url = base_url + 'reset'

let queryTerm = '';

var entity_origen_ids = [];
var entity_destiny_ids = [];

var returnedRelations = [];

var rectangleZoomWidth = 100;

const svg = d3.select("#overview");
const detailedSvg = d3.select('#detail');

for (var i = 1; i < 13; i++) {
    entity_origen_ids.push('entity_origin_' + i);
    entity_destiny_ids.push('entity_destiny_' + i);
}

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
    }).then(res => {
        returnedRelations = res;
        createGraph(res.relations)
    });
}

function getBubbleData() {
    fetch(entities_url).then(data => {
        return data.json()
    }).then(res => {
        createBubbleGraph(res.entities_count)
    });
}

function getRelationsAndQuery() {
    getRelations();
    sendQuery();
}

function resetSearch() {
    fetch(reset_url).then(data => {
        return data.json()
    }).then(res => {
        resetView();
    });
}

function createBubbleGraph(entity_list) {
    nodes = [{ 'radius': 10 }, { 'radius': 5 }, { 'radius': 50 }, { 'radius': 15 }, { 'radius': 20 }];
    drawBubbleGraph(entity_list);
}

function createGraph(relations) {
    nodes = [];
    links = [];
    relations.forEach(
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
                'relation': element.relation_text,
                'relation_type': element.relation_type
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

function filterGraph() {
    const entityOriginList = [];
    for (id of entity_origen_ids) {
        const originInput = document.getElementById(id);
        if (originInput.checked) {
            entityOriginList.push(originInput.value);
        }
    }

    const entityDestinyList = [];
    for (id of entity_destiny_ids) {
        const destinyInput = document.getElementById(id);
        if (destinyInput.checked) {
            entityDestinyList.push(destinyInput.value);
        }
    }
    filterNodes(entityOriginList, entityDestinyList);
}

function filterNodes(entityOriginList, entityDestinyList) {
    if (entityOriginList.length > 0 || entityDestinyList.length > 0) {
        detailedSvg.selectAll("*").remove();
        filteredRelations = [];

        if (entityOriginList.length > 0 && entityDestinyList.length > 0) {
            filteredRelations = returnedRelations.relations.filter(rel =>
                entityOriginList.includes(rel.entity_origin.entity_type)
                && entityDestinyList.includes(rel.entity_end.entity_type));
        }

        if (entityDestinyList.length == 0) {
            filteredRelations = returnedRelations.relations.filter(rel =>
                entityOriginList.includes(rel.entity_origin.entity_type));
        }

        if (entityOriginList.length == 0) {
            filteredRelations = returnedRelations.relations.filter(rel =>
                entityDestinyList.includes(rel.entity_end.entity_type));
        }

        createGraph(filteredRelations);
    }
}

function resetView() {
    for (id of entity_origen_ids) {
        const originInput = document.getElementById(id);
        originInput.checked = false;
    }

    for (id of entity_destiny_ids) {
        const destinyInput = document.getElementById(id);
        destinyInput.checked = false;
    }
    svg.selectAll("*").remove();
    detailedSvg.selectAll("*").remove();
}

function modifyZoom(zoomValue) {
    rectangleZoomWidth = zoomValue;
}