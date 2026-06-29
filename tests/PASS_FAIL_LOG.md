# PASS / FAIL LOG - Interior Design & Space Layout harness

Run at: 2026-06-29T23:04:23
Scenarios: 10 total | 10 passed | 0 failed | ALL_PASS=True

## Summary
| # | Scenario | Result | Total | Band | Gates | Degraded | Roadmap items |
|---|----------|--------|-------|------|-------|----------|---------------|
| 1 | S1_studio_apartment | PASS | 65.2 | fair | pass | no | 9 |
| 2 | S2_home_office_addition | PASS | 72.8 | fair | pass | no | 5 |
| 3 | S3_feng_shui_request | PASS | 69.6 | fair | pass | no | 5 |
| 4 | S4_small_kitchen_flow | PASS | 56.2 | weak | pass | no | 4 |
| 5 | S5_rental_no_renovation | PASS | 54.6 | weak | pass | no | 7 |
| 6 | S6_incomplete_input | PASS | 0.0 | not_graded | fail | yes | 0 |
| 7 | S7_offline_degraded | PASS | 70.2 | fair | pass | yes | 4 |
| 8 | S8_micro_noncompliant | PASS | 22.5 | poor | pass | no | 10 |
| 9 | S9_openplan_competing_focals | PASS | 81.4 | good | pass | no | 5 |
| 10 | S10_bad_kitchen_and_bathroom | PASS | 65.3 | fair | pass | no | 5 |

## Per-scenario detail
### S1_studio_apartment - PASS
- Description: 28m2 studio floor plan, better function + flow
- Frameworks cited: Christopher Alexander - A Pattern Language, Feng Shui Form School & Bagua mapping, Gestalt principles of visual composition, Human Factors / Anthropometrics (Neufert Architects' Data), W WELL Building Standard (daylight & comfort)
- Frameworks match expected: True
- Assertions:
  - [PASS] gates_passed
  - [PASS] scorecard_has_8_dims
  - [PASS] roadmap_nonempty
  - [PASS] fengshui_labelled
- Gates:
  - [PASS] no_silent_assumptions - OK
  - [PASS] every_dimension_scored_with_evidence - All 8 dimensions have a score and evidence.
  - [PASS] at_least_one_named_framework_cited - Cited frameworks: Christopher Alexander - A Pattern Language, Feng Shui Form School & Bagua mapping, Gestalt principles of visual composition, Human Factors / Anthropometrics (Neufert Architects' Data), W WELL Building Standard (daylight & comfort)
  - [PASS] roadmap_items_measurable - OK
  - [PASS] fengshui_labelled_as_traditional - OK
  - [PASS] devils_advocate_review - OK

### S2_home_office_addition - PASS
- Description: Add a WFH desk to a bedroom
- Frameworks cited: Christopher Alexander - A Pattern Language, Feng Shui Form School & Bagua mapping, Gestalt principles of visual composition, Human Factors / Anthropometrics (Neufert Architects' Data), W WELL Building Standard (daylight & comfort)
- Frameworks match expected: True
- Assertions:
  - [PASS] gates_passed
  - [PASS] scorecard_has_8_dims
  - [PASS] roadmap_nonempty
- Gates:
  - [PASS] no_silent_assumptions - OK
  - [PASS] every_dimension_scored_with_evidence - All 8 dimensions have a score and evidence.
  - [PASS] at_least_one_named_framework_cited - Cited frameworks: Christopher Alexander - A Pattern Language, Feng Shui Form School & Bagua mapping, Gestalt principles of visual composition, Human Factors / Anthropometrics (Neufert Architects' Data), W WELL Building Standard (daylight & comfort)
  - [PASS] roadmap_items_measurable - OK
  - [PASS] fengshui_labelled_as_traditional - OK
  - [PASS] devils_advocate_review - OK

### S3_feng_shui_request - PASS
- Description: User asks for command-position bed placement
- Frameworks cited: Christopher Alexander - A Pattern Language, Feng Shui Form School & Bagua mapping, Gestalt principles of visual composition, Human Factors / Anthropometrics (Neufert Architects' Data), W WELL Building Standard (daylight & comfort)
- Frameworks match expected: True
- Assertions:
  - [PASS] gates_passed
  - [PASS] fengshui_enabled
  - [PASS] fengshui_labelled
  - [PASS] roadmap_nonempty
- Gates:
  - [PASS] no_silent_assumptions - OK
  - [PASS] every_dimension_scored_with_evidence - All 8 dimensions have a score and evidence.
  - [PASS] at_least_one_named_framework_cited - Cited frameworks: Christopher Alexander - A Pattern Language, Feng Shui Form School & Bagua mapping, Gestalt principles of visual composition, Human Factors / Anthropometrics (Neufert Architects' Data), W WELL Building Standard (daylight & comfort)
  - [PASS] roadmap_items_measurable - OK
  - [PASS] fengshui_labelled_as_traditional - OK
  - [PASS] devils_advocate_review - OK

### S4_small_kitchen_flow - PASS
- Description: Cramped kitchen work triangle
- Frameworks cited: Christopher Alexander - A Pattern Language, Feng Shui Form School & Bagua mapping, Gestalt principles of visual composition, Human Factors / Anthropometrics (Neufert Architects' Data), W WELL Building Standard (daylight & comfort)
- Frameworks match expected: True
- Assertions:
  - [PASS] gates_passed
  - [PASS] scorecard_has_8_dims
  - [PASS] roadmap_nonempty
- Gates:
  - [PASS] no_silent_assumptions - OK
  - [PASS] every_dimension_scored_with_evidence - All 8 dimensions have a score and evidence.
  - [PASS] at_least_one_named_framework_cited - Cited frameworks: Christopher Alexander - A Pattern Language, Feng Shui Form School & Bagua mapping, Gestalt principles of visual composition, Human Factors / Anthropometrics (Neufert Architects' Data), W WELL Building Standard (daylight & comfort)
  - [PASS] roadmap_items_measurable - OK
  - [PASS] fengshui_labelled_as_traditional - OK
  - [PASS] devils_advocate_review - OK

### S5_rental_no_renovation - PASS
- Description: Cannot move walls; furniture-only roadmap
- Frameworks cited: Christopher Alexander - A Pattern Language, Feng Shui Form School & Bagua mapping, Gestalt principles of visual composition, Human Factors / Anthropometrics (Neufert Architects' Data), W WELL Building Standard (daylight & comfort)
- Frameworks match expected: True
- Assertions:
  - [PASS] gates_passed
  - [PASS] roadmap_nonempty
  - [PASS] no_renovation_roadmap_items
- Gates:
  - [PASS] no_silent_assumptions - OK
  - [PASS] every_dimension_scored_with_evidence - All 8 dimensions have a score and evidence.
  - [PASS] at_least_one_named_framework_cited - Cited frameworks: Christopher Alexander - A Pattern Language, Feng Shui Form School & Bagua mapping, Gestalt principles of visual composition, Human Factors / Anthropometrics (Neufert Architects' Data), W WELL Building Standard (daylight & comfort)
  - [PASS] roadmap_items_measurable - OK
  - [PASS] fengshui_labelled_as_traditional - OK
  - [PASS] devils_advocate_review - OK

### S6_incomplete_input - PASS
- Description: Vague one-line description, no artifact
- Frameworks cited: (none)
- Frameworks match expected: True
- Assertions:
  - [PASS] gates_failed
  - [PASS] no_scorecard
  - [PASS] clarifying_questions_present
- Gates:
  - [FAIL] no_silent_assumptions - Mandatory fields missing: What rooms/spaces are in the layout, with width x length in meters?, Who uses the space (occupants, ages, mobility needs)?, What is your main goal (e.g. better flow, more light, feng shui harmony)?, Which compass direction does the main entrance/primary window face?
  - [FAIL] every_dimension_scored_with_evidence - Scoring skipped pending clarification.
  - [FAIL] at_least_one_named_framework_cited - No framework selected until intake is complete.
  - [PASS] roadmap_items_measurable - No roadmap produced yet; gate n/a.
  - [PASS] fengshui_labelled_as_traditional - No feng shui overlay produced yet; gate n/a.
  - [PASS] devils_advocate_review - No findings to challenge yet; gate n/a.

### S7_offline_degraded - PASS
- Description: Normal request but live search unavailable
- Frameworks cited: Christopher Alexander - A Pattern Language, Feng Shui Form School & Bagua mapping, Gestalt principles of visual composition, Human Factors / Anthropometrics (Neufert Architects' Data), W WELL Building Standard (daylight & comfort)
- Frameworks match expected: True
- Assertions:
  - [PASS] degraded_mode
  - [PASS] degradation_note_present
  - [PASS] frameworks_cited_from_internal
- Gates:
  - [PASS] no_silent_assumptions - OK
  - [PASS] every_dimension_scored_with_evidence - All 8 dimensions have a score and evidence.
  - [PASS] at_least_one_named_framework_cited - Cited frameworks: Christopher Alexander - A Pattern Language, Feng Shui Form School & Bagua mapping, Gestalt principles of visual composition, Human Factors / Anthropometrics (Neufert Architects' Data), W WELL Building Standard (daylight & comfort)
  - [PASS] roadmap_items_measurable - OK
  - [PASS] fengshui_labelled_as_traditional - OK
  - [PASS] devils_advocate_review - OK

### S8_micro_noncompliant - PASS
- Description: Adversarial: extremely tiny room below all Neufert minima
- Frameworks cited: Christopher Alexander - A Pattern Language, Feng Shui Form School & Bagua mapping, Gestalt principles of visual composition, Human Factors / Anthropometrics (Neufert Architects' Data), W WELL Building Standard (daylight & comfort)
- Frameworks match expected: True
- Assertions:
  - [PASS] gates_passed
  - [PASS] scorecard_has_8_dims
  - [PASS] roadmap_nonempty
  - [PASS] low_overall_score
- Gates:
  - [PASS] no_silent_assumptions - OK
  - [PASS] every_dimension_scored_with_evidence - All 8 dimensions have a score and evidence.
  - [PASS] at_least_one_named_framework_cited - Cited frameworks: Christopher Alexander - A Pattern Language, Feng Shui Form School & Bagua mapping, Gestalt principles of visual composition, Human Factors / Anthropometrics (Neufert Architects' Data), W WELL Building Standard (daylight & comfort)
  - [PASS] roadmap_items_measurable - OK
  - [PASS] fengshui_labelled_as_traditional - OK
  - [PASS] devils_advocate_review - OK

### S9_openplan_competing_focals - PASS
- Description: Adversarial: open-plan living with too many competing focal points, no orientation
- Frameworks cited: Christopher Alexander - A Pattern Language, Feng Shui Form School & Bagua mapping, Gestalt principles of visual composition, Human Factors / Anthropometrics (Neufert Architects' Data), W WELL Building Standard (daylight & comfort)
- Frameworks match expected: True
- Assertions:
  - [PASS] gates_passed
  - [PASS] fengshui_disabled
  - [PASS] roadmap_nonempty
- Gates:
  - [PASS] no_silent_assumptions - OK
  - [PASS] every_dimension_scored_with_evidence - All 8 dimensions have a score and evidence.
  - [PASS] at_least_one_named_framework_cited - Cited frameworks: Christopher Alexander - A Pattern Language, Feng Shui Form School & Bagua mapping, Gestalt principles of visual composition, Human Factors / Anthropometrics (Neufert Architects' Data), W WELL Building Standard (daylight & comfort)
  - [PASS] roadmap_items_measurable - OK
  - [PASS] fengshui_labelled_as_traditional - OK
  - [PASS] devils_advocate_review - OK

### S10_bad_kitchen_and_bathroom - PASS
- Description: Adversarial: over-spread work triangle and windowless bathroom
- Frameworks cited: Christopher Alexander - A Pattern Language, Feng Shui Form School & Bagua mapping, Gestalt principles of visual composition, Human Factors / Anthropometrics (Neufert Architects' Data), W WELL Building Standard (daylight & comfort)
- Frameworks match expected: True
- Assertions:
  - [PASS] gates_passed
  - [PASS] scorecard_has_8_dims
  - [PASS] roadmap_nonempty
- Gates:
  - [PASS] no_silent_assumptions - OK
  - [PASS] every_dimension_scored_with_evidence - All 8 dimensions have a score and evidence.
  - [PASS] at_least_one_named_framework_cited - Cited frameworks: Christopher Alexander - A Pattern Language, Feng Shui Form School & Bagua mapping, Gestalt principles of visual composition, Human Factors / Anthropometrics (Neufert Architects' Data), W WELL Building Standard (daylight & comfort)
  - [PASS] roadmap_items_measurable - OK
  - [PASS] fengshui_labelled_as_traditional - OK
  - [PASS] devils_advocate_review - OK
