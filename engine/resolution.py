from dataclasses import dataclass

from engine.cnf import Clause, to_clauses, to_cnf
from engine.formula import Formula, Not


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
    lines: list[ResolutionLine] = []
    known_clauses: dict[Clause, int] = {}
    next_id = 1

    # 1. Convert premises to clauses
    for prem in premises:
        cnf_f = to_cnf(prem).result
        for c in to_clauses(cnf_f):
            if c not in known_clauses:
                line = ResolutionLine(id=next_id, clause=c, source="premise")
                lines.append(line)
                known_clauses[c] = next_id
                next_id += 1

    # 2. Convert negated conclusion to clauses
    neg_c = Not(conclusion)
    cnf_neg = to_cnf(neg_c).result
    for c in to_clauses(cnf_neg):
        if c not in known_clauses:
            line = ResolutionLine(id=next_id, clause=c, source="negated conclusion")
            lines.append(line)
            known_clauses[c] = next_id
            next_id += 1

    # Check if empty clause already present
    empty = frozenset()
    if empty in known_clauses:
        return ResolutionProof(proved=True, lines=lines)

    # 3. Resolution loop
    i = 0
    while i < len(lines):
        line1 = lines[i]
        c1 = line1.clause

        for j in range(i):
            line2 = lines[j]
            c2 = line2.clause

            # Find literals in c1 that can resolve with c2
            for lit1 in c1:
                if lit1.startswith("¬"):
                    atom = lit1[1:]
                    comp = atom
                else:
                    atom = lit1
                    comp = f"¬{atom}"

                if comp in c2:
                    resolvent = (c1 - {lit1}) | (c2 - {comp})

                    # Discard tautological resolvent containing X and ¬X
                    has_tautology = any(
                        f"¬{lit}" in resolvent
                        for lit in resolvent
                        if not lit.startswith("¬")
                    )
                    if has_tautology:
                        continue

                    if resolvent not in known_clauses:
                        line = ResolutionLine(
                            id=next_id,
                            clause=resolvent,
                            source="resolvent",
                            parents=(line2.id, line1.id),
                            on=atom,
                        )
                        lines.append(line)
                        known_clauses[resolvent] = next_id
                        next_id += 1

                        if resolvent == empty:
                            return ResolutionProof(proved=True, lines=lines)
        i += 1

    return ResolutionProof(proved=False, lines=lines)

