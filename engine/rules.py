"""
Rules of inference: checking one step of the player's proof.

The player picks a rule, picks one or two lines, and writes a new line.
check_step() says whether the new line really follows by that rule.

Every rule has its own small function below, named check_<rule>. Each of them
answers in the same way:
    - it returns None when the step is correct;
    - otherwise it returns a sentence saying what is wrong.

In the patterns, P, Q and R stand for any formulas, not only single letters.
"""

from dataclasses import dataclass

from engine.formula import And, Formula, Implies, Not, Or
from engine.parser import format_formula


@dataclass(frozen=True)
class Rule:
    id: str                    # used in case files, e.g. "modus_ponens"
    name: str                  # shown to the player
    premises: tuple[str, ...]  # the textbook pattern, shown in the rule picker
    conclusion: str


RULES = [
    Rule("modus_ponens", "Modus Ponens", ("P → Q", "P"), "Q"),
    Rule("modus_tollens", "Modus Tollens", ("P → Q", "¬Q"), "¬P"),
    Rule("hypothetical_syllogism", "Hypothetical Syllogism", ("P → Q", "Q → R"), "P → R"),
    Rule("disjunctive_syllogism", "Disjunctive Syllogism", ("P ∨ Q", "¬P"), "Q"),
    Rule("addition", "Addition", ("P",), "P ∨ Q"),
    Rule("simplification", "Simplification", ("P ∧ Q",), "P"),
    Rule("conjunction", "Conjunction", ("P", "Q"), "P ∧ Q"),
    Rule("resolution", "Resolution", ("P ∨ Q", "¬P ∨ R"), "Q ∨ R"),
    Rule("contraposition", "Contraposition", ("P → Q",), "¬Q → ¬P"),
]


@dataclass
class StepResult:
    valid: bool
    reason: str  # shown to the player


def find_rule(rule_id: str) -> Rule:
    """Returns the rule with this id. Raises ValueError if there is none."""
    for rule in RULES:
        if rule.id == rule_id:
            return rule
    raise ValueError(f"Unknown rule id: {rule_id}")


def check_step(rule_id: str, premises: list[Formula], conclusion: Formula) -> StepResult:
    """
    Checks one proof step: do these premises give this conclusion by this rule?

    rule_id     an id from RULES
    premises    the lines the player selected, in either order
    conclusion  the line the player wants to add

    Raises ValueError on an unknown rule_id.
    """
    rule = find_rule(rule_id)

    needed = len(rule.premises)
    if len(premises) != needed:
        word = "premise" if needed == 1 else "premises"
        return StepResult(False, f"{rule.name} needs {needed} {word}, but got {len(premises)}.")

    check = CHECKERS[rule_id]
    problem = check(premises, conclusion)
    if problem is None:
        return StepResult(True, f"Valid step by {rule.name}.")
    return StepResult(False, problem)


# ------------------------------------------------------------------ helpers


def both_orders(premises: list[Formula]) -> list[tuple[Formula, Formula]]:
    """The two premises as (first, second) and as (second, first), so the order does not matter."""
    first, second = premises
    return [(first, second), (second, first)]


def are_opposites(one: Formula, other: Formula) -> bool:
    """True when one formula is the other with ¬ in front, such as Q and ¬Q."""
    return one == Not(other) or other == Not(one)


def has_kind(premises: list[Formula], kind: type) -> bool:
    """True when at least one of the premises is of this kind, for example an implication."""
    for premise in premises:
        if isinstance(premise, kind):
            return True
    return False


# ---------------------------------------------------- one function per rule


def check_modus_ponens(premises: list[Formula], conclusion: Formula) -> str | None:
    """P → Q, P ⊢ Q"""
    if not has_kind(premises, Implies):
        return "Modus Ponens needs an implication (→)."

    for implication, other in both_orders(premises):
        if not isinstance(implication, Implies):
            continue
        if other == implication.left:
            if conclusion == implication.right:
                return None
            return f"Modus Ponens with this implication gives {format_formula(implication.right)}."
        # Two well-known mistakes get their own message.
        if other == implication.right:
            return "Affirming the consequent: P → Q and Q does not prove P."
        if other == Not(implication.left):
            return "Denying the antecedent: P → Q and ¬P does not prove ¬Q."

    return "Modus Ponens needs the left side of the implication as the second premise."


def check_modus_tollens(premises: list[Formula], conclusion: Formula) -> str | None:
    """P → Q, ¬Q ⊢ ¬P"""
    if not has_kind(premises, Implies):
        return "Modus Tollens needs an implication (→)."

    for implication, other in both_orders(premises):
        if not isinstance(implication, Implies):
            continue
        if are_opposites(other, implication.right):
            expected = Not(implication.left)
            if conclusion == expected:
                return None
            return f"Modus Tollens with this implication gives {format_formula(expected)}."
        if other == implication.right:
            return "Modus Tollens needs the negation of the right side."
        if other == Not(implication.left):
            return "Denying the antecedent: P → Q and ¬P does not prove ¬Q."

    return "Modus Tollens needs the negation of the right side of the implication."


def check_hypothetical_syllogism(premises: list[Formula], conclusion: Formula) -> str | None:
    """P → Q, Q → R ⊢ P → R"""
    first, second = premises
    if not (isinstance(first, Implies) and isinstance(second, Implies)):
        return "Hypothetical Syllogism needs two implications (→)."

    for start, end in both_orders(premises):
        if start.right == end.left:
            expected = Implies(start.left, end.right)
            if conclusion == expected:
                return None
            return f"Hypothetical Syllogism gives {format_formula(expected)}."

    return (
        "Hypothetical Syllogism requires the right side of one implication "
        "to match the left side of the other."
    )


def check_disjunctive_syllogism(premises: list[Formula], conclusion: Formula) -> str | None:
    """P ∨ Q, ¬P ⊢ Q   (and also P ∨ Q, ¬Q ⊢ P)"""
    if not has_kind(premises, Or):
        return "Disjunctive Syllogism needs a disjunction (∨)."

    for disjunction, other in both_orders(premises):
        if not isinstance(disjunction, Or):
            continue
        if are_opposites(other, disjunction.left):
            if conclusion == disjunction.right:
                return None
            return f"Disjunctive Syllogism gives {format_formula(disjunction.right)}."
        if are_opposites(other, disjunction.right):
            if conclusion == disjunction.left:
                return None
            return f"Disjunctive Syllogism gives {format_formula(disjunction.left)}."

    return "Disjunctive Syllogism needs the negation of one side of the disjunction."


def check_addition(premises: list[Formula], conclusion: Formula) -> str | None:
    """P ⊢ P ∨ Q, with anything at all as Q"""
    premise = premises[0]
    if not isinstance(conclusion, Or):
        return "Addition must produce a disjunction (∨)."
    if conclusion.left == premise or conclusion.right == premise:
        return None
    return "Addition requires one side of the disjunction to match the premise."


def check_simplification(premises: list[Formula], conclusion: Formula) -> str | None:
    """P ∧ Q ⊢ P   (and also P ∧ Q ⊢ Q)"""
    premise = premises[0]
    if not isinstance(premise, And):
        return "Simplification needs a conjunction (∧)."
    if conclusion == premise.left or conclusion == premise.right:
        return None
    return "Simplification must give one of the conjuncts."


def check_conjunction(premises: list[Formula], conclusion: Formula) -> str | None:
    """P, Q ⊢ P ∧ Q"""
    first, second = premises
    if not isinstance(conclusion, And):
        return "Conjunction must produce an AND (∧)."
    if conclusion == And(first, second) or conclusion == And(second, first):
        return None
    return "Conjunction must combine the two premises with ∧."


def check_resolution(premises: list[Formula], conclusion: Formula) -> str | None:
    """P ∨ Q, ¬P ∨ R ⊢ Q ∨ R: one side of each line cancels, the other two sides stay."""
    first, second = premises
    if not (isinstance(first, Or) and isinstance(second, Or)):
        return "Resolution needs two disjunctions (∨)."

    # Try each side of the first line against each side of the second.
    for cancelled_1, kept_1 in [(first.left, first.right), (first.right, first.left)]:
        for cancelled_2, kept_2 in [(second.left, second.right), (second.right, second.left)]:
            if are_opposites(cancelled_1, cancelled_2):
                if conclusion == Or(kept_1, kept_2) or conclusion == Or(kept_2, kept_1):
                    return None

    return "Resolution needs an atom and its negation to cancel across two disjunctions."


def check_contraposition(premises: list[Formula], conclusion: Formula) -> str | None:
    """P → Q ⊢ ¬Q → ¬P"""
    premise = premises[0]
    if not isinstance(premise, Implies):
        return "Contraposition needs an implication (→)."
    if conclusion == Implies(Not(premise.right), Not(premise.left)):
        return None
    return "Contraposition swaps and negates both sides: P → Q gives ¬Q → ¬P."


# Which function checks which rule.
CHECKERS = {
    "modus_ponens": check_modus_ponens,
    "modus_tollens": check_modus_tollens,
    "hypothetical_syllogism": check_hypothetical_syllogism,
    "disjunctive_syllogism": check_disjunctive_syllogism,
    "addition": check_addition,
    "simplification": check_simplification,
    "conjunction": check_conjunction,
    "resolution": check_resolution,
    "contraposition": check_contraposition,
}
