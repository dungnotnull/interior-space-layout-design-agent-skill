"""Shared cluster contract for the ``design-creative-media`` skill cluster.

Sibling skills (e.g. colour-and-material-palette, lighting-design,
acoustic-room-tuning) can reuse this package's standardized output schema
(``Deliverable``), the named-framework registry, and the quality-gate runner
without re-implementing them. This module is the stable, versioned import
surface for cross-skill wiring (Phase 5).

Reuse map
---------
- ``Deliverable`` / ``ScoreCard`` / ``DimensionScore`` - shared scored-deliverable
  schema (schema_version = 1.0.0).
- ``frameworks.FRAMEWORKS`` - shared named-framework registry; sibling skills
  add their own ``Framework`` entries to the same dict or consume ours.
- ``gates.run_all_gates`` - shared quality-gate runner (every dimension scored
  with evidence; at least one framework cited; measurable roadmap items; no
  silent assumptions; labelled overlays; devil's-advocate review).
- ``intake.build_profile`` + ``clarifying_questions`` - shared intake contract.
- ``improvement_roadmap.RECIPES`` - constraint-aware remediation recipe library;
  sibling skills may register additional recipes keyed by weakness signature.

To reuse from a sibling skill::

    from interior_layout.cluster_contract import (
        CLUSTER_SCHEMA_VERSION, build_shared_deliverable, run_shared_gates,
        register_framework, register_recipe,
    )
"""
from __future__ import annotations

from typing import Any, Dict, List

from .frameworks import FRAMEWORKS, Framework, DEFAULT_WEIGHTS, DIMENSIONS
from .improvement_roadmap import RECIPES
from .schema import (
    Deliverable,
    DimensionScore,
    GateResult,
    Profile,
    Roadmap,
    RoadmapItem,
    ScoreCard,
    SCHEMA_VERSION,
)

CLUSTER_SCHEMA_VERSION = SCHEMA_VERSION  # 1.0.0 - shared across the cluster

__all__ = [
    "CLUSTER_SCHEMA_VERSION",
    "Deliverable", "ScoreCard", "DimensionScore", "Roadmap", "RoadmapItem",
    "GateResult", "Profile", "Framework", "FRAMEWORKS", "DIMENSIONS",
    "DEFAULT_WEIGHTS", "RECIPES",
    "register_framework", "register_recipe", "build_shared_deliverable",
    "run_shared_gates",
]


def register_framework(framework: Framework) -> None:
    """Add a sibling-skill framework to the shared registry.

    Raises ``ValueError`` if a different framework is already registered under
    the same key (guard against silent collisions across skills).
    """
    existing = FRAMEWORKS.get(framework.key)
    if existing is not None and existing is not framework:
        raise ValueError("Framework key collision: %s is already registered." % framework.key)
    FRAMEWORKS[framework.key] = framework


def register_recipe(key: str, recipe: Dict[str, Any]) -> None:
    """Register an additional constraint-aware remediation recipe."""
    RECIPES[key] = recipe


def build_shared_deliverable(profile: Profile, scorecard: ScoreCard,
                              roadmap: Roadmap, gate_results: List[GateResult],
                              frameworks_cited: List[str], sources: List[str],
                              executive_summary: str, top_findings: List[str],
                              fengshui=None, degraded: bool = False,
                              degradation_note: str = "") -> Deliverable:
    """Assemble a cluster-standard Deliverable from sub-skill outputs."""
    from .schema import FengShuiOverlay
    if fengshui is None:
        fengshui = FengShuiOverlay(enabled=False, label="", facing_direction="unknown")
    return Deliverable(
        schema_version=SCHEMA_VERSION,
        project_id=profile.project_id,
        executive_summary=executive_summary,
        top_findings=top_findings,
        scorecard=scorecard,
        findings=list(scorecard.dimensions),
        roadmap=roadmap,
        fengshui=fengshui,
        frameworks_cited=frameworks_cited,
        sources=sources,
        gates=gate_results,
        gates_passed=all(g.passed for g in gate_results),
        degraded_mode=degraded,
        degradation_note=degradation_note,
    )


def run_shared_gates(profile: Profile, scorecard: ScoreCard, roadmap: Roadmap,
                     overlay_label: str = "") -> List[GateResult]:
    """Run the cluster-standard quality gates for any sibling skill."""
    from .gates import (gate_no_silent_assumptions, gate_every_dimension_scored,
                        gate_framework_cited, gate_roadmap_measurable,
                        gate_fengshui_labelled, devils_advocate)
    gates: List[GateResult] = [
        gate_no_silent_assumptions(profile),
        gate_every_dimension_scored(scorecard),
        gate_framework_cited(scorecard),
        gate_roadmap_measurable(roadmap),
        gate_fengshui_labelled({"label": overlay_label}) if overlay_label
        else GateResult(name="overlay_labelled", passed=True,
                        detail="No labelled overlay produced; gate n/a."),
        devils_advocate(scorecard, roadmap),
    ]
    return gates
