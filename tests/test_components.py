"""
The functions in ui/components.py that build HTML. They only return strings,
so they are tested without running a screen.
"""

import xml.etree.ElementTree as ET

from engine import build_truth_table, check_argument, parse
from game.game_state import ProofLine
from tools.make_art import PICTURES
from ui.components import (
    ART_DIR,
    art_variables,
    clause_text,
    detective_html,
    html_table,
    line_kind,
    proof_html,
    score_html,
    stars_html,
    stepper_html,
    truth_table_cells,
    truth_table_html,
)


def test_truth_table_cells_number_the_rows_and_show_t_and_f():
    table = build_truth_table([parse("P -> Q")])

    headings, rows = truth_table_cells(table)

    assert headings == ["#", "P", "Q", "P → Q"]
    assert rows == [
        ["1", "T", "T", "T"],
        ["2", "T", "F", "F"],
        ["3", "F", "T", "T"],
        ["4", "F", "F", "T"],
    ]


def test_truth_table_cells_do_not_repeat_a_column():
    """An atom given as a formula, or the same formula twice, gets one column."""
    table = build_truth_table([parse("P"), parse("P & Q"), parse("P & Q")])

    headings, rows = truth_table_cells(table)

    assert headings == ["#", "P", "Q", "P ∧ Q"]
    assert all(len(row) == 4 for row in rows)


def test_truth_table_html_tints_critical_and_counterexample_rows():
    result = check_argument([parse("P -> Q"), parse("Q")], parse("P"))

    html = truth_table_html(result.table, result.critical_rows, result.counterexamples)

    # Rows 1 and 3 make both premises true; row 3 also makes the conclusion false.
    assert '<tr class="critical"><td>1</td>' in html
    assert '<tr class="counter"><td>3</td>' in html
    assert '<tr class=""><td>2</td>' in html


def test_html_table_escapes_its_text():
    html = html_table(["<b>"], [["<script>"]])

    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "<th>&lt;b&gt;</th>" in html


def test_stepper_marks_earlier_stages_done_and_the_current_one_active():
    html = stepper_html(2)

    assert '<div class="mp-step done"><span class="mp-step-num">1</span>Evidence</div>' in html
    assert '<div class="mp-step active"><span class="mp-step-num">2</span>Deduction</div>' in html
    assert '<div class="mp-step "><span class="mp-step-num">3</span>Verdict</div>' in html


def test_line_kind_follows_the_justification():
    assert line_kind("Statement (Gardener)") == "statement"
    assert line_kind("Clue (neighbour)") == "clue"
    assert line_kind("Assumption (for contradiction)") == "assumption"
    assert line_kind("Modus Tollens 2, 3") == "derived"


def test_proof_html_shows_number_formula_and_justification():
    lines = [
        ProofLine(1, parse("W -> G"), "Statement (Gardener)"),
        ProofLine(2, parse("~G"), "Modus Tollens 1, 3"),
    ]

    html = proof_html(lines)

    assert '<div class="mp-line statement"><span class="mp-num">1</span>' in html
    assert '<span class="mp-formula">W → G</span>' in html
    assert '<div class="mp-line derived"><span class="mp-num">2</span>' in html
    assert '<span class="mp-from">Modus Tollens 1, 3</span>' in html


def test_stars_html_lights_the_right_number():
    assert stars_html(3) == '<span class="mp-stars">★★★<span class="unlit"></span></span>'
    assert stars_html(1) == '<span class="mp-stars">★<span class="unlit">★★</span></span>'


def test_score_html_signs_the_points_and_ends_with_the_total():
    html = score_html([("Case solved", 100), ("Hints used: 1", -15)], 85)

    assert "<span>Case solved</span><span>+100</span>" in html
    assert "<span>Hints used: 1</span><span>-15</span>" in html
    assert '<div class="mp-score-row total"><span>Score</span><span>85</span></div>' in html


def test_clause_text():
    assert clause_text(frozenset({"Q", "¬P"})) == "¬P ∨ Q"
    assert clause_text(frozenset()).startswith("□")


# ----------------------------------------------------------------- pictures

PICTURE_NAMES = {
    "city", "office", "lab",
    "detective", "detective-happy", "portrait", "portrait-happy",
}


def test_every_picture_is_a_well_formed_svg():
    paths = list(ART_DIR.glob("*.svg"))

    assert {path.stem for path in paths} == PICTURE_NAMES
    for path in paths:
        root = ET.parse(path).getroot()      # raises if the file is not valid XML
        assert root.tag.endswith("svg")


def test_art_variables_give_style_css_one_variable_per_picture():
    css = art_variables()

    for name in PICTURE_NAMES:
        assert f'--mp-art-{name}: url("data:image/svg+xml;base64,' in css


def test_the_pictures_are_what_the_drawing_script_produces():
    """If tools/make_art.py is changed, it has to be run again."""
    for name, draw in PICTURES.items():
        assert (ART_DIR / f"{name}.svg").read_text(encoding="utf-8") == draw()


def test_detective_html_shows_the_name_the_words_and_the_mood():
    html = detective_html("Mind the <gap>.")

    assert "Inspector Modus" in html
    assert "Mind the &lt;gap&gt;." in html
    assert '<div class="mp-portrait"></div>' in html
    assert '<div class="mp-portrait smile"></div>' in detective_html("Case closed.", smiling=True)
