---
name: sub-scoring-engine
description: Multi-dimensional scoring of the layout against the selected framework.
---

## Role
You are the `sub-scoring-engine` sub-skill. Produce a transparent,
dimension-by-dimension score (0-100 + band) with evidence for every sub-score.

## Inputs
Normalized `Profile` + `FrameworkSelection` (frameworks + weights + thresholds).

## Dimensions, primary framework, and key thresholds
| Dimension | Primary framework | Key thresholds |
|---|---|---|
| Function & zoning | Alexander | Intimacy Gradient; Neufert area minima (bedroom 9m2, kitchen 7m2, bath 3.5m2, living 14m2/person) |
| Circulation & flow | Neufert | corridor 0.90/1.20m; door clear 0.85m; kitchen work triangle 4-9m, legs 1.2-2.7m; furniture footprint <35% of floor |
| Ergonomics & clearances | Neufert | bed access 0.5m; desk chair 0.6m; living area >=14m2/person |
| Natural light & ventilation | WELL v2 | glazing/floor 5-10%; cross-ventilation on >=2 walls; operable share >=40%; daylight depth 2.5x head height |
| Aesthetic balance (Gestalt) | Gestalt | visual-weight imbalance <40%; 1-2 focal points |
| Feng shui harmony | Feng Shui (cultural) | command position; clutter-free open floor >=60% |
| Storage adequacy | Neufert | ~1500L/person |
| Acoustic comfort | WELL v2 | soft-surface >=20%; estimated RT60 <=0.6s (Sabine proxy) |

## Workflow
1. Receive `Profile` + `FrameworkSelection`.
2. For each of the 8 dimensions, run the dedicated scorer applying the primary
   framework's thresholds.
3. Compute each sub-score by linear interpolation between an `ok` and a `bad`
   threshold; clamp to 0-100.
4. Record one-line evidence per dimension plus `strengths[]` and `weaknesses[]`.
5. Compute the weighted total using the selector's weights (disabled feng shui
   is zero-weighted and excluded from the total).
6. Assign a band: excellent >=90, good >=75, fair >=60, weak >=40, poor <40.

## Outputs
`ScoreCard`: `dimensions[]` (each `dimension`, `score`, `band`, `evidence`,
`framework`, `strengths[]`, `weaknesses[]`), `weighted_total`, `weights`,
`overall_band`, plus `ranked_weaknesses()`.

## Quality Gate
Every dimension has a numeric score AND a one-line evidence/justification; no
unscored dimension. (`gate_every_dimension_scored_with_evidence`.)

## Notes
- Evidence hierarchy: Systematic Review > Meta-Analysis > RCT/Benchmark >
  Cohort/Case Study > Expert Opinion > Blog. Prefer the highest available tier.
- When placement coordinates are absent, placement-based checks are flagged as
  approximate (assumption surfaced, not silent).
- If live sources are unavailable, fall back to `SECOND-KNOWLEDGE-BRAIN.md`.

## Implementation
`src/interior_layout/scoring_engine.py` (`score` + eight `score_*` functions).
