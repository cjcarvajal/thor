var nWidth = 960,
    nHeight = 500;

var numNodes = 100
var nodes = d3.range(numNodes).map(function (d) {
    return { radius: Math.random() * 25 }
})

function drawBubbleGraph(nodes) {
    d3.select('#bubble').selectAll('*').remove();
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

        texts.enter()
            .append('text')
            .merge(texts)
            .text(d => { return d.name })
            .attr('color', 'black')
            .attr('font-size', d => { return getFontSize(d.counter, d.name) })
            .attr('x', function (d) {
                radius = radiusScale(d.counter)
                return d.x - radiusScale(d.counter) + (radius / 4);
            })
            .attr('y', function (d) {
                return d.y + (radius / 10);
            })
            .on('mouseover', handleOnMouseOver)
            .on('mouseout', handleMouseOut)
        texts.exit().remove()

    }

    function handleOnMouseOver(d, i) {
        d3.select(this).attr('font-size', 40);
    }

    function handleMouseOut(d, i) {
        d3.select(this).attr('font-size', getFontSize(d.counter, d.name));
    }

    function getFontSize(counter, name) {
        radius = radiusScale(counter);
        return radius / (name.length * 0.33);
    }

}

