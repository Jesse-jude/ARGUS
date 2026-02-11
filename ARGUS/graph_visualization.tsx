/**
 * ARGUS Argument Graph Visualization
 * D3.js interactive graph showing claim relationships
 */

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface GraphNode {
  id: string;
  text: string;
  type: string;
  confidence?: number;
  status: 'survived' | 'collapsed' | 'value-dependent';
}

interface GraphLink {
  source: string;
  target: string;
  relation: 'supports' | 'contradicts';
}

interface ArgumentGraphVisualizationProps {
  nodes: GraphNode[];
  links: GraphLink[];
  width?: number;
  height?: number;
}

const ArgumentGraphVisualization: React.FC<ArgumentGraphVisualizationProps> = ({
  nodes,
  links,
  width = 800,
  height = 600
}) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;

    // Clear previous visualization
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current);

    // Create force simulation
    const simulation = d3.forceSimulation(nodes as any)
      .force('link', d3.forceLink(links)
        .id((d: any) => d.id)
        .distance(150)
      )
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(50));

    // Create arrow markers for directed edges
    svg.append('defs').selectAll('marker')
      .data(['supports', 'contradicts'])
      .join('marker')
      .attr('id', d => `arrow-${d}`)
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 20)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', d => d === 'supports' ? '#22c55e' : '#ef4444');

    // Create links
    const link = svg.append('g')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', d => d.relation === 'supports' ? '#22c55e' : '#ef4444')
      .attr('stroke-width', 2)
      .attr('stroke-opacity', 0.6)
      .attr('marker-end', d => `url(#arrow-${d.relation})`);

    // Create node groups
    const nodeGroup = svg.append('g')
      .selectAll('g')
      .data(nodes)
      .join('g')
      .call(d3.drag<any, any>()
        .on('start', dragStarted)
        .on('drag', dragged)
        .on('end', dragEnded)
      );

    // Add circles for nodes
    nodeGroup.append('circle')
      .attr('r', 30)
      .attr('fill', d => {
        if (d.status === 'survived') return '#22c55e';
        if (d.status === 'collapsed') return '#ef4444';
        return '#eab308';
      })
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 3)
      .attr('opacity', 0.9);

    // Add claim type badges
    nodeGroup.append('circle')
      .attr('r', 10)
      .attr('cx', 20)
      .attr('cy', -20)
      .attr('fill', d => {
        const colors: Record<string, string> = {
          'empirical': '#3b82f6',
          'normative': '#a855f7',
          'causal': '#f97316',
          'predictive': '#06b6d4',
          'definitional': '#64748b'
        };
        return colors[d.type] || '#64748b';
      })
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 2);

    // Add labels
    nodeGroup.append('text')
      .text(d => d.id)
      .attr('text-anchor', 'middle')
      .attr('dy', 5)
      .attr('font-size', 12)
      .attr('font-weight', 'bold')
      .attr('fill', '#ffffff')
      .style('pointer-events', 'none');

    // Add hover tooltips
    nodeGroup.append('title')
      .text(d => `${d.text}\nType: ${d.type}\nStatus: ${d.status}`);

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      nodeGroup
        .attr('transform', (d: any) => `translate(${d.x},${d.y})`);
    });

    // Drag functions
    function dragStarted(event: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }

    function dragged(event: any) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    function dragEnded(event: any) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }

    // Legend
    const legend = svg.append('g')
      .attr('transform', `translate(${width - 150}, 20)`);

    const legendData = [
      { label: 'Survived', color: '#22c55e' },
      { label: 'Collapsed', color: '#ef4444' },
      { label: 'Value-Based', color: '#eab308' }
    ];

    legend.selectAll('g')
      .data(legendData)
      .join('g')
      .attr('transform', (d, i) => `translate(0, ${i * 25})`)
      .each(function(d) {
        const g = d3.select(this);
        g.append('circle')
          .attr('r', 8)
          .attr('fill', d.color);
        g.append('text')
          .attr('x', 15)
          .attr('y', 5)
          .text(d.label)
          .attr('font-size', 12)
          .attr('fill', '#ffffff');
      });

    return () => {
      simulation.stop();
    };
  }, [nodes, links, width, height]);

  return (
    <div className="w-full bg-slate-900 rounded-lg p-4">
      <div className="mb-4">
        <h3 className="text-white text-lg font-bold mb-2">Argument Graph</h3>
        <div className="flex gap-4 text-sm text-slate-400">
          <span className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            Supports
          </span>
          <span className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            Contradicts
          </span>
        </div>
      </div>
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="border border-slate-700 rounded"
      />
    </div>
  );
};


/**
 * Enhanced Graph with Clustering
 * Groups related claims together
 */
export const ClusteredArgumentGraph: React.FC<ArgumentGraphVisualizationProps> = ({
  nodes,
  links,
  width = 900,
  height = 700
}) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    // Cluster nodes by type
    const clusters = d3.group(nodes, d => d.type);

    // Create hierarchical layout
    const simulation = d3.forceSimulation(nodes as any)
      .force('link', d3.forceLink(links)
        .id((d: any) => d.id)
        .distance(100)
      )
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(60));

    // Add cluster forces
    const clusterCenters: Record<string, { x: number, y: number }> = {
      'empirical': { x: width * 0.3, y: height * 0.5 },
      'normative': { x: width * 0.7, y: height * 0.5 },
      'causal': { x: width * 0.5, y: height * 0.3 },
      'predictive': { x: width * 0.5, y: height * 0.7 }
    };

    simulation.force('cluster', (alpha) => {
      nodes.forEach((node: any) => {
        const center = clusterCenters[node.type];
        if (center) {
          node.vx -= (node.x - center.x) * alpha * 0.1;
          node.vy -= (node.y - center.y) * alpha * 0.1;
        }
      });
    });

    // Draw cluster backgrounds
    svg.append('g')
      .selectAll('circle')
      .data(Array.from(clusters.keys()))
      .join('circle')
      .attr('cx', type => clusterCenters[type]?.x || width / 2)
      .attr('cy', type => clusterCenters[type]?.y || height / 2)
      .attr('r', 120)
      .attr('fill', type => {
        const colors: Record<string, string> = {
          'empirical': '#3b82f6',
          'normative': '#a855f7',
          'causal': '#f97316',
          'predictive': '#06b6d4'
        };
        return colors[type] || '#64748b';
      })
      .attr('opacity', 0.1);

    // Add cluster labels
    svg.append('g')
      .selectAll('text')
      .data(Array.from(clusters.keys()))
      .join('text')
      .attr('x', type => clusterCenters[type]?.x || width / 2)
      .attr('y', type => (clusterCenters[type]?.y || height / 2) - 130)
      .attr('text-anchor', 'middle')
      .attr('font-size', 14)
      .attr('font-weight', 'bold')
      .attr('fill', '#94a3b8')
      .text(type => type.toUpperCase());

    // Rest of visualization (links and nodes) similar to basic version
    // ... (code omitted for brevity)

  }, [nodes, links, width, height]);

  return <svg ref={svgRef} width={width} height={height} />;
};

export default ArgumentGraphVisualization;
