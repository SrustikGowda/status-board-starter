import pytest

import slo
from budget import allowed_minutes, allowed_requests


def rows(*states):
    """One check per second. 'g' good, 's' slow (ok but 900 ms), 'e' error."""
    spec = {"g": (50, True), "s": (900, True), "e": (50, False)}
    return [(100.0 + i, *spec[s]) for i, s in enumerate(states)]


def test_good_needs_ok_and_fast():
    r = rows("g", "s", "e")
    assert [slo.is_good(x, 300) for x in r] == [True, False, False]


def test_sli_and_empty():
    assert slo.sli_percent(99, 100) == 99.0
    assert slo.sli_percent(0, 0) == 100.0


def test_budget_numbers():
    assert slo.budget_allowed(200, 99.0) == pytest.approx(2.0)
    assert slo.budget_remaining(2.0, 1) == pytest.approx(50.0)
    assert slo.budget_remaining(2.0, 5) == pytest.approx(-150.0)
    assert slo.budget_remaining(0, 0) == 100.0


def test_burn_rate_uses_only_the_window():
    r = rows(*"gggggggg" + "ee")
    assert slo.burn_rate(r, 300, 99.0, 2) == pytest.approx(100.0)
    assert slo.burn_rate(r, 300, 99.0, 10) == pytest.approx(20.0)
    assert slo.burn_rate([], 300, 99.0, 10) == 0.0


def test_verdict_edges():
    assert slo.verdict(26) == "BUDGET OK"
    assert slo.verdict(25) == "BUDGET LOW"
    assert slo.verdict(0.1) == "BUDGET LOW"
    assert slo.verdict(0) == "BUDGET EMPTY: pause risky changes"
    assert slo.verdict(-300) == "BUDGET EMPTY: pause risky changes"


def test_alert_edges():
    assert slo.alert(14.4) == "PAGE: burning 14x too fast"
    assert slo.alert(6) == "PAGE: burning 6x too fast"
    assert slo.alert(5.9) == "TICKET: budget will run out"
    assert slo.alert(1) == "TICKET: budget will run out"
    assert slo.alert(0.9) == "No alert"


def test_likely_cause_picks_last_change_before_first_bad():
    r = rows("g", "g", "g", "e")  # first bad at t=103
    changes = [(90.0, "old"), (102.0, "deploy v2"), (110.0, "later")]
    assert slo.likely_cause(r, changes, 300) == ("deploy v2", pytest.approx(1.0))
    assert slo.likely_cause(rows("g", "g"), changes, 300) is None


def test_overspent_is_a_multiple_of_the_allowance():
    assert slo.overspent(1.7, 50) == pytest.approx(29.4, abs=0.05)
    assert slo.overspent(2.0, 2) is None
    assert slo.overspent(0, 0) is None


def test_errors_are_counted_apart_from_slow_answers():
    r = rows("g", "s", "s", "e", "g")
    assert slo.count_errors_and_slow(r, 300) == (1, 2)
    assert slo.count_errors_and_slow(rows("g", "g"), 300) == (0, 0)


def test_load_files(tmp_path):
    c = tmp_path / "checks.csv"
    c.write_text("2.0,50,ok\n1.0,400,ok\n3.0,10,error\n")
    loaded = slo.load_checks(str(c))
    assert [r[0] for r in loaded] == [1.0, 2.0, 3.0]
    assert slo.count_bad(loaded, 300) == 2
    log = tmp_path / "changes.log"
    log.write_text("5.0,deploy v2, with a comma\n")
    assert slo.load_changes(str(log)) == [(5.0, "deploy v2, with a comma")]
    assert slo.load_changes(str(tmp_path / "missing.log")) == []


def test_budget_helper():
    assert allowed_minutes(99.9, 28) == pytest.approx(40.32)
    assert allowed_requests(99.9, 1_000_000) == pytest.approx(1000)
