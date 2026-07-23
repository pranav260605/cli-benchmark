"""
DASHBOARD GENERATOR -- Turns the two results files into ONE self-contained
HTML file: compliance score + usability success rate, side by side,
per model, with a final recommendation.
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
        f"Use {best_model} for agent-friendly CLI generation -- "
        f"{best.get('avg_compliance', 0)}/10 rubric compliance and "
        f"{best.get('usability_rate', 0)}% real usability success "
        f"(a blind agent could actually operate its CLIs)."
    )

    html = f"""<!DOCTYPE html>
<html><head>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body{{background:#0D0D1A;color:#F1F5F9;font-family:sans-serif;
     padding:2rem;max-width:750px;margin:0 auto}}
h1{{color:#CBA6F7;font-size:1.3rem}}
.rec{{background:#0F2A22;border:1px solid #1A4A32;border-radius:10px;
     padding:1rem;color:#6EE7C0;margin:1rem 0;line-height:1.6}}
.note{{background:#2E1B14;border:1px solid #7C2D12;border-radius:10px;
      padding:.85rem 1rem;color:#F2A38A;font-size:.85rem;margin-bottom:1rem}}
.chart-box{{background:#13132B;border:1px solid #2A2A4A;border-radius:10px;
     padding:1rem;margin-bottom:1rem}}
</style></head>
<body>
<h1>Agent-Friendly CLI Benchmark -- 7 Models x 5 Scenarios</h1>
<div class="rec">-> {recommendation}</div>
<div class="note">
  Compliance = does the code follow the 10 SKILL.md rules (checked
  by text search + LLM judge). Usability = did a DIFFERENT blind AI
  agent actually succeed at using the tool with zero prior knowledge,
  using only its --describe output. Both matter -- a tool can look
  correct and still fail in practice.
</div>
<div class="chart-box"><canvas id="complianceChart"></canvas></div>
<div class="chart-box"><canvas id="usabilityChart"></canvas></div>
<script>
new Chart(document.getElementById('complianceChart'), {{
  type: 'bar',
  data: {{ labels: {json.dumps(models)},
    datasets: [{{label: 'Compliance Score /10',
      data: {json.dumps(compliance_arr)}, backgroundColor: '#534AB7'}}] }},
  options: {{plugins:{{title:{{display:true,
    text:'Rubric Compliance (10 rules)',color:'#F1F5F9'}}}},
    scales:{{y:{{max:10,ticks:{{color:'#94A3B8'}}}},
    x:{{ticks:{{color:'#94A3B8'}}}}}}}}
}});
new Chart(document.getElementById('usabilityChart'), {{
  type: 'bar',
  data: {{ labels: {json.dumps(models)},
    datasets: [{{label: 'Usability Success %',
      data: {json.dumps(usability_arr)}, backgroundColor: '#10A37F'}}] }},
  options: {{plugins:{{title:{{display:true,
    text:'Blind-Agent Usability Success Rate',color:'#F1F5F9'}}}},
    scales:{{y:{{max:100,ticks:{{color:'#94A3B8'}}}},
    x:{{ticks:{{color:'#94A3B8'}}}}}}}}
}});
</script>
</body></html>"""

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
    
    