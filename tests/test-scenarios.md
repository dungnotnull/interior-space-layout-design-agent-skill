# Test Scenarios - Interior Design & Space Layout (function + feng shui)

These scenarios validate the harness, scoring, gates, and graceful degradation.
They are **executable**: each scenario lives in `tests/data/scenarios.json` and
is run by `python tests/run_scenarios.py`, which writes `tests/PASS_FAIL_LOG.md`
and `tests/results.json`. Ten scenarios (5 core + 3 edge/adversarial + 2 extra
adversarial); all currently PASS.

## Scenario 1: Studio apartment
- **Input:** 28m2 studio (3 rooms) floor plan; renter, no renovation; goals: flow + feng shui.
- **Expected:** Zoned layout, circulation fixes, feng shui overlay, prioritized furniture plan.
- **Frameworks:** Alexander, Neufert, Feng Shui.
- **Gates:** every dimension scored with evidence; roadmap items measurable.
- **Pass criteria:** scorecard of 8 dims, labelled feng shui overlay, non-empty roadmap.

## Scenario 2: Home office addition
- **Input:** Add a WFH desk to a bedroom; renovation allowed.
- **Expected:** Ergonomic placement, lighting/acoustic recommendations, scored before/after.
- **Frameworks:** Neufert, WELL.
- **Pass criteria:** 8-dim scorecard, non-empty measurable roadmap.

## Scenario 3: Feng shui request
- **Input:** User asks for command-position bed placement; beam present.
- **Expected:** Bagua overlay with remedies, labelled as traditional guidance.
- **Frameworks:** Feng Shui.
- **Pass criteria:** feng shui enabled + labelled, non-empty roadmap.

## Scenario 4: Small-kitchen flow
- **Input:** Cramped kitchen work triangle (legs too tight).
- **Expected:** Work-triangle analysis vs Neufert, reflow roadmap.
- **Frameworks:** Neufert.
- **Pass criteria:** 8-dim scorecard, non-empty roadmap.

## Scenario 5: Rental, no renovation
- **Input:** Cannot move walls; furniture-only plan.
- **Expected:** Furniture-only roadmap respecting fixed constraints.
- **Frameworks:** Neufert, Gestalt.
- **Pass criteria:** roadmap contains no structural/renovation items.

## Scenario 6: Incomplete input (edge)
- **Input:** Vague one-line description, no artifact.
- **Expected:** Intake flags missing fields, asks targeted questions; no score fabricated.
- **Pass criteria:** gates fail, no scorecard, clarifying questions present.

## Scenario 7: Offline / sources unavailable (graceful degradation)
- **Input:** Normal request, but live search unavailable.
- **Expected:** Fall back to SECOND-KNOWLEDGE-BRAIN.md, state reduced confidence.
- **Pass criteria:** degraded mode flagged, degradation note present, internal frameworks cited.

## Scenario 8: Micro non-compliant room (adversarial)
- **Input:** 3.24m2 living room for 2 occupants, below all Neufert minima.
- **Expected:** Very low overall score; roadmap of structural upgrades.
- **Pass criteria:** gates pass, 8-dim scorecard, overall score < 60, non-empty roadmap.

## Scenario 9: Open-plan with competing focal points (adversarial)
- **Input:** 48m2 open living with 5 focal anchors; renter; no orientation.
- **Expected:** Gestalt flags competing focal points; feng shui disabled; furniture-only fixes.
- **Pass criteria:** gates pass, feng shui disabled, non-empty roadmap.

## Scenario 10: Bad kitchen + windowless bathroom (adversarial)
- **Input:** Over-spread work triangle (legs >2.7m) and a windowless bathroom.
- **Expected:** Neufert work-triangle weakness + WELL ventilation gap; reflow roadmap.
- **Pass criteria:** gates pass, 8-dim scorecard, non-empty roadmap.

## Running

```bash
python tests/run_scenarios.py            # -> tests/PASS_FAIL_LOG.md, tests/results.json
pytest tests/                           # 25 unit tests
```
