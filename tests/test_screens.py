"""
Runs each screen with Streamlit's test runner, which executes the page without a browser.
"""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

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


@pytest.mark.parametrize("screen", SCREENS)
def test_screen_runs_without_an_error(screen):
    app = open_screen(screen)

    assert not app.exception
    assert app.title[0].value == SCREENS[screen]


def test_a_case_can_be_opened_and_closed():
    app = open_screen("ui/case_files.py")

    app.button(key="case-01").click().run()
    assert not app.exception
    assert app.title[0].value == "The Quiet Dog"

    app.button[0].click().run()
    assert app.title[0].value == "Case files"
