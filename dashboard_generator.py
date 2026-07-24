"""
DASHBOARD GENERATOR -- Vibrant Red & Yellow Theme Edition
Turns benchmark results into a catchy, dynamic, and high-impact HTML dashboard.
"""

import os, json
from collections import defaultdict


def aggregate(compliance_results: list, usability_results: list) -> dict:
    """Averages scores per model across all 5 scenarios."""
    by_model = defaultdict(lambda: {"compliance_scores": [], "usability_pass": 0, "usability_total": 0})

    for r in compliance_results:
        by_model[r["model"]]["compliance_scores"].append(r["score"])

    for r in usability_results:
        if r.get("skipped"):
            continue
        by_model[r["model"]]["usability_total"] += 1
        if r.get("execution_succeeded"):
            by_model[r["model"]]["usability_pass"] += 1

    summary = {}
    for model, data in by_model.items():
        avg_compliance = (sum(data["compliance_scores"]) / len(data["compliance_scores"])
                           if data["compliance_scores"] else 0)
        usability_rate = (data["usability_pass"] / data["usability_total"] * 100
                           if data["usability_total"] else 0)
        summary[model] = {
            "avg_compliance": round(avg_compliance, 1),
            "usability_rate": round(usability_rate, 1),
        }
    return summary


def generate_dashboard(compliance_results, usability_results,
                        output_path="output/dashboard.html"):
    summary = aggregate(compliance_results, usability_results)
    models         = list(summary.keys())
    compliance_arr = [summary[m]["avg_compliance"] for m in models]
    usability_arr  = [summary[m]["usability_rate"] for m in models]

    def combined_score(m):
        return summary[m]["avg_compliance"] + (summary[m]["usability_rate"] / 10)

    best_model = max(models, key=combined_score) if models else "N/A"
    best = summary.get(best_model, {})

    recommendation = (
        f"Top Performer: {best_model} — "
        f"{best.get('avg_compliance', 0)}/10 rubric compliance & "
        f"{best.get('usability_rate', 0)}% real usability success!"
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Agent-Friendly CLI Benchmark Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  background: #0B0B14;
  color: #F8FAFC;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  padding: 2.5rem 1.5rem;
  max-width: 850px;
  margin: 0 auto;
  line-height: 1.6;
}}
.header {{
  text-align: center;
  margin-bottom: 2rem;
}}
.header h1 {{
  font-size: 2.2rem;
  font-weight: 900;
  background: linear-gradient(135deg, #FF2E55, #FFD000);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 0.4rem;
}}
.header p {{
  color: #94A3B8;
  font-size: 0.95rem;
  font-weight: 500;
}}
.rec {{
  background: linear-gradient(135deg, rgba(255, 46, 85, 0.18), rgba(255, 208, 0, 0.12));
  border: 2px solid #FF2E55;
  border-radius: 14px;
  padding: 1.25rem 1.5rem;
  color: #FFE600;
  font-weight: 700;
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 0 25px rgba(255, 46, 85, 0.35);
  display: flex;
  align-items: center;
  gap: 12px;
}}
.rec-icon {{
  font-size: 1.8rem;
}}
.note {{
  background: rgba(255, 208, 0, 0.08);
  border-left: 4px solid #FFD000;
  border-radius: 0 12px 12px 0;
  padding: 1rem 1.25rem;
  color: #E2E8F0;
  font-size: 0.9rem;
  margin-bottom: 2rem;
}}
.chart-box {{
  background: #141424;
  border: 1px solid #2A2A44;
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1.75rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  transition: transform 0.2s ease, border-color 0.2s ease;
}}
.chart-box:hover {{
  border-color: #FF2E55;
  transform: translateY(-2px);
}}
.badge {{
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 10px;
}}
.badge-red {{
  background: rgba(255, 46, 85, 0.2);
  color: #FF2E55;
  border: 1px solid #FF2E55;
}}
.badge-yellow {{
  background: rgba(255, 208, 0, 0.2);
  color: #FFD000;
  border: 1px solid #FFD000;
}}
</style>
</head>
<body>

<div class="header">
  <h1>⚡ Agent-Friendly CLI Benchmark</h1>
  <p>7 Models × 5 Scenarios • Multi-Layer Evaluation</p>
</div>

<div class="rec">
  <span class="rec-icon">🔥</span>
  <div>{recommendation}</div>
</div>

<div class="note">
  <strong style="color:#FFD000;">📌 Benchmark Methodology:</strong><br>
  • <strong style="color:#FF2E55;">Layer 1 (Compliance):</strong> Checks 10 SKILL.md rules via static search + LLM Judge.<br>
  • <strong style="color:#FFD000;">Layer 2 (Usability):</strong> Tests if a completely <em>blind AI agent</em> can operate the generated tool using only its <code>--describe</code> self-documentation.
</div>

<div class="chart-box">
  <span class="badge badge-red">Layer 1 Evaluation</span>
  <canvas id="complianceChart"></canvas>
</div>

<div class="chart-box">
  <span class="badge badge-yellow">Layer 2 Real Execution</span>
  <canvas id="usabilityChart"></canvas>
</div>

<script>
new Chart(document.getElementById('complianceChart'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(models)},
    datasets: [{{
      label: 'Compliance Score (/10)',
      data: {json.dumps(compliance_arr)},
      backgroundColor: 'rgba(255, 46, 85, 0.85)',
      borderColor: '#FF2E55',
      borderWidth: 2,
      borderRadius: 8
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{
      title: {{
        display: true,
        text: 'Rubric Compliance (10 Agent-Friendly Rules)',
        color: '#F8FAFC',
        font: {{ size: 16, weight: 'bold' }}
      }},
      legend: {{ labels: {{ color: '#94A3B8' }} }}
    }},
    scales: {{
      y: {{ max: 10, min: 0, ticks: {{ color: '#94A3B8' }}, grid: {{ color: '#2A2A44' }} }},
      x: {{ ticks: {{ color: '#F8FAFC', font: {{ weight: 'bold' }} }}, grid: {{ display: false }} }}
    }}
  }}
}});

new Chart(document.getElementById('usabilityChart'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(models)},
    datasets: [{{
      label: 'Usability Success Rate (%)',
      data: {json.dumps(usability_arr)},
      backgroundColor: 'rgba(255, 208, 0, 0.85)',
      borderColor: '#FFD000',
      borderWidth: 2,
      borderRadius: 8
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{
      title: {{
        display: true,
        text: 'Blind-Agent Execution Success Rate (%)',
        color: '#F8FAFC',
        font: {{ size: 16, weight: 'bold' }}
      }},
      legend: {{ labels: {{ color: '#94A3B8' }} }}
    }},
    scales: {{
      y: {{ max: 100, min: 0, ticks: {{ color: '#94A3B8' }}, grid: {{ color: '#2A2A44' }} }},
      x: {{ ticks: {{ color: '#F8FAFC', font: {{ weight: 'bold' }} }}, grid: {{ display: false }} }}
    }}
  }}
}});
</script>
</body>
</html>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  📊 Dashboard saved -> {output_path}")
    print(f"  📌 {recommendation}")
    return recommendation


if __name__ == "__main__":
    with open("results/compliance_scores.json") as f:
        comp = json.load(f)
    with open("results/usability_scores.json") as f:
        usab = json.load(f)
    generate_dashboard(comp, usab)