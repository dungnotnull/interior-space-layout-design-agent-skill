# PROJECT-detail.md — Interior Design & Space Layout (function + feng shui)

## Executive Summary
`interior-space-layout-design` turns Claude into a senior interior designer and space planner fluent in both Western human-factors design and East-Asian feng shui (Bagua/Form School) practice. It runs a research-first harness that intakes the user's case, binds it to named world-renowned frameworks, scores it on 8 dimensions, and returns a prioritized improvement roadmap with effort/impact. The skill is self-improving: `tools/knowledge_updater.py` continuously refreshes its knowledge base from authoritative sources.

## Problem Statement
Homeowners, renters, and small studios lack an objective way to evaluate a floor plan or room layout for function, flow, ergonomics, lighting, and harmony before committing money to furniture or renovation.

## Target Users & Use Cases
- Primary: practitioners and non-experts who need an expert-grade, evidence-based assessment of their interior design & space layout (function + feng shui) artifact.
- Trigger examples:
  - User says: "Studio apartment" → skill zoned layout, circulation fixes, feng shui overlay, prioritized furniture plan
  - User says: "Home office addition" → skill ergonomic placement, lighting and acoustic recommendations, scored before/after
  - User says: "Feng shui request" → skill bagua overlay with remedies, labelled as traditional guidance

## Harness Architecture
```
intake/requirements
    │  profile-intake → framework-selector → scoring-engine → improvement-roadmap → fengshui-overlay → synthesis
    ▼
[named frameworks] → [multi-dimensional scoring] → [prioritized roadmap] → [quality/compliance gates] → DELIVERABLE
```

## Evaluation Frameworks (world-renowned, citable)
- **Christopher Alexander — A Pattern Language** — Named spatial patterns for human-centered design
- **Human Factors / Anthropometrics (Neufert Architects' Data)** — Clearance, reach, and circulation standards
- **Feng Shui Form School & Bagua mapping** — Energy-flow and orientation analysis
- **Gestalt principles of visual composition** — Balance, proximity, focal points
- **WELL Building Standard (daylight & comfort)** — Lighting, air, and thermal comfort criteria

## Scoring Dimensions
1. Function & zoning
2. Circulation & flow
3. Ergonomics & clearances
4. Natural light & ventilation
5. Aesthetic balance (Gestalt)
6. Feng shui harmony
7. Storage adequacy
8. Acoustic comfort

## Full Sub-Skill Catalog
### `sub-profile-intake`
- **Purpose:** Collect a complete, normalized profile before any analysis so downstream scoring is grounded in real inputs, not assumptions.
- **Inputs:** Free-form user description, uploaded artifacts, answers to clarifying questions
- **Outputs:** Normalized profile object (JSON-like) with goals, constraints, current state, and explicit unknowns flagged
- **Tools:** Read, WebSearch
- **Quality gate:** All mandatory fields captured or explicitly marked 'unknown'; no silent assumptions.
### `sub-framework-selector`
- **Purpose:** Map the intake context to one or more named, citable evaluation frameworks so scoring is never ad hoc.
- **Inputs:** Normalized profile, domain sub-type
- **Outputs:** Chosen framework(s) with citation, rationale, and the scoring rubric they imply
- **Tools:** Read, WebSearch, WebFetch
- **Quality gate:** At least one named framework selected with a source citation and a documented reason.
### `sub-scoring-engine`
- **Purpose:** Produce a transparent, dimension-by-dimension score (0-100 or band) with evidence for every sub-score.
- **Inputs:** Normalized profile, selected framework + rubric
- **Outputs:** Per-dimension scores, weighted total, strengths, and ranked weaknesses each tied to evidence
- **Tools:** Read, WebSearch
- **Quality gate:** Every dimension has a numeric score AND a one-line evidence/justification; no unscored dimension.
### `sub-improvement-roadmap`
- **Purpose:** Convert weaknesses into a sequenced, effort/impact-ranked action plan the user can execute.
- **Inputs:** Scored weaknesses, user constraints
- **Outputs:** Prioritized roadmap (Quick wins / Major projects / Long-term) with effort, impact, and success metric per item
- **Tools:** Read, Write
- **Quality gate:** Every recommendation has effort, impact, and a measurable success criterion.
### `sub-fengshui-overlay`
- **Purpose:** Provide feng shui guidance transparently labelled as a cultural/traditional framework, never as engineering fact.
- **Inputs:** Floor plan orientation, entrance, occupant goals
- **Outputs:** Bagua map, command-position notes, remedies
- **Tools:** Read, WebSearch
- **Quality gate:** Feng shui guidance is clearly labelled as a traditional framework distinct from human-factors findings.

## Skill File Format Specification
Each skill file uses YAML frontmatter (`name`, `description`) followed by: Role & Persona, Workflow (Harness Flow), Sub-skills Available, Tools, Output Format, Quality Gates. `skills/main.md` is the harness entry point and invokes the sub-skills above in order.

## E2E Execution Flow
1. Parse the user request and uploaded artifact(s).
2. Run intake/requirements sub-skill; flag unknowns (no silent assumptions).
3. (No safety gate for this cluster.)
4. Select governing framework(s) and rubric.
5. Score every dimension with cited evidence.
6. Generate the prioritized roadmap (effort/impact + success metric).
7. Run quality/devil's-advocate review.
8. Synthesize the final professional deliverable; pass all quality gates before display.

## SECOND-KNOWLEDGE-BRAIN Integration
- Sources: Neufert Architects' Data, Council on Tall Buildings / human factors refs, ArchDaily layout references, WELL Building Standard
- ArXiv categories: cs.HC, cs.GR
- Search queries: "interior layout ergonomics circulation", "daylighting indoor comfort standards", "spatial perception human factors"
- Append format: dated entries with Title, Authors, Year, Venue, DOI/Link, Relevance.

## Supporting Tools Spec
`tools/knowledge_updater.py`: crawl4ai → fetch → parse → score (recency × relevance) → dedupe (URL/DOI hash) → append to `SECOND-KNOWLEDGE-BRAIN.md`. Schedule: weekly cron.

## Quality Gates (must all pass before output)
- Every scored dimension has evidence.
- At least one named framework cited.
- Roadmap items each have effort, impact, and a measurable success metric.
- Devil's-advocate review passed.

## Test Scenarios
1. **Studio apartment** — Input: User shares a 28m2 studio floor plan and wants better function + flow → Expected: Zoned layout, circulation fixes, feng shui overlay, prioritized furniture plan
2. **Home office addition** — Input: User wants to add a WFH desk to a bedroom → Expected: Ergonomic placement, lighting and acoustic recommendations, scored before/after
3. **Feng shui request** — Input: User explicitly asks for command-position bed placement → Expected: Bagua overlay with remedies, labelled as traditional guidance
4. **Small-kitchen flow** — Input: User reports cramped kitchen work triangle → Expected: Work-triangle analysis vs Neufert clearances, reflow roadmap
5. **Rental, no renovation** — Input: User cannot move walls → Expected: Furniture-only roadmap respecting fixed constraints, scored

## Key Design Decisions
1. Scoring is always bound to named, citable frameworks — never ad hoc.
2. Intake forbids silent assumptions; unknowns are surfaced.
3. Roadmap is effort/impact-ranked and measurable.
4. Knowledge base is self-updating for trend alignment.
5. Devil's-advocate review is mandatory before output.
