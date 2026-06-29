# interior-space-layout-design

> Score and improve interior layouts on **aesthetics, usability, circulation, and feng shui** - with every judgment bound to a named, citable framework.

[![CI](https://github.com/dungnotnull/interior-space-layout-design-agent-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/dungnotnull/interior-space-layout-design-agent-skill/actions/workflows/ci.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-25%20unit%20%2B%2010%20E2E-brightgreen.svg)](#tests)

`interior-space-layout-design` is a deterministic, evidence-based interior design
and space-planning engine. Give it a room or floor-plan description and it will:

1. **Intake** the case and flag every unknown (never invents missing data).
2. **Bind** the case to world-renowned, citable frameworks (Alexander, Neufert,
   WELL, Gestalt, Feng Shui Form School).
3. **Score** 8 dimensions on a 0-100 scale, each with one-line evidence.
4. **Roadmap** weaknesses into a constraint-aware, effort/impact-ranked plan with
   measurable success metrics.
5. **Overlay** optional Bagua/Form-School feng shui guidance - always labelled as
   a traditional/cultural framework, never as engineering fact.

It is **self-improving**: `tools/knowledge_updater.py` refreshes the living
knowledge base weekly from authoritative sources.

> No model training. No API keys. No LLM calls at runtime. The core engine is
> pure Python (standard library only) and runs deterministically and offline.

---

## Table of contents

- [Why this exists](#why-this-exists)
- [Key features](#key-features)
- [How it works](#how-it-works)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Input schema](#input-schema)
- [Scoring dimensions and frameworks](#scoring-dimensions-and-frameworks)
- [Quality gates](#quality-gates)
- [Self-improving knowledge base](#self-improving-knowledge-base)
- [Command-line interface](#command-line-interface)
- [Tests](#tests)
- [Project layout](#project-layout)
- [Cross-skill cluster integration](#cross-skill-cluster-integration)
- [Design principles](#design-principles)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Why this exists

Homeowners, renters, and small studios lack an objective way to evaluate a
floor plan or room layout for **function, flow, ergonomics, lighting, and
harmony** before committing money to furniture or renovation. Most online
"layout checkers" score from intuition or taste. This project scores from
**named frameworks with published thresholds**, so every number is reproducible
and every recommendation is traceable to a citation.

## Key features

- **8-dimension scorecard** (0-100 + band) with evidence per dimension.
- **5 named, citable frameworks** with explicit, published thresholds.
- **Constraint-aware roadmap** - renters get furniture-only fixes, no structural
  items sneak through.
- **Graceful degradation** - missing data returns clarifying questions instead
  of a fabricated score; offline mode falls back to the embedded knowledge base.
- **Traditional/cultural overlays** (feng shui) are always explicitly labelled,
  distinct from human-factors engineering findings.
- **Self-improving knowledge base** with dedup and recency/relevance scoring.
- **Shared cluster contract** so sibling design skills reuse the same schema,
  framework registry, and quality gates.
- **Zero runtime dependencies** for the core engine (Python stdlib only).

## How it works

```
user request
   |
   v
[sub-profile-intake] --normalize--> Profile (unknowns flagged, never invented)
   |
   v
[sub-framework-selector] --bind--> named frameworks + dimension weights
   |
   v
[sub-scoring-engine] --score--> 8 dimensions x (0-100 + evidence + framework)
   |
   v
[sub-improvement-roadmap] --plan--> quick wins / major / long-term (measurable)
   |
   v
[sub-fengshui-overlay] --overlay--> Bagua + command position (labelled cultural)
   |
   v
[quality gates] --6 non-skippable gates + devil's-advocate review-->
   |
   v
DELIVERABLE (scorecard + roadmap + feng shui + sources + gate status)
```

## Installation

```bash
# editable install (exposes the `interior-layout` CLI)
pip install -e .

# optional: rich web crawl for the self-improving knowledge base
pip install -e ".[crawl]"

# development / testing
pip install -e ".[dev]"
```

Or run directly without installing (the tooling adds `src/` to `PYTHONPATH`):

```bash
python -m interior_layout.cli evaluate --input scenario.json
python tools/knowledge_updater.py --no-crawl4ai --dry-run
```

Requirements: Python 3.8+. The core engine needs nothing beyond the standard
library.

## Quick start

### As a library

```python
from interior_layout.main import run, render_markdown

profile = {
    "project_id": "demo",
    "rooms": [{
        "name": "Bedroom", "function": "bedroom",
        "width_m": 4.0, "length_m": 4.0, "height_m": 2.7, "orientation_deg": 90,
        "windows": [{"wall": "E", "width_m": 1.6, "head_height_m": 2.1, "operable": True}],
        "doors":   [{"wall": "S", "width_m": 0.85, "swing": "in"}],
        "furniture": [
            {"name": "Bed",      "type": "bed",     "width_m": 1.6, "length_m": 2.0,
             "x_m": 0.4, "y_m": 0.4, "storage_liters": 150},
            {"name": "Wardrobe", "type": "closet",   "width_m": 1.2, "length_m": 0.6,
             "x_m": 3.0, "y_m": 0.3, "storage_liters": 800},
            {"name": "Rug",      "type": "rug",      "width_m": 2.0, "length_m": 1.5,
             "x_m": 1.0, "y_m": 2.0},
        ],
    }],
    "occupants": [{"role": "adult", "age": 30}],
    "goals": ["better sleep", "feng shui harmony"],
    "constraints": {"renovation_allowed": False, "renter": True, "budget_usd": 500},
    "orientation_deg": 90,
}

deliverable = run(profile)
print(render_markdown(deliverable))   # human-readable report
print(deliverable.to_json())         # machine-readable standardized schema
```

### As a CLI

```bash
interior-layout evaluate --input scenario.json --output report.md
interior-layout evaluate --input scenario.json --json        # JSON deliverable
interior-layout gates --input scenario.json                  # quality-gate status only
interior-layout clarifying-questions --input partial.json    # intake gaps
```

## Input schema

A JSON object:

| Field | Required | Description |
|---|---|---|
| `rooms[]` | yes | `name`, `function` (living/bedroom/kitchen/...), `width_m`, `length_m`; optional `height_m`, `orientation_deg`, `windows[]`, `doors[]`, `furniture[]`, `adjacent[]`, `notes` |
| `occupants[]` | yes | `role`; optional `age`, `height_cm`, `needs[]` |
| `goals[]` | yes | free-text goals (drive framework selection and weights) |
| `constraints` | no | `renovation_allowed`, `renter`, `budget_usd`, `fixed_elements[]`, `timeline` |
| `orientation_deg` | no | main entrance/building facing (enables feng shui overlay) |

Worked examples live in `tests/data/scenarios.json`.

### Furniture placement

Each furniture item may carry `x_m`/`y_m` coordinates (meters, room origin at
a corner). When coordinates are present, the engine runs placement-based
checks (bed side clearance, desk chair clearance, visual-weight balance,
command position). When absent, those checks are flagged as approximate - never
silently assumed.

## Scoring dimensions and frameworks

| Dimension | Primary framework | Key thresholds |
|---|---|---|
| Function & zoning | Alexander - A Pattern Language | Intimacy Gradient; Neufert area minima (bedroom 9 m2, kitchen 7 m2, bath 3.5 m2, living 14 m2/person) |
| Circulation & flow | Neufert Architects' Data | corridor 0.90/1.20 m; door clear 0.85 m; kitchen work triangle 4-9 m, legs 1.2-2.7 m |
| Ergonomics & clearances | Neufert Architects' Data | bed access 0.5 m; desk chair 0.6 m; living area >= 14 m2/person |
| Natural light & ventilation | WELL Building Standard v2 | glazing/floor 5-10%; cross-ventilation on >= 2 walls; operable share >= 40%; daylight depth 2.5x head height |
| Aesthetic balance (Gestalt) | Gestalt principles | visual-weight imbalance < 40%; 1-2 focal points |
| Feng shui harmony | Feng Shui Form School (cultural) | command position; clutter-free open floor >= 60% |
| Storage adequacy | Neufert Architects' Data | ~1500 L per person |
| Acoustic comfort | WELL Building Standard v2 | soft-surface >= 20%; estimated RT60 <= 0.6 s (Sabine proxy) |

Bands: excellent >= 90, good >= 75, fair >= 60, weak >= 40, poor < 40.

### Frameworks cited

- **Christopher Alexander - A Pattern Language** (1977, Oxford University Press)
- **Neufert Architects' Data** (2012, Wiley-Blackwell)
- **WELL Building Standard v2** (2023, IWBI)
- **Gestalt principles of visual composition** (Wertheimer, 1923)
- **Feng Shui Form School & Bagua mapping** (traditional/cultural)

## Quality gates

All six gates must pass before output is released. None is skippable.

1. **No silent assumptions** - missing mandatory fields are flagged as `unknown`,
   never invented.
2. **Every dimension scored with evidence** - numeric score + one-line
   justification.
3. **At least one named framework cited**.
4. **Roadmap items are measurable** - each has effort, impact (1-5), and a
   measurable success metric.
5. **Cultural overlays are labelled** - feng shui carries a `TRADITIONAL`/
   `CULTURAL` label, distinct from engineering findings.
6. **Devil's-advocate review** - the top findings are challenged before output.

When mandatory data is missing, the harness returns a **clarification
deliverable** (questions, no score). When live web sources are unavailable, it
runs in **degraded mode** against the embedded knowledge base and says so.

## Self-improving knowledge base

`SECOND-KNOWLEDGE-BRAIN.md` is a living knowledge base, pre-seeded with 10
curated, cited entries (each with a date, citation, relevance score, and
content hash for dedup). Refresh it weekly:

```bash
python tools/knowledge_updater.py                 # ArXiv API + crawl4ai (if installed)
python tools/knowledge_updater.py --no-crawl4ai   # ArXiv API only (stdlib)
python tools/knowledge_updater.py --dry-run       # preview, do not write
```

See `cron/knowledge_updater.cron` for scheduling. Dedup is by URL/DOI hash.

## Command-line interface

| Command | Purpose |
|---|---|
| `evaluate --input FILE [--json] [--output FILE]` | Run the full harness and emit a report |
| `gates --input FILE` | Run the harness and print quality-gate status only |
| `clarifying-questions --input FILE` | Print clarifying questions for an incomplete intake |

Flags: `--offline` (degraded mode), `--allow-assumptions` (score even with
missing mandatory fields, assumptions flagged). Exit code is non-zero if any
gate fails.

## Tests

```bash
pytest tests/                    # 25 unit tests
python tests/run_scenarios.py   # 10 end-to-end scenarios -> tests/PASS_FAIL_LOG.md
```

Current status: **25/25 unit tests pass, 10/10 end-to-end scenarios pass.**
The scenario suite covers studio apartments, home-office additions, explicit
feng shui requests, cramped kitchens, no-renovation rentals, incomplete-input
edge cases, offline degradation, and three adversarial cases (micro
non-compliant room, competing focal points, over-spread work triangle).

## Project layout

```
interior-space-layout-design/
- skills/                       Claude skill markdown (intake, selector, scoring, roadmap, fengshui, main)
- src/interior_layout/          production Python harness (stdlib core)
  - schema.py                 standardized output schema (Deliverable v1.0.0)
  - frameworks.py             named-framework registry + thresholds
  - intake.py                 sub-profile-intake
  - framework_selector.py     sub-framework-selector
  - scoring_engine.py         sub-scoring-engine (8 dimensions)
  - improvement_roadmap.py    sub-improvement-roadmap (constraint-aware recipes)
  - fengshui_overlay.py       sub-fengshui-overlay (labelled cultural)
  - gates.py                  6 non-skippable quality gates + devil's-advocate
  - synthesis.py              deliverable assembly
  - main.py                   harness orchestration + markdown renderer
  - cli.py                    interior-layout CLI
  - knowledge_updater.py      SECOND-KNOWLEDGE-BRAIN pipeline
  - cluster_contract.py       shared cross-skill contract (Phase 5)
- tools/knowledge_updater.py   knowledge-pipeline entry point
- tests/                        scenarios + pytest suite + PASS_FAIL_LOG.md
- SECOND-KNOWLEDGE-BRAIN.md    living knowledge base (seeded)
- CLUSTER-INTEGRATION.md       cross-skill reuse map
- pyproject.toml  README.md  LICENSE  CHANGELOG.md  requirements.txt
- .github/workflows/ci.yml     CI (pytest + scenarios + updater smoke)
```

## Cross-skill cluster integration

This skill is part of the `design-creative-media` cluster. Sibling skills
(colour-and-material-palette, lighting-design, acoustic-room-tuning,
furniture-arrangement-optimizer) reuse the standardized `Deliverable` schema,
the named-framework registry, the constraint-aware recipe library, and the
shared quality-gate runner via `src/interior_layout/cluster_contract.py`.
See `CLUSTER-INTEGRATION.md` for the full reuse map and extension protocol.

```python
from interior_layout.cluster_contract import (
    CLUSTER_SCHEMA_VERSION, build_shared_deliverable, run_shared_gates,
    register_framework, register_recipe, Framework,
)
```

## Design principles

1. Scoring is always bound to named, citable frameworks - never ad hoc.
2. Intake forbids silent assumptions; unknowns are surfaced.
3. The roadmap is effort/impact-ranked and measurable.
4. The knowledge base is self-updating for trend alignment.
5. Devil's-advocate review is mandatory before output.
6. Cultural/traditional guidance is explicitly labelled, never passed off as
   engineering fact.
7. Graceful degradation over failure: missing data and offline mode degrade
   gracefully with explicit signalling.

## Roadmap

- [x] Phases 0-5 complete (research, sub-skills, harness, knowledge pipeline,
      testing, cross-skill wiring).
- [ ] First live weekly crawl batch (run `tools/knowledge_updater.py`).
- [ ] Additional sibling cluster skills consuming the shared contract.
- [ ] Optional Pydantic-based validation layer for stricter input contracts.

## Contributing

Contributions are welcome. Please:

1. Open an issue describing the change.
2. Run `pytest tests/` and `python tests/run_scenarios.py` - both must pass.
3. Keep every score bound to a named framework with evidence.
4. Prefer stdlib-only additions; gate optional dependencies behind extras.

## License

MIT - see [LICENSE](LICENSE).
