"""Tests of the documentation checks: published numbers and Markdown anchors."""
import copy
import pathlib
import sys
import unittest

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_links  # noqa: E402
import check_numbers  # noqa: E402


class Numbers(unittest.TestCase):
    def setUp(self):
        self.numbers = yaml.safe_load((ROOT / "docs" / "numbers.yaml").read_text(encoding="utf-8"))

    def test_the_repository_agrees_with_its_numbers(self):
        self.assertEqual(check_numbers.check(self.numbers), [])

    def test_a_changed_number_is_reported_everywhere_it_is_published(self):
        changed = copy.deepcopy(self.numbers)
        changed["funnel"]["sent"] += 1
        problems = check_numbers.check(changed)
        files = {p.split(":")[0] for p in problems}
        self.assertTrue({"README.md", "docs/metrics.md", "tools/poster.html"} <= files, problems)

    def test_spanish_and_english_formats(self):
        self.assertEqual(check_numbers.formatted("14800", "es"), "14.800")
        self.assertEqual(check_numbers.formatted("14800", "en"), "14,800")
        self.assertEqual(check_numbers.formatted("2026-10-13", "en"), "2026-10-13")


class Anchors(unittest.TestCase):
    def test_slugs_follow_github(self):
        self.assertEqual(check_links.slug("What it does — and what it does not"), "what-it-does--and-what-it-does-not")
        self.assertEqual(check_links.slug("Layer 1 · ATS mechanics"), "layer-1--ats-mechanics")
        self.assertEqual(check_links.slug("The `day` skill"), "the-day-skill")
        self.assertEqual(check_links.slug("Boundaries — what the agent never does"),
                         "boundaries--what-the-agent-never-does")


if __name__ == "__main__":
    unittest.main()
