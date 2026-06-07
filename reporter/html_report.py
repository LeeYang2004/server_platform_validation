# reporter/html_report.py
from jinja2 import Template
from pathlib import Path
from datetime import datetime

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>ServerBench Report</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 960px; margin: 40px auto; color: #222; }
    h1 { color: #ED1C24; } /* AMD red */
    .pass { color: green; font-weight: bold; }
    .fail { color: red; font-weight: bold; }
    table { width: 100%; border-collapse: collapse; margin: 16px 0; }
    th { background: #333; color: white; padding: 8px; text-align: left; }
    td { padding: 8px; border-bottom: 1px solid #ddd; }
    .finding { background: #fff3cd; padding: 6px 10px; border-left: 4px solid orange; margin: 4px 0; }
    .summary-bar { display: flex; gap: 24px; margin: 20px 0; }
    .stat { background: #f5f5f5; padding: 16px 24px; border-radius: 6px; }
    .stat h2 { margin: 0; font-size: 2em; }
    .stat p { margin: 4px 0 0; color: #666; }
  </style>
</head>
<body>
  <h1>ServerBench Validation Report</h1>
  <p>Generated: {{ timestamp }} | Total Workloads: {{ results|length }} |
     Passed: <span class="pass">{{ results|selectattr('status','eq','PASS')|list|length }}</span> /
     Failed: <span class="fail">{{ results|selectattr('status','eq','FAIL')|list|length }}</span>
  </p>

  {% for r in results %}
  <h2>{{ r.name | upper }} — <span class="{{ 'pass' if r.status == 'PASS' else 'fail' }}">{{ r.status }}</span></h2>
  
  <table>
    <tr><th>Metric</th><th>Value</th></tr>
    {% for k, v in r.metrics.items() %}
    <tr><td>{{ k }}</td><td>{{ v }}</td></tr>
    {% endfor %}
  </table>

  {% if r.regressions %}
  <h3>⚠ Regression Findings</h3>
  {% for f in r.regressions %}
  <div class="finding">
    <strong>{{ f.severity }}</strong>: {{ f.field }} = {{ f.value }} 
    (threshold: {{ f.threshold }})
  </div>
  {% endfor %}
  {% endif %}
  {% endfor %}

</body>
</html>
"""

def generate_report(results: list, output_path: str):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    html = Template(TEMPLATE).render(
        results=results,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    with open(output_path, "w") as f:
        f.write(html)