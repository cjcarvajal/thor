const detailedNodeRadius = 8;
const detailedMargin = 80;
const labelMargin = detailedNodeRadius + 5;
const detailedWidth = 570;
const fontSize = 10;

const xScale = d3.scaleLinear().range([0 + detailedMargin, detailedWidth - detailedMargin]);
const yScale = d3.scaleLinear().range([0 + detailedMargin, 500 - detailedMargin]);

function drawDetailedGraph(nodes, links) {
    detailedSvg.selectAll("*").remove();
    xScale.domain([d3.min(nodes, d => d.x), d3.max(nodes, d => d.x)]);
    yScale.domain([d3.min(nodes, d => d.y), d3.max(nodes, d => d.y)]);

    detailedLinks = [];
    links.forEach(link => {
        const nodeOrigin = _.findWhere(nodes, { text: link.source });
        const nodeTarget = _.findWhere(nodes, { text: link.target });
        detailedLinks.push({
            'x1': nodeOrigin.x,
            'y1': nodeOrigin.y,
            'x2': nodeTarget.x,
            'y2': nodeTarget.y,
            'relation': link.relation,
            'source': link.source,
            'target': link.target,
            'relation_type': link.relation_type

        });
    });

    var link = detailedSvg.append("g")
        .selectAll('.link')
        .data(detailedLinks)
        .enter()
        .append('line')
        .on('mouseover', function (obj) {
            detailedSvg.selectAll(".relation").remove();
            detailedSvg.append("text")
                .attr('class', 'relation')
                .attr("x", 10)
                .attr("y", 15)
                .text(obj.source + ' ' + obj.relation + ' ' + obj.target);
        })
        .attr('class', 'link')
        .attr("stroke", d => { return linkColorScale(d.relation_type) })
        .attr("stroke-opacity", 0.6)
        .style("stroke-width", 2)
        .attr("x1", d => xScale(d.x1))
        .attr("y1", d => yScale(d.y1))
        .attr("x2", d => xScale(d.x2))
        .attr("y2", d => yScale(d.y2));

    var node = detailedSvg.append("g")
        .attr('class', 'nodes')
        .selectAll('g')
        .data(nodes)
        .enter()
        .append('g');

    const circles = node.append('circle')
        .attr('r', detailedNodeRadius)
        .attr('fill', d => { return colorScale(d.type) })
        .attr('cx', d => { return xScale(d.x) })
        .attr('cy', d => { return yScale(d.y) })

    const labels = node.append('text')
        .text(d => { return d.text })
        .attr('x', d => { return adjustLabelXAxis(d.x, d.text) })
        .attr('y', d => yScale(d.y) - labelMargin)
        .attr("font-size", fontSize + "px");
}

function adjustLabelXAxis(xPos, text) {
    const calculatedPos = xScale(xPos) - labelMargin;
    const additionalSpace = text.length * fontSize;
    const correctionMargin = additionalSpace / 3;

    if (calculatedPos + additionalSpace > detailedWidth) {
        return calculatedPos - correctionMargin;
    } else {
        return calculatedPos;
    }
}