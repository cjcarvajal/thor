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
    }).then(res => console.log(res));
    sendQuery();
}