"""Canonical data model and standardized output schema for the
Interior Design & Space Layout (function + feng shui) harness.

The schema is framework-independent so the same structure can be reused by
sibling skills in the ``design-creative-media`` cluster (Phase 5 wiring).
It uses only the Python standard library so the core engine runs with zero
external dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional
import json


class StrEnum(str, Enum):
    """A string enum that JSON-serializes as its value."""

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.value


class WallOrientation(StrEnum):
    N = "N"
    NE = "NE"
    E = "E"
    SE = "SE"
    S = "S"
    SW = "SW"
    W = "W"
    NW = "NW"


class RoomFunction(StrEnum):
    LIVING = "living"
    BEDROOM = "bedroom"
    KITCHEN = "kitchen"
    DINING = "dining"
    BATHROOM = "bathroom"
    OFFICE = "office"
    STUDIO = "studio"
    HALLWAY = "hallway"
    STORAGE = "storage"
    BALCONY = "balcony"
    OTHER = "other"


class ScoreBand(StrEnum):
    EXCELLENT = "excellent"  # 90-100
    GOOD = "good"            # 75-89
    FAIR = "fair"            # 60-74
    WEAK = "weak"            # 40-59
    POOR = "poor"            # 0-39


class EffortLevel(StrEnum):
    TRIVIAL = "trivial"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAJOR = "major"


class RoadmapTier(StrEnum):
    QUICK_WIN = "quick_win"
    MAJOR_PROJECT = "major_project"
    LONG_TERM = "long_term"


def band_for(score: float) -> ScoreBand:
    if score >= 90:
        return ScoreBand.EXCELLENT
    if score >= 75:
        return ScoreBand.GOOD
    if score >= 60:
        return ScoreBand.FAIR
    if score >= 40:
        return ScoreBand.WEAK
    return ScoreBand.POOR


@dataclass
class Window:
    wall: str  # WallOrientation value or degree string
    width_m: float
    sill_height_m: float = 1.0
    head_height_m: float = 2.1
    operable: bool = True

    @property
    def area_m2(self) -> float:
        return max(0.0, (self.head_height_m - self.sill_height_m)) * self.width_m


@dataclass
class Door:
    wall: str
    width_m: float
    swing: str = "in"  # "in" | "out" | "pocket" | "slide"
    to_room: str = ""
    clear_width_m: Optional[float] = None

    @property
    def effective_clear_width(self) -> float:
        return self.clear_width_m if self.clear_width_m else self.width_m


@dataclass
class Furniture:
    name: str
    type: str
    width_m: float
    length_m: float
    x_m: Optional[float] = None
    y_m: Optional[float] = None
    fixed: bool = False
    storage_liters: float = 0.0


@dataclass
class Room:
    name: str
    function: str  # RoomFunction value
    width_m: float
    length_m: float
    height_m: float = 2.7
    windows: List[Window] = field(default_factory=list)
    doors: List[Door] = field(default_factory=list)
    furniture: List[Furniture] = field(default_factory=list)
    adjacent: List[str] = field(default_factory=list)
    orientation_deg: Optional[float] = None  # facing direction of primary window
    notes: str = ""

    @property
    def area_m2(self) -> float:
        return round(self.width_m * self.length_m, 2)

    @property
    def perimeter_m(self) -> float:
        return 2.0 * (self.width_m + self.length_m)

    @property
    def window_area_m2(self) -> float:
        return round(sum(w.area_m2 for w in self.windows), 2)

    @property
    def glazing_ratio(self) -> float:
        return round(self.window_area_m2 / self.area_m2, 4) if self.area_m2 else 0.0

    @property
    def storage_liters(self) -> float:
        return round(sum(f.storage_liters for f in self.furniture), 1)


@dataclass
class Occupant:
    role: str  # e.g. "adult", "child", "infant", "elderly", "pet"
    age: Optional[int] = None
    height_cm: Optional[float] = None
    needs: List[str] = field(default_factory=list)


@dataclass
class Constraints:
    renovation_allowed: bool = True
    renter: bool = False
    budget_usd: Optional[float] = None
    fixed_elements: List[str] = field(default_factory=list)
    timeline: str = ""


@dataclass
class Profile:
    """Normalized intake profile (output of sub-profile-intake)."""

    project_id: str
    rooms: List[Room] = field(default_factory=list)
    occupants: List[Occupant] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    constraints: Constraints = field(default_factory=Constraints)
    location: str = ""
    orientation_deg: Optional[float] = None  # main entrance / building facing
    entrance_description: str = ""
    raw_description: str = ""
    artifacts: List[str] = field(default_factory=list)
    unknowns: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_area_m2(self) -> float:
        return round(sum(r.area_m2 for r in self.rooms), 2)

    @property
    def total_window_area_m2(self) -> float:
        return round(sum(r.window_area_m2 for r in self.rooms), 2)

    @property
    def total_storage_liters(self) -> float:
        return round(sum(r.storage_liters for r in self.rooms), 1)

    def rooms_of(self, function: str) -> List[Room]:
        return [r for r in self.rooms if r.function == function]


@dataclass
class Weakness:
    dimension: str
    description: str
    severity: float  # 0-1, higher = worse
    evidence: str
    framework: str
    remediable: bool = True


@dataclass
class DimensionScore:
    dimension: str
    score: float  # 0-100
    band: str
    evidence: str
    framework: str
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)


@dataclass
class ScoreCard:
    dimensions: List[DimensionScore] = field(default_factory=list)
    weighted_total: float = 0.0
    weights: Dict[str, float] = field(default_factory=dict)
    overall_band: str = ""

    def dimension(self, name: str) -> Optional[DimensionScore]:
        for d in self.dimensions:
            if d.dimension == name:
                return d
        return None

    def ranked_weaknesses(self) -> List[Weakness]:
        out: List[Weakness] = []
        for d in self.dimensions:
            sev = (100.0 - d.score) / 100.0
            for w in d.weaknesses:
                out.append(Weakness(
                    dimension=d.dimension,
                    description=w,
                    severity=round(max(0.1, sev), 3),
                    evidence=d.evidence,
                    framework=d.framework,
                ))
        out.sort(key=lambda x: x.severity, reverse=True)
        return out


@dataclass
class RoadmapItem:
    title: str
    tier: str  # RoadmapTier value
    effort_hours: float
    effort_level: str  # EffortLevel value
    impact: int  # 1-5
    impact_description: str
    success_metric: str
    steps: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    addresses_dimensions: List[str] = field(default_factory=list)
    cost_estimate_usd: Optional[float] = None


@dataclass
class Roadmap:
    items: List[RoadmapItem] = field(default_factory=list)

    def by_tier(self, tier: str) -> List[RoadmapItem]:
        return [i for i in self.items if i.tier == tier]


@dataclass
class BaguaSector:
    name: str
    life_aspect: str
    element: str
    direction: str
    present: bool
    notes: str = ""
    remedies: List[str] = field(default_factory=list)


@dataclass
class FengShuiOverlay:
    enabled: bool
    label: str  # always a traditional-framework disclaimer
    facing_direction: str
    bagua_sectors: List[BaguaSector] = field(default_factory=list)
    command_position_notes: List[str] = field(default_factory=list)
    remedies: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)


@dataclass
class GateResult:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class Deliverable:
    """Final synthesized output (standardized across the cluster)."""

    schema_version: str
    project_id: str
    executive_summary: str
    top_findings: List[str]
    scorecard: ScoreCard
    findings: List[DimensionScore]
    roadmap: Roadmap
    fengshui: FengShuiOverlay
    frameworks_cited: List[str]
    sources: List[str]
    gates: List[GateResult]
    gates_passed: bool
    degraded_mode: bool
    degradation_note: str = ""
    clarifying_questions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False, default=str)


SCHEMA_VERSION = "1.0.0"

