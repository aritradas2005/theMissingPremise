import pytest

from engine import are_equivalent, check_argument, classify, parse


def formulas(*texts):
    return [parse(text) for text in texts]


@pytest.mark.parametrize(
    "text, kind",
    [
        ("P | ~P", "tautology"),
        ("(P -> Q) & P -> Q", "tautology"),
        ("P & ~P", "contradiction"),
        ("P -> Q", "contingency"),
        ("P", "contingency"),
    ],
)
def test_classify(text, kind):
    assert classify(parse(text)) == kind


@pytest.mark.parametrize(
    "left, right",
    [
        ("P -> Q", "~P | Q"),                 # implication as a disjunction
        ("P -> Q", "~Q -> ~P"),               # contrapositive
        ("~(P & Q)", "~P | ~Q"),              # De Morgan
        ("~(P | Q)", "~P & ~Q"),              # De Morgan
        ("P <-> Q", "(P -> Q) & (Q -> P)"),   # biconditional
        ("~~P", "P"),                         # double negation
        ("P", "P & (Q | ~Q)"),                # different atoms on each side
    ],
)
def test_equivalent_formulas(left, right):
    assert are_equivalent(parse(left), parse(right))


@pytest.mark.parametrize(
    "left, right",
    [
        ("P -> Q", "Q -> P"),    # converse
        ("P -> Q", "~P -> ~Q"),  # inverse
        ("P & Q", "P | Q"),
        ("P", "Q"),
    ],
)
def test_formulas_that_are_not_equivalent(left, right):
    assert not are_equivalent(parse(left), parse(right))


@pytest.mark.parametrize(
    "premises, conclusion",
    [
        (["P -> Q", "P"], "Q"),                # modus ponens
        (["P -> Q", "~Q"], "~P"),              # modus tollens
        (["P -> Q", "Q -> R"], "P -> R"),      # hypothetical syllogism
        (["P | Q", "~P"], "Q"),                # disjunctive syllogism
        (["P | Q", "~P | R"], "Q | R"),        # resolution
        (["W -> G", "G -> B", "~B"], "~W"),    # case-01 with its missing premise
    ],
)
def test_valid_arguments(premises, conclusion):
    result = check_argument(formulas(*premises), parse(conclusion))
    assert result.valid
    assert result.counterexamples == []


def test_affirming_the_consequent_is_invalid_with_its_counterexample_row():
    result = check_argument(formulas("P -> Q", "Q"), parse("P"))

    assert not result.valid
    assert len(result.counterexamples) == 1
    row = result.table.rows[result.counterexamples[0]]
    assert row.assignment == {"P": False, "Q": True}


def test_case_01_is_invalid_without_its_missing_premise():
    result = check_argument(formulas("W -> G", "G -> B"), parse("~W"))

    assert not result.valid
    row = result.table.rows[result.counterexamples[0]]
    assert row.assignment == {"B": True, "G": True, "W": True}


def test_table_columns_are_the_premises_then_the_conclusion():
    premises = formulas("P -> Q", "P")
    conclusion = parse("Q")
    result = check_argument(premises, conclusion)

    assert result.table.columns == premises + [conclusion]
    # Rows are TT, TF, FT, FF; both premises are true only on TT.
    assert result.critical_rows == [0]


def test_no_premises_is_valid_only_for_a_tautology():
    tautology = check_argument([], parse("P | ~P"))
    assert tautology.valid
    assert tautology.critical_rows == [0, 1]

    assert not check_argument([], parse("P")).valid


def test_contradictory_premises_have_no_critical_rows_and_are_valid():
    result = check_argument(formulas("P", "~P"), parse("Q"))

    assert result.critical_rows == []
    assert result.valid


def test_a_premise_entails_itself():
    assert check_argument(formulas("P"), parse("P")).valid
