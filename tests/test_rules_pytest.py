import pytest

from app.rules import analyze_jd


# -----------------------------
# Core regression tests
# -----------------------------
#
# Why these exist:
# - They lock in the behavior you want for the key business rules.
# - They catch subtle regressions (negation scope, abbreviation splitting, etc.)
# - They are cheap to expand: just add more cases to the table.
# -----------------------------


@pytest.mark.parametrize(
    "text, exp_clearance, exp_citizenship",
    [
        # --- Positive cases (should be True) ---
        (
            "Security clearance is required. US citizenship is required.",
            True,
            True,
        ),
        (
            "Must have an active TS/SCI clearance.",
            True,
            False,
        ),
        (
            "Must be a U.S. citizen.",
            False,
            True,
        ),
        (
            "U.S. citizenship required.",
            False,
            True,
        ),
        # --- Neutral cases (should be False) ---
        (
            "We are hiring a software engineer to build APIs.",
            False,
            False,
        ),
        (
            "This role involves backend development and on-call rotations.",
            False,
            False,
        ),
        # --- Negation cases (should be False) ---
        (
            "No clearance required. No U.S. citizenship required.",
            False,
            False,
        ),
        (
            "Clearance is not required. Citizenship not required.",
            False,
            False,
        ),
        # --- Abbreviation regression (previously broke sentence splitting) ---
        # Why: protect 'U.S.' from being split into 'No U.S.' and 'citizenship required.'
        (
            "No U.S. citizenship required.",
            False,
            False,
        ),
    ],
)
def test_analyze_jd_flags(text, exp_clearance, exp_citizenship):
    r = analyze_jd(text)
    assert r["requires_clearance"] == exp_clearance
    assert r["requires_citizenship"] == exp_citizenship


def test_hits_and_evidence_consistency_positive():
    """
    Why:
    - When a flag is True, we expect the label in 'hits'
    - Evidence should be non-empty and contain original JD sentences
    - This checks the *contract* of your analyzer, not exact evidence content
    """
    text = "Security clearance is required. US citizenship is required."
    r = analyze_jd(text)

    assert r["requires_clearance"] is True
    assert r["requires_citizenship"] is True

    assert "clearance" in r["hits"]
    assert "citizenship" in r["hits"]

    assert isinstance(r["evidence"], list)
    assert len(r["evidence"]) >= 1


def test_hits_and_evidence_consistency_negative():
    """
    Why:
    - If both flags are False, 'hits' should be empty
    - Evidence should be empty (or at least not contain false-positive sentences)
    - This prevents silent drift where evidence accumulates even when no hit exists
    """
    text = "We are hiring a software engineer to build APIs."
    r = analyze_jd(text)

    assert r["requires_clearance"] is False
    assert r["requires_citizenship"] is False
    assert r["hits"] == []
    assert r["evidence"] == []


@pytest.mark.parametrize(
    "text",
    [
        "",
        "   ",
        None,
    ],
)
def test_empty_input_is_safe(text):
    """
    Why:
    - Real systems often pass empty strings or None
    - Analyzer should not crash; should return stable empty result
    """
    r = analyze_jd(text)
    assert r["requires_clearance"] is False
    assert r["requires_citizenship"] is False
    assert r["hits"] == []
    assert r["evidence"] == []
