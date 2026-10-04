"""
Automatic proof by resolution refutation: assume the conclusion is false
and derive a contradiction (the empty clause) from the premises.
"""

from dataclasses import dataclass

from engine.cnf import Clause
from engine.formula import Formula


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


def prove_by_resolution(premises: list[Formula], conclusion: Formula) -> ResolutionProof:
    """
    Tries to prove P1, ..., Pn ∴ C:
      1. convert every premise and ¬C to clauses
      2. resolve pairs of clauses until the empty clause appears (proved)
         or no new clause can be made (not proved)

    The answer must agree with check_argument() in validity.py.
    """
    raise NotImplementedError("prove_by_resolution")
