"""
The engine: all the mathematics, with no screen code.

The game and the screens import from here only, for example
    from engine import parse, check_argument
so engine files can be reorganised without touching them.
"""

from engine.cnf import MAX_CNF_STEPS, Clause, CnfConversion, CnfStep, to_clauses, to_cnf
from engine.evaluator import Assignment, evaluate, get_atoms, get_subformulas
from engine.formula import BINARY, SYMBOLS, And, Atom, Formula, Iff, Implies, Not, Or
from engine.missing_premise import CandidateResult, find_liars, is_consistent, try_candidates
from engine.parser import (
    ALIASES,
    MAX_NESTING,
    MAX_TOKENS,
    PRECEDENCE,
    ParseError,
    Token,
    format_formula,
    parse,
    tokenize,
)
from engine.resolution import (
    MAX_RESOLUTION_LINES,
    ResolutionLine,
    ResolutionProof,
    prove_by_resolution,
)
from engine.rules import RULES, Rule, StepResult, check_step, find_rule
from engine.truth_table import MAX_ATOMS, TruthTable, TruthTableRow, build_truth_table
from engine.validity import ArgumentResult, are_equivalent, check_argument, classify
