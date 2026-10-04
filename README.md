# The Missing Premise

A detective game where every case is an argument in propositional logic. Witness statements and clues are premises, the accusation is the conclusion, and the player has to find the premise that is missing and then prove the conclusion step by step with rules of inference.

ISE-2 project for Discrete Mathematics (7MA206), Track A (Gamified Application), Unit I: Logic & Proof Techniques.

> Status: skeleton. The screens, the case format and the function signatures are in place; the logic is not written yet.

## Team

| Roll no. | Name | Module |
| --- | --- | --- |
|  |  | Logic core: parser, evaluator, truth table, validity |
|  |  | Inference: rule checker, CNF, resolution, missing premise |
|  |  | Game and UI: screens, deduction board, scoring, cases |

## Set up

Needs Python 3.10 or newer. Install the two libraries once:

```bash
python -m pip install -r requirements.txt
```

## Run the game

```bash
python -m streamlit run app.py
```

The game opens in your browser at http://localhost:8501. The first time, Streamlit may ask for an email address; press Enter to skip.

## Run the tests

```bash
python -m pytest
```

## Writing formulas

| Connective | Symbol | You can also type |
| --- | --- | --- |
| not | ¬ | `~` `!` |
| and | ∧ | `&` `^` |
| or | ∨ | `\|` |
| implies | → | `->` `=>` |
| if and only if | ↔ | `<->` `<=>` |

Atom names start with a letter: `P`, `Q`, `Butler_Lied`. From tightest to loosest the connectives bind as ¬, ∧, ∨, →, ↔, and `P -> Q -> R` means `P -> (Q -> R)`.

## How the code is organised

```
app.py                page setup and the menu
engine/               the mathematics; no screen code
  formula.py            the formula tree
  parser.py             text to formula, formula to text
  evaluator.py          truth value of a formula under one assignment
  truth_table.py        all assignments
  validity.py           tautology, equivalence, valid argument
  rules.py              rules of inference and the step checker
  cnf.py                conjunctive normal form, step by step
  resolution.py         automatic proof by resolution
  missing_premise.py    consistency, missing premise, finding the liar
game/                 case files, the state of a case in play, scoring
ui/                   one file per screen, plus shared pieces
data/cases/           one JSON file per case, listed in index.json
tests/                one test file per module
docs/screenshots/     screenshots for the report
.streamlit/config.toml  colours and font
```

The screens call the game layer, the game layer calls the engine, and the engine knows nothing about either.

## Case files

A case is a JSON file in `data/cases/`, listed in `data/cases/index.json`. See `data/cases/case-01.json` for a complete example.

| Field | Meaning |
| --- | --- |
| `atoms` | each atom and what it means in English |
| `statements` | what the witnesses say, each with its formula |
| `clues` | facts found at the scene; some close the gap, some are distractions |
| `conclusion` | what the detective must prove |
| `rules` | the rules of inference the player may use |

The file does not say which clue is the missing premise. The engine works that out, so a case typed in on the custom case screen plays the same way as a written one.
