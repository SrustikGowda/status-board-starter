import detect


def checks(*values, start=100.0):
    """One check per half second. A number is milliseconds, None is no answer."""
    return [(start + i * 0.5, v) for i, v in enumerate(values)]


def test_band_is_median_plus_margin():
    middle, band, used, end = detect.learn(checks(*[2, 4, 3] * 30), margin=5)
    assert (middle, band, used, end) == (3, 8, 60, 60)


def test_learning_uses_only_first_60_answered_and_skips_none():
    data = checks(3, None, *[3] * 59, 900)  # the 60th answer is the 61st check
    middle, band, used, end = detect.learn(data, margin=5)
    assert (middle, used, end) == (3, 60, 61)


def test_flags_above_band_and_no_answer():
    data = checks(3, 8, 9, None, 700)
    assert detect.flag(data, band=8) == data[2:]  # 8 is not above 8


def test_grouping_by_gap():
    flags = [(10, 9), (11, None), (15.5, 9), (30, 9)]
    incidents = detect.group(flags, gap=5)
    assert [len(i) for i in incidents] == [3, 1]
    assert detect.group([], gap=5) == []


def test_likely_cause_is_latest_change_before():
    changes = [(10, "deploy version 2"), (50, "rollback to version 1")]
    assert detect.likely_cause(changes, 11.5) == ("deploy version 2", 1.5)
    assert detect.likely_cause(changes, 60)[0] == "rollback to version 1"
    assert detect.likely_cause(changes, 5) is None


def test_report_one_incident_blames_the_deploy():
    data = checks(*[3] * 60, *[3] * 10, *[600] * 20, None, *[3] * 10)
    # the deploy happened one second before the first slow check
    lines = detect.report(data, [(data[70][0] - 1, "deploy version 2")], 5, 5)
    text = "\n".join(lines)
    assert "1 incident (not 21 alerts)" in text
    assert "deploy version 2, 1 s before it started" in text
    assert max(len(line) for line in lines) <= 64


def test_wide_margin_leaves_only_the_no_answer():
    data = checks(*[3] * 60, *[600] * 20, None, *[3] * 10)
    changes = [(data[60][0] - 1, "deploy version 2"), (data[80][0] - 1, "rollback to version 1")]
    text = "\n".join(detect.report(data, changes, 1000, 5))
    assert "Outside the band: 1 check\n" in text
    assert "rollback to version 1" in text
