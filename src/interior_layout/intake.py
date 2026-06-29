"""sub-profile-intake implementation.

Turns a free-form / semi-structured user request into a normalized
:class:`Profile`. Mandatory fields are validated; anything missing is flagged
as an explicit ``unknown`` rather than silently assumed (Design Principle 2).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .schema import (
    Constraints,
    Door,
    Furniture,
    Occupant,
    Profile,
    Room,
    RoomFunction,
    WallOrientation,
    Window,
)


MANDATORY_PROFILE_FIELDS: Tuple[str, ...] = (
    "rooms", "occupants", "goals",
)
MANDATORY_ROOM_FIELDS: Tuple[str, ...] = (
    "name", "function", "width_m", "length_m",
)

VALID_FUNCTIONS = {f.value for f in RoomFunction}
VALID_WALLS = {w.value for w in WallOrientation}


class IntakeError(ValueError):
    """Raised when mandatory data cannot be recovered and the caller has not
    opted into a degraded run. Carries the list of missing fields."""


def _num(value: Any, default: Optional[float] = None) -> Optional[float]:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _norm_wall(wall: Any) -> str:
    if not wall:
        return ""
    s = str(wall).strip().upper()
    if s in VALID_WALLS:
        return s
    # numeric degrees -> nearest 8-point compass
    deg = _num(wall)
    if deg is not None:
        return _deg_to_compass(deg)
    return str(wall).strip()


def _deg_to_compass(deg: float) -> str:
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = int((deg % 360 + 22.5) // 45) % 8
    return dirs[idx]


def _build_window(raw: Dict[str, Any]) -> Window:
    return Window(
        wall=_norm_wall(raw.get("wall", "")),
        width_m=float(raw.get("width_m", 0.0) or 0.0),
        sill_height_m=float(raw.get("sill_height_m", 1.0) or 1.0),
        head_height_m=float(raw.get("head_height_m", 2.1) or 2.1),
        operable=bool(raw.get("operable", True)),
    )


def _build_door(raw: Dict[str, Any]) -> Door:
    return Door(
        wall=_norm_wall(raw.get("wall", "")),
        width_m=float(raw.get("width_m", 0.0) or 0.0),
        swing=str(raw.get("swing", "in") or "in"),
        to_room=str(raw.get("to_room", "") or ""),
        clear_width_m=_num(raw.get("clear_width_m")),
    )


def _build_furniture(raw: Dict[str, Any]) -> Furniture:
    return Furniture(
        name=str(raw.get("name", "") or ""),
        type=str(raw.get("type", "") or ""),
        width_m=float(raw.get("width_m", 0.0) or 0.0),
        length_m=float(raw.get("length_m", 0.0) or 0.0),
        x_m=_num(raw.get("x_m")),
        y_m=_num(raw.get("y_m")),
        fixed=bool(raw.get("fixed", False)),
        storage_liters=float(raw.get("storage_liters", 0.0) or 0.0),
    )


def _build_room(raw: Dict[str, Any], unknowns: List[str]) -> Room:
    for f in MANDATORY_ROOM_FIELDS:
        if raw.get(f) in (None, "", []):
            unknowns.append("room.%s" % f)
    func = str(raw.get("function", "other") or "other").lower()
    if func not in VALID_FUNCTIONS:
        unknowns.append("room.function.invalid:%s" % func)
        func = RoomFunction.OTHER.value
    width = _num(raw.get("width_m"))
    length = _num(raw.get("length_m"))
    if width is None or width <= 0:
        unknowns.append("room.%s.width_m" % raw.get("name", "?"))
        width = 0.0
    if length is None or length <= 0:
        unknowns.append("room.%s.length_m" % raw.get("name", "?"))
        length = 0.0
    return Room(
        name=str(raw.get("name", "") or ""),
        function=func,
        width_m=width,
        length_m=length,
        height_m=float(raw.get("height_m", 2.7) or 2.7),
        windows=[_build_window(w) for w in raw.get("windows", []) or []],
        doors=[_build_door(d) for d in raw.get("doors", []) or []],
        furniture=[_build_furniture(f) for f in raw.get("furniture", []) or []],
        adjacent=list(raw.get("adjacent", []) or []),
        orientation_deg=_num(raw.get("orientation_deg")),
        notes=str(raw.get("notes", "") or ""),
    )


def _build_occupant(raw: Dict[str, Any]) -> Occupant:
    return Occupant(
        role=str(raw.get("role", "adult") or "adult"),
        age=int(raw.get("age")) if raw.get("age") not in (None, "") else None,
        height_cm=_num(raw.get("height_cm")),
        needs=list(raw.get("needs", []) or []),
    )


def _build_constraints(raw: Dict[str, Any]) -> Constraints:
    return Constraints(
        renovation_allowed=bool(raw.get("renovation_allowed", True)),
        renter=bool(raw.get("renter", False)),
        budget_usd=_num(raw.get("budget_usd")),
        fixed_elements=list(raw.get("fixed_elements", []) or []),
        timeline=str(raw.get("timeline", "") or ""),
    )


def build_profile(data: Dict[str, Any], strict: bool = False) -> Profile:
    """Build a normalized :class:`Profile` from a raw dict.

    Missing mandatory fields are recorded in ``profile.unknowns``. If ``strict``
    is True and any mandatory field is missing, :class:`IntakeError` is raised
    so the harness can ask clarifying questions instead of fabricating a score.
    """
    unknowns: List[str] = []

    for f in MANDATORY_PROFILE_FIELDS:
        if not data.get(f):
            unknowns.append("profile.%s" % f)

    rooms_raw = data.get("rooms", []) or []
    if not rooms_raw:
        unknowns.append("profile.rooms")
    rooms = [_build_room(r, unknowns) for r in rooms_raw]

    occupants = [_build_occupant(o) for o in data.get("occupants", []) or []]
    if not occupants:
        unknowns.append("profile.occupants")

    goals = list(data.get("goals", []) or [])
    if not goals:
        unknowns.append("profile.goals")

    constraints = _build_constraints(data.get("constraints", {}) or {})
    if constraints.renter:
        # renters cannot move structural walls; reflect that automatically.
        constraints.renovation_allowed = False
        if "walls" not in str(constraints.fixed_elements).lower():
            constraints.fixed_elements.append("load-bearing walls")

    orientation_deg = _num(data.get("orientation_deg"))
    if orientation_deg is None and data.get("orientation"):
        orientation_deg = _num(data.get("orientation"))

    profile = Profile(
        project_id=str(data.get("project_id", _autoid(data)) or _autoid(data)),
        rooms=rooms,
        occupants=occupants,
        goals=goals,
        constraints=constraints,
        location=str(data.get("location", "") or ""),
        orientation_deg=orientation_deg,
        entrance_description=str(data.get("entrance_description", "") or ""),
        raw_description=str(data.get("raw_description", "") or ""),
        artifacts=list(data.get("artifacts", []) or []),
        unknowns=unknowns,
        metadata=dict(data.get("metadata", {}) or {}),
    )

    if strict and unknowns:
        raise IntakeError(
            "Missing mandatory fields: %s" % ", ".join(unknowns), unknowns
        )
    return profile


def _autoid(data: Dict[str, Any]) -> str:
    import hashlib
    payload = repr(sorted(data.items())).encode("utf-8", "ignore")
    return "proj_" + hashlib.sha1(payload).hexdigest()[:10]


def mandatory_fields_missing(profile: Profile) -> List[str]:
    """Return the list of mandatory fields still unknown after intake."""
    missing: List[str] = []
    if not profile.rooms:
        missing.append("rooms")
    if not profile.occupants:
        missing.append("occupants")
    if not profile.goals:
        missing.append("goals")
    for r in profile.rooms:
        if r.width_m <= 0 or r.length_m <= 0:
            missing.append("room.%s.dimensions" % r.name)
    return missing


def clarifying_questions(profile: Profile) -> List[str]:
    """Generate targeted questions for fields the user has not supplied."""
    qs: List[str] = []
    if not profile.rooms:
        qs.append("What rooms/spaces are in the layout, with width x length in meters?")
    if not profile.occupants:
        qs.append("Who uses the space (occupants, ages, mobility needs)?")
    if not profile.goals:
        qs.append("What is your main goal (e.g. better flow, more light, feng shui harmony)?")
    for r in profile.rooms:
        if r.width_m <= 0 or r.length_m <= 0:
            qs.append("What are the dimensions (m) of the %s?" % r.name or "room")
        if not r.windows:
            qs.append("Where are the windows in the %s (wall + width)?" % r.name)
    if profile.orientation_deg is None:
        qs.append("Which compass direction does the main entrance/primary window face?")
    if not profile.constraints.renovation_allowed and not profile.constraints.fixed_elements:
        qs.append("Which elements are fixed and cannot be changed (rental constraints)?")
    return qs
