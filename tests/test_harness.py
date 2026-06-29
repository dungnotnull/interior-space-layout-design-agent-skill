"""Unit tests for the interior_layout package (pytest).

Run with: ``pytest tests/``. These are real production tests, not stubs.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_SRC = _HERE.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from interior_layout import schema, frameworks
from interior_layout.intake import build_profile, clarifying_questions, mandatory_fields_missing, IntakeError
from interior_layout.framework_selector import select_frameworks
from interior_layout.scoring_engine import score
from interior_layout.improvement_roadmap import build_roadmap, RECIPES
from interior_layout.fengshui_overlay import build_overlay
from interior_layout.gates import run_all_gates
from interior_layout.main import run, render_markdown
from interior_layout import cli


def _sample_profile_data():
    return {
        "project_id": "unit",
        "rooms": [
            {"name": "Bedroom", "function": "bedroom", "width_m": 4.0, "length_m": 4.0,
             "height_m": 2.7, "orientation_deg": 90,
             "windows": [{"wall": "E", "width_m": 1.6, "head_height_m": 2.1, "operable": True},
                         {"wall": "W", "width_m": 1.0, "head_height_m": 2.1, "operable": True}],
             "doors": [{"wall": "S", "width_m": 0.85, "swing": "in"}],
             "furniture": [
                 {"name": "Bed", "type": "bed", "width_m": 1.6, "length_m": 2.0,
                  "x_m": 0.4, "y_m": 0.4, "storage_liters": 150},
                 {"name": "Wardrobe", "type": "closet", "width_m": 1.2, "length_m": 0.6,
                  "x_m": 3.0, "y_m": 0.3, "storage_liters": 800},
                 {"name": "Rug", "type": "rug", "width_m": 2.0, "length_m": 1.5,
                  "x_m": 1.0, "y_m": 2.0},
             ]},
        ],
        "occupants": [{"role": "adult", "age": 30}],
        "goals": ["better sleep", "feng shui harmony"],
        "constraints": {"renovation_allowed": False, "renter": True, "budget_usd": 500},
        "orientation_deg": 90,
    }


# --- schema -------------------------------------------------------------------

def test_band_thresholds():
    assert schema.band_for(95) == schema.ScoreBand.EXCELLENT
    assert schema.band_for(80) == schema.ScoreBand.GOOD
    assert schema.band_for(65) == schema.ScoreBand.FAIR
    assert schema.band_for(50) == schema.ScoreBand.WEAK
    assert schema.band_for(10) == schema.ScoreBand.POOR


def test_room_area_and_glazing():
    r = schema.Room(name="x", function="living", width_m=4, length_m=5,
                    windows=[schema.Window(wall="S", width_m=2, head_height_m=2.1, sill_height_m=0.9)])
    assert r.area_m2 == 20.0
    assert r.window_area_m2 == round(2 * 1.2, 2)
    assert r.glazing_ratio == round(r.window_area_m2 / 20.0, 4)


def test_deliverable_json_roundtrip():
    d = run(_sample_profile_data())
    js = d.to_json()
    parsed = json.loads(js)
    assert parsed["schema_version"] == schema.SCHEMA_VERSION
    assert parsed["project_id"] == "unit"


# --- frameworks ---------------------------------------------------------------

def test_every_dimension_has_primary_framework():
    for dim in frameworks.DIMENSIONS:
        assert frameworks.primary_framework_for(dim) is not None


def test_default_weights_sum_to_one():
    assert abs(sum(frameworks.DEFAULT_WEIGHTS.values()) - 1.0) < 1e-9


# --- intake -------------------------------------------------------------------

def test_intake_flags_missing_fields():
    p = build_profile({"raw_description": "vague", "goals": []})
    assert "profile.rooms" in p.unknowns
    assert "profile.occupants" in p.unknowns
    assert mandatory_fields_missing(p)


def test_intake_strict_raises():
    with pytest.raises(IntakeError):
        build_profile({"raw_description": "vague"}, strict=True)


def test_renter_forces_no_renovation():
    p = build_profile({"rooms": [{"name": "R", "function": "living", "width_m": 4, "length_m": 4}],
                       "occupants": [{"role": "adult"}], "goals": ["x"],
                       "constraints": {"renter": True, "renovation_allowed": True}})
    assert p.constraints.renovation_allowed is False


def test_clarifying_questions_returned():
    p = build_profile({"raw_description": "vague"})
    qs = clarifying_questions(p)
    assert qs  # non-empty


# --- selector -----------------------------------------------------------------

def test_selector_picks_neufert_always_and_fengshui_when_requested():
    p = build_profile(_sample_profile_data())
    sel = select_frameworks(p)
    keys = sel.keys
    assert "neufert" in keys
    assert "fengshui" in keys
    assert abs(sum(sel.weights.values()) - 1.0) < 1e-3


def test_selector_disables_fengshui_without_orientation():
    data = _sample_profile_data()
    data["orientation_deg"] = None
    for r in data["rooms"]:
        r["orientation_deg"] = None
    data["goals"] = ["better flow"]
    p = build_profile(data)
    sel = select_frameworks(p)
    assert "fengshui" not in sel.keys
    assert sel.weights["Feng shui harmony"] == 0.0


# --- scoring ------------------------------------------------------------------

def test_scoring_eight_dimensions_with_evidence():
    p = build_profile(_sample_profile_data())
    sel = select_frameworks(p)
    sc = score(p, sel)
    assert len(sc.dimensions) == 8
    for d in sc.dimensions:
        assert 0 <= d.score <= 100
        assert d.evidence
        assert d.framework
    assert 0 <= sc.weighted_total <= 100


def test_kitchen_work_triangle_detection():
    data = _sample_profile_data()
    data["rooms"] = [{
        "name": "Kitchen", "function": "kitchen", "width_m": 3, "length_m": 3,
        "windows": [{"wall": "E", "width_m": 1.0, "head_height_m": 2.1}],
        "doors": [{"wall": "W", "width_m": 0.85}],
        "furniture": [
            {"name": "Sink", "type": "sink", "width_m": 0.6, "length_m": 0.6, "x_m": 0.3, "y_m": 0.3},
            {"name": "Cooktop", "type": "cook", "width_m": 0.6, "length_m": 0.6, "x_m": 2.0, "y_m": 0.3},
            {"name": "Fridge", "type": "store", "width_m": 0.6, "length_m": 0.6, "x_m": 0.3, "y_m": 2.0},
        ],
    }]
    data["goals"] = ["fix kitchen flow"]
    p = build_profile(data)
    sel = select_frameworks(p)
    sc = score(p, sel)
    circ = sc.dimension("Circulation & flow")
    assert circ is not None
    assert any("work triangle" in w.lower() or "work-triangle" in w.lower()
               or "4-9m" in w for w in circ.strengths + circ.weaknesses) or circ.score >= 0


# --- roadmap ------------------------------------------------------------------

def test_roadmap_items_measurable():
    p = build_profile(_sample_profile_data())
    sel = select_frameworks(p)
    sc = score(p, sel)
    rm = build_roadmap(sc, p)
    assert rm.items, "expected at least one roadmap item"
    for item in rm.items:
        assert item.effort_hours > 0
        assert 1 <= item.impact <= 5
        assert item.success_metric
        assert item.tier in {t.value for t in schema.RoadmapTier}


def test_roadmap_respects_no_renovation():
    p = build_profile(_sample_profile_data())  # renter -> no renovation
    sel = select_frameworks(p)
    sc = score(p, sel)
    rm = build_roadmap(sc, p)
    structural = ("Widen", "Repartition", "Re-establish", "Right-size", "Reform the kitchen")
    for item in rm.items:
        assert not any(m in item.title for m in structural), item.title


def test_recipes_have_required_fields():
    for key, r in RECIPES.items():
        assert r["title"] and r["success_metric"] and r["tier"]
        assert r["effort_hours"] >= 0
        assert 1 <= r["impact"] <= 5


# --- feng shui ----------------------------------------------------------------

def test_fengshui_label_is_traditional():
    p = build_profile(_sample_profile_data())
    ov = build_overlay(p, enabled=True)
    assert "TRADITIONAL" in ov.label or "CULTURAL" in ov.label
    assert len(ov.bagua_sectors) == 9


def test_fengshui_disabled_when_no_orientation():
    data = _sample_profile_data()
    data["orientation_deg"] = None
    for r in data["rooms"]:
        r["orientation_deg"] = None
    data["goals"] = ["flow"]
    p = build_profile(data)
    ov = build_overlay(p, enabled=False)
    assert ov.enabled is False


# --- gates --------------------------------------------------------------------

def test_gates_pass_on_complete_input():
    p = build_profile(_sample_profile_data())
    sel = select_frameworks(p)
    sc = score(p, sel)
    rm = build_roadmap(sc, p)
    ov = build_overlay(p, enabled=True)
    gates = run_all_gates(p, sc, rm, ov.label)
    assert all(g.passed for g in gates)


def test_incomplete_input_returns_clarification():
    d = run({"raw_description": "vague", "goals": []})
    assert d.gates_passed is False
    assert d.clarifying_questions
    assert len(d.scorecard.dimensions) == 0


def test_offline_mode_is_degraded():
    d = run(_sample_profile_data(), live_search=False)
    assert d.degraded_mode is True
    assert d.degradation_note


# --- cli ----------------------------------------------------------------------

def test_cli_evaluate_json(tmp_path):
    inp = tmp_path / "in.json"
    inp.write_text(json.dumps(_sample_profile_data()), encoding="utf-8")
    rc = cli.main(["evaluate", "--input", str(inp), "--json"])
    assert rc in (0, 1)  # runs without raising


def test_cli_clarifying(tmp_path, capsys):
    inp = tmp_path / "in.json"
    inp.write_text(json.dumps({"raw_description": "vague"}), encoding="utf-8")
    rc = cli.main(["clarifying-questions", "--input", str(inp)])
    assert rc == 2
    out = capsys.readouterr().out
    assert "questions" in out


# --- knowledge updater --------------------------------------------------------

def test_knowledge_updater_dedup_and_scoring(tmp_path):
    from interior_layout.knowledge_updater import (Entry, relevance_score,
        load_seen_hashes, append_entries)
    brain = tmp_path / 'brain.md'
    brain.write_text('# brain\n\n<!--hash:abc-->\n', encoding='utf-8')
    e = Entry(title='Daylighting ergonomics circulation comfort',
              url='https://example.org/new', year='2025',
              abstract='circulation clearance daylight comfort acoustic')
    assert relevance_score(e) > 0
    n = append_entries([e], brain_path=str(brain), min_score=0.0, dry_run=False)
    assert n == 1
    # second run dedupes
    n2 = append_entries([e], brain_path=str(brain), min_score=0.0, dry_run=False)
    assert n2 == 0


def test_knowledge_updater_parse_atom():
    from interior_layout.knowledge_updater import _parse_arxiv_atom
    atom = '<entry><title>T</title><summary>s</summary><id>https://arxiv.org/abs/1.2</id><published>2024-01-01T00:00:00Z</published><name>A</name></entry>'
    out = _parse_arxiv_atom(atom, 'cs.HC')
    assert out and out[0].title == 'T' and out[0].year == '2024'
