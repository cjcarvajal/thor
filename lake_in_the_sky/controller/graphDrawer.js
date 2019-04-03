
const width = 960;
const height = 700;
const svg = d3.select("#principal");
const transform = d3.zoomIdentity;

const linkDistance = 10;
const nodeRadius = 5;

const colorScale = d3.scaleOrdinal(d3.schemeSet1);

const bigG = svg.append("g");

const rectangleZoomWidth = 100;
const rectangleZoomHeight = 100;

svg.call(d3.zoom()
    .scaleExtent([1 / 2, 8])
    .on("zoom", zoomed));

function zoomed() {
    bigG.attr("transform", d3.event.transform);
}

function drawGraph(nodes, links) {
    bigG.selectAll("*").remove();
    var simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink().id(function (d) { return d.text; }))
        .force('charge', d3.forceManyBody())
        .force('center', d3.forceCenter(width / 2, height / 2))
        .on('tick', ticked);

    simulation.force("link").links(links);

    var link = bigG.append("g")
        .selectAll('.link')
        .data(links)
        .enter()
        .append('line')
        .attr('class', 'link')
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6)
        .style("stroke-width", 2);

    var node = bigG.append("g")
        .attr('class', 'nodes')
        .selectAll('g')
        .data(nodes)
        .enter()
        .append('g');

    var circles = node.append('circle')
        .attr('r', nodeRadius)
        .attr('fill', d => { return colorScale(d.type) })
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));

    //const labels = node.append('text').text(d => { return d.text }).attr('x', 6).attr('y', 3);

    function ticked() {

        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node.attr("transform", function (d) {
            return "translate(" + d.x + "," + d.y + ")";
        })
    }

    function dragstarted(d) {
        if (!d3.event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
    }

    function dragended(d) {
        if (!d3.event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    bigG.on("mousemove", function () {
        var mouse = d3.mouse(this);
        console.log(mouse[0], mouse[1]);
        filterNodes(mouse[0], mouse[1]);
    })

    function filterNodes(xPos, yPos) {
        filteredNodes = nodes.filter(n => (Math.abs(xPos - n.x) < rectangleZoomWidth) &&
            (Math.abs(yPos - n.y) < rectangleZoomWidth));
        console.log(filteredNodes);
    }
}