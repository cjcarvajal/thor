
const width = 432;
const height = 700;
const svg = d3.select("#overview");
const detailedSvg = d3.select('#detail');

const transform = d3.zoomIdentity;

const linkDistance = 10;
const nodeRadius = 5;

var lockZoomRect = false;

const colorScale = d3.scaleOrdinal(d3.schemePaired);
colorScale.domain(['CAUSE_OF_DEATH', 'TITLE', 'CRIMINAL_CHARGE',
    'RELIGION', 'MISC', 'NUMBER', 'PERSON', 'LOCATION', 'ORGANIZATION',
    'DATE', 'NATIONALITY', 'IDEOLOGY']);

const linkColorScale = d3.scaleOrdinal()
    .domain([1, 2, 3])
    .range(['#999', '#e34a33', '#1c9099']);

const bigG = svg.append("g");

svg.call(d3.zoom()
    .scaleExtent([1 / 2, 8])
    .on("zoom", zoomed));

svg.on("click", function () {
    lockZoomRect = !lockZoomRect;
});

svg.on("mousemove", function () {
    if (lockZoomRect) {
        var mouse = d3.mouse(this);
        actualXPos = mouse[0];
        actualYPos = mouse[1];
        svg.selectAll("rect").remove();

        svg.append("rect")
            .attr("x", actualXPos - rectangleZoomWidth / 2)
            .attr("y", actualYPos - rectangleZoomWidth / 2)
            .attr("width", rectangleZoomWidth)
            .attr("height", rectangleZoomWidth)
            .style("fill", "none")
            .style("stroke", "black")
    }
});

svg.on("mouseleave", function () {
    svg.selectAll("rect").remove();
})

function zoomed() {
    bigG.attr("transform", d3.event.transform);
}

function drawOverviewGraph(nodes, links) {
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
        .attr("stroke", d => { return linkColorScale(d.relation_type) })
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
        if (lockZoomRect) {
            var mouse = d3.mouse(this);
            detailedNodes = filterNodes(mouse[0], mouse[1]);
            detailedLinks = filterLinks(mouse[0], mouse[1]);
            drawDetailedGraph(detailedNodes, detailedLinks);
        }
    })

    function filterNodes(xPos, yPos) {
        filteredNodes = nodes.filter(n => (Math.abs(xPos - n.x) < rectangleZoomWidth) &&
            (Math.abs(yPos - n.y) < rectangleZoomWidth));

        newGraphNodes = [];
        filteredNodes.forEach(node => {
            newGraphNodes.push({
                'type': node.type,
                'text': node.text,
                'vx': node.vx,
                'vy': node.vy,
                'x': node.x,
                'y': node.y
            });
        });
        return newGraphNodes;
    }

    function filterLinks(xPos, yPos) {
        filteredLinks = links.filter(n =>
            ((Math.abs(xPos - n.source.x) < rectangleZoomWidth) &&
                (Math.abs(yPos - n.source.y) < rectangleZoomWidth)) &&
            ((Math.abs(xPos - n.target.x) < rectangleZoomWidth) &&
                (Math.abs(yPos - n.target.y) < rectangleZoomWidth))
        );
        newGraphLinks = [];
        filteredLinks.forEach(link => {
            newGraphLinks.push({
                'source': link.source.text,
                'target': link.target.text,
                'relation': link.relation,
                'relation_type': link.relation_type
            });
        });
        return newGraphLinks;

    }
}

//Draw legend
const entityTypes = [
    { 'type': 'CAUSE_OF_DEATH', 'value': 'Causa de muerte' },
    { 'type': 'TITLE', 'value': 'Cargo' },
    { 'type': 'CRIMINAL_CHARGE', 'value': 'Delito' },
    { 'type': 'RELIGION', 'value': 'Religión' },
    { 'type': 'MISC', 'value': 'Otros' },
    { 'type': 'NUMBER', 'value': 'Número' },
    { 'type': 'PERSON', 'value': 'Personas' },
    { 'type': 'LOCATION', 'value': 'Lugar' },
    { 'type': 'ORGANIZATION', 'value': 'Organización' },
    { 'type': 'DATE', 'value': 'Fecha' },
    { 'type': 'NATIONALITY', 'value': 'Nacionalidad' },
    { 'type': 'IDEOLOGY', 'value': 'Idelología' }];

const legendNodeRadius = 8;
const legendSvg = d3.select("#nodesLegend");
const upperMargin = 30;
const legendTextUpperMargin = upperMargin + 4;
legendCircles = legendSvg.selectAll("circle")
    .data(entityTypes)
    .enter();

legendCircles.append('circle')
    .attr('r', legendNodeRadius)
    .attr('fill', d => { return colorScale(d.type) })
    .attr("cx", function (d, i) { if (i < 6) return 30; else return 200; })
    .attr("cy", function (d, i) {
        if (i < 6) {
            return (i * 3 * legendNodeRadius) + upperMargin;
        } else {
            return ((i - 6) * 3 * legendNodeRadius) + upperMargin;
        }
    })

legendCircles.append('text')
    .text(d => d.value)
    .attr('x', function (d, i) { if (i < 6) return 45; else return 215; })
    .attr('y', function (d, i) {
        if (i < 6) {
            return i * 3 * legendNodeRadius + legendTextUpperMargin;
        } else {
            return (i - 6) * 3 * legendNodeRadius + legendTextUpperMargin;
        }
    })

