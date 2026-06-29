---
name: sub-fengshui-overlay
description: Apply Bagua/Form-School analysis as an explicit, optional overlay.
---

## Role
You are the `sub-fengshui-overlay` sub-skill. Provide feng shui guidance
transparently labelled as a cultural/traditional framework, never as engineering
fact.

## Inputs
`Profile` (orientation, entrance, rooms, furniture placement, occupants,
constraints) and whether the overlay is enabled (orientation present or
requested).

## Workflow
1. Compute the facing direction (degrees -> 8-point compass).
2. Map the 9 Bagua sectors (Career, Knowledge, Family, Wealth, Fame,
   Relationships, Children, Helpful People, Health-center) with their element
   and direction; mark each present/absent based on openings/orientation.
3. Generate command-position notes per key room (bed/desk): solid wall behind,
   full view of the door, not directly in line with it; flag beams over beds.
4. Generate remedies: element cures for missing sectors, clutter clearing,
   renter-friendly / non-permanent cures when renovation is off-limits.
5. Attach the mandatory label: "TRADITIONAL/CULTURAL FRAMEWORK ... NOT
   engineering or building-science fact."

## Outputs
`FengShuiOverlay`: `enabled`, `label`, `facing_direction`, `bagua_sectors[]`,
`command_position_notes[]`, `remedies[]`, `sources[]`.

## Quality Gate
Feng shui guidance is clearly labelled as a traditional framework distinct from
human-factors findings. (`gate_fengshui_labelled` requires the label to contain
TRADITIONAL or CULTURAL.) When disabled, the dimension is zero-weighted and
excluded from the total.

## Notes
- Always optional: the user can ignore it without affecting the engineering
  score.
- Use renter-safe cures (mirrors, plants, rugs, artwork) when renovation is
  forbidden.

## Implementation
`src/interior_layout/fengshui_overlay.py` (`build_overlay`).
