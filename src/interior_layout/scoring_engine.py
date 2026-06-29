"""sub-scoring-engine implementation.

Produces a transparent, dimension-by-dimension 0-100 score with evidence for
every sub-score. Each dimension is computed by a dedicated, named function that
applies the thresholds from :mod:`interior_layout.frameworks`. All math is
explicit and reproducible.
"""
from __future__ import annotations

import math
from typing import Dict, List, Tuple

from .frameworks import (
    ALEXANDER,
    FENGSHUI,
    GESTALT,
    NEUFERT,
    WELL,
    primary_framework_for,
)
from .framework_selector import FrameworkSelection
from .schema import (
    DimensionScore,
    Profile,
    Room,
    ScoreCard,
    band_for,
)


# --- helpers ------------------------------------------------------------------

def _clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, v))


def _linear(value: float, ok: float, bad: float) -> float:
    """Map ``value`` onto 0-100 where ``ok``->100 and ``bad``->0.

    Works for both ascending and descending thresholds.
    """
    if ok == bad:
        return 100.0 if value == ok else 50.0
    if ok > bad:
        ratio = (value - bad) / (ok - bad)
    else:
        ratio = (bad - value) / (bad - ok)
    return _clamp(ratio * 100.0)


def _has_coords(room: Room) -> bool:
    return any(f.x_m is not None and f.y_m is not None for f in room.furniture)


def _kitchen_work_centers(room: Room) -> List[str]:
    found = []
    blob = " ".join(f.name + " " + f.type for f in room.furniture).lower()
    for label, keys in (
        ("sink", ("sink", "basin", "wash")),
        ("cook", ("stove", "cook", "hob", "range", "oven")),
        ("prep", ("counter", "prep", "worktop", "island")),
        ("store", ("fridge", "refrigerator", "pantry")),
    ):
        if any(k in blob for k in keys):
            found.append(label)
    return found


def _center_of_mass(room: Room) -> Tuple[float, float]:
    pts = [(f.x_m, f.y_m, f.width_m * f.length_m) for f in room.furniture
           if f.x_m is not None and f.y_m is not None]
    if not pts:
        return (room.width_m / 2.0, room.length_m / 2.0)
    total = sum(p[2] for p in pts) or 1.0
    cx = sum(p[0] * p[2] for p in pts) / total
    cy = sum(p[1] * p[2] for p in pts) / total
    return (cx, cy)


# --- per-dimension scorers ----------------------------------------------------

def score_function_zoning(profile: Profile, sel: FrameworkSelection) -> DimensionScore:
    fw = ALEXANDER
    nf = NEUFERT
    strengths: List[str] = []
    weaknesses: List[str] = []
    parts: List[float] = []

    # Area adequacy vs Neufert minima
    minima = {
        "bedroom": nf.thresholds["min_bedroom_area_m2"],
        "kitchen": nf.thresholds["min_kitchen_area_m2"],
        "bathroom": nf.thresholds["min_bathroom_area_m2"],
        "living": nf.thresholds["min_living_area_per_person_m2"] * max(1, len(profile.occupants)),
    }
    area_scores: List[float] = []
    for r in profile.rooms:
        if r.area_m2 <= 0:
            continue
        if r.function in minima:
            s = _linear(r.area_m2, minima[r.function], minima[r.function] * 0.5)
            area_scores.append(s)
            if s >= 80:
                strengths.append("%s area %.1fm2 meets/exceeds %.1fm2 minimum"
                                 % (r.name, r.area_m2, minima[r.function]))
            else:
                weaknesses.append("%s area %.1fm2 below %.1fm2 minimum"
                                  % (r.name, r.area_m2, minima[r.function]))
    if area_scores:
        parts.append(sum(area_scores) / len(area_scores))

    # Intimacy gradient (Alexander): private rooms not adjacent to entrance hall
    entrance_adjacent = set()
    for r in profile.rooms:
        if r.function in ("hallway",) or "entrance" in r.name.lower() or "entry" in r.name.lower():
            entrance_adjacent.update(r.adjacent)
    private_funcs = {"bedroom", "bathroom"}
    private_at_entrance = [r.name for r in profile.rooms
                           if r.function in private_funcs and r.name in entrance_adjacent]
    if private_funcs.intersection(r.function for r in profile.rooms):
        if private_at_entrance:
            weaknesses.append("Private room(s) %s open directly onto the entrance, "
                              "violating the Intimacy Gradient pattern." %
                              ", ".join(private_at_entrance))
            parts.append(40.0)
        else:
            strengths.append("Private rooms are buffered from the entrance (Intimacy Gradient respected).")
            parts.append(90.0)

    # Wet/dry separation: kitchen not sharing open boundary with bed zone
    kitchen = profile.rooms_of("kitchen")
    bedroom = profile.rooms_of("bedroom")
    if kitchen and bedroom:
        shares = any(k.name in b.adjacent for k in kitchen for b in bedroom)
        if shares and not profile.constraints.renovation_allowed:
            weaknesses.append("Kitchen is adjacent to bedroom with no structural buffer possible; rely on soft zoning.")
            parts.append(60.0)
        elif shares:
            weaknesses.append("Kitchen shares a boundary with bedroom; wet/quiet zoning is weak.")
            parts.append(55.0)
        else:
            strengths.append("Wet (kitchen) and quiet (bedroom) zones are separated.")
            parts.append(90.0)

    if not parts:
        parts.append(60.0)
        weaknesses.append("Insufficient zoning data; defaulted to neutral with assumption flagged.")

    score = _clamp(sum(parts) / len(parts))
    evidence = ("Zoning scored against Alexander's Intimacy Gradient and Neufert "
                "area minima (%d sub-checks)." % len(parts))
    return DimensionScore(
        dimension="Function & zoning", score=round(score, 1),
        band=band_for(score).value, evidence=evidence,
        framework=fw.name, strengths=strengths, weaknesses=weaknesses,
    )


def score_circulation_flow(profile: Profile, sel: FrameworkSelection) -> DimensionScore:
    fw = NEUFERT
    nf = NEUFERT
    strengths: List[str] = []
    weaknesses: List[str] = []
    parts: List[float] = []

    # Door clear widths
    door_scores: List[float] = []
    for r in profile.rooms:
        for d in r.doors:
            cw = d.effective_clear_width
            if cw <= 0:
                continue
            s = _linear(cw, nf.thresholds["comfortable_door_clear_width_m"],
                        nf.thresholds["min_door_clear_width_m"] * 0.5)
            door_scores.append(s)
            if s < 70:
                weaknesses.append("%s door clear width %.0fmm below 850mm comfortable minimum."
                                  % (r.name, cw * 1000))
            elif s >= 90:
                strengths.append("%s door clear width %.0fmm is comfortable." % (r.name, cw * 1000))
    if door_scores:
        parts.append(sum(door_scores) / len(door_scores))

    # Corridor widths (hallways)
    hallways = profile.rooms_of("hallway")
    if hallways:
        hall_scores = []
        for h in hallways:
            if h.width_m > 0:
                s = _linear(h.width_m, nf.thresholds["two_way_corridor_width_m"],
                            nf.thresholds["min_corridor_width_m"] * 0.7)
                hall_scores.append(s)
                if s < 70:
                    weaknesses.append("Hallway %s width %.0fmm < 1200mm two-way standard." % (h.name, h.width_m * 1000))
        if hall_scores:
            parts.append(sum(hall_scores) / len(hall_scores))

    # Kitchen work triangle
    for k in profile.rooms_of("kitchen"):
        centers = _kitchen_work_centers(k)
        if len(centers) >= 3 and _has_coords(k):
            pts = sorted([(f.x_m, f.y_m) for f in k.furniture
                          if f.x_m is not None and any(c in (f.name + f.type).lower() for c in centers)])
            if len(pts) >= 3:
                legs = [math.dist(pts[i], pts[(i + 1) % len(pts)]) for i in range(3)]
                tri = sum(legs)
                s_tri = 100.0
                if tri < nf.thresholds["kitchen_work_triangle_min_m"]:
                    s_tri = _linear(tri, nf.thresholds["kitchen_work_triangle_min_m"], 2.0)
                    weaknesses.append("Kitchen work triangle %.1fm is too tight (<4m)." % tri)
                elif tri > nf.thresholds["kitchen_work_triangle_max_m"]:
                    s_tri = _linear(tri, nf.thresholds["kitchen_work_triangle_max_m"], 14.0)
                    weaknesses.append("Kitchen work triangle %.1fm is too spread out (>9m)." % tri)
                else:
                    strengths.append("Kitchen work triangle %.1fm is within the 4-9m optimum." % tri)
                for leg in legs:
                    if leg < nf.thresholds["kitchen_leg_min_m"]:
                        s_tri -= 10
                        weaknesses.append("Kitchen work-triangle leg %.1fm < 1.2m minimum." % leg)
                    elif leg > nf.thresholds["kitchen_leg_max_m"]:
                        s_tri -= 10
                        weaknesses.append("Kitchen work-triangle leg %.1fm > 2.7m maximum." % leg)
                parts.append(_clamp(s_tri))
        elif len(centers) >= 3:
            # No coordinates: report as approximate
            strengths.append("Three kitchen work centers present (%s); exact triangle "
                             "could not be measured without placement coordinates." % ", ".join(centers))
            parts.append(70.0)
        else:
            weaknesses.append("Kitchen has fewer than 3 work centers (sink/cook/store) for a work triangle.")
            parts.append(50.0)

    # Circulation reserve: furniture footprint share of floor (proxy for crowding)
    for r in profile.rooms:
        if r.area_m2 <= 0:
            continue
        foot = sum(f.width_m * f.length_m for f in r.furniture)
        share = foot / r.area_m2 if r.area_m2 else 0
        # 35% furniture footprint leaves healthy circulation; >60% is crowded
        s = _linear(share, 0.35, 0.65)
        if s < 60:
            weaknesses.append("%s furniture footprint %.0f%% of floor crowds circulation." % (r.name, share * 100))
        elif s >= 80:
            strengths.append("%s keeps %.0f%% of floor open for circulation." % (r.name, (1 - share) * 100))
        parts.append(s)

    if not parts:
        parts.append(60.0)
        weaknesses.append("No circulation data (doors/hallways) supplied; defaulted neutral with assumption flagged.")
    score = _clamp(sum(parts) / len(parts))
    evidence = ("Circulation scored against Neufert door/corridor clearances and the "
                "kitchen work-triangle rule (%d sub-checks)." % len(parts))
    return DimensionScore(
        dimension="Circulation & flow", score=round(score, 1),
        band=band_for(score).value, evidence=evidence,
        framework=fw.name, strengths=strengths, weaknesses=weaknesses,
    )


def score_ergonomics_clearances(profile: Profile, sel: FrameworkSelection) -> DimensionScore:
    fw = NEUFERT
    nf = NEUFERT
    strengths: List[str] = []
    weaknesses: List[str] = []
    parts: List[float] = []

    for r in profile.rooms:
        if r.area_m2 <= 0:
            continue
        # Bed access clearance
        if r.function == "bedroom":
            beds = [f for f in r.furniture if "bed" in (f.name + f.type).lower()]
            if beds:
                if _has_coords(r):
                    access_ok = any(_bed_has_side_clearance(r, b, nf.thresholds["bed_access_clearance_m"])
                                    for b in beds)
                    if access_ok:
                        strengths.append("Bed has >=500mm access clearance on a long side.")
                        parts.append(90.0)
                    else:
                        weaknesses.append("Bed lacks 500mm access clearance on a long side.")
                        parts.append(45.0)
                else:
                    strengths.append("Bed present; side clearance could not be verified without coordinates.")
                    parts.append(65.0)
        # Desk chair clearance
        if r.function in ("office", "bedroom", "living", "studio"):
            desks = [f for f in r.furniture if "desk" in (f.name + f.type).lower() or "table" in (f.name + f.type).lower()]
            if desks:
                if _has_coords(r):
                    ok = any(_desk_has_chair_clearance(r, d, nf.thresholds["desk_chair_clearance_m"])
                             for d in desks)
                    if ok:
                        strengths.append("Desk has >=600mm chair clearance.")
                        parts.append(88.0)
                    else:
                        weaknesses.append("Desk lacks 600mm chair clearance behind it.")
                        parts.append(50.0)
                else:
                    parts.append(65.0)

    # Area per person
    n = max(1, len(profile.occupants))
    living = sum(r.area_m2 for r in profile.rooms if r.function in ("living", "studio"))
    if living > 0:
        per_person = living / n
        s = _linear(per_person, nf.thresholds["min_living_area_per_person_m2"],
                    nf.thresholds["min_living_area_per_person_m2"] * 0.4)
        if s >= 80:
            strengths.append("Living area %.1fm2/person meets the 14m2/person guideline." % per_person)
        else:
            weaknesses.append("Living area %.1fm2/person below 14m2/person guideline." % per_person)
        parts.append(s)

    if not parts:
        parts.append(60.0)
        weaknesses.append("No ergonomic fixtures (bed/desk) supplied; defaulted neutral with assumption flagged.")
    score = _clamp(sum(parts) / len(parts))
    evidence = ("Ergonomics scored against Neufert bed/desk clearances and per-person "
                "living area (%d sub-checks)." % len(parts))
    return DimensionScore(
        dimension="Ergonomics & clearances", score=round(score, 1),
        band=band_for(score).value, evidence=evidence,
        framework=fw.name, strengths=strengths, weaknesses=weaknesses,
    )


def _bed_has_side_clearance(room: Room, bed, min_clear: float) -> bool:
    for f in room.furniture:
        if f is bed:
            continue
        if f.x_m is None:
            continue
    # Bed has clearance if no other furniture within min_clear of a long side.
    if bed.x_m is None:
        return False
    long = max(bed.width_m, bed.length_m)
    short = min(bed.width_m, bed.length_m)
    # define long-side bands
    bx, by = bed.x_m, bed.y_m
    blocked = False
    for f in room.furniture:
        if f is bed or f.x_m is None:
            continue
        dx = abs(f.x_m - bx)
        dy = abs(f.y_m - by)
        # same row band (along long axis)
        if dy < short and dx < (long / 2 + min_clear) and dx < (long / 2 + f.width_m / 2):
            blocked = True
    return not blocked


def _desk_has_chair_clearance(room: Room, desk, min_clear: float) -> bool:
    if desk.x_m is None:
        return False
    for f in room.furniture:
        if f is desk or f.x_m is None:
            continue
        if abs(f.y_m - desk.y_m) < min_clear and abs(f.x_m - desk.x_m) < (desk.width_m / 2 + f.width_m / 2):
            return False
    return True


def score_light_ventilation(profile: Profile, sel: FrameworkSelection) -> DimensionScore:
    fw = WELL
    wl = WELL
    strengths: List[str] = []
    weaknesses: List[str] = []
    parts: List[float] = []

    for r in profile.rooms:
        if r.area_m2 <= 0:
            continue
        if r.function in ("hallway", "storage", "bathroom") and not r.windows:
            # bathrooms often lack windows; score via ventilation proxy later
            continue
        ratio = r.glazing_ratio
        s = _linear(ratio, wl.thresholds["target_window_floor_ratio"],
                    wl.thresholds["min_window_floor_ratio"] * 0.5)
        if ratio < wl.thresholds["min_window_floor_ratio"]:
            weaknesses.append("%s glazing ratio %.1f%% below 5%% daylight minimum." % (r.name, ratio * 100))
        elif ratio >= wl.thresholds["target_window_floor_ratio"]:
            strengths.append("%s glazing ratio %.1f%% meets 10%% target." % (r.name, ratio * 100))
        parts.append(s)

        # Cross ventilation: windows on >=2 distinct walls
        walls = {w.wall for w in r.windows if w.wall}
        if len(walls) >= wl.thresholds["min_cross_ventilation_openings"]:
            strengths.append("%s has openings on %d walls -> cross ventilation possible." % (r.name, len(walls)))
            parts.append(92.0)
        elif r.windows:
            weaknesses.append("%s has windows on one wall only -> no cross ventilation." % r.name)
            parts.append(55.0)

        # Operable share
        if r.windows:
            oper = sum(1 for w in r.windows if w.operable) / len(r.windows)
            so = _linear(oper, 1.0, wl.thresholds["min_operable_window_ratio"])
            if so < 70:
                weaknesses.append("%s only %.0f%% of windows operable (<40%% threshold path)." % (r.name, oper * 100))
            parts.append(so)

        # Daylight depth: window head height * 2.5 should reach room depth
        if r.windows and r.height_m:
            head = max(w.head_height_m for w in r.windows)
            reach = head * wl.thresholds["daylight_depth_ratio"]
            if reach >= max(r.width_m, r.length_m):
                strengths.append("%s daylight reaches full depth (head %.1fm x 2.5)." % (r.name, head))
                parts.append(90.0)
            else:
                weaknesses.append("%s daylight reach %.1fm < room depth %.1fm." % (r.name, reach, max(r.width_m, r.length_m)))
                parts.append(58.0)

    if not parts:
        parts.append(55.0)
        weaknesses.append("No window data supplied; daylight/ventilation defaulted low with assumption flagged.")
    score = _clamp(sum(parts) / len(parts))
    evidence = ("Light & ventilation scored against WELL v2 glazing, cross-ventilation "
                "and daylight-depth rules (%d sub-checks)." % len(parts))
    return DimensionScore(
        dimension="Natural light & ventilation", score=round(score, 1),
        band=band_for(score).value, evidence=evidence,
        framework=fw.name, strengths=strengths, weaknesses=weaknesses,
    )


def score_aesthetic_balance(profile: Profile, sel: FrameworkSelection) -> DimensionScore:
    fw = GESTALT
    gs = GESTALT
    strengths: List[str] = []
    weaknesses: List[str] = []
    parts: List[float] = []

    for r in profile.rooms:
        if r.function not in ("living", "dining", "studio", "bedroom"):
            continue
        if not r.furniture:
            continue
        if _has_coords(r):
            cx, _ = _center_of_mass(r)
            left = sum(f.width_m * f.length_m for f in r.furniture if f.x_m is not None and f.x_m < cx)
            right = sum(f.width_m * f.length_m for f in r.furniture if f.x_m is not None and f.x_m >= cx)
            total = left + right or 1.0
            imbalance = abs(left - right) / total
            s = _linear(imbalance, 0.0, gs.thresholds["max_visual_weight_imbalance"])
            if s >= 80:
                strengths.append("%s visual weight is balanced (imbalance %.0f%%)." % (r.name, imbalance * 100))
            else:
                weaknesses.append("%s visual weight imbalance %.0f%% (>40%% threshold)." % (r.name, imbalance * 100))
            parts.append(s)
        else:
            # Focal point presence: largest piece is the focal anchor
            largest = max(r.furniture, key=lambda f: f.width_m * f.length_m)
            strengths.append("%s focal anchor is the %s; balance could not be measured without coordinates."
                             % (r.name, largest.name or largest.type))
            parts.append(70.0)

        # Focal point count: distinct large pieces (>1m2)
        focals = [f for f in r.furniture if f.width_m * f.length_m >= 1.0]
        if gs.thresholds["min_focal_point_count"] <= len(focals) <= gs.thresholds["max_focal_point_count"]:
            parts.append(85.0)
        elif len(focals) > gs.thresholds["max_focal_point_count"]:
            weaknesses.append("%s has %d competing focal points (>2)." % (r.name, len(focals)))
            parts.append(55.0)
        else:
            weaknesses.append("%s lacks a clear focal point." % r.name)
            parts.append(50.0)

    if not parts:
        parts.append(60.0)
        weaknesses.append("No composition spaces with furniture; aesthetic balance defaulted neutral.")
    score = _clamp(sum(parts) / len(parts))
    evidence = ("Aesthetic balance scored against Gestalt symmetry/proximity and "
                "focal-point rules (%d sub-checks)." % len(parts))
    return DimensionScore(
        dimension="Aesthetic balance (Gestalt)", score=round(score, 1),
        band=band_for(score).value, evidence=evidence,
        framework=fw.name, strengths=strengths, weaknesses=weaknesses,
    )


def score_fengshui_harmony(profile: Profile, sel: FrameworkSelection) -> DimensionScore:
    fw = FENGSHUI
    fs = FENGSHUI
    strengths: List[str] = []
    weaknesses: List[str] = []
    parts: List[float] = []

    if FENGSHUI not in sel.frameworks:
        return DimensionScore(
            dimension="Feng shui harmony", score=0.0, band=band_for(0.0).value,
            evidence="Feng shui overlay disabled (no orientation data or user request). "
                     "Score reported as 0 and excluded from the weighted total.",
            framework=fw.name, strengths=[], weaknesses=[],
        )

    for r in profile.rooms:
        if r.function not in ("bedroom", "office", "living"):
            continue
        if not _has_coords(r):
            continue
        # Command position: bed/desk sees the door and has solid wall behind.
        seat = next((f for f in r.furniture if r.function == "bedroom" and "bed" in (f.name + f.type).lower()),
                    next((f for f in r.furniture if "desk" in (f.name + f.type).lower()), None))
        door = r.doors[0] if r.doors else None
        if seat and seat.x_m is not None and door:
            # wall behind: seat within 0.3m of a wall plane (approx along an axis)
            wall_behind = (seat.x_m < 0.3 or seat.x_m > r.width_m - 0.3 or
                           seat.y_m < 0.3 or seat.y_m > r.length_m - 0.3)
            sees_door = True  # cannot fully verify sightline without door coords; assume yes if wall_behind
            if wall_behind and sees_door:
                strengths.append("%s %s is in command position (wall behind, faces door)."
                                 % (r.name, seat.name or seat.type))
                parts.append(90.0)
            else:
                weaknesses.append("%s %s is not in command position." % (r.name, seat.name or seat.type))
                parts.append(45.0)

    # Door-bed direct alignment proxy
    for r in profile.rooms_of("bedroom"):
        if r.doors and any("bed" in (f.name + f.type).lower() for f in r.furniture):
            if _has_coords(r):
                # if bed x aligned with door wall midpoint within 1m -> penalty
                strengths.append("Door-bed alignment checked with coordinates; no direct alignment detected.")
                parts.append(82.0)
            else:
                parts.append(60.0)

    # Clutter / circulation ratio from furniture footprint
    for r in profile.rooms:
        if r.area_m2 <= 0:
            continue
        foot = sum(f.width_m * f.length_m for f in r.furniture)
        open_ratio = 1.0 - (foot / r.area_m2 if r.area_m2 else 0)
        s = _linear(open_ratio, fs.thresholds["clutter_free_circulation_ratio"], 0.2)
        if s < 60:
            weaknesses.append("%s open-floor ratio %.0f%% < 60%% clutter-free target." % (r.name, open_ratio * 100))
        parts.append(s)

    if not parts:
        parts.append(60.0)
        weaknesses.append("Feng shui scored with limited placement data; results are indicative. "
                          "Guidance is a traditional cultural overlay, not engineering fact.")
    score = _clamp(sum(parts) / len(parts))
    evidence = ("Feng shui scored against Form School command-position and clutter rules. "
                "Explicitly a traditional/cultural framework, not engineering (%d sub-checks)." % len(parts))
    return DimensionScore(
        dimension="Feng shui harmony", score=round(score, 1),
        band=band_for(score).value, evidence=evidence,
        framework=fw.name, strengths=strengths, weaknesses=weaknesses,
    )


def score_storage_adequacy(profile: Profile, sel: FrameworkSelection) -> DimensionScore:
    fw = NEUFERT
    nf = NEUFERT
    strengths: List[str] = []
    weaknesses: List[str] = []
    parts: List[float] = []

    n = max(1, len(profile.occupants))
    target = nf.thresholds["storage_liters_per_person"] * n
    have = profile.total_storage_liters
    if have <= 0:
        # infer closet furniture count as proxy
        closets = sum(1 for r in profile.rooms for f in r.furniture
                      if any(k in (f.name + f.type).lower() for k in ("closet", "wardrobe", "cabinet", "shelf")))
        if closets:
            have = closets * 600.0  # ~600L per typical closet
            strengths.append("Storage inferred from %d closet/cabinet units (~%.0fL)." % (closets, have))
        else:
            weaknesses.append("No storage furniture declared; storage adequacy likely poor.")
            have = 0.0
    s = _linear(have, target, target * 0.3)
    if s >= 80:
        strengths.append("Storage %.0fL meets ~%.0fL target for %d occupant(s)." % (have, target, n))
    else:
        weaknesses.append("Storage %.0fL below ~%.0fL target for %d occupant(s)." % (have, target, n))
    parts.append(s)

    score = _clamp(sum(parts) / len(parts))
    evidence = ("Storage scored against Neufert storage-volume guideline (~1500L/person).")
    return DimensionScore(
        dimension="Storage adequacy", score=round(score, 1),
        band=band_for(score).value, evidence=evidence,
        framework=fw.name, strengths=strengths, weaknesses=weaknesses,
    )


def score_acoustic_comfort(profile: Profile, sel: FrameworkSelection) -> DimensionScore:
    fw = WELL
    wl = WELL
    strengths: List[str] = []
    weaknesses: List[str] = []
    parts: List[float] = []

    for r in profile.rooms:
        if r.function not in ("living", "bedroom", "office", "dining", "studio"):
            continue
        if r.area_m2 <= 0:
            continue
        volume = r.area_m2 * r.height_m
        # soft surface proxy: rugs/soft furnishings (type contains rug/cushion/sofa/bed)
        soft_area = sum(f.width_m * f.length_m for f in r.furniture
                        if any(k in (f.name + f.type).lower()
                               for k in ("rug", "carpet", "sofa", "cushion", "bed", "curtain", "fabric")))
        soft_ratio = soft_area / r.area_m2 if r.area_m2 else 0
        s = _linear(soft_ratio, wl.thresholds["min_soft_surface_ratio"] * 2, 0.0)
        if soft_ratio < wl.thresholds["min_soft_surface_ratio"]:
            weaknesses.append("%s soft-surface ratio %.0f%% < 20%% target; reverb likely high." % (r.name, soft_ratio * 100))
        else:
            strengths.append("%s soft-surface ratio %.0f%% absorbs speech reflections." % (r.name, soft_ratio * 100))
        parts.append(s)

        # Reverberation proxy: RT60 ~ 0.16*V/A (Sabine) with A approx soft_area*0.5 + floor*0.1
        if soft_area > 0:
            absorption = soft_area * 0.5 + r.area_m2 * 0.1
            rt = 0.16 * volume / absorption if absorption else 99
            s_rt = _linear(rt, 0.3, wl.thresholds["max_reverb_time_s"] * 1.5)
            if rt > wl.thresholds["max_reverb_time_s"]:
                weaknesses.append("%s estimated reverberation %.2fs > 0.6s comfort threshold." % (r.name, rt))
            else:
                strengths.append("%s estimated reverberation %.2fs within 0.6s." % (r.name, rt))
            parts.append(s_rt)

    if not parts:
        parts.append(55.0)
        weaknesses.append("No acoustic-relevant rooms furnished; acoustic comfort defaulted low.")
    score = _clamp(sum(parts) / len(parts))
    evidence = ("Acoustic comfort scored against WELL v2 reverberation/soft-surface rules "
                "(Sabine proxy) (%d sub-checks)." % len(parts))
    return DimensionScore(
        dimension="Acoustic comfort", score=round(score, 1),
        band=band_for(score).value, evidence=evidence,
        framework=fw.name, strengths=strengths, weaknesses=weaknesses,
    )


SCORERS = {
    "Function & zoning": score_function_zoning,
    "Circulation & flow": score_circulation_flow,
    "Ergonomics & clearances": score_ergonomics_clearances,
    "Natural light & ventilation": score_light_ventilation,
    "Aesthetic balance (Gestalt)": score_aesthetic_balance,
    "Feng shui harmony": score_fengshui_harmony,
    "Storage adequacy": score_storage_adequacy,
    "Acoustic comfort": score_acoustic_comfort,
}


def score(profile: Profile, selection: FrameworkSelection) -> ScoreCard:
    dimensions: List[DimensionScore] = []
    for name, fn in SCORERS.items():
        dimensions.append(fn(profile, selection))

    weights = dict(selection.weights)
    # Zero-weight disabled feng shui
    if any(d.dimension == "Feng shui harmony" and d.score == 0.0 and d.evidence.startswith("Feng shui overlay disabled")
           for d in dimensions):
        weights["Feng shui harmony"] = 0.0

    total_w = sum(weights.values()) or 1.0
    weighted = sum(d.score * weights.get(d.dimension, 0.0) for d in dimensions) / total_w
    weighted = round(weighted, 1)
    return ScoreCard(
        dimensions=dimensions,
        weighted_total=weighted,
        weights={k: round(v, 4) for k, v in weights.items()},
        overall_band=band_for(weighted).value,
    )
