import unittest
from app.rules import analyze_jd


class TestSmoke(unittest.TestCase):
    def test_positive_case(self):
        text = "Security clearance is required. US citizenship is required."
        r = analyze_jd(text)
        self.assertTrue(r["requires_clearance"])
        self.assertTrue(r["requires_citizenship"])
        self.assertIn("clearance", r["hits"])
        self.assertIn("citizenship", r["hits"])
        self.assertGreaterEqual(len(r["evidence"]), 1)

    def test_neutral_case(self):
        text = "We are hiring a software engineer to build APIs."
        r = analyze_jd(text)
        self.assertFalse(r["requires_clearance"])
        self.assertFalse(r["requires_citizenship"])
        self.assertEqual(r["hits"], [])
        self.assertEqual(r["evidence"], [])

    def test_negation_case(self):
        text = "No clearance required. No U.S. citizenship required."
        r = analyze_jd(text)
        self.assertFalse(r["requires_clearance"])
        self.assertFalse(r["requires_citizenship"])


if __name__ == "__main__":
    unittest.main()
