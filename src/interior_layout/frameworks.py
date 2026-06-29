"""Named, citable evaluation frameworks and the rubrics they imply.

Each framework declares: a citation, the dimensions it governs, and the
quantitative thresholds used by the scoring engine. Thresholds are drawn from
the published standards referenced in SECOND-KNOWLEDGE-BRAIN.md and are kept
explicit so every score is reproducible.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class Framework:
    key: str
    name: str
    citation: str
    source_url: str
    governs: List[str]
    thresholds: Dict[str, float] = field(default_factory=dict)
    rationale_template: str = ""


# --- Threshold constants (SI units) -------------------------------------------

# Neufert Architects' Data - circulation & clearance standards (metric)
NEUFERT = Framework(
    key="neufert",
    name="Human Factors / Anthropometrics (Neufert Architects' Data)",
    citation="Neufert, E. & Neufert, P. (2012). Architects' Data, 4th ed. Wiley-Blackwell.",
    source_url="https://www.wiley.com/en-us/Architects%27+Data-p-9781118308551",
    governs=["Circulation & flow", "Ergonomics & clearances", "Storage adequacy"],
    thresholds={
        "min_corridor_width_m": 0.90,        # one-way passage
        "two_way_corridor_width_m": 1.20,
        "min_door_clear_width_m": 0.80,
        "comfortable_door_clear_width_m": 0.85,
        "bed_access_clearance_m": 0.50,
        "desk_chair_clearance_m": 0.60,
        "kitchen_work_triangle_min_m": 4.00, # sum of three legs
        "kitchen_work_triangle_max_m": 9.00,
        "kitchen_leg_min_m": 1.20,
        "kitchen_leg_max_m": 2.70,
        "min_living_area_per_person_m2": 14.0,
        "min_bedroom_area_m2": 9.0,
        "min_kitchen_area_m2": 7.0,
        "min_bathroom_area_m2": 3.5,
        "storage_liters_per_person": 1500.0,
        "min_closet_depth_m": 0.60,
    },
    rationale_template=(
        "Applies published anthropometric clearances and area minima so that "
        "circulation, ergonomics, and storage are judged against measurable "
        "human-factors data rather than intuition."
    ),
)

# Christopher Alexander - A Pattern Language
ALEXANDER = Framework(
    key="alexander",
    name="Christopher Alexander - A Pattern Language",
    citation="Alexander, C., Ishikawa, S. & Silverstein, M. (1977). A Pattern Language. Oxford University Press.",
    source_url="https://www.oup.com/us/catalog/general/subject/ArchitectureDesign/~~/c2Y9YWJkMWFyZG5lc3NwZXJzb25zZGs=",
    governs=["Function & zoning", "Circulation & flow", "Aesthetic balance (Gestalt)"],
    thresholds={
        "min_intimacy_gradient": 1.0,        # private rooms away from entrance
        "max_dead_lobby_ratio": 0.08,        # share of floor wasted on pure circulation lobbies
        "min_window_seat_ratio": 0.10,       # alcove / window-place share of living area
        "ceiling_height_variety": 1,         # at least one height change for intimacy
        "min_passageway_light_ratio": 0.03,
    },
    rationale_template=(
        "Maps the plan to named patterns (Intimacy Gradient, Short Passages, "
        "Window Place, Ceiling Height Variety) to judge zoning coherence and "
        "the lived quality of circulation."
    ),
)

# WELL Building Standard - light, air, thermal & acoustic comfort
WELL = Framework(
    key="well",
    name="W WELL Building Standard (daylight & comfort)",
    citation="International WELL Building Institute (2023). WELL Building Standard v2. International WELL Building Institute.",
    source_url="https://www.wellcertified.com/",
    governs=["Natural light & ventilation", "Acoustic comfort"],
    thresholds={
        "min_window_floor_ratio": 0.05,      # glazing area / floor area (approx daylight rule)
        "target_window_floor_ratio": 0.10,
        "min_cross_ventilation_openings": 2, # openings on opposite/aspected walls
        "min_operable_window_ratio": 0.40,   # operable share of glazing
        "max_reverb_time_s": 0.6,            # speech-frequency reverberation in living spaces
        "min_soft_surface_ratio": 0.20,      # rugs/soft furnishings share of floor
        "daylight_depth_ratio": 2.5,         # daylight reaches 2.5x window head height
    },
    rationale_template=(
        "Judges daylight, ventilation, and acoustic comfort against the WELL "
        "Building Standard v2 comfort concepts for indoor environments."
    ),
)

# Gestalt principles of visual composition
GESTALT = Framework(
    key="gestalt",
    name="Gestalt principles of visual composition",
    citation="Wertheimer, M. (1923). Untersuchungen zur Lehre von der Gestalt II. Psychologische Forschung, 4, 301-350.",
    source_url="https://link.springer.com/article/10.1007/BF00410637",
    governs=["Aesthetic balance (Gestalt)"],
    thresholds={
        "max_visual_weight_imbalance": 0.40, # |left-right| / total
        "min_focal_point_count": 1,
        "max_focal_point_count": 2,
        "proximity_cluster_tolerance_m": 0.30,
    },
    rationale_template=(
        "Scores balance, proximity, and focal-point clarity using Gestalt "
        "composition laws so aesthetic judgment is explicit, not taste-based."
    ),
)

# Feng Shui Form School & Bagua mapping (traditional/cultural - explicitly labelled)
FENGSHUI = Framework(
    key="fengshui",
    name="Feng Shui Form School & Bagua mapping",
    citation="Lip, E. (2006). Feng Shui: Environments of Power. Mastery Academy. (Traditional/cultural framework, not engineering science.)",
    source_url="https://www.masteryacademy.com/",
    governs=["Feng shui harmony"],
    thresholds={
        "command_position_clearance_m": 1.20, # bed/desk sees door, wall behind
        "min_door_to_bed_distance_m": 1.50,   # door not directly facing bed
        "beam_over_bed_penalty": 1,
        "clutter_free_circulation_ratio": 0.60,
    },
    rationale_template=(
        "Applies Bagua sector mapping and Form School command-position rules. "
        "Explicitly labelled as a traditional cultural framework distinct from "
        "human-factors engineering findings."
    ),
)


FRAMEWORKS: Dict[str, Framework] = {
    f.key: f for f in (NEUFERT, ALEXANDER, WELL, GESTALT, FENGSHUI)
}

DIMENSIONS = [
    "Function & zoning",
    "Circulation & flow",
    "Ergonomics & clearances",
    "Natural light & ventilation",
    "Aesthetic balance (Gestalt)",
    "Feng shui harmony",
    "Storage adequacy",
    "Acoustic comfort",
]

# Default dimension weights (sum to 1.0). Tunable per profile by the selector.
DEFAULT_WEIGHTS: Dict[str, float] = {
    "Function & zoning": 0.18,
    "Circulation & flow": 0.16,
    "Ergonomics & clearances": 0.16,
    "Natural light & ventilation": 0.14,
    "Aesthetic balance (Gestalt)": 0.10,
    "Feng shui harmony": 0.08,
    "Storage adequacy": 0.10,
    "Acoustic comfort": 0.08,
}


def frameworks_for_dimension(dimension: str) -> List[Framework]:
    return [f for f in FRAMEWORKS.values() if dimension in f.governs]


def primary_framework_for(dimension: str) -> Framework:
    """First framework listed as governing a dimension (the primary citation)."""
    fw = frameworks_for_dimension(dimension)
    return fw[0] if fw else NEUFERT
