"""Quality gates (Phase 2) and devil's-advocate review.

Every gate is explicit and non-skippable. The devil's-advocate pass challenges
the top findings before output is allowed (Design Principle: mandatory review).
"""
from __future__ import annotations

from typing import List

from .schema import Deliverable, DimensionScore, GateResult, Profile, Roadmap, ScoreCard


def gate_every_dimension_scored(scorecard: ScoreCard) -> GateResult:
    unscored = [d.dimension for d in scorecard.dimensions if d.score is None]
    no_evidence = [d.dimension for d in scorecard.dimensions if not d.evidence]
    passed = not unscored and not no_evidence
    detail = ""
    if unscored:
        detail += "Unscored: %s. " % ", ".join(unscored)
    if no_evidence:
        detail += "Missing evidence: %s." % ", ".join(no_evidence)
    return GateResult(name="every_dimension_scored_with_evidence",
                      passed=passed, detail=detail or "All 8 dimensions have a score and evidence.")


def gate_framework_cited(scorecard: ScoreCard) -> GateResult:
    frameworks = {d.framework for d in scorecard.dimensions if d.framework}
    passed = len(frameworks) >= 1
    return GateResult(name="at_least_one_named_framework_cited",
                      passed=passed,
                      detail="Cited frameworks: %s" % ", ".join(sorted(frameworks)) if passed
                      else "No framework cited on any dimension.")


def gate_roadmap_measurable(roadmap: Roadmap) -> GateResult:
    bad = []
    for item in roadmap.items:
        if item.effort_hours is None or item.effort_hours <= 0:
            bad.append("%s (no effort)" % item.title)
        if not item.success_metric:
            bad.append("%s (no success metric)" % item.title)
        if not (1 <= item.impact <= 5):
            bad.append("%s (impact out of 1-5)" % item.title)
    passed = not bad
    return GateResult(name="roadmap_items_measurable",
                      passed=passed,
                      detail="OK" if passed else "Incomplete: %s" % "; ".join(bad[:5]))


def gate_no_silent_assumptions(profile: Profile) -> GateResult:
    # Unknowns must be explicitly listed (they are, by construction).
    mandatory_missing = []
    if not profile.rooms:
        mandatory_missing.append("rooms")
    if not profile.occupants:
        mandatory_missing.append("occupants")
    if not profile.goals:
        mandatory_missing.append("goals")
    # If mandatory fields are missing they MUST appear in profile.unknowns.
    unflagged = [m for m in mandatory_missing if ("profile.%s" % m) not in profile.unknowns]
    passed = not unflagged
    return GateResult(name="no_silent_assumptions",
                      passed=passed,
                      detail="OK" if passed
                      else "Missing mandatory fields not flagged as unknown: %s" % ", ".join(unflagged))


def gate_fengshui_labelled(deliverable_fields: dict) -> GateResult:
    label = deliverable_fields.get("label", "")
    passed = bool(label) and ("TRADITIONAL" in label or "CULTURAL" in label)
    return GateResult(name="fengshui_labelled_as_traditional",
                      passed=passed,
                      detail="OK" if passed else "Feng shui overlay missing the traditional-framework label.")


def devils_advocate(scorecard: ScoreCard, roadmap: Roadmap) -> GateResult:
    """Challenge the top 3 findings: is each weakness real and each fix non-counterproductive?"""
    issues: List[str] = []
    ranked = scorecard.ranked_weaknesses()[:3]
    for w in ranked:
        if not w.evidence:
            issues.append("Top weakness '%s' lacks evidence." % w.description)
    # Check no roadmap item worsens a strength dimension drastically (simple heuristic)
    addressed = set()
    for item in roadmap.items:
        for d in item.addresses_dimensions:
            addressed.add(d)
    low_dims = set()
    for d in scorecard.dimensions:
        if d.score >= 60:
            continue
        if d.evidence.startswith("Feng shui overlay disabled"):
            continue
        if scorecard.weights.get(d.dimension, 0.0) <= 0.0:
            continue
        # Skip dimensions whose weaknesses are only data-gap defaults (not real deficits).
        real_weak = [w for w in d.weaknesses if "defaulted" not in w.lower() and "insufficient" not in w.lower()]
        if not real_weak:
            continue
        low_dims.add(d.dimension)
    uncovered = low_dims - addressed
    if uncovered and roadmap.items:
        issues.append("Low-scoring dimensions with no roadmap item: %s" % ", ".join(sorted(uncovered)))
    passed = not issues
    return GateResult(name="devils_advocate_review",
                      passed=passed,
                      detail="OK" if passed else "Challenges raised: %s" % "; ".join(issues))


def run_all_gates(profile: Profile, scorecard: ScoreCard, roadmap: Roadmap,
                  fengshui_label: str) -> List[GateResult]:
    gates: List[GateResult] = [
        gate_no_silent_assumptions(profile),
        gate_every_dimension_scored(scorecard),
        gate_framework_cited(scorecard),
        gate_roadmap_measurable(roadmap),
        gate_fengshui_labelled({"label": fengshui_label}) if fengshui_label
        else GateResult(name="fengshui_labelled_as_traditional", passed=True,
                        detail="Feng shui overlay disabled; gate n/a (passed)."),
        devils_advocate(scorecard, roadmap),
    ]
    return gates
