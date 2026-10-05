"""
Runs each screen with Streamlit's test runner, which executes the page and
presses its buttons without a browser.
"""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from engine import format_formula

APP = str(Path(__file__).parent.parent / "app.py")

# Screen file → the title it should show.
SCREENS = {
    "ui/home.py": "The Missing Premise",
    "ui/case_files.py": "Case files",
    "ui/custom_case.py": "Custom case",
    "ui/truth_table_lab.py": "Truth table lab",
}


def open_screen(screen: str) -> AppTest:
    app = AppTest.from_file(APP, default_timeout=30).run()
    return app.switch_page(screen).run()


def messages(elements) -> list[str]:
    return [element.value for element in elements]


def page_html(app: AppTest) -> str:
    """Everything the screen drew with st.markdown, which includes our own HTML."""
    return "\n".join(messages(app.markdown))


def board(app: AppTest, key: str) -> list[str]:
    """The formulas on the deduction board of a game, as text."""
    return [format_formula(line.formula) for line in app.session_state["games"][key].lines]


def take_step(app: AppTest, key: str, rule: str, lines: list[int], new_line: str) -> AppTest:
    """Fills in the step builder of a game and presses "Check this step"."""
    app.button_group(key=f"{key}_step_rule").set_value(rule)
    app.button_group(key=f"{key}_step_lines").set_value(lines)
    app.text_input(key=f"{key}_step_new_line").set_value(new_line)
    return app.button(key=f"{key}_check").click().run()


@pytest.mark.parametrize("screen", SCREENS)
def test_screen_runs_without_an_error(screen):
    app = open_screen(screen)

    assert not app.exception
    assert app.title[0].value == SCREENS[screen]


def test_every_screen_shows_the_rank_badge():
    app = open_screen("ui/home.py")
    assert "Rookie" in page_html(app)
    assert "0/5 cases" in page_html(app)


# ---------------------------------------------------------- truth table lab


def test_lab_shows_the_table_and_verdict_for_a_typed_formula():
    app = open_screen("ui/truth_table_lab.py")

    app.text_input(key="lab_formula").input("(P -> Q) & P -> Q").run()

    assert not app.exception
    assert messages(app.success) == ["Tautology: true in all 4 rows."]
    html = page_html(app)
    for heading in ["P", "Q", "P → Q", "(P → Q) ∧ P", "(P → Q) ∧ P → Q"]:
        assert f"<th>{heading}</th>" in html
    # Row 2 is P true, Q false: the implication is false there.
    assert "<td>2</td><td>T</td><td>F</td><td>F</td><td>F</td><td>T</td>" in html


def test_lab_points_at_the_mistake_in_a_malformed_formula():
    app = open_screen("ui/truth_table_lab.py")

    app.text_input(key="lab_formula").input("P & (Q").run()

    assert not app.exception
    assert messages(app.error) == ["This bracket is never closed."]
    assert app.code[0].value == "P & (Q\n    ^"
    assert "mp-table" not in page_html(app)


def test_lab_rejects_more_atoms_than_a_table_can_hold():
    app = open_screen("ui/truth_table_lab.py")

    app.text_input(key="lab_formula").input("A & B & C & D & E & F & G & H & I").run()

    assert not app.exception
    assert "The limit is 8 atoms." in app.error[0].value


def test_lab_keys_type_into_the_formula_box():
    app = open_screen("ui/truth_table_lab.py")
    app.text_input(key="lab_formula").input("P").run()
    keys = {button.label: button.key for button in app.button}

    app.button(key=keys["∧"]).click().run()
    app.button(key=keys["Q"]).click().run()
    assert app.text_input(key="lab_formula").value == "P∧Q"

    app.button(key=keys["⌫"]).click().run()
    assert app.text_input(key="lab_formula").value == "P∧"


def test_lab_compares_two_formulas():
    app = open_screen("ui/truth_table_lab.py")
    app.text_input(key="lab_formula").input("P -> Q").run()

    app.text_input(key="lab_compare").input("~Q -> ~P").run()
    assert any(message.startswith("Equivalent") for message in messages(app.success))

    app.text_input(key="lab_compare").input("Q -> P").run()
    assert "Not equivalent: they differ on row 2, 3." in messages(app.error)
    assert '<tr class="counter"><td>2</td>' in page_html(app)


# -------------------------------------------------------------- custom case


def type_custom_case(premises: str, conclusion: str, clues: str = "") -> AppTest:
    app = open_screen("ui/custom_case.py")
    app.text_area(key="custom_premises").input(premises)
    app.text_area(key="custom_clues").input(clues)
    app.text_input(key="custom_conclusion").input(conclusion)
    return app.run()


def test_custom_case_gives_a_verdict_a_table_and_a_resolution_proof():
    app = type_custom_case("P -> Q\nP", "Q")

    assert not app.exception
    assert any(message.startswith("Valid.") for message in messages(app.success))
    assert any("empty clause was derived" in message for message in messages(app.success))
    assert [heading.value for heading in app.subheader][:3] == ["Verdict", "Truth table", "Resolution proof"]
    # Only the first row makes both premises true, so it is the one critical row.
    assert '<tr class="critical"><td>1</td>' in page_html(app)


def test_custom_case_marks_the_counterexample_rows():
    app = type_custom_case("P -> Q\nQ", "P")

    assert any(message.startswith("Invalid.") for message in messages(app.error))
    # Row 3 is P false, Q true: both premises true, the conclusion false.
    assert '<tr class="counter"><td>3</td><td>F</td><td>T</td>' in page_html(app)


def test_custom_case_finds_the_missing_premise_among_the_typed_clues():
    app = type_custom_case("P -> Q\nQ -> R", "R", clues="~Q\nP")

    assert any(message.startswith("Invalid.") for message in messages(app.error))
    html = page_html(app)
    assert "<td>¬Q</td><td>Does not close the gap</td>" in html
    assert "<td>P</td><td>Missing premise: with it, the conclusion follows</td>" in html


@pytest.mark.parametrize(
    "premises, conclusion, expected",
    [
        ("", "P | ~P", "Valid with no premises"),                # no premises
        ("P\n~P", "Q", "Valid, but only vacuously"),             # contradictory premises
        ("P ->", "Q", "The formula stops too early"),            # malformed premise
        ("P", "Q #", "'#' cannot be used in a formula."),        # malformed conclusion
        ("A & B & C & D & E & F & G & H & I", "A", "The limit is 8 atoms."),
    ],
)
def test_custom_case_edge_cases(premises, conclusion, expected):
    app = type_custom_case(premises, conclusion)

    assert not app.exception
    shown = messages(app.success) + messages(app.warning) + messages(app.error)
    assert any(expected in message for message in shown)


def test_custom_case_can_be_played_and_is_dropped_when_the_formulas_change():
    app = type_custom_case("P -> Q\nQ -> R", "R", clues="P")
    app.button(key="custom_play").click().run()

    app.button(key="custom_clue_clue 1").click().run()
    take_step(app, "custom", "modus_ponens", [1, 3], "Q")
    take_step(app, "custom", "modus_ponens", [2, 4], "R")

    assert not app.exception
    assert "Case solved by direct proof." in messages(app.success)

    app.text_input(key="custom_conclusion").input("Q").run()
    assert not app.exception
    assert "custom" not in app.session_state["games"]


# --------------------------------------------------------------- case files


def open_buttons(app: AppTest) -> list[str]:
    return [button.key for button in app.button if not button.disabled]


def test_only_the_first_case_is_open_at_the_start():
    app = open_screen("ui/case_files.py")
    assert len(app.button) == 5
    assert open_buttons(app) == ["case-01"]

    app.toggle(key="unlock_all").set_value(True).run()
    assert len(open_buttons(app)) == 5


def test_a_case_can_be_opened_and_closed():
    app = open_screen("ui/case_files.py")

    app.button(key="case-01").click().run()
    assert not app.exception
    assert app.title[0].value == "The Quiet Dog"
    assert len(app.chat_message) == 2        # the two witness statements
    # The letters are shown as a key, each meaning in quotes, not as facts.
    html = page_html(app)
    assert "Key to the letters" in html
    assert '<span class="mp-legend-meaning">“The dog barked”</span>' in html

    app.button(key="back").click().run()
    assert app.title[0].value == "Case files"


def test_a_case_played_to_the_end_scores_and_opens_the_next_one():
    app = open_screen("ui/case_files.py")
    app.button(key="case-01").click().run()
    assert any("A premise is missing" in message for message in messages(app.warning))
    assert '<div class="mp-step active"><span class="mp-step-num">1</span>' in page_html(app)
    assert "Inspector Modus" in page_html(app)
    assert '<div class="mp-portrait"></div>' in page_html(app)
    assert '<div class="mp-sidekick"></div>' in page_html(app)       # standing at the left

    # The hint in the empty box must not give away the answer to the first step.
    assert "~G" not in app.text_input(key="case-01_step_new_line").placeholder

    app.button(key="case-01_clue_neighbour").click().run()
    assert any("premises on the board are enough" in message for message in messages(app.success))
    assert '<div class="mp-step active"><span class="mp-step-num">2</span>' in page_html(app)

    take_step(app, "case-01", "modus_tollens", [1, 3], "~W")      # rejected
    assert app.session_state["games"]["case-01"].mistakes == 1
    assert board(app, "case-01") == ["W → G", "G → B", "¬B"]

    take_step(app, "case-01", "modus_tollens", [2, 3], "~G")
    assert "Valid step by Modus Tollens." in messages(app.success)
    # An accepted step empties the builder.
    assert app.button_group(key="case-01_step_lines").value == []
    assert app.text_input(key="case-01_step_new_line").value == ""

    take_step(app, "case-01", "modus_tollens", [1, 4], "~W")
    assert not app.exception
    assert "Case solved by direct proof." in messages(app.success)
    assert board(app, "case-01") == ["W → G", "G → B", "¬B", "¬G", "¬W"]
    assert app.session_state["scores"]["case-01"] == 90
    html = page_html(app)
    assert "Case closed" in html
    assert '<div class="mp-portrait smile"></div>' in html      # the detective is pleased
    assert '<div class="mp-sidekick happy"></div>' in html
    assert "Constable" not in html and "90 pts" in html      # 90 points is still a Rookie

    app.button(key="next_case").click().run()
    assert app.title[0].value == "The Locked Study"

    app.button(key="back").click().run()
    assert open_buttons(app) == ["case-01", "case-02"]


def test_the_on_screen_keys_type_the_new_line():
    app = open_screen("ui/case_files.py")
    app.button(key="case-01").click().run()
    app.button(key="case-01_clue_neighbour").click().run()
    keys = {button.label: button.key for button in app.button}

    app.button(key=keys["¬"]).click().run()
    app.button(key=keys["G"]).click().run()
    assert app.text_input(key="case-01_step_new_line").value == "¬G"

    app.button_group(key="case-01_step_lines").set_value([2, 3])
    app.button(key="case-01_check").click().run()
    assert board(app, "case-01")[-1] == "¬G"


def test_a_case_can_be_solved_by_contradiction():
    app = open_screen("ui/case_files.py")
    app.toggle(key="unlock_all").set_value(True).run()
    app.button(key="case-04").click().run()

    app.button(key="case-04_clue_passport").click().run()
    app.button(key="case-04_assume").click().run()
    take_step(app, "case-04", "disjunctive_syllogism", [1, 4], "N")
    take_step(app, "case-04", "modus_ponens", [2, 5], "T")

    assert not app.exception
    assert "Case solved by proof by contradiction." in messages(app.success)


def test_hint_and_start_again():
    app = open_screen("ui/case_files.py")
    app.button(key="case-01").click().run()

    app.button(key="case-01_hint").click().run()
    assert "A premise is missing. Look again at: Next door." in messages(app.info)

    app.button(key="case-01_clue_mud").click().run()
    assert len(board(app, "case-01")) == 3

    app.button(key="case-01_restart").click().run()
    assert not app.exception
    assert board(app, "case-01") == ["W → G", "G → B"]     # back to the witness statements
    assert "A premise is missing. Look again at: Next door." not in messages(app.info)
