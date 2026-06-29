"""Test runner for the Interior Design & Space Layout harness.

Runs every scenario in ``tests/data/scenarios.json`` through the harness,
evaluates the declared assertions, and writes ``tests/PASS_FAIL_LOG.md`` plus a
machine-readable ``tests/results.json``. Exits non-zero if any scenario fails.

Usage::

    python tests/run_scenarios.py
    python tests/run_scenarios.py --print-markdown
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

_HERE = Path(__file__).resolve().parent
_SRC = _HERE.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from interior_layout.main import run  # noqa: E402
from interior_layout.fengshui_overlay import FENGSHUI  # noqa: E402  (ensure import path)
from interior_layout import frameworks as fw_mod  # noqa: E402

SCENARIOS_PATH = _HERE / "data" / "scenarios.json"
LOG_PATH = _HERE / "PASS_FAIL_LOG.md"
RESULTS_PATH = _HERE / "results.json"


def _check_assertion(name: str, d, scenario: Dict[str, Any]) -> bool:
    if name == "gates_passed":
        return bool(d.gates_passed)
    if name == "gates_failed":
        return not d.gates_passed
    if name == "scorecard_has_8_dims":
        return len(d.scorecard.dimensions) == 8
    if name == "no_scorecard":
        return len(d.scorecard.dimensions) == 0
    if name == "roadmap_nonempty":
        return len(d.roadmap.items) > 0
    if name == "fengshui_enabled":
        return bool(d.fengshui.enabled)
    if name == "fengshui_labelled":
        return "TRADITIONAL" in (d.fengshui.label or "") or "CULTURAL" in (d.fengshui.label or "")
    if name == "clarifying_questions_present":
        return len(d.clarifying_questions) > 0
    if name == "degraded_mode":
        return bool(d.degraded_mode)
    if name == "degradation_note_present":
        return bool(d.degradation_note)
    if name == "frameworks_cited_from_internal":
        return any("Feng Shui" in c or "Neufert" in c or "Alexander" in c
                   or "WELL" in c or "Gestalt" in c for c in d.frameworks_cited)
    if name == "low_overall_score":
        return d.scorecard.weighted_total < 60
    if name == "fengshui_disabled":
        return d.fengshui.enabled is False
    if name == "no_renovation_roadmap_items":
        # No roadmap item should require structural work when renovation forbidden.
        structural_markers = ("Widen", "Repartition", "Re-establish", "Right-size", "Reform the kitchen")
        return all(not any(m in i.title for m in structural_markers) for i in d.roadmap.items)
    raise ValueError("Unknown assertion: %s" % name)


def _check_frameworks(expected: List[str], d) -> bool:
    if not expected:
        return True
    blob = " ".join(d.frameworks_cited + d.sources)
    return all(k.lower() in blob.lower() for k in expected)


def run_all() -> Dict[str, Any]:
    scenarios = json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))
    results: List[Dict[str, Any]] = []
    all_pass = True
    for sc in scenarios:
        options = sc.get("options", {}) or {}
        d = run(sc["input"], live_search=options.get("live_search", True),
                allow_assumption_based_score=options.get("allow_assumptions", False))
        assertion_results = []
        for a in sc.get("assertions", []):
            ok = _check_assertion(a, d, sc)
            assertion_results.append({"assertion": a, "passed": ok})
        fw_ok = _check_frameworks(sc.get("expected_frameworks", []), d)
        scenario_pass = all(r["passed"] for r in assertion_results) and fw_ok
        all_pass = all_pass and scenario_pass
        results.append({
            "id": sc["id"],
            "description": sc["description"],
            "passed": scenario_pass,
            "weighted_total": d.scorecard.weighted_total,
            "overall_band": d.scorecard.overall_band,
            "gates_passed": d.gates_passed,
            "degraded_mode": d.degraded_mode,
            "frameworks_cited": d.frameworks_cited,
            "roadmap_items": len(d.roadmap.items),
            "assertions": assertion_results,
            "frameworks_match": fw_ok,
            "gate_details": [{"name": g.name, "passed": g.passed, "detail": g.detail}
                             for g in d.gates],
        })
    summary = {
        "run_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "total": len(results),
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "all_pass": all_pass,
        "results": results,
    }
    return summary


def write_log(summary: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("# PASS / FAIL LOG - Interior Design & Space Layout harness")
    lines.append("")
    lines.append("Run at: %s" % summary["run_at"])
    lines.append("Scenarios: %d total | %d passed | %d failed | ALL_PASS=%s"
                 % (summary["total"], summary["passed"], summary["failed"],
                    summary["all_pass"]))
    lines.append("")
    lines.append("## Summary")
    lines.append("| # | Scenario | Result | Total | Band | Gates | Degraded | Roadmap items |")
    lines.append("|---|----------|--------|-------|------|-------|----------|---------------|")
    for i, r in enumerate(summary["results"], 1):
        lines.append("| %d | %s | %s | %s | %s | %s | %s | %d |" % (
            i, r["id"], "PASS" if r["passed"] else "FAIL",
            r["weighted_total"], r["overall_band"],
            "pass" if r["gates_passed"] else "fail",
            "yes" if r["degraded_mode"] else "no", r["roadmap_items"]))
    lines.append("")
    lines.append("## Per-scenario detail")
    for r in summary["results"]:
        lines.append("### %s - %s" % (r["id"], "PASS" if r["passed"] else "FAIL"))
        lines.append("- Description: %s" % r["description"])
        lines.append("- Frameworks cited: %s" % (", ".join(r["frameworks_cited"]) or "(none)"))
        lines.append("- Frameworks match expected: %s" % r["frameworks_match"])
        lines.append("- Assertions:")
        for a in r["assertions"]:
            lines.append("  - [%s] %s" % ("PASS" if a["passed"] else "FAIL", a["assertion"]))
        lines.append("- Gates:")
        for g in r["gate_details"]:
            lines.append("  - [%s] %s - %s" % ("PASS" if g["passed"] else "FAIL", g["name"], g["detail"]))
        lines.append("")
    LOG_PATH.write_text("\n".join(lines), encoding="utf-8")
    RESULTS_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Run the harness test scenarios.")
    p.add_argument("--print-markdown", action="store_true", help="Print the PASS/FAIL log to stdout.")
    args = p.parse_args(argv)
    summary = run_all()
    write_log(summary)
    print("Ran %d scenarios: %d passed, %d failed. ALL_PASS=%s"
          % (summary["total"], summary["passed"], summary["failed"], summary["all_pass"]))
    print("Log: %s" % LOG_PATH)
    if args.print_markdown:
        print(LOG_PATH.read_text(encoding="utf-8"))
    return 0 if summary["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
