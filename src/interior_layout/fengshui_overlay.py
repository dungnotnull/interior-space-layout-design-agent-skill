"""sub-fengshui-overlay implementation.

Applies Bagua sector mapping and Form School command-position rules. Every
output is explicitly labelled as a traditional/cultural framework distinct from
the human-factors engineering findings (Design Principle 4).
"""
from __future__ import annotations

import math
from typing import List, Optional, Tuple

from .frameworks import FENGSHUI
from .schema import BaguaSector, FengShuiOverlay, Profile, Room


# Classical 8-sector Bagua (BTB/Compass hybrid). Directions are listed clockwise
# from the main facing direction (the "mouth of qi" / entrance).
BAGUA_SECTORS = [
    ("Career", "Career / Life Path", "Water", "N"),
    ("Knowledge", "Knowledge / Self-Cultivation", "Earth", "NE"),
    ("Family", "Family / Health", "Wood", "E"),
    ("Wealth", "Wealth / Abundance", "Wood", "SE"),
    ("Fame", "Fame / Reputation", "Fire", "S"),
    ("Relationships", "Love / Relationships", "Earth", "SW"),
    ("Children", "Children / Creativity", "Metal", "W"),
    ("Helpful People", "Travel / Helpful People", "Metal", "NW"),
    ("Health (Center)", "Health / Unity", "Earth", "CENTER"),
]


def _compass(deg: Optional[float]) -> str:
    if deg is None:
        return "unknown"
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = int((deg % 360 + 22.5) // 45) % 8
    return dirs[idx]


def _sector_present(profile: Profile, direction: str) -> Tuple[bool, str]:
    """A sector is 'present' if a room window/door faces that direction, or if
    the sector direction falls within the plan's orientation spread."""
    dirs_in_plan = set()
    if profile.orientation_deg is not None:
        dirs_in_plan.add(_compass(profile.orientation_deg))
    for r in profile.rooms:
        if r.orientation_deg is not None:
            dirs_in_plan.add(_compass(r.orientation_deg))
        for w in r.windows:
            if w.wall:
                dirs_in_plan.add(str(w.wall).upper())
        for d in r.doors:
            if d.wall:
                dirs_in_plan.add(str(d.wall).upper())
    if direction == "CENTER":
        return (len(profile.rooms) >= 3, "center requires a defined heart space (3+ rooms).")
    return (direction in dirs_in_plan,
            "%s-facing opening detected" % direction if direction in dirs_in_plan
            else "no %s-facing opening detected" % direction)


def _command_position_notes(profile: Profile) -> List[str]:
    notes: List[str] = []
    for r in profile.rooms:
        if r.function not in ("bedroom", "office", "living"):
            continue
        seat = None
        if r.function == "bedroom":
            seat = next((f for f in r.furniture if "bed" in (f.name + f.type).lower()), None)
        elif r.function == "office":
            seat = next((f for f in r.furniture if "desk" in (f.name + f.type).lower()), None)
        if seat is None:
            continue
        if seat.x_m is None:
            notes.append("%s: place the %s in command position - solid wall behind, "
                         "full view of the door, but not directly in line with it."
                         % (r.name, seat.name or seat.type))
            continue
        wall_behind = (seat.x_m < 0.3 or seat.x_m > r.width_m - 0.3 or
                       seat.y_m < 0.3 or seat.y_m > r.length_m - 0.3)
        if wall_behind:
            notes.append("%s: %s has a solid wall behind (good command position foundation)."
                         % (r.name, seat.name or seat.type))
        else:
            notes.append("%s: %s floats away from a wall - move it to command position."
                         % (r.name, seat.name or seat.type))
        # Beam over bed (we approximate: notes field may mention beam)
        if "beam" in r.notes.lower():
            notes.append("%s: a beam crosses over the %s - relocate it to avoid the beam (Form School rule)."
                         % (r.name, seat.name or seat.type))
    return notes


def _remedies(profile: Profile, sectors: List[BaguaSector]) -> List[str]:
    remedies: List[str] = []
    missing = [s for s in sectors if not s.present and s.direction != "CENTER"]
    if missing:
        names = ", ".join(s.name for s in missing[:3])
        remedies.append("Strengthen under-represented sectors (%s) with a symbol, "
                        "plant, light, or colour keyed to the sector's element." % names)
    if any("beam" in r.notes.lower() for r in profile.rooms):
        remedies.append("Soften exposed beams over seating/beds with a fabric canopy or relocate the furniture.")
    if profile.constraints.renter:
        remedies.append("As a renter, apply non-permanent cures: mirrors, plants, rugs, and artwork rather than structural changes.")
    if not profile.constraints.renovation_allowed:
        remedies.append("Renovation is off-limits; use furniture relocation and elemental decor as the primary cures.")
    # Clutter remedy tied to open-floor ratio
    for r in profile.rooms:
        if r.area_m2 <= 0:
            continue
        foot = sum(f.width_m * f.length_m for f in r.furniture)
        if foot / r.area_m2 > 0.5:
            remedies.append("Clear clutter in the %s to restore qi flow; aim for >=60%% open floor." % r.name)
            break
    return remedies


def build_overlay(profile: Profile, enabled: bool) -> FengShuiOverlay:
    facing = _compass(profile.orientation_deg)
    sectors: List[BaguaSector] = []
    for name, aspect, element, direction in BAGUA_SECTORS:
        present, note = _sector_present(profile, direction)
        remedies: List[str] = []
        if not present and direction != "CENTER":
            remedies.append("Add a %s-element cure (%s) to activate the %s sector."
                            % (element.lower(), _element_cure(element), name))
        sectors.append(BaguaSector(
            name=name, life_aspect=aspect, element=element,
            direction=direction, present=present, notes=note, remedies=remedies,
        ))

    notes = _command_position_notes(profile)
    remedies = _remedies(profile, sectors)

    return FengShuiOverlay(
        enabled=enabled,
        label=("TRADITIONAL/CULTURAL FRAMEWORK - Feng Shui Form School & Bagua "
               "mapping. This overlay is cultural guidance, NOT engineering or "
               "building-science fact. Treat remedies as optional tradition."),
        facing_direction=facing,
        bagua_sectors=sectors,
        command_position_notes=notes,
        remedies=remedies,
        sources=[FENGSHUI.citation],
    )


def _element_cure(element: str) -> str:
    return {
        "Water": "mirror, fountain, or dark wavy shapes",
        "Earth": "ceramics, crystals, or earthen tones",
        "Wood": "live plants or vertical green stripes",
        "Fire": "candles, red accents, or bright lighting",
        "Metal": "metal objects, round forms, or white/metallic tones",
    }.get(element, "an elemental object")
