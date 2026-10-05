"""
The look of the game: loading the stylesheet and the pictures, and two tiny
helpers that every screen uses.

Streamlit's own widgets (buttons, text boxes) are used for everything the
player presses or types in. Things that are only displayed, such as proof
lines, stamps and stars, are written as small pieces of HTML so that
ui/style.css can make them look like part of a game.
"""

import base64
from html import escape
from pathlib import Path

import streamlit as st

STYLE_FILE = Path(__file__).parent / "style.css"
ART_DIR = Path(__file__).parent / "art"


def picture_variables() -> str:
    """
    Makes every picture in ui/art available to style.css under a name:
    city.svg becomes --mp-art-city, office.svg becomes --mp-art-office, and so on.

    Each picture is written into the page itself as text (that is what base64
    does), so the browser does not have to fetch separate picture files.
    """
    lines = ""
    for path in sorted(ART_DIR.glob("*.svg")):
        as_text = base64.b64encode(path.read_bytes()).decode("ascii")
        lines += f'--mp-art-{path.stem}: url("data:image/svg+xml;base64,{as_text}");'
    return ":root {" + lines + "}"


def load_style() -> None:
    """Adds ui/style.css and the pictures to the page. Called once, from app.py."""
    css = STYLE_FILE.read_text(encoding="utf-8")
    st.html(f"<style>{css}{picture_variables()}</style>")


def set_scene(name: str) -> None:
    """Chooses the background picture of the current screen: "city", "office" or "lab"."""
    st.html(f"<style>:root {{ --mp-scene: var(--mp-art-{name}); }}</style>")


def show_html(html: str) -> None:
    """Puts a piece of HTML on the screen."""
    st.markdown(html, unsafe_allow_html=True)


def kicker(text: str) -> None:
    """The small label above a title, like the tab on a case folder."""
    # escape() turns characters such as < into harmless text. It is used on
    # every piece of text that comes from a case file or from the player.
    show_html(f'<div class="mp-kicker">{escape(text)}</div>')
