"""Main harness - orchestrates the full Interior Design & Space Layout pipeline.

Flow: intake -> framework-selector -> scoring-engine -> improvement-roadmap ->
fengshui-overlay -> quality gates -> synthesis. No gate is skippable.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from . import gates as gates_mod
from .fengshui_overlay import build_overlay
from .framework_selector import FrameworkSelection, select_frameworks
from .improvement_roadmap import build_roadmap
from .intake import build_profile, clarifying_questions, mandatory_fields_missing
from .scoring_engine import score as run_scoring
from .schema import Deliverable, Profile
from .synthesis import build_clarification_deliverable, build_deliverable


def run(data: Dict[str, Any],
        live_search: bool = True,
        allow_assumption_based_score: bool = False) -> Deliverable:
    """Run the full harness on a raw intake dict.

    Parameters
    ----------
    data:
        Semi-structured user request (see ``tests/scenarios`` for the schema).
    live_search:
        Whether WebSearch/WebFetch are available. When False the harness runs
        in degraded mode and states the limitation (Scenario 7 behaviour).
    allow_assumption_based_score:
        If True, score even when mandatory fields are missing (assumptions are
        flagged). Default False - mandatory gaps return a clarification
        deliverable instead of a fabricated score (Scenario 6 behaviour).
    """
    profile = build_profile(data, strict=False)

    missing = mandatory_fields_missing(profile)
    degraded = (not live_search) or bool(profile.unknowns)
    degradation_note = ""
    if not live_search:
        degradation_note = ("WebSearch/WebFetch unavailable. Scores rely on the "
                            "embedded SECOND-KNOWLEDGE-BRAIN.md knowledge base and "
                            "the named frameworks; confidence is reduced.")

    if missing and not allow_assumption_based_score:
        questions = clarifying_questions(profile)
        return build_clarification_deliverable(profile, questions, degraded, degradation_note)

    selection: FrameworkSelection = select_frameworks(profile)
    scorecard = run_scoring(profile, selection)
    roadmap = build_roadmap(scorecard, profile)

    fengshui_enabled = any(f.key == "fengshui" for f in selection.frameworks)
    fengshui = build_overlay(profile, enabled=fengshui_enabled)

    gate_results = gates_mod.run_all_gates(profile, scorecard, roadmap, fengshui.label)
    return build_deliverable(profile, selection, scorecard, roadmap,
                             fengshui, gate_results, degraded, degradation_note)


def render_markdown(deliverable: Deliverable) -> str:
    """Render a deliverable as the user-facing markdown report (Output Format)."""
    d = deliverable
    lines = []
    lines.append("# Interior Design & Space Layout - Assessment Report")
    lines.append("")
    lines.append("**Schema version:** %s  |  **Project:** %s" % (d.schema_version, d.project_id))
    if d.degraded_mode:
        lines.append("> **Degraded mode:** %s" % (d.degradation_note or "reduced confidence"))
    lines.append("")
    lines.append("## 1. Executive Summary")
    lines.append(d.executive_summary)
    lines.append("")
    lines.append("### Top findings")
    for f in d.top_findings:
        lines.append("- %s" % f)
    lines.append("")

    if d.clarifying_questions:
        lines.append("## Clarifying questions (intake incomplete)")
        for q in d.clarifying_questions:
            lines.append("- %s" % q)
        lines.append("")

    if d.scorecard.dimensions:
        lines.append("## 2. Scorecard")
        lines.append("| Dimension | Score | Band | Framework | Evidence |")
        lines.append("|---|---|---|---|---|")
        for dim in d.scorecard.dimensions:
            lines.append("| %s | %.0f | %s | %s | %s |" % (
                dim.dimension, dim.score, dim.band, dim.framework, dim.evidence.replace("|", "/")))
        lines.append("")
        lines.append("**Weighted total: %.0f/100 (%s)**" % (d.scorecard.weighted_total, d.scorecard.overall_band))
        lines.append("")

        lines.append("## 3. Detailed Findings")
        for dim in d.findings:
            lines.append("### %s - %.0f/100 (%s)" % (dim.dimension, dim.score, dim.band))
            lines.append("- Framework: %s" % dim.framework)
            lines.append("- Evidence: %s" % dim.evidence)
            if dim.strengths:
                lines.append("- Strengths:")
                for s in dim.strengths:
                    lines.append("  - %s" % s)
            if dim.weaknesses:
                lines.append("- Weaknesses:")
                for w in dim.weaknesses:
                    lines.append("  - %s" % w)
            lines.append("")

    if d.roadmap.items:
        lines.append("## 4. Prioritized Improvement Roadmap")
        for tier_label, tier_key in (("Quick wins", "quick_win"),
                                     ("Major projects", "major_project"),
                                     ("Long-term", "long_term")):
            items = d.roadmap.by_tier(tier_key)
            if not items:
                continue
            lines.append("### %s" % tier_label)
            for item in items:
                lines.append("- **%s**" % item.title)
                lines.append("  - Effort: %.1fh (%s) | Impact: %d/5 (%s) | Metric: %s"
                             % (item.effort_hours, item.effort_level, item.impact,
                                item.impact_description, item.success_metric))
                if item.cost_estimate_usd is not None:
                    lines.append("  - Estimated cost: ~$%.0f" % item.cost_estimate_usd)
                if item.steps:
                    lines.append("  - Steps:")
                    for st in item.steps:
                        lines.append("    - %s" % st)
                if item.references:
                    lines.append("  - References: %s" % "; ".join(item.references))
            lines.append("")

    if d.fengshui.enabled or d.fengshui.bagua_sectors:
        lines.append("## 5. Feng Shui Overlay")
        lines.append("> %s" % d.fengshui.label)
        lines.append("- Facing direction: %s" % d.fengshui.facing_direction)
        if d.fengshui.bagua_sectors:
            lines.append("### Bagua sectors")
            lines.append("| Sector | Aspect | Element | Direction | Present |")
            lines.append("|---|---|---|---|---|")
            for s in d.fengshui.bagua_sectors:
                lines.append("| %s | %s | %s | %s | %s |" % (
                    s.name, s.life_aspect, s.element, s.direction,
                    "yes" if s.present else "no"))
        if d.fengshui.command_position_notes:
            lines.append("### Command-position notes")
            for n in d.fengshui.command_position_notes:
                lines.append("- %s" % n)
        if d.fengshui.remedies:
            lines.append("### Remedies")
            for r in d.fengshui.remedies:
                lines.append("- %s" % r)
        lines.append("")

    lines.append("## 6. Sources & Frameworks Cited")
    for s in d.sources:
        lines.append("- %s" % s)
    for fw in d.frameworks_cited:
        lines.append("- Framework: %s" % fw)
    lines.append("")

    lines.append("## 7. Quality Gates")
    for g in d.gates:
        mark = "PASS" if g.passed else "FAIL"
        lines.append("- [%s] %s - %s" % (mark, g.name, g.detail))
    lines.append("")
    lines.append("**All gates passed: %s**" % ("yes" if d.gates_passed else "no"))
    return "\n".join(lines)
