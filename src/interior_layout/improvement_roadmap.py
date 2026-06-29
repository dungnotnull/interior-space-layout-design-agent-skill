"""sub-improvement-roadmap implementation.

Converts ranked weaknesses into a sequenced, effort/impact-ranked action plan.
Each item carries effort, impact, and a measurable success metric (Design
Principle 3). Recommendations respect renovation constraints.
"""
from __future__ import annotations

from typing import Dict, List

from .frameworks import ALEXANDER, FENGSHUI, GESTALT, NEUFERT, WELL
from .schema import (
    EffortLevel,
    Profile,
    Roadmap,
    RoadmapItem,
    RoadmapTier,
    ScoreCard,
    Weakness,
)


# Remediation recipe library keyed by a normalized weakness signature.
# Each recipe is constraint-aware: ``needs_renovation`` items are skipped when
# the profile forbids renovation, replaced by a furniture-only alternative.
RECIPES: Dict[str, Dict] = {
    "area_below_minimum": {
        "title": "Right-size the {room} to meet the {min}m2 minimum",
        "tier": RoadmapTier.MAJOR_PROJECT.value,
        "effort_hours": 40.0,
        "effort_level": EffortLevel.HIGH.value,
        "impact": 4,
        "needs_renovation": True,
        "success_metric": "{room} area >= {min}m2 (measured on revised plan).",
        "steps": [
            "Sketch the revised footprint keeping structural loads viable.",
            "Move a non-load-bearing partition to recover the missing area.",
            "Re-validate circulation clearances after the move.",
        ],
        "alt_title": "Re-zone the {room} with furniture to recover usable area",
        "alt_steps": [
            "Remove one low-priority furniture piece to free floor area.",
            "Add a wall-mounted fold-away piece (e.g. Murphy desk) to reclaim function.",
            "Re-measure usable circulation area after decluttering.",
        ],
        "alt_success_metric": "Usable {room} circulation area increases by >=1m2.",
        "references": [NEUFERT.citation],
    },
    "door_clear_width_low": {
        "title": "Widen the {room} door to >=850mm clear",
        "tier": RoadmapTier.MAJOR_PROJECT.value,
        "effort_hours": 12.0,
        "effort_level": EffortLevel.MEDIUM.value,
        "impact": 4,
        "needs_renovation": True,
        "success_metric": "Door clear width >=850mm verified with a measuring tape.",
        "steps": [
            "Replace the door frame with an 900mm unit; keep swing direction.",
            "Rehang the door to preserve 850mm clear opening.",
        ],
        "alt_title": "Swap the {room} door for a pocket/slide unit (no wall move)",
        "alt_steps": [
            "Install a surface-mounted sliding door kit.",
            "Verify 850mm clear opening and no swing obstruction.",
        ],
        "alt_success_metric": "Door clear width >=850mm with no structural change.",
        "references": [NEUFERT.citation],
    },
    "hallway_width_low": {
        "title": "Widen {room} to a 1200mm two-way corridor",
        "tier": RoadmapTier.MAJOR_PROJECT.value,
        "effort_hours": 24.0,
        "effort_level": EffortLevel.HIGH.value,
        "impact": 3,
        "needs_renovation": True,
        "success_metric": "Corridor clear width >=1200mm along its full length.",
        "steps": ["Realign the enclosing partition; preserve load path.", "Re-test two-way passage."],
        "alt_title": "Reclaim hallway width by removing intrusive furniture",
        "alt_steps": ["Remove consoles/shelves encroaching the corridor.", "Keep >=900mm one-way clear."],
        "alt_success_metric": "Corridor clear width >=900mm one-way.",
        "references": [NEUFERT.citation, ALEXANDER.citation],
    },
    "work_triangle_out_of_range": {
        "title": "Reform the kitchen work triangle to 4-9m total",
        "tier": RoadmapTier.MAJOR_PROJECT.value,
        "effort_hours": 20.0,
        "effort_level": EffortLevel.HIGH.value,
        "impact": 5,
        "needs_renovation": False,
        "success_metric": "Sum of sink-cook-store legs between 4m and 9m; each leg 1.2-2.7m.",
        "steps": [
            "Relocate the refrigerator or cooktop to bring legs into range.",
            "Add a mobile island/prep cart if a leg is too long.",
        ],
        "references": [NEUFERT.citation],
    },
    "crowded_circulation": {
        "title": "Declutter {room} to restore circulation reserve",
        "tier": RoadmapTier.QUICK_WIN.value,
        "effort_hours": 3.0,
        "effort_level": EffortLevel.LOW.value,
        "impact": 3,
        "needs_renovation": False,
        "success_metric": "Furniture footprint share of {room} floor drops below 50%.",
        "steps": ["Remove one redundant piece.", "Relocate the kept piece against a wall."],
        "references": [NEUFERT.citation, ALEXANDER.citation],
    },
    "glazing_below_minimum": {
        "title": "Add daylight to {room} (window or light tube)",
        "tier": RoadmapTier.MAJOR_PROJECT.value,
        "effort_hours": 16.0,
        "effort_level": EffortLevel.HIGH.value,
        "impact": 5,
        "needs_renovation": True,
        "success_metric": "{room} glazing/floor ratio >=5%; measured daylight factor >=1.5%.",
        "steps": ["Cut a new opening or enlarge existing window.", "Add operable sash for ventilation."],
        "alt_title": "Boost {room} daylight without structural change",
        "alt_steps": [
            "Add a mirror opposite the window to bounce daylight.",
            "Swap heavy drapes for sheer blinds; paint walls light reflectance.",
        ],
        "alt_success_metric": "Perceived daylight brightness increases; measured at desk >=300 lux daytime.",
        "references": [WELL.citation],
    },
    "no_cross_ventilation": {
        "title": "Create cross ventilation in {room}",
        "tier": RoadmapTier.QUICK_WIN.value,
        "effort_hours": 2.0,
        "effort_level": EffortLevel.LOW.value,
        "impact": 4,
        "needs_renovation": False,
        "success_metric": "{room} has operable openings on >=2 walls or a paired high/low vent path.",
        "steps": ["Make the existing window operable.", "Add a through-wall vent on the opposite wall."],
        "references": [WELL.citation],
    },
    "low_operable_window_ratio": {
        "title": "Make {room} windows operable",
        "tier": RoadmapTier.QUICK_WIN.value,
        "effort_hours": 4.0,
        "effort_level": EffortLevel.LOW.value,
        "impact": 3,
        "needs_renovation": False,
        "success_metric": ">=80% of {room} glazing is operable.",
        "steps": ["Replace fixed sash with casement/awning.", "Verify hardware opens fully."],
        "references": [WELL.citation],
    },
    "daylight_depth_short": {
        "title": "Extend daylight reach in {room}",
        "tier": RoadmapTier.QUICK_WIN.value,
        "effort_hours": 2.0,
        "effort_level": EffortLevel.LOW.value,
        "impact": 3,
        "needs_renovation": False,
        "success_metric": "Daylit zone (2.5 x head height) reaches >=80% of {room} depth.",
        "steps": ["Raise window head if feasible.", "Use light shelves / reflective ceiling paint."],
        "references": [WELL.citation],
    },
    "visual_weight_imbalance": {
        "title": "Rebalance {room} composition",
        "tier": RoadmapTier.QUICK_WIN.value,
        "effort_hours": 1.5,
        "effort_level": EffortLevel.TRIVIAL.value,
        "impact": 3,
        "needs_renovation": False,
        "success_metric": "Left/right visual weight imbalance in {room} < 20%.",
        "steps": ["Shift the heaviest piece toward the lighter side.", "Add a balancing accent (lamp/art)."],
        "references": [GESTALT.citation],
    },
    "competing_focal_points": {
        "title": "Establish a single focal point in {room}",
        "tier": RoadmapTier.QUICK_WIN.value,
        "effort_hours": 1.0,
        "effort_level": EffortLevel.TRIVIAL.value,
        "impact": 3,
        "needs_renovation": False,
        "success_metric": "{room} has 1-2 declared focal points; others de-emphasized.",
        "steps": ["Pick the anchor piece.", "Lower visual weight of competitors (color/size)."],
        "references": [GESTALT.citation],
    },
    "no_focal_point": {
        "title": "Introduce a focal anchor in {room}",
        "tier": RoadmapTier.QUICK_WIN.value,
        "effort_hours": 1.5,
        "effort_level": EffortLevel.TRIVIAL.value,
        "impact": 3,
        "needs_renovation": False,
        "success_metric": "{room} has at least one >=1m2 anchor piece facing the seat.",
        "steps": ["Add an anchor (art/media wall, statement piece).", "Orient seating toward it."],
        "references": [GESTALT.citation, ALEXANDER.citation],
    },
    "bed_access_clearance": {
        "title": "Restore >=500mm bed access clearance",
        "tier": RoadmapTier.QUICK_WIN.value,
        "effort_hours": 1.0,
        "effort_level": EffortLevel.LOW.value,
        "impact": 4,
        "needs_renovation": False,
        "success_metric": "A 500mm clear strip runs the full length of one bed side.",
        "steps": ["Pull the bed 500mm off the wall.", "Remove blocking nightstand if needed."],
        "references": [NEUFERT.citation],
    },
    "desk_chair_clearance": {
        "title": "Provide >=600mm chair clearance behind the desk",
        "tier": RoadmapTier.QUICK_WIN.value,
        "effort_hours": 0.5,
        "effort_level": EffortLevel.TRIVIAL.value,
        "impact": 4,
        "needs_renovation": False,
        "success_metric": "A 600mm clear zone exists behind the desk for the chair.",
        "steps": ["Move desk 600mm off the wall or remove obstacles behind it."],
        "references": [NEUFERT.citation],
    },
    "living_area_per_person_low": {
        "title": "Increase effective living area per person",
        "tier": RoadmapTier.LONG_TERM.value,
        "effort_hours": 50.0,
        "effort_level": EffortLevel.MAJOR.value,
        "impact": 4,
        "needs_renovation": True,
        "success_metric": "Living area >=14m2 per occupant.",
        "steps": ["Repartition to expand the living zone.", "Re-home a function to an underused room."],
        "alt_title": "Make the living area feel larger per person",
        "alt_steps": ["Use multi-functional furniture.", "Reduce oversized pieces to free perceived area."],
        "alt_success_metric": "Perceived living area per person improves; circulation >=50% of floor.",
        "references": [NEUFERT.citation, ALEXANDER.citation],
    },
    "private_room_at_entrance": {
        "title": "Re-establish the Intimacy Gradient (buffer private rooms)",
        "tier": RoadmapTier.MAJOR_PROJECT.value,
        "effort_hours": 18.0,
        "effort_level": EffortLevel.HIGH.value,
        "impact": 3,
        "needs_renovation": True,
        "success_metric": "No private room opens directly onto the entrance hall.",
        "steps": ["Insert a foyer/screen between entrance and private rooms.", "Reassign the door swing path."],
        "alt_title": "Soft-buffer the private room from the entrance",
        "alt_steps": ["Add a screen/bookshelf as a visual buffer.", "Hang a curtain to separate the entry."],
        "alt_success_metric": "Sightline from entrance to private room is blocked.",
        "references": [ALEXANDER.citation],
    },
    "wet_quiet_zoning_weak": {
        "title": "Separate the wet (kitchen) and quiet (bedroom) zones",
        "tier": RoadmapTier.MAJOR_PROJECT.value,
        "effort_hours": 24.0,
        "effort_level": EffortLevel.HIGH.value,
        "impact": 4,
        "needs_renovation": True,
        "success_metric": "Kitchen and bedroom share no direct boundary; buffer >=1 room.",
        "steps": ["Insert a buffer space (pantry/hall) between zones.", "Upgrade shared wall acoustic rating."],
        "alt_title": "Acoustically buffer the kitchen-bedroom boundary",
        "alt_steps": ["Add a bookshelf mass wall on the shared boundary.", "Use soft closing hardware + rug."],
        "alt_success_metric": "Measured speech transfer kitchen->bedroom drops by >=10dB.",
        "references": [ALEXANDER.citation, WELL.citation],
    },
    "storage_below_target": {
        "title": "Add storage to reach ~1500L/person",
        "tier": RoadmapTier.MAJOR_PROJECT.value,
        "effort_hours": 10.0,
        "effort_level": EffortLevel.MEDIUM.value,
        "impact": 4,
        "needs_renovation": False,
        "success_metric": "Total storage >= 1500L x number of occupants.",
        "steps": ["Add floor-to-ceiling wardrobes.", "Use under-bed and over-door storage."],
        "references": [NEUFERT.citation],
    },
    "soft_surface_ratio_low": {
        "title": "Add soft surfaces to {room} to absorb reflections",
        "tier": RoadmapTier.QUICK_WIN.value,
        "effort_hours": 1.5,
        "effort_level": EffortLevel.LOW.value,
        "impact": 3,
        "needs_renovation": False,
        "success_metric": "{room} soft-surface ratio >=20%; estimated RT60 <=0.6s.",
        "steps": ["Add a rug covering >=20% of floor.", "Introduce upholstered pieces/curtains."],
        "references": [WELL.citation],
    },
    "reverb_high": {
        "title": "Lower reverberation in {room}",
        "tier": RoadmapTier.QUICK_WIN.value,
        "effort_hours": 2.0,
        "effort_level": EffortLevel.LOW.value,
        "impact": 3,
        "needs_renovation": False,
        "success_metric": "{room} estimated RT60 <=0.6s.",
        "steps": ["Add absorptive panels/rug.", "Hang fabric wall art."],
        "references": [WELL.citation],
    },
    "not_command_position": {
        "title": "Move the {room} key piece into command position",
        "tier": RoadmapTier.QUICK_WIN.value,
        "effort_hours": 1.0,
        "effort_level": EffortLevel.TRIVIAL.value,
        "impact": 3,
        "needs_renovation": False,
        "success_metric": "Bed/desk has a solid wall behind and a clear view of the door.",
        "steps": ["Relocate the bed/desk against the far wall facing the door.", "Avoid placing it under a beam."],
        "references": [FENGSHUI.citation],
    },
    "open_floor_ratio_low": {
        "title": "Reduce clutter in {room} for energy and circulation",
        "tier": RoadmapTier.QUICK_WIN.value,
        "effort_hours": 1.5,
        "effort_level": EffortLevel.LOW.value,
        "impact": 3,
        "needs_renovation": False,
        "success_metric": "{room} open-floor ratio >=60%.",
        "steps": ["Edit belongings; store off-season items.", "Conceal clutter in closed storage."],
        "references": [FENGSHUI.citation, ALEXANDER.citation],
    },
}


def _classify(w: Weakness) -> str:
    t = (w.description or "").lower()
    if "area" in t and "below" in t:
        return "area_below_minimum"
    if "door clear width" in t:
        return "door_clear_width_low"
    if "hallway" in t and "width" in t:
        return "hallway_width_low"
    if "work triangle" in t or "work-triangle" in t:
        return "work_triangle_out_of_range"
    if "crowds circulation" in t or "open-floor ratio" in t:
        return "open_floor_ratio_low" if "open-floor" in t else "crowded_circulation"
    if "glazing ratio" in t and "below" in t:
        return "glazing_below_minimum"
    if "cross ventilation" in t and "one wall" in t:
        return "no_cross_ventilation"
    if "operable" in t and "windows" in t:
        return "low_operable_window_ratio"
    if "daylight reach" in t:
        return "daylight_depth_short"
    if "visual weight imbalance" in t:
        return "visual_weight_imbalance"
    if "competing focal" in t:
        return "competing_focal_points"
    if "lacks a clear focal" in t:
        return "no_focal_point"
    if "500mm access clearance" in t:
        return "bed_access_clearance"
    if "600mm chair clearance" in t:
        return "desk_chair_clearance"
    if "living area" in t and "per person" in t:
        return "living_area_per_person_low"
    if "intimacy gradient" in t or "private room" in t:
        return "private_room_at_entrance"
    if "wet" in t and "quiet" in t or "kitchen" in t and "bedroom" in t and "buffer" in t:
        return "wet_quiet_zoning_weak"
    if "storage" in t and "below" in t:
        return "storage_below_target"
    if "soft-surface" in t and ("below" in t or "< 20%" in t or "<20%" in t):
        return "soft_surface_ratio_low"
    if "reverberation" in t and ">" in t:
        return "reverb_high"
    if "command position" in t and "not" in t:
        return "not_command_position"
    return ""


def _room_of(w: Weakness) -> str:
    # Try to extract the room name leading the description.
    desc = w.description or ""
    if desc and desc.split()[0].rstrip(":,").isalpha():
        return desc.split()[0].rstrip(":,")
    return "the space"


def build_roadmap(scorecard: ScoreCard, profile: Profile) -> Roadmap:
    weaknesses = scorecard.ranked_weaknesses()
    items: List[RoadmapItem] = []
    seen_keys = set()
    can_renovate = profile.constraints.renovation_allowed

    for w in weaknesses:
        key = _classify(w)
        if not key:
            continue
        recipe = RECIPES.get(key)
        if not recipe:
            continue
        room = _room_of(w)
        dedupe = (key, room)
        if dedupe in seen_keys:
            continue
        seen_keys.add(dedupe)

        needs_reno = recipe.get("needs_renovation", False)
        if needs_reno and not can_renovate and "alt_title" in recipe:
            args = _fmt_args(recipe)
            title = recipe["alt_title"].format(room=room, **args)
            steps = [s.format(room=room) for s in recipe["alt_steps"]]
            success = recipe["alt_success_metric"].format(room=room)
            tier = RoadmapTier.QUICK_WIN.value
            effort_hours = max(1.0, recipe["effort_hours"] * 0.25)
            effort_level = EffortLevel.LOW.value
            impact = max(2, recipe["impact"] - 1)
        else:
            if needs_reno and not can_renovate:
                # No furniture-only alternative; skip structural item.
                continue
            args = _fmt_args(recipe)
            title = recipe["title"].format(room=room, **args)
            steps = [s.format(room=room) for s in recipe["steps"]]
            success = recipe["success_metric"].format(room=room, **args)
            tier = recipe["tier"]
            effort_hours = recipe["effort_hours"]
            effort_level = recipe["effort_level"]
            impact = recipe["impact"]

        items.append(RoadmapItem(
            title=title,
            tier=tier,
            effort_hours=effort_hours,
            effort_level=effort_level,
            impact=impact,
            impact_description=_impact_text(impact),
            success_metric=success,
            steps=steps,
            references=list(recipe.get("references", [])),
            addresses_dimensions=[w.dimension],
            cost_estimate_usd=_cost_estimate(effort_level, profile),
        ))

    # Sort by tier order then impact desc
    tier_order = {RoadmapTier.QUICK_WIN.value: 0,
                  RoadmapTier.MAJOR_PROJECT.value: 1,
                  RoadmapTier.LONG_TERM.value: 2}
    items.sort(key=lambda i: (tier_order.get(i.tier, 9), -i.impact))
    return Roadmap(items=items)


def _fmt_args(recipe: Dict) -> Dict:
    # supply a default min for area recipes
    return {"min": recipe.get("min", "")}


def _impact_text(impact: int) -> str:
    return {1: "negligible", 2: "minor", 3: "moderate",
            4: "high", 5: "transformative"}.get(impact, "moderate")


def _cost_estimate(level: str, profile: Profile) -> float:
    base = {"trivial": 25.0, "low": 120.0, "medium": 600.0,
            "high": 2500.0, "major": 12000.0}.get(level, 200.0)
    if profile.constraints.budget_usd and base > profile.constraints.budget_usd:
        base = profile.constraints.budget_usd
    return round(base, 2)



