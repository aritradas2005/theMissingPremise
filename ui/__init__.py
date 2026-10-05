"""
The screens of the game. Nothing in this folder does any logic: the screens
ask the game/ and engine/ folders for answers and draw them.

The four screens (Streamlit runs a screen's file from top to bottom every time
the player does something):
    home.py             the title screen
    case_files.py       the cabinet of cases, and one case being played
    custom_case.py      type your own argument, analyse it and play it
    truth_table_lab.py  the truth table of any formula

The pieces the screens share:
    board.py            the deduction board: evidence, proof lines, verdict
    step_builder.py     choosing a rule, lines and a new line; hint and restart buttons
    session.py          remembering the games and scores between clicks
    formula_box.py      reading typed formulas; the on-screen keys
    tables.py           drawing tables, including the truth table
    resolution_view.py  drawing the automatic resolution proof
    board_pieces.py     small drawn pieces: stage tracker, stamps, stars, score sheet
    detective.py        the detective's speech bubble and standing figure
    look.py             loading the stylesheet and the pictures
    style.css           colours, fonts and spacing
    art/                the pictures
"""
