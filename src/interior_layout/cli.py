"""Command-line interface for the interior-space-layout-design harness.

Usage::

    interior-layout evaluate --input scenario.json --output report.md
    interior-layout evaluate --json scenario.json          # emit JSON deliverable
    interior-layout gates --input scenario.json            # print gate status only
    interior-layout clarifying-questions --input partial.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

from .main import render_markdown, run
from .intake import build_profile, clarifying_questions, mandatory_fields_missing


def _load_input(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise SystemExit("Input file not found: %s" % p)
    with p.open("r", encoding="utf-8") as f:
        if p.suffix.lower() == ".json":
            return json.load(f)
        # Allow a minimal "key: value" free-form fallback for quick demos.
        text = f.read()
        return {"raw_description": text, "goals": [], "rooms": [], "occupants": []}


def cmd_evaluate(args: argparse.Namespace) -> int:
    data = _load_input(args.input)
    deliverable = run(data, live_search=not args.offline,
                      allow_assumption_based_score=args.allow_assumptions)
    if args.json:
        print(deliverable.to_json())
    else:
        print(render_markdown(deliverable))
    return 0 if deliverable.gates_passed else 1


def cmd_gates(args: argparse.Namespace) -> int:
    data = _load_input(args.input)
    deliverable = run(data, live_search=not args.offline)
    for g in deliverable.gates:
        print("[%s] %s - %s" % ("PASS" if g.passed else "FAIL", g.name, g.detail))
    print("ALL_PASS=%s" % ("true" if deliverable.gates_passed else "false"))
    return 0 if deliverable.gates_passed else 1


def cmd_clarifying(args: argparse.Namespace) -> int:
    data = _load_input(args.input)
    profile = build_profile(data, strict=False)
    missing = mandatory_fields_missing(profile)
    questions = clarifying_questions(profile)
    print(json.dumps({"missing": missing, "questions": questions, "unknowns": profile.unknowns},
                     indent=2, ensure_ascii=False))
    return 0 if not missing else 2


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="interior-layout",
                                description="Interior Design & Space Layout scoring harness.")
    sub = p.add_subparsers(dest="command", required=True)

    e = sub.add_parser("evaluate", help="Run the full harness and emit a report.")
    e.add_argument("--input", required=True, help="Path to a JSON profile file.")
    e.add_argument("--output", help="Optional path to write the markdown report.")
    e.add_argument("--json", action="store_true", help="Emit the JSON deliverable instead of markdown.")
    e.add_argument("--offline", action="store_true", help="Run in degraded (no live search) mode.")
    e.add_argument("--allow-assumptions", action="store_true",
                   help="Score even when mandatory fields are missing (assumptions flagged).")
    e.set_defaults(func=cmd_evaluate)

    g = sub.add_parser("gates", help="Run the harness and print only quality-gate status.")
    g.add_argument("--input", required=True)
    g.add_argument("--offline", action="store_true")
    g.set_defaults(func=cmd_gates)

    c = sub.add_parser("clarifying-questions", help="Print clarifying questions for an incomplete intake.")
    c.add_argument("--input", required=True)
    c.set_defaults(func=cmd_clarifying)
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "output", None) and not args.json:
        data = _load_input(args.input)
        deliverable = run(data, live_search=not args.offline,
                          allow_assumption_based_score=getattr(args, "allow_assumptions", False))
        Path(args.output).write_text(render_markdown(deliverable), encoding="utf-8")
        print("Report written to %s" % args.output)
        return 0 if deliverable.gates_passed else 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
