"""
Draws the game's pictures and saves them in ui/art/: the three backgrounds and
the detective.

Run it again after changing it:   python tools/make_art.py

The pictures are SVG files. An SVG file is plain text that lists shapes
(rectangles, circles, lines), and the browser draws them at any size without
blurring. Each function below builds one picture by writing those shapes out as
text. The random numbers come from a fixed seed, so every run draws exactly the
same picture.
"""

import random
from pathlib import Path

ART_DIR = Path(__file__).parent.parent / "ui" / "art"

WIDTH = 1600
HEIGHT = 900

BRASS = "#e3c06a"


def rect(x, y, width, height, fill, opacity=1.0) -> str:
    """A rectangle: its top-left corner, its size and its colour."""
    return (
        f'<rect x="{x:.0f}" y="{y:.0f}" width="{width:.0f}" height="{height:.0f}" '
        f'fill="{fill}" opacity="{opacity:.2f}"/>'
    )


def svg(shapes: list[str]) -> str:
    """Wraps a list of shapes into a complete picture that fills the screen."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
        'preserveAspectRatio="xMidYMax slice">\n' + "\n".join(shapes) + "\n</svg>\n"
    )


# -------------------------------------------------------------------- city


def skyline(rng, widths, heights, colour, window_gap, lit_chance, window_opacity) -> list[str]:
    """
    A row of buildings across the picture, each a rectangle with a grid of
    windows, a few of them lit.
    """
    shapes = []
    x = -20
    while x < WIDTH:
        width = rng.randint(*widths)

        # Buildings are taller towards the edges, which leaves the middle of
        # the picture open for the title.
        edge = abs(x + width / 2 - WIDTH / 2) / (WIDTH / 2)   # 0 in the middle, 1 at the edge
        height = rng.randint(*heights) * (0.45 + 0.55 * edge)
        top = HEIGHT - height
        shapes.append(rect(x, top, width, height, colour))

        # Some roofs carry an aerial.
        if rng.random() < 0.3:
            aerial_x = x + rng.randint(8, width - 8)
            shapes.append(
                f'<line x1="{aerial_x}" y1="{top:.0f}" x2="{aerial_x}" y2="{top - rng.randint(18, 46):.0f}" '
                f'stroke="{colour}" stroke-width="2"/>'
            )

        gap_x, gap_y = window_gap
        for window_x in range(int(x) + 8, int(x + width) - 10, gap_x):
            for window_y in range(int(top) + 12, HEIGHT - 30, gap_y):
                if rng.random() < lit_chance:
                    shapes.append(
                        rect(window_x, window_y, gap_x * 0.45, gap_y * 0.5, BRASS,
                             window_opacity * rng.uniform(0.5, 1.0))
                    )

        x += width + rng.randint(0, 6)
    return shapes


def city() -> str:
    """The title screen: a city at night under a full moon, in the rain."""
    rng = random.Random(7)

    shapes = [
        "<defs>"
        '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#06070c"/>'
        '<stop offset="0.6" stop-color="#121420"/>'
        '<stop offset="1" stop-color="#2b2214"/>'
        "</linearGradient>"
        '<radialGradient id="glow">'
        '<stop offset="0" stop-color="#f3e6c0" stop-opacity="0.5"/>'
        '<stop offset="1" stop-color="#f3e6c0" stop-opacity="0"/>'
        "</radialGradient>"
        '<linearGradient id="fog" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#0f0e0c" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#0f0e0c" stop-opacity="0.9"/>'
        "</linearGradient>"
        # Rain is one short stroke repeated as a tilted pattern.
        '<pattern id="rain" width="46" height="90" patternUnits="userSpaceOnUse" patternTransform="rotate(14)">'
        '<line x1="10" y1="0" x2="10" y2="28" stroke="#cfd6e6" stroke-width="1" opacity="0.16"/>'
        '<line x1="33" y1="45" x2="33" y2="66" stroke="#cfd6e6" stroke-width="1" opacity="0.10"/>'
        "</pattern>"
        "</defs>",
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="url(#sky)"/>',
    ]

    for _ in range(90):  # stars
        shapes.append(
            f'<circle cx="{rng.uniform(0, WIDTH):.0f}" cy="{rng.uniform(0, 430):.0f}" '
            f'r="{rng.choice([0.8, 1.0, 1.5])}" fill="#f3e6c0" opacity="{rng.uniform(0.2, 0.7):.2f}"/>'
        )

    shapes.append('<circle cx="1290" cy="170" r="240" fill="url(#glow)"/>')   # the moon's halo
    shapes.append('<circle cx="1290" cy="170" r="60" fill="#efe3c2" opacity="0.92"/>')
    shapes.append('<circle cx="1272" cy="156" r="12" fill="#d9cba4" opacity="0.6"/>')   # craters
    shapes.append('<circle cx="1308" cy="188" r="8" fill="#d9cba4" opacity="0.6"/>')

    # Two rows of buildings: a pale one far away, a dark one close up.
    shapes += skyline(rng, (50, 110), (260, 420), "#171a27", (14, 18), 0.14, 0.30)
    shapes += skyline(rng, (90, 180), (330, 620), "#0a0a0f", (22, 30), 0.11, 0.70)

    shapes.append(f'<rect y="{HEIGHT - 200}" width="{WIDTH}" height="200" fill="url(#fog)"/>')
    shapes.append(f'<rect width="{WIDTH}" height="{HEIGHT}" fill="url(#rain)"/>')
    return svg(shapes)


# ------------------------------------------------------------------ office


def office() -> str:
    """The detective's office: light through the blinds, a desk, a lamp and a coat stand."""
    shapes = [
        "<defs>"
        '<linearGradient id="wall" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#1b1813"/>'
        '<stop offset="1" stop-color="#100e0b"/>'
        "</linearGradient>"
        '<radialGradient id="lamp">'
        '<stop offset="0" stop-color="#f1d58a" stop-opacity="0.55"/>'
        '<stop offset="1" stop-color="#f1d58a" stop-opacity="0"/>'
        "</radialGradient>"
        "</defs>",
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="url(#wall)"/>',
    ]

    # Light from the window falls across the wall in slanted bars.
    for bar in range(15):
        y = 40 + bar * 46
        shapes.append(
            f'<polygon points="380,{y + 170} 1600,{y} 1600,{y + 22} 380,{y + 192}" '
            f'fill="{BRASS}" opacity="0.045"/>'
        )

    # The window, top right: a frame, the night outside, and the slats of the blind.
    shapes.append(rect(1196, 60, 354, 492, "#090807"))
    shapes.append(rect(1210, 74, 326, 464, "#1a2334"))
    for slat in range(21):
        shapes.append(rect(1210, 76 + slat * 22, 326, 13, "#2b261d"))
    shapes.append('<line x1="1528" y1="74" x2="1528" y2="610" stroke="#3b3527" stroke-width="2"/>')
    shapes.append('<circle cx="1528" cy="614" r="5" fill="#3b3527"/>')

    # A framed certificate and a clock on the wall, top left.
    shapes.append('<rect x="96" y="120" width="150" height="110" fill="none" stroke="#3b3527" stroke-width="6"/>')
    shapes.append(rect(112, 136, 118, 78, "#221e17"))
    for line in range(4):
        shapes.append(rect(126, 152 + line * 14, 90 - line * 12, 4, "#3b3527"))
    shapes.append('<circle cx="340" cy="150" r="42" fill="#15130f" stroke="#3b3527" stroke-width="5"/>')
    shapes.append('<line x1="340" y1="150" x2="340" y2="122" stroke="#6d6349" stroke-width="3"/>')
    shapes.append('<line x1="340" y1="150" x2="360" y2="160" stroke="#6d6349" stroke-width="3"/>')

    # The coat stand by the door, far left: a pole, a hat and a hanging coat.
    shapes.append(rect(58, 330, 8, 470, "#0a0908"))
    shapes.append('<ellipse cx="62" cy="336" rx="46" ry="9" fill="#0a0908"/>')                    # hat brim
    shapes.append('<path d="M30 334 C30 300 48 292 62 292 C76 292 94 300 94 334 Z" fill="#0a0908"/>')  # hat crown
    shapes.append('<path d="M62 380 C104 392 120 470 112 640 L70 650 Z" fill="#0d0c0a"/>')        # coat

    # The desk along the bottom, with its lamp and a stack of case folders.
    shapes.append(rect(0, 792, WIDTH, 108, "#0a0908"))
    shapes.append(f'<line x1="0" y1="792" x2="{WIDTH}" y2="792" stroke="#3b3527" stroke-width="2"/>')

    shapes.append('<ellipse cx="250" cy="770" rx="230" ry="80" fill="url(#lamp)"/>')     # pool of light
    shapes.append('<ellipse cx="190" cy="790" rx="48" ry="9" fill="#050505"/>')          # lamp base
    shapes.append('<path d="M190 788 L176 680 L232 624" fill="none" stroke="#050505" stroke-width="8"/>')
    shapes.append('<path d="M196 600 L282 628 L262 690 L186 646 Z" fill="#14110b" stroke="#6d5622" stroke-width="3"/>')

    for folder, (colour, tilt) in enumerate([("#3a3020", -3), ("#463a26", 2), ("#54462e", -1)]):
        y = 770 - folder * 14
        shapes.append(
            f'<rect x="1290" y="{y}" width="210" height="16" fill="{colour}" '
            f'transform="rotate({tilt} 1395 {y + 8})"/>'
        )

    return svg(shapes)


# --------------------------------------------------------------------- lab


def lab() -> str:
    """The logic lab: squared paper covered in faint logic symbols."""
    rng = random.Random(23)

    shapes = [
        "<defs>"
        '<pattern id="small" width="40" height="40" patternUnits="userSpaceOnUse">'
        '<path d="M40 0 H0 V40" fill="none" stroke="#9fb9c4" stroke-width="1" opacity="0.06"/>'
        "</pattern>"
        '<pattern id="large" width="200" height="200" patternUnits="userSpaceOnUse">'
        '<path d="M200 0 H0 V200" fill="none" stroke="#9fb9c4" stroke-width="1.5" opacity="0.10"/>'
        "</pattern>"
        "</defs>",
        rect(0, 0, WIDTH, HEIGHT, "#0d1317"),
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="url(#small)"/>',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="url(#large)"/>',
    ]

    symbols = ["¬", "∧", "∨", "→", "↔", "⊢", "∴", "T", "F", "P", "Q", "R"]
    for _ in range(54):
        x = rng.uniform(20, WIDTH - 20)
        y = rng.uniform(40, HEIGHT - 20)
        shapes.append(
            f'<text x="{x:.0f}" y="{y:.0f}" font-family="Consolas, \'Courier New\', monospace" '
            f'font-size="{rng.randint(26, 70)}" fill="#9fb9c4" opacity="{rng.uniform(0.04, 0.10):.2f}" '
            f'transform="rotate({rng.randint(-20, 20)} {x:.0f} {y:.0f})">{rng.choice(symbols)}</text>'
        )

    # Two overlapping circles, and a magnifying glass in the corner.
    shapes.append('<circle cx="230" cy="660" r="120" fill="none" stroke="#9fb9c4" stroke-width="2" opacity="0.09"/>')
    shapes.append('<circle cx="350" cy="660" r="120" fill="none" stroke="#9fb9c4" stroke-width="2" opacity="0.09"/>')
    shapes.append('<circle cx="1360" cy="600" r="150" fill="none" stroke="#d0a94e" stroke-width="10" opacity="0.10"/>')
    shapes.append('<line x1="1468" y1="708" x2="1580" y2="820" stroke="#d0a94e" stroke-width="22" '
                  'stroke-linecap="round" opacity="0.10"/>')

    return svg(shapes)


# --------------------------------------------------------------- detective

# The detective's colours.
OUTLINE = "#3b2414"
COAT = "#c08b4f"
COAT_LIGHT = "#d3a063"
COAT_DARK = "#9a6a38"
HAT = "#b07a42"
HAT_BAND = "#4a2e1a"
SKIN = "#f5cfa6"
HAIR = "#5a3a22"
VEST = "#3a2a23"
SHIRT = "#f4efe6"
TIE = "#8c2f25"
TROUSERS = "#3d3d44"
SHOE = "#5a3219"
RIM = "#e0a93f"
GLASS = "#a9d9ec"


def shape(d: str, fill: str, width: float = 5) -> str:
    """A filled outline. d is the path: M moves, L draws a line, C and Q draw curves, Z closes."""
    return (
        f'<path d="{d}" fill="{fill}" stroke="{OUTLINE}" stroke-width="{width}" '
        'stroke-linejoin="round"/>'
    )


def stroke(d: str, colour: str, width: float) -> str:
    """A line with round ends and no fill."""
    return (
        f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{width}" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
    )


def sleeve(d: str) -> list[str]:
    """An arm: one thick line in the coat colour on top of a slightly thicker dark one."""
    return [stroke(d, OUTLINE, 48), stroke(d, COAT, 39)]


def oval(cx, cy, rx, ry, fill, width: float = 0, opacity: float = 1.0) -> str:
    """An oval: its centre and its two radii. width is the thickness of its outline, 0 for none."""
    outline = f' stroke="{OUTLINE}" stroke-width="{width}"' if width else ""
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" opacity="{opacity}"{outline}/>'


def face(mood: str) -> list[str]:
    """Eyebrows, eyes and mouth. mood is "calm" or "happy"."""
    if mood == "happy":
        return [
            stroke("M146 208 Q166 197 186 208", OUTLINE, 7),      # raised eyebrows
            stroke("M214 208 Q234 197 254 208", OUTLINE, 7),
            stroke("M148 246 Q166 222 184 246", OUTLINE, 6),      # eyes closed in a smile
            stroke("M216 246 Q234 222 252 246", OUTLINE, 6),
            shape("M176 272 Q200 308 226 272 Z", TIE, 4),          # open mouth
            '<path d="M185 275 L217 275 L213 283 L189 283 Z" fill="#ffffff"/>',
        ]
    return [
        stroke("M146 204 L186 213", OUTLINE, 8),                  # eyebrows drawn together
        stroke("M214 213 L254 204", OUTLINE, 8),
        oval(166, 241, 19, 23, "#ffffff", 3.5),                   # eyes
        oval(234, 241, 19, 23, "#ffffff", 3.5),
        oval(169, 244, 11, 16, HAIR),
        oval(231, 244, 11, 16, HAIR),
        oval(164, 236, 5, 5, "#ffffff"),
        oval(226, 236, 5, 5, "#ffffff"),
        stroke("M180 280 Q206 294 226 274", OUTLINE, 4.5),        # a one-sided smile
    ]


def detective_shapes(mood: str) -> list[str]:
    """Every shape of the detective, from the back of the picture to the front."""
    shapes = [oval(200, 586, 120, 12, "#000000", opacity=0.35)]   # shadow on the ground

    # Legs and shoes.
    shapes += [
        shape("M158 468 L197 468 L195 560 L160 560 Z", TROUSERS),
        shape("M203 468 L242 468 L240 560 L205 560 Z", TROUSERS),
        shape("M140 582 C140 566 152 554 168 554 L197 554 L197 582 Z", SHOE),
        shape("M203 554 L232 554 C248 554 260 566 260 582 L203 582 Z", SHOE),
    ]

    # The trench coat, with a darker fold down its left side.
    shapes += [
        shape("M170 290 C140 292 122 302 116 322 L100 500 Q200 522 300 500 "
              "L284 322 C278 302 260 292 230 290 Z", COAT),
        f'<path d="M118 326 L103 499 L140 506 L148 332 Z" fill="{COAT_DARK}" opacity="0.5"/>',
    ]

    # The coat hangs open: trousers, waistcoat, shirt and tie show in the gap.
    shapes += [
        shape("M178 300 L222 300 L246 506 L154 506 Z", TROUSERS, 4),
        shape("M168 298 L232 298 L240 412 L206 430 L200 424 L194 430 L160 412 Z", VEST, 4),
        oval(200, 348, 4.5, 4.5, RIM),
        oval(200, 376, 4.5, 4.5, RIM),
        oval(200, 404, 4.5, 4.5, RIM),
        shape("M182 294 L218 294 L200 336 Z", SHIRT, 3),
        shape("M193 298 L207 298 L205 310 L210 340 L200 358 L190 340 L195 310 Z", TIE, 3),
        shape("M148 298 L184 290 L198 332 L170 380 L142 334 Z", COAT_LIGHT, 4),   # lapels
        shape("M252 298 L216 290 L202 332 L230 380 L258 334 Z", COAT_LIGHT, 4),
    ]

    # Left arm with the hand in the coat pocket; right arm raised.
    shapes += sleeve("M126 324 L106 392 L136 430")
    shapes.append(stroke("M112 428 L154 438", OUTLINE, 4))          # the pockets
    shapes.append(stroke("M252 438 L288 430", OUTLINE, 4))
    shapes += sleeve("M274 324 L308 392 L322 326")

    # The magnifying glass in the raised hand.
    shapes += [
        stroke("M328 298 L340 268", OUTLINE, 15),
        stroke("M328 298 L340 268", "#7a4a22", 9),
        oval(324, 306, 17, 17, SKIN, 4),
        f'<circle cx="350" cy="228" r="38" fill="{GLASS}" stroke="{OUTLINE}" stroke-width="16"/>',
        f'<circle cx="350" cy="228" r="38" fill="none" stroke="{RIM}" stroke-width="9"/>',
        stroke("M330 216 A24 24 0 0 1 350 204", "#ffffff", 5),      # a glint on the glass
    ]

    # The head: ears, face, cheeks, hair.
    shapes += [
        oval(110, 226, 12, 16, SKIN, 4),
        oval(290, 226, 12, 16, SKIN, 4),
        shape("M112 204 C112 262 152 302 200 302 C248 302 288 262 288 204 "
              "C288 170 250 148 200 148 C150 148 112 170 112 204 Z", SKIN),
        oval(142, 266, 13, 8, "#f0a58a", opacity=0.5),
        oval(258, 266, 13, 8, "#f0a58a", opacity=0.5),
        shape("M112 184 C100 206 104 238 120 252 L134 216 L128 180 Z", HAIR, 4),
        shape("M288 184 C300 206 296 238 280 252 L266 216 L272 180 Z", HAIR, 4),
        shape("M118 172 L146 198 L160 182 L180 197 L196 181 L214 197 L232 181 "
              "L252 198 L266 182 L282 172 L282 150 L118 150 Z", HAIR, 4),
        stroke("M198 254 Q206 262 196 266", "#c98f5f", 3.5),        # nose
    ]
    shapes += face(mood)

    # The fedora: brim, crown, band and the dent in the top.
    shapes += [
        oval(200, 158, 150, 28, HAT, 5),
        shape("M118 152 C110 96 140 58 200 58 C260 58 290 96 282 152 Q200 180 118 152 Z", HAT),
        shape("M116 128 Q200 158 284 128 L282 152 Q200 180 118 152 Z", HAT_BAND, 4),
        stroke("M166 66 Q200 94 234 66", "#86592c", 5),
    ]
    return shapes


def detective(mood: str = "calm") -> str:
    """The detective standing, for the title screen and the side of the play screens."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 600">\n'
        + "\n".join(detective_shapes(mood))
        + "\n</svg>\n"
    )


def portrait(mood: str = "calm") -> str:
    """The detective's head in a round frame, for the speech bubble."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">\n'
        "<defs>"
        '<radialGradient id="back" cx="0.5" cy="0.35" r="0.75">'
        '<stop offset="0" stop-color="#3a3120"/><stop offset="1" stop-color="#0f0e0c"/>'
        "</radialGradient>"
        '<clipPath id="frame"><circle cx="100" cy="100" r="94"/></clipPath>'
        "</defs>\n"
        '<circle cx="100" cy="100" r="94" fill="url(#back)"/>\n'
        # The whole drawing, shrunk and moved so that the head fills the frame.
        '<g clip-path="url(#frame)"><g transform="translate(100 104) scale(0.58) translate(-200 -196)">\n'
        + "\n".join(detective_shapes(mood)[1:])     # everything but the ground shadow
        + "\n</g></g>\n"
        '<circle cx="100" cy="100" r="94" fill="none" stroke="#d0a94e" stroke-width="5"/>\n'
        "</svg>\n"
    )


def happy_detective() -> str:
    """The standing detective, smiling: shown when a case is closed."""
    return detective("happy")


def happy_portrait() -> str:
    """The round portrait, smiling."""
    return portrait("happy")


# -------------------------------------------------------------------- main

PICTURES = {
    "city": city,
    "office": office,
    "lab": lab,
    "detective": detective,
    "detective-happy": happy_detective,
    "portrait": portrait,
    "portrait-happy": happy_portrait,
}


def main() -> None:
    """Draws every picture and saves it in ui/art/."""
    ART_DIR.mkdir(exist_ok=True)
    for name, draw in PICTURES.items():
        path = ART_DIR / f"{name}.svg"
        path.write_text(draw(), encoding="utf-8", newline="\n")
        print(f"{path.name}: {path.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
