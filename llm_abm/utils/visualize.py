"""
Simple visualization utilities for ABM simulations
"""

import json


def generate_population_chart_html(results, title="ABM Simulation"):
    """
    Generate standalone HTML file with population chart using Chart.js

    Args:
        results: Simulation results dictionary
        title: Chart title

    Returns:
        html: Complete HTML string
    """
    history = results['metrics']['history']

    # Extract data for chart
    steps = [h['step'] for h in history]
    agent_types = set()
    for h in history:
        agent_types.update(h['agent_counts'].keys())

    datasets = []
    colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']

    for idx, agent_type in enumerate(agent_types):
        data = [h['agent_counts'].get(agent_type, 0) for h in history]
        color = colors[idx % len(colors)]

        datasets.append({
            'label': agent_type.capitalize(),
            'data': data,
            'borderColor': color,
            'backgroundColor': color + '33',  # Add alpha
            'tension': 0.1,
            'fill': True
        })

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            margin-top: 0;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #007bff;
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }}
        .stat-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
        }}
        .chart-container {{
            position: relative;
            margin-top: 30px;
            height: 400px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-label">Steps Completed</div>
                <div class="stat-value">{results['final_step']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Initial Agents</div>
                <div class="stat-value">{results['summary']['initial_agents']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Final Agents</div>
                <div class="stat-value">{results['summary']['final_agents']}</div>
            </div>
        </div>

        <div class="chart-container">
            <canvas id="populationChart"></canvas>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('populationChart').getContext('2d');
        const chart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(steps)},
                datasets: {json.dumps(datasets)}
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Population Over Time',
                        font: {{ size: 16 }}
                    }},
                    legend: {{
                        display: true,
                        position: 'top'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'Population'
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: 'Step'
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""

    return html


def generate_grid_visualization_html(model, title="ABM Grid"):
    """
    Generate standalone HTML file with grid visualization

    Args:
        model: Current model state
        title: Visualization title

    Returns:
        html: Complete HTML string
    """
    grid = model['grid']
    agents = [a for a in model['agents'] if a['alive']]

    # Group agents by type for color assignment
    agent_types = list(set(a['type'] for a in agents))
    colors = {
        agent_types[i]: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'][i % 4]
        for i in range(len(agent_types))
    }

    # Create agent position map
    agent_positions = {}
    for agent in agents:
        pos = (agent['position']['x'], agent['position']['y'])
        if pos not in agent_positions:
            agent_positions[pos] = []
        agent_positions[pos].append(agent)

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .container {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            margin-top: 0;
            text-align: center;
        }}
        .legend {{
            display: flex;
            gap: 20px;
            justify-content: center;
            margin: 20px 0;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 2px solid #333;
        }}
        #grid {{
            border: 2px solid #333;
            margin: 20px auto;
            display: block;
        }}
        .info {{
            text-align: center;
            color: #666;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>

        <div class="legend">
            {chr(10).join(f'<div class="legend-item"><div class="legend-color" style="background: {colors[t]}"></div><span>{t.capitalize()}: {sum(1 for a in agents if a["type"] == t)}</span></div>' for t in agent_types)}
        </div>

        <canvas id="grid" width="{grid['width'] * 10}" height="{grid['height'] * 10}"></canvas>

        <div class="info">
            Grid: {grid['width']}x{grid['height']} |
            Total Agents: {len(agents)} |
            Step: {model['step']}
        </div>
    </div>

    <script>
        const canvas = document.getElementById('grid');
        const ctx = canvas.getContext('2d');
        const gridWidth = {grid['width']};
        const gridHeight = {grid['height']};
        const cellSize = 10;

        // Draw grid background
        ctx.fillStyle = '#f0f0f0';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw grid lines
        ctx.strokeStyle = '#ddd';
        ctx.lineWidth = 1;
        for (let x = 0; x <= gridWidth; x++) {{
            ctx.beginPath();
            ctx.moveTo(x * cellSize, 0);
            ctx.lineTo(x * cellSize, gridHeight * cellSize);
            ctx.stroke();
        }}
        for (let y = 0; y <= gridHeight; y++) {{
            ctx.beginPath();
            ctx.moveTo(0, y * cellSize);
            ctx.lineTo(gridWidth * cellSize, y * cellSize);
            ctx.stroke();
        }}

        // Draw agents
        const agentPositions = {json.dumps({f"{pos[0]},{pos[1]}": [{"type": a["type"], "energy": a["energy"]} for a in agents] for pos, agents in agent_positions.items()})};
        const colors = {json.dumps(colors)};

        for (const [posKey, agentsAtPos] of Object.entries(agentPositions)) {{
            const [x, y] = posKey.split(',').map(Number);
            const agent = agentsAtPos[0]; // Draw first agent at position

            ctx.fillStyle = colors[agent.type];
            ctx.beginPath();
            ctx.arc(
                x * cellSize + cellSize / 2,
                y * cellSize + cellSize / 2,
                cellSize / 3,
                0,
                2 * Math.PI
            );
            ctx.fill();
            ctx.strokeStyle = '#333';
            ctx.lineWidth = 1;
            ctx.stroke();

            // Draw count if multiple agents
            if (agentsAtPos.length > 1) {{
                ctx.fillStyle = '#000';
                ctx.font = '8px sans-serif';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(
                    agentsAtPos.length.toString(),
                    x * cellSize + cellSize / 2,
                    y * cellSize + cellSize / 2
                );
            }}
        }}
    </script>
</body>
</html>"""

    return html


def save_visualization(results_or_model, filename="visualization.html", viz_type="population"):
    """
    Save visualization to HTML file

    Args:
        results_or_model: Either simulation results or current model state
        filename: Output filename
        viz_type: "population" for chart, "grid" for spatial view

    Returns:
        filename: Path to saved file
    """
    if viz_type == "population":
        html = generate_population_chart_html(results_or_model)
    elif viz_type == "grid":
        html = generate_grid_visualization_html(results_or_model)
    else:
        raise ValueError(f"Unknown visualization type: {viz_type}")

    with open(filename, 'w') as f:
        f.write(html)

    return filename
