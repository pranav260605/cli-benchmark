"""
RUN ALL -- The master switch. One command runs the entire benchmark:
generate CLIs -> score compliance -> run usability tests -> build dashboard -> write README.
"""

from generator import generate_all
from rubric import score_all_generated
from usability_tester import test_all
from dashboard_generator import generate_dashboard
from readme_generator import generate_readme


def main():
    print("=" * 60)
    print("  AGENT-FRIENDLY CLI BENCHMARK -- Full Pipeline")
    print("=" * 60)

    print("\n[1/4] Generating CLIs across 7 models x 5 scenarios...")
    generate_all()

    print("\n[2/4] Scoring compliance (10-rule rubric)...")
    compliance_results = score_all_generated()

    print("\n[3/4] Running usability tests (Layer 2)...")
    usability_results = test_all(compliance_results)

    print("\n[4/4] Building dashboard + README...")
    generate_dashboard(compliance_results, usability_results)
    generate_readme(compliance_results, usability_results)

    print("\n✅ DONE. Open output/dashboard.html in your browser.")


if __name__ == "__main__":
    main()