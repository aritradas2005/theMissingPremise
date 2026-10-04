"""
Rules of inference: checking that one step of the player's proof is a correct use of a rule.
"""

from dataclasses import dataclass

from engine.formula import Formula


@dataclass(frozen=True)
class Rule:
    id: str                    # used in case files, e.g. "modus_ponens"
    name: str                  # shown to the player
    premises: tuple[str, ...]  # the textbook pattern, shown in the rule picker
    conclusion: str


# The rules the player can use. P, Q and R stand for any formulas, not only single atoms.
RULES = [
    Rule("modus_ponens", "Modus Ponens", ("P → Q", "P"), "Q"),
    Rule("modus_tollens", "Modus Tollens", ("P → Q", "¬Q"), "¬P"),
    Rule("hypothetical_syllogism", "Hypothetical Syllogism", ("P → Q", "Q → R"), "P → R"),
    Rule("disjunctive_syllogism", "Disjunctive Syllogism", ("P ∨ Q", "¬P"), "Q"),
    Rule("addition", "Addition", ("P",), "P ∨ Q"),
    Rule("simplification", "Simplification", ("P ∧ Q",), "P"),
    Rule("conjunction", "Conjunction", ("P", "Q"), "P ∧ Q"),
    Rule("resolution", "Resolution", ("P ∨ Q", "¬P ∨ R"), "Q ∨ R"),
]


@dataclass
class StepResult:
    valid: bool
    reason: str  # shown to the player, e.g. "Modus Ponens needs an implication and its left side."


def check_step(rule_id: str, premises: list[Formula], conclusion: Formula) -> StepResult:
    """
    Checks one proof step: do these premises give this conclusion by this rule?

    rule_id     an id from RULES
    premises    the lines the player selected, in either order
    conclusion  the line the player wants to add

    Raises ValueError on an unknown rule_id.
    """
    raise NotImplementedError("check_step")
