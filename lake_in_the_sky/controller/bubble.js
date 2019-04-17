var nWidth = 960,
    nHeight = 500;

var numNodes = 100
var nodes = d3.range(numNodes).map(function (d) {
    return { radius: Math.random() * 25 }
})

function drawBubbleGraph(nodes) {
    const radiusScale = d3.scaleLinear()
        .domain([d3.min(nodes, d => d.counter), d3.max(nodes, d => d.counter)])
        .range([10, nHeight / 5]);

    var simulation = d3.forceSimulation(nodes)
        .force('charge', d3.forceManyBody().strength(5))
        .force('center', d3.forceCenter(nWidth / 2, nHeight / 2))
        .force('collision', d3.forceCollide().radius(function (d) {
            return radiusScale(d.counter);
        }))
        .on('tick', ticked);

    function ticked() {
        var u = d3.select('#bubble')
            .selectAll('circle')
            .data(nodes);

        var texts = d3.select('#bubble').selectAll('text').data(nodes);

        v.enter()
            .append('text')
            .text(d => d.name)
            .attr('color', 'black')
            .attr('font-size', 15)
            .attr('x', function (d) {
                return d.x;
            })
            .attr('y', function (d) {
                return d.x;
            })


        u.enter()
            .append('circle')
            .attr('r', d => { return radiusScale(d.counter) })
            .merge(u)
            .attr('fill', d => { return colorScale(d.type) })
            .attr('cx', function (d) {
                return d.x
            })
            .attr('cy', function (d) {
                return d.y
            })
        u.exit().remove()
    }

}