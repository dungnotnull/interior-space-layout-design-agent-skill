"""Synthesis: assembles the final professional deliverable from the harness
outputs and writes the executive summary, top findings, and sources list.
"""
from __future__ import annotations

from typing import List

from .framework_selector import FrameworkSelection
from .schema import (
    Deliverable,
    DimensionScore,
    FengShuiOverlay,
    GateResult,
    Profile,
    Roadmap,
    ScoreCard,
    SCHEMA_VERSION,
)


def top_findings(scorecard: ScoreCard, limit: int = 3) -> List[str]:
    """Highest-leverage findings = lowest-scoring dimensions with evidence."""
    ranked = sorted(scorecard.dimensions, key=lambda d: d.score)
    out: List[str] = []
    for d in ranked[:limit]:
        lead_weak = d.weaknesses[0] if d.weaknesses else d.evidence
        out.append("%s (%.0f/100): %s" % (d.dimension, d.score, lead_weak))
    return out


def executive_summary(profile: Profile, scorecard: ScoreCard,
                       roadmap: Roadmap, degraded: bool) -> str:
    quick = roadmap.by_tier("quick_win")
    major = roadmap.by_tier("major_project")
    longterm = roadmap.by_tier("long_term")
    summary = (
        "Overall layout score: %.0f/100 (%s) across %d rooms totalling %.1f m2 "
        "for %d occupant(s)." % (scorecard.weighted_total, scorecard.overall_band,
                                 len(profile.rooms), profile.total_area_m2,
                                 len(profile.occupants))
    )
    summary += " Roadmap: %d quick win(s), %d major project(s), %d long-term item(s)." % (
        len(quick), len(major), len(longterm))
    if degraded:
        summary += " Running in DEGRADED MODE - live web sources were unavailable; " \
                   "scores rely on the embedded knowledge base and named frameworks."
    if profile.unknowns:
        summary += " %d unknown input field(s) were explicitly flagged rather than assumed." % len(profile.unknowns)
    return summary


def build_deliverable(profile: Profile, selection: FrameworkSelection,
                      scorecard: ScoreCard, roadmap: Roadmap,
                      fengshui: FengShuiOverlay, gates: List[GateResult],
                      degraded: bool, degradation_note: str) -> Deliverable:
    findings: List[DimensionScore] = list(scorecard.dimensions)
    frameworks_cited = sorted({d.framework for d in scorecard.dimensions if d.framework})
    sources = sorted({c for f in selection.frameworks for c in [f.citation, f.source_url]}
                     | {s for s in fengshui.sources})
    gates_passed = all(g.passed for g in gates)
    return Deliverable(
        schema_version=SCHEMA_VERSION,
        project_id=profile.project_id,
        executive_summary=executive_summary(profile, scorecard, roadmap, degraded),
        top_findings=top_findings(scorecard),
        scorecard=scorecard,
        findings=findings,
        roadmap=roadmap,
        fengshui=fengshui,
        frameworks_cited=frameworks_cited,
        sources=sources,
        gates=gates,
        gates_passed=gates_passed,
        degraded_mode=degraded,
        degradation_note=degradation_note,
    )


def build_clarification_deliverable(profile: Profile, questions: List[str],
                                    degraded: bool, degradation_note: str) -> Deliverable:
    """Returned when mandatory intake data is missing - no score is produced
    from assumptions (Scenario 6 behaviour)."""
    from .schema import ScoreCard, FengShuiOverlay, Roadmap
    empty = ScoreCard(dimensions=[], weighted_total=0.0, weights={}, overall_band="not_graded")
    gates = [GateResult(name="no_silent_assumptions", passed=False,
                        detail="Mandatory fields missing: %s" % ", ".join(questions)),
             GateResult(name="every_dimension_scored_with_evidence", passed=False,
                        detail="Scoring skipped pending clarification."),
             GateResult(name="at_least_one_named_framework_cited", passed=False,
                        detail="No framework selected until intake is complete."),
             GateResult(name="roadmap_items_measurable", passed=True,
                        detail="No roadmap produced yet; gate n/a."),
             GateResult(name="fengshui_labelled_as_traditional", passed=True,
                        detail="No feng shui overlay produced yet; gate n/a."),
             GateResult(name="devils_advocate_review", passed=True,
                        detail="No findings to challenge yet; gate n/a.")]
    return Deliverable(
        schema_version=SCHEMA_VERSION,
        project_id=profile.project_id,
        executive_summary=("Insufficient input to score safely. %d mandatory field(s) "
                           "missing. Please answer the clarifying questions; no score "
                           "was produced from assumptions." % len(questions)),
        top_findings=["Intake incomplete - see clarifying questions."],
        scorecard=empty,
        findings=[],
        roadmap=Roadmap(),
        fengshui=FengShuiOverlay(enabled=False, label="", facing_direction="unknown"),
        frameworks_cited=[],
        sources=[],
        gates=gates,
        gates_passed=False,
        degraded_mode=degraded,
        degradation_note=degradation_note,
        clarifying_questions=questions,
    )

