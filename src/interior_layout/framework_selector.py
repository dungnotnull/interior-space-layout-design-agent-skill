"""sub-framework-selector implementation.

Maps a normalized :class:`Profile` to one or more named, citable frameworks
and produces the scoring weights each framework implies. Selection is
rule-based and traceable: every selected framework carries a documented reason.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .frameworks import (
    ALEXANDER,
    DEFAULT_WEIGHTS,
    FENGSHUI,
    FRAMEWORKS,
    Framework,
    GESTALT,
    NEUFERT,
    WELL,
)
from .schema import Profile


@dataclass
class FrameworkSelection:
    frameworks: List[Framework] = field(default_factory=list)
    weights: Dict[str, float] = field(default_factory=dict)
    rationale: Dict[str, str] = field(default_factory=dict)
    rubric_notes: str = ""

    @property
    def keys(self) -> List[str]:
        return [f.key for f in self.frameworks]

    @property
    def citations(self) -> List[str]:
        return [f.citation for f in self.frameworks]


def _has_function(profile: Profile, *funcs: str) -> bool:
    return any(r.function in funcs for r in profile.rooms)


def _goal_mentions(profile: Profile, *keywords: str) -> bool:
    blob = " ".join(profile.goals).lower() + " " + profile.raw_description.lower()
    return any(k in blob for k in keywords)


def select_frameworks(profile: Profile) -> FrameworkSelection:
    """Choose frameworks + weights for the case.

    Rules:
    - Neufert always applies (clearances/area/storage are universal).
    - Alexander applies whenever multiple rooms/zones exist.
    - WELL applies whenever daylight/ventilation/acoustics are relevant (always
      for habitable rooms, but weighted higher when comfort goals are stated).
    - Gestalt applies for living/dining/studio spaces where composition matters.
    - Feng Shui applies when requested OR when orientation data is present; it is
      always rendered as an explicitly-labelled overlay, never as engineering.
    """
    selected: List[Framework] = [NEUFERT]
    rationale: Dict[str, str] = {
        NEUFERT.key: NEUFERT.rationale_template,
    }

    if len(profile.rooms) >= 1:
        selected.append(ALEXANDER)
        rationale[ALEXANDER.key] = ALEXANDER.rationale_template

    habitable = _has_function(
        profile, "living", "bedroom", "studio", "office", "dining"
    )
    if habitable or _goal_mentions(profile, "light", "ventilation", "air", "acoustic", "comfort"):
        selected.append(WELL)
        rationale[WELL.key] = WELL.rationale_template
    else:
        # WELL still governs comfort dimensions; keep it but de-weighted.
        selected.append(WELL)
        rationale[WELL.key] = (
            "Comfort dimensions are still scored under WELL; down-weighted "
            "because no habitable comfort goal was stated."
        )

    composition_spaces = _has_function(profile, "living", "dining", "studio")
    if composition_spaces or _goal_mentions(profile, "balance", "aesthetic", "symmetry", "focal"):
        selected.append(GESTALT)
        rationale[GESTALT.key] = GESTALT.rationale_template

    wants_fengshui = _goal_mentions(
        profile, "feng shui", "fengshui", "bagua", "command position", "harmony"
    )
    has_orientation = profile.orientation_deg is not None or any(
        r.orientation_deg is not None for r in profile.rooms
    )
    if wants_fengshui or has_orientation:
        selected.append(FENGSHUI)
        rationale[FENGSHUI.key] = FENGSHUI.rationale_template + (
            " Enabled because the user requested it or supplied orientation data; "
            "rendered as an optional cultural overlay."
            if wants_fengshui else
            " Enabled because orientation data is available; rendered as an "
            "optional cultural overlay the user can ignore."
        )

    # De-duplicate while preserving order.
    seen = set()
    unique: List[Framework] = []
    for f in selected:
        if f.key not in seen:
            seen.add(f.key)
            unique.append(f)
    selected = unique

    weights = _derive_weights(profile, selected)

    rubric = (
        "Scoring is dimension-by-dimension on a 0-100 scale. Each dimension's "
        "primary framework supplies the thresholds; secondary frameworks supply "
        "supporting evidence. Weights reflect stated goals and the case type."
    )
    return FrameworkSelection(
        frameworks=selected,
        weights=weights,
        rationale=rationale,
        rubric_notes=rubric,
    )


def _derive_weights(profile: Profile, selected: List[Framework]) -> Dict[str, float]:
    weights = dict(DEFAULT_WEIGHTS)

    # If the user cannot renovate, down-weight dimensions that mostly need
    # structural change and up-weight furniture/moveable dimensions.
    if not profile.constraints.renovation_allowed:
        weights["Circulation & flow"] *= 0.7
        weights["Natural light & ventilation"] *= 0.8
        weights["Function & zoning"] *= 0.8
        weights["Aesthetic balance (Gestalt)"] *= 1.2
        weights["Storage adequacy"] *= 1.25
        weights["Ergonomics & clearances"] *= 1.15

    if _goal_mentions(profile, "feng shui", "fengshui", "bagua"):
        weights["Feng shui harmony"] = max(weights["Feng shui harmony"], 0.18)

    if _goal_mentions(profile, "light", "daylight", "ventilation"):
        weights["Natural light & ventilation"] = max(weights["Natural light & ventilation"], 0.20)

    if _goal_mentions(profile, "flow", "circulation", "triangle", "cramped"):
        weights["Circulation & flow"] = max(weights["Circulation & flow"], 0.22)

    if _goal_mentions(profile, "acoustic", "noise", "quiet"):
        weights["Acoustic comfort"] = max(weights["Acoustic comfort"], 0.16)

    # Drop weights for frameworks not selected (feng shui when disabled).
    if FENGSHUI not in selected:
        weights["Feng shui harmony"] = 0.0

    # Renormalize to sum 1.0
    total = sum(weights.values())
    if total > 0:
        weights = {k: round(v / total, 4) for k, v in weights.items()}
    return weights


def framework_by_key(key: str) -> Framework:
    return FRAMEWORKS[key]
