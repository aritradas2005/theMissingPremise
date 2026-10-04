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
    Rule("contraposition", "Contraposition", ("P → Q",), "¬Q → ¬P"),
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
    rule_map = {r.id: r for r in RULES}
    if rule_id not in rule_map:
        raise ValueError(f"Unknown rule id: {rule_id}")

    rule = rule_map[rule_id]
    expected_count = len(rule.premises)
    if len(premises) != expected_count:
        s = "premise" if expected_count == 1 else "premises"
        return StepResult(False, f"{rule.name} needs {expected_count} {s}, but got {len(premises)}.")

    from engine.formula import And, Implies, Not, Or
    from engine.parser import format_formula

    if rule_id == "modus_ponens":
        p1, p2 = premises
        orders = [(p1, p2), (p2, p1)]
        has_implication = any(isinstance(imp, Implies) for imp, _ in orders)
        if not has_implication:
            return StepResult(False, "Modus Ponens needs an implication (→).")

        for imp, other in orders:
            if isinstance(imp, Implies):
                if other == imp.left:
                    if conclusion == imp.right:
                        return StepResult(True, f"Valid step by {rule.name}.")
                    return StepResult(
                        False,
                        f"Modus Ponens with this implication gives {format_formula(imp.right)}.",
                    )
                if other == imp.right:
                    return StepResult(
                        False, "Affirming the consequent: P → Q and Q does not prove P."
                    )
                if other == Not(imp.left):
                    return StepResult(
                        False, "Denying the antecedent: P → Q and ¬P does not prove ¬Q."
                    )
        return StepResult(
            False,
            "Modus Ponens needs the left side of the implication as the second premise.",
        )

    if rule_id == "modus_tollens":
        p1, p2 = premises
        orders = [(p1, p2), (p2, p1)]
        has_implication = any(isinstance(imp, Implies) for imp, _ in orders)
        if not has_implication:
            return StepResult(False, "Modus Tollens needs an implication (→).")

        for imp, other in orders:
            if isinstance(imp, Implies):
                expected_neg = Not(imp.right)
                if other == expected_neg or (isinstance(imp.right, Not) and other == imp.right.operand):
                    expected_conclusion = Not(imp.left)
                    if conclusion == expected_conclusion:
                        return StepResult(True, f"Valid step by {rule.name}.")
                    return StepResult(
                        False,
                        f"Modus Tollens with this implication gives {format_formula(expected_conclusion)}.",
                    )
                if other == imp.right:
                    return StepResult(
                        False, "Modus Tollens needs the negation of the right side."
                    )
                if other == Not(imp.left):
                    return StepResult(
                        False, "Denying the antecedent: P → Q and ¬P does not prove ¬Q."
                    )
        return StepResult(
            False,
            "Modus Tollens needs the negation of the right side of the implication.",
        )

    if rule_id == "hypothetical_syllogism":
        p1, p2 = premises
        if not (isinstance(p1, Implies) and isinstance(p2, Implies)):
            return StepResult(False, "Hypothetical Syllogism needs two implications (→).")

        orders = [(p1, p2), (p2, p1)]
        for imp1, imp2 in orders:
            if imp1.right == imp2.left:
                expected = Implies(imp1.left, imp2.right)
                if conclusion == expected:
                    return StepResult(True, f"Valid step by {rule.name}.")
                return StepResult(
                    False, f"Hypothetical Syllogism gives {format_formula(expected)}."
                )
        return StepResult(
            False,
            "Hypothetical Syllogism requires the right side of one implication to match the left side of the other.",
        )

    if rule_id == "disjunctive_syllogism":
        p1, p2 = premises
        orders = [(p1, p2), (p2, p1)]
        has_or = any(isinstance(disj, Or) for disj, _ in orders)
        if not has_or:
            return StepResult(False, "Disjunctive Syllogism needs a disjunction (∨).")

        for disj, other in orders:
            if isinstance(disj, Or):
                # Check if other negates disj.left
                if other == Not(disj.left) or (isinstance(disj.left, Not) and other == disj.left.operand):
                    if conclusion == disj.right:
                        return StepResult(True, f"Valid step by {rule.name}.")
                    return StepResult(
                        False, f"Disjunctive Syllogism gives {format_formula(disj.right)}."
                    )
                # Check if other negates disj.right
                if other == Not(disj.right) or (isinstance(disj.right, Not) and other == disj.right.operand):
                    if conclusion == disj.left:
                        return StepResult(True, f"Valid step by {rule.name}.")
                    return StepResult(
                        False, f"Disjunctive Syllogism gives {format_formula(disj.left)}."
                    )
        return StepResult(
            False,
            "Disjunctive Syllogism needs the negation of one side of the disjunction.",
        )

    if rule_id == "addition":
        p1 = premises[0]
        if not isinstance(conclusion, Or):
            return StepResult(False, "Addition must produce a disjunction (∨).")
        if conclusion.left == p1 or conclusion.right == p1:
            return StepResult(True, f"Valid step by {rule.name}.")
        return StepResult(
            False, "Addition requires one side of the disjunction to match the premise."
        )

    if rule_id == "simplification":
        p1 = premises[0]
        if not isinstance(p1, And):
            return StepResult(False, "Simplification needs a conjunction (∧).")
        if conclusion == p1.left or conclusion == p1.right:
            return StepResult(True, f"Valid step by {rule.name}.")
        return StepResult(
            False, "Simplification must give one of the conjuncts."
        )

    if rule_id == "conjunction":
        p1, p2 = premises
        if not isinstance(conclusion, And):
            return StepResult(False, "Conjunction must produce an AND (∧).")
        if (conclusion.left == p1 and conclusion.right == p2) or (
            conclusion.left == p2 and conclusion.right == p1
        ):
            return StepResult(True, f"Valid step by {rule.name}.")
        return StepResult(
            False, "Conjunction must combine the two premises with ∧."
        )

    if rule_id == "resolution":
        p1, p2 = premises
        if not (isinstance(p1, Or) and isinstance(p2, Or)):
            return StepResult(False, "Resolution needs two disjunctions (∨).")

        for l1, r1 in [(p1.left, p1.right), (p1.right, p1.left)]:
            for l2, r2 in [(p2.left, p2.right), (p2.right, p2.left)]:
                if (
                    l1 == Not(l2)
                    or l2 == Not(l1)
                    or (isinstance(l1, Not) and l1.operand == l2)
                    or (isinstance(l2, Not) and l2.operand == l1)
                ):
                    if conclusion in (Or(r1, r2), Or(r2, r1)):
                        return StepResult(True, f"Valid step by {rule.name}.")
        return StepResult(
            False,
            "Resolution needs an atom and its negation to cancel across two disjunctions.",
        )

    if rule_id == "contraposition":
        p1 = premises[0]
        if not isinstance(p1, Implies):
            return StepResult(False, "Contraposition needs an implication (→).")
        expected = Implies(Not(p1.right), Not(p1.left))
        if conclusion == expected:
            return StepResult(True, f"Valid step by {rule.name}.")
        return StepResult(
            False, "Contraposition swaps and negates both sides: P → Q gives ¬Q → ¬P."
        )

    return StepResult(False, f"Unrecognized rule {rule_id}.")

