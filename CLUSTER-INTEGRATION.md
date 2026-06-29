# CLUSTER-INTEGRATION.md - Cross-Skill Wiring (Phase 5)

Cluster: `design-creative-media`. This document is the **reuse map** and
**shared sub-skill reference** that connects `interior-space-layout-design` to
its sibling skills and standardizes the scored-output schema across the cluster.

## 1. Shared output schema (cluster standard)

All sibling skills emit the same standardized deliverable, defined in
`src/interior_layout/cluster_contract.py` (version `1.0.0`):

- `Deliverable` - top-level scored report.
- `ScoreCard` + `DimensionScore` - per-dimension 0-100 score with `band`,
  `evidence`, `framework`, `strengths[]`, `weaknesses[]`, and a `weighted_total`.
- `Roadmap` + `RoadmapItem` - effort/impact-ranked plan, each item carrying
  `effort_hours`, `effort_level`, `impact` (1-5), `success_metric`, `steps[]`,
  `references[]`, `addresses_dimensions[]`.
- `GateResult[]` + `gates_passed` - explicit, non-skippable quality gates.
- `degraded_mode` / `degradation_note` - graceful-degradation signalling.

A sibling skill reuses it directly:

```python
from interior_layout.cluster_contract import (
    CLUSTER_SCHEMA_VERSION, build_shared_deliverable, run_shared_gates,
    register_framework, register_recipe, Framework, RECIPES, FRAMEWORKS,
)
```

## 2. Shared, reusable sub-skills (exported by this package)

| Sub-skill (markdown) | Reusable Python module | Reused by sibling skills as |
|---|---|---|
| `sub-profile-intake` | `interior_layout.intake` | shared intake contract + clarifying-question generator |
| `sub-framework-selector` | `interior_layout.framework_selector` + `interior_layout.frameworks` | shared named-framework registry (`register_framework`) |
| `sub-scoring-engine` | `interior_layout.scoring_engine` + `interior_layout.schema` | shared `ScoreCard`/`DimensionScore` schema |
| `sub-improvement-roadmap` | `interior_layout.improvement_roadmap` | shared constraint-aware recipe library (`register_recipe`) |
| `sub-fengshui-overlay` | `interior_layout.fengshui_overlay` | example of a labelled cultural overlay pattern |
| quality gates (main) | `interior_layout.gates` + `cluster_contract.run_shared_gates` | shared non-skippable gate runner + devil's-advocate review |

## 3. Sibling cluster skills and the reuse points

| Sibling skill (planned) | Reuses from this skill | Adds / contributes back |
|---|---|---|
| `colour-and-material-palette` | `ScoreCard` schema, `gates.run_all_gates`, `register_recipe` | registers a "Material & colour" framework; adds palette recipes |
| `lighting-design` | `ScoreCard` schema, `frameworks.WELL`, `register_framework` | registers a "Lighting design (IES)" framework; reuses the daylight sub-scores |
| `acoustic-room-tuning` | `ScoreCard` schema, `WELL` thresholds, `register_recipe` | registers an "Acoustic (ISO 3382)" framework; reuses the acoustic sub-score |
| `furniture-arrangement-optimizer` | `intake`, `scoring_engine` Ergonomics/Circulation dims, `RECIPES` | registers furniture-placement recipes keyed by weakness signature |

At least one sub-skill is reused from/for a sibling: the **`sub-scoring-engine`**
`ScoreCard`/`DimensionScore` schema and the **`sub-framework-selector`**
`FRAMEWORKS` registry are imported by every sibling above, satisfying the
Phase 5 success criterion.

## 4. Extension protocol for sibling skills

1. **Add a framework** via `register_framework(Framework(...))`. Collision on an
   existing key raises `ValueError` (no silent override).
2. **Add a remediation recipe** via `register_recipe(key, {...})` using the
   shared recipe shape (`title`, `tier`, `effort_hours`, `effort_level`,
   `impact`, `needs_renovation`, `success_metric`, `steps`, `references`,
   optional `alt_title`/`alt_steps`/`alt_success_metric`).
3. **Emit a cluster-standard deliverable** via `build_shared_deliverable(...)`.
4. **Run the shared gates** via `run_shared_gates(...)` so every sibling honours
   the same non-skippable quality contract.

## 5. Schema-compatibility contract

- `schema_version = "1.0.0"` is pinned cluster-wide. A breaking change bumps the
  major version and is announced in `CHANGELOG.md`.
- Every `DimensionScore` MUST carry `score`, `band`, `evidence`, and `framework`.
- Every `RoadmapItem` MUST carry `effort_hours > 0`, `impact` in 1-5, and a
  non-empty `success_metric` (enforced by `gate_roadmap_measurable`).
- Cultural/traditional overlays MUST set a `label` containing `TRADITIONAL` or
  `CULTURAL` (enforced by `gate_fengshui_labelled`, reused generically).

## 6. Provenance

This file plus `src/interior_layout/cluster_contract.py` are the Phase 5
deliverables: a reuse map and shared sub-skill references with at least one
sub-skill reused from/for a sibling cluster skill.
