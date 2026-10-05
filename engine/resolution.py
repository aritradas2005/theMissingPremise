"""
Automatic proof by resolution refutation.

The idea: to prove that a conclusion follows from the premises, suppose it
does not. Write the premises and the NEGATED conclusion as clauses, then keep
combining clauses. If the empty clause appears, the supposition was
impossible, so the conclusion does follow.

Combining two clauses is called resolving them: when one holds a literal and
the other holds its opposite, those two cancel and everything else is kept.
    P ∨ Q   and   ¬P ∨ R   give   Q ∨ R
    P       and   ¬P       give   the empty clause, a contradiction
"""

from dataclasses import dataclass

from engine.cnf import Clause, is_always_true, to_clauses, to_cnf
from engine.formula import Formula, Not

# Every new clause is compared with every earlier one, so the work grows with
# the square of the number of clauses. A search that reaches this many is
# stopped with an error instead of running for minutes.
MAX_RESOLUTION_LINES = 500


@dataclass
class ResolutionLine:
    id: int                                 # line number, starting at 1
    clause: Clause
    source: str                             # "premise", "negated conclusion" or "resolvent"
    parents: tuple[int, int] | None = None  # for a resolvent: the ids of the two lines resolved
    on: str | None = None                   # for a resolvent: the atom that was cancelled


@dataclass
class ResolutionProof:
    proved: bool                 # True when the empty clause was derived
    lines: list[ResolutionLine]  # the clauses in the order they were added


def opposite_literal(literal: str) -> str:
    """The opposite of "P" is "¬P", and the opposite of "¬P" is "P"."""
    if literal.startswith("¬"):
        return literal[1:]
    return "¬" + literal


def resolve(first: Clause, second: Clause) -> list[tuple[Clause, str]]:
    """
    Every clause that can be made by cancelling a literal of the first clause
    against its opposite in the second. Each comes with the atom that was cancelled.
    """
    results = []
    for literal in sorted(first):
        opposite = opposite_literal(literal)
        if opposite in second:
            merged = (first - {literal}) | (second - {opposite})
            if not is_always_true(merged):
                atom = literal.lstrip("¬")
                results.append((merged, atom))
    return results


def add_starting_clauses(lines: list[ResolutionLine], formulas: list[Formula], source: str) -> None:
    """Converts formulas to clauses and adds each new clause as a numbered line."""
    for formula in formulas:
        for clause in to_clauses(to_cnf(formula).result):
            if not is_known(lines, clause):
                lines.append(ResolutionLine(len(lines) + 1, clause, source))


def is_known(lines: list[ResolutionLine], clause: Clause) -> bool:
    """True when this clause is already one of the lines."""
    for line in lines:
        if line.clause == clause:
            return True
    return False


def prove_by_resolution(premises: list[Formula], conclusion: Formula) -> ResolutionProof:
    """
    Tries to prove P1, ..., Pn ∴ C:
      1. convert every premise and ¬C to clauses
      2. resolve pairs of clauses until the empty clause appears (proved)
         or no new clause can be made (not proved)

    The answer agrees with check_argument() in validity.py.

    Raises ValueError if the search reaches MAX_RESOLUTION_LINES clauses, or if a
    formula is too large to convert to clauses.
    """
    empty_clause = frozenset()

    lines = []
    add_starting_clauses(lines, premises, "premise")
    add_starting_clauses(lines, [Not(conclusion)], "negated conclusion")
    if is_known(lines, empty_clause):
        return ResolutionProof(proved=True, lines=lines)

    # Take the lines in order and resolve each with every line before it.
    # New clauses are added to the end of the list, so they get their turn too.
    seen = {line.clause for line in lines}   # a set, for a quick "have we met this clause?"
    position = 0
    while position < len(lines):
        newer = lines[position]
        for older in lines[:position]:
            for clause, atom in resolve(newer.clause, older.clause):
                if clause in seen:
                    continue
                if len(lines) >= MAX_RESOLUTION_LINES:
                    raise ValueError(
                        f"The search was stopped after {MAX_RESOLUTION_LINES} clauses: "
                        "this argument is too large for a readable resolution proof."
                    )
                seen.add(clause)
                lines.append(
                    ResolutionLine(len(lines) + 1, clause, "resolvent", (older.id, newer.id), atom)
                )
                if clause == empty_clause:
                    return ResolutionProof(proved=True, lines=lines)
        position += 1

    return ResolutionProof(proved=False, lines=lines)
