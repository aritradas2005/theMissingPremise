"""
The detective, Inspector Modus: what he says, and where he stands.

He appears in two ways. On a narrow window he is a small round portrait beside
his speech bubble. On a wide window he stands at the left edge of the screen
and the portrait is hidden. Which of the two is shown is decided in
ui/style.css, from the width of the window.
"""

from html import escape

from ui.look import show_html

DETECTIVE_NAME = "Inspector Modus"


def detective_html(text: str, smiling: bool = False) -> str:
    """The detective's portrait beside a speech bubble holding the text."""
    portrait = "mp-portrait smile" if smiling else "mp-portrait"
    return (
        '<div class="mp-detective">'
        f'<div class="{portrait}"></div>'
        '<div class="mp-bubble">'
        f'<div class="mp-speaker">{DETECTIVE_NAME}</div>'
        f"<div>{escape(text)}</div>"
        "</div></div>"
    )


def detective_says(text: str, smiling: bool = False) -> None:
    """Shows the detective saying something."""
    show_html(detective_html(text, smiling))


def sidekick_html(happy: bool = False) -> str:
    """The detective standing at the left edge of the screen."""
    figure = "mp-sidekick happy" if happy else "mp-sidekick"
    return f'<div class="{figure}"></div>'


def show_sidekick(happy: bool = False) -> None:
    """Shows the standing detective. Call it once on a screen."""
    show_html(sidekick_html(happy))
