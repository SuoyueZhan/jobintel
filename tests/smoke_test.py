from app.rules import analyze_jd

def assert_true(cond: bool, msg: str):
    if not cond:
        raise AssertionError(msg)

def run():
    # 1) Positive case
    text1 = "Security clearance is required. US citizenship is required."
    r1 = analyze_jd(text1)
    assert_true(r1["requires_clearance"] is True, "Expected clearance=True for positive case")
    assert_true(r1["requires_citizenship"] is True, "Expected citizenship=True for positive case")
    assert_true("clearance" in r1["hits"], "Expected 'clearance' in hits")
    assert_true("citizenship" in r1["hits"], "Expected 'citizenship' in hits")
    assert_true(len(r1["evidence"]) >= 1, "Expected at least 1 evidence sentence")

    # 2) Neutral case
    text2 = "We are hiring a software engineer to build APIs."
    r2 = analyze_jd(text2)
    assert_true(r2["requires_clearance"] is False, "Expected clearance=False for neutral case")
    assert_true(r2["requires_citizenship"] is False, "Expected citizenship=False for neutral case")
    assert_true(r2["hits"] == [], "Expected hits=[] for neutral case")
    assert_true(r2["evidence"] == [], "Expected evidence=[] for neutral case")

    # 3) Basic negation (our negation is simple; treat this as a sanity check)
    text3 = "No clearance required. No U.S. citizenship required."
    r3 = analyze_jd(text3)
    # Depending on your current negation logic, these should be False.
    assert_true(r3["requires_clearance"] is False, "Expected clearance=False for negation case")
    assert_true(r3["requires_citizenship"] is False, "Expected citizenship=False for negation case")

    print("SMOKE TEST PASSED")

if __name__ == "__main__":
    run()
