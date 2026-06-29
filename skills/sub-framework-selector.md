---
name: sub-framework-selector
description: Select the most appropriate world-renowned space-planning framework(s) for this case.
---

## Role
You are the `sub-framework-selector` sub-skill. Map the intake context to one or
more named, citable frameworks so scoring is never ad hoc, and derive the
dimension weights the case implies.

## Inputs
Normalized `Profile` (from `sub-profile-intake`), domain sub-type, stated goals.

## Framework registry
- **Neufert** - always selected (clearances/area/storage are universal).
- **Alexander - A Pattern Language** - selected when rooms/zones exist.
- **WELL Building Standard** - selected for habitable/comfort cases (always,
  but down-weighted when no comfort goal is stated).
- **Gestalt** - selected for composition spaces (living/dining/studio) or when
  aesthetic goals are stated.
- **Feng Shui Form School** - selected when the user requests it OR orientation
  data is present; always rendered as an optional cultural overlay.

## Workflow
1. Receive the `Profile`.
2. Apply selection rules (above); de-duplicate while preserving order.
3. Derive dimension weights from goals + constraints:
   - renters down-weight structural-change dimensions, up-weight moveable ones;
   - stated goals up-weight the matching dimension (e.g. "flow" -> Circulation).
4. Zero-weight Feng shui harmony when the overlay is disabled.
5. Renormalize weights to sum to 1.0.
6. Return `FrameworkSelection` (frameworks, weights, rationale per framework,
   rubric notes).

## Outputs
- `frameworks[]` - each with `key`, `name`, `citation`, `source_url`, `governs`,
  `thresholds`, `rationale_template`.
- `weights{}` - per-dimension weights summing to 1.0.
- `rationale{}` - documented reason per selected framework.

## Quality Gate
At least one named framework selected with a source citation and a documented
reason. (`gate_framework_cited` verifies this downstream via the scorecard.)

## Implementation
`src/interior_layout/framework_selector.py` (`select_frameworks`) and
`src/interior_layout/frameworks.py` (registry + thresholds).
