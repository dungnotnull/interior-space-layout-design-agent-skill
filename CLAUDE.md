# CLAUDE.md — Interior Design & Space Layout (function + feng shui)

**Skill name:** `interior-space-layout-design`
**Tagline:** Score and improve interior layouts on aesthetics, usability, circulation, and feng shui.
**Source idea:** #89 (cluster: `design-creative-media`)
**Current phase:** Phase 4 — Testing & Validation (initial build complete)

## Problem This Skill Solves
Homeowners, renters, and small studios lack an objective way to evaluate a floor plan or room layout for function, flow, ergonomics, lighting, and harmony before committing money to furniture or renovation.

## Harness Flow Summary
1. **sub-profile-intake** → Collect a complete, normalized profile before any analysis so downstream scoring is grounded in real inputs, not assumptions.
2. **sub-framework-selector** → Map the intake context to one or more named, citable evaluation frameworks so scoring is never ad hoc.
3. **sub-scoring-engine** → Produce a transparent, dimension-by-dimension score (0-100 or band) with evidence for every sub-score.
4. **sub-improvement-roadmap** → Convert weaknesses into a sequenced, effort/impact-ranked action plan the user can execute.
5. **sub-fengshui-overlay** → Provide feng shui guidance transparently labelled as a cultural/traditional framework, never as engineering fact.
6. **main (synthesis)** → assemble the scored deliverable + prioritized roadmap and run final quality gates.

## Gates
No safety/compliance gate applies to this cluster; standard quality gates still apply.

## Sub-skills
- `skills/sub-profile-intake.md` — Structured intake of room dimensions, fixed elements, occupants, and lifestyle plus goals, constraints, and context.
- `skills/sub-framework-selector.md` — Select the most appropriate world-renowned space-planning framework(s) for this case.
- `skills/sub-scoring-engine.md` — Multi-dimensional scoring of the layout against the selected framework.
- `skills/sub-improvement-roadmap.md` — Prioritized improvement roadmap for the layout with effort/impact.
- `skills/sub-fengshui-overlay.md` — Apply Bagua/Form-School analysis as an explicit, optional overlay.

## Tools Required
WebSearch, WebFetch, Read, Write, Bash

## Knowledge Sources
- [Neufert Architects' Data](https://www.wiley.com)
- [Council on Tall Buildings / human factors refs](https://www.ctbuh.org)
- [ArchDaily layout references](https://www.archdaily.com)
- [WELL Building Standard](https://www.wellcertified.com)

ArXiv / research categories crawled: cs.HC, cs.GR

## Supporting Tools
- `tools/knowledge_updater.py` — crawl4ai pipeline that refreshes `SECOND-KNOWLEDGE-BRAIN.md` weekly from the sources above.

## Active Development Tasks
- [x] Scaffold deliverables and sub-skills
- [x] Define scoring dimensions against named frameworks
- [ ] Expand `SECOND-KNOWLEDGE-BRAIN.md` with first crawl batch
- [ ] Add 3 more adversarial test scenarios
- [ ] Wire shared cluster sub-skills for reuse

## Reference Docs
- `PROJECT-detail.md` — full technical spec
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` — phase roadmap
- `SECOND-KNOWLEDGE-BRAIN.md` — living domain knowledge base
