---
name: sub-improvement-roadmap
description: Prioritized improvement roadmap for the layout with effort/impact.
---

## Role
You are the `sub-improvement-roadmap` sub-skill. Convert ranked weaknesses into
a sequenced, effort/impact-ranked action plan the user can actually execute.

## Inputs
`ScoreCard.ranked_weaknesses()` (severity-ranked), `Profile.constraints`.

## Workflow
1. Receive ranked weaknesses.
2. Classify each weakness to a remediation `recipe` key (e.g.
   `door_clear_width_low`, `glazing_below_minimum`, `visual_weight_imbalance`,
   `not_command_position`).
3. For each matched recipe, emit a `RoadmapItem`. When a recipe
   `needs_renovation` and the profile forbids renovation, use the recipe's
   furniture-only `alt_*` fields (or skip if none exists).
4. Deduplicate by (recipe key, room).
5. Sort by tier (quick_win -> major_project -> long_term), then impact desc.

## Outputs
`Roadmap` of `RoadmapItem`s, each with:
- `title`, `tier` (quick_win/major_project/long_term)
- `effort_hours`, `effort_level` (trivial/low/medium/high/major)
- `impact` (1-5) + `impact_description`
- `success_metric` (measurable, e.g. "Door clear width >=850mm verified")
- `steps[]`, `references[]`, `addresses_dimensions[]`, `cost_estimate_usd`

Tiers:
- **Quick wins** - <5h, no renovation (declutter, relocate, add rug, mirrors).
- **Major projects** - structural or large purchases (widen doors, add windows).
- **Long-term** - repartitioning, re-zoning.

## Quality Gate
Every recommendation has effort, impact, and a measurable success criterion.
(`gate_roadmap_measurable`.) Renovation-required items never appear when the
profile forbids renovation.

## Implementation
`src/interior_layout/improvement_roadmap.py` (`build_roadmap`, `RECIPES`).
Recipes are constraint-aware and reusable cluster-wide via
`cluster_contract.register_recipe`.
