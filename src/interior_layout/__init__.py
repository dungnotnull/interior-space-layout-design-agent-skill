"""Interior Design & Space Layout (function + feng shui) - production harness.

A framework-grounded, evidence-based interior layout scoring and improvement
engine. See ``PROJECT-detail.md`` for the full specification.

Quick start::

    from interior_layout.main import run, render_markdown
    deliverable = run(profile_dict)
    print(render_markdown(deliverable))
"""
from __future__ import annotations

from .schema import (  # noqa: F401
    Deliverable, Profile, Room, ScoreCard, DimensionScore, Roadmap, RoadmapItem,
    FengShuiOverlay, SCHEMA_VERSION,
)
from .main import run, render_markdown  # noqa: F401

__version__ = "1.0.0"
__all__ = ["run", "render_markdown", "Deliverable", "Profile", "SCHEMA_VERSION", "__version__"]
