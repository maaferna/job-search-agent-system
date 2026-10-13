"""Tests of the reference implementations. Run from the repository root:

    python3 -m unittest discover -s tests -t .
"""
import copy
import datetime as dt
import json
import pathlib
import shutil
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "reference"))

import ats_coverage  # noqa: E402
import dated_rules  # noqa: E402
import gate  # noqa: E402
import mini_board  # noqa: E402
import pipeline_check  # noqa: E402
import probability  # noqa: E402

SCHEMA = json.loads(pipeline_check.SCHEMA.read_text(encoding="utf-8"))
ENTRIES = pipeline_check.load_entries(pipeline_check.EXAMPLE)
D = dt.date


def entry(**fields):
    base = {"id": "t-1", "employer": "Example Co.", "role": "Data Engineer", "state": "prospect"}
    base.update(fields)
    return base


class PipelineCheck(unittest.TestCase):
    def errors(self, e):
        return pipeline_check.validate(e, SCHEMA, e["id"])

    def test_example_data_is_valid(self):
        errors, _ = pipeline_check.check(pipeline_check.EXAMPLE)
        self.assertEqual(errors, [])

    def test_closed_vocabulary(self):
        self.assertTrue(any("not one of" in m for m in self.errors(entry(modality="remote-ish"))))

    def test_unknown_field_is_an_error(self):
        self.assertTrue(any("unknown field" in m for m in self.errors(entry(salary="x"))))

    def test_discarded_needs_a_reason(self):
        self.assertIn("t-1: missing 'reason'", self.errors(entry(state="discarded")))

    def test_closed_needs_who_and_why(self):
        errs = self.errors(entry(state="no_response", sent=D(2026, 1, 1)))
        self.assertIn("t-1: missing 'closed_by'", errs)
        self.assertIn("t-1: missing 'closure_reason'", errs)

    def test_direct_contact_needs_a_connection_event(self):
        errors, _ = pipeline_check.cross_checks([entry(direct_contact=True)])
        self.assertTrue(errors)

    def test_missing_id_and_quoted_dates_do_not_crash(self):
        errors, _ = pipeline_check.cross_checks([{"employer": "X", "role": "Y", "sent": "2026-01-02",
                                                  "published": "2026-01-05"}])
        self.assertIn("entry 0: sent before it was published", errors)

    def test_same_vacancy_twice_is_a_warning(self):
        _, warnings = pipeline_check.cross_checks([entry(), entry(id="t-2")])
        self.assertTrue(warnings)


class DatedRules(unittest.TestCase):
    RULES = [{"id": "r", "versions": [{"since": D(2026, 8, 1), "rule": "old"},
                                      {"since": D(2026, 9, 9), "rule": "new"}]}]

    def discard(self, cited, closes):
        return {"id": "x", "state": "discarded", "closes": closes, "reason": f"discarded on {cited} under rule r"}

    def test_flags_live_discard_under_old_version(self):
        hits = dated_rules.findings(self.RULES, [self.discard("2026-09-02", D(2026, 10, 26))], D(2026, 10, 13))
        self.assertEqual(len(hits), 1)

    def test_ignores_closed_posting(self):
        self.assertEqual(dated_rules.findings(
            self.RULES, [self.discard("2026-09-02", D(2026, 10, 1))], D(2026, 10, 13)), [])

    def test_ignores_discard_under_current_version(self):
        self.assertEqual(dated_rules.findings(
            self.RULES, [self.discard("2026-09-20", D(2026, 10, 26))], D(2026, 10, 13)), [])

    def test_quoted_closing_date_and_unnamed_rule(self):
        entry = {"id": "x", "state": "discarded", "closes": "2026-10-26", "reason": "discarded on 2026-09-02"}
        self.assertEqual(len(dated_rules.findings(self.RULES, [entry], D(2026, 10, 13))), 1)

    def test_rule_id_must_match_as_a_whole_word(self):
        rules = self.RULES + [{"id": "r-long", "versions": [{"since": D(2026, 8, 1), "rule": "x"}]}]
        entry = self.discard("2026-09-02", D(2026, 10, 26)) | {"reason": "discarded on 2026-09-02 under rule r-long"}
        self.assertEqual(dated_rules.findings(rules, [entry], D(2026, 10, 13)), [])

    def test_example_data_has_exactly_one_finding(self):
        import yaml
        rules = yaml.safe_load(dated_rules.RULES.read_text())["rules"]
        self.assertEqual(len(dated_rules.findings(rules, ENTRIES, D(2026, 10, 13))), 1)


class Probability(unittest.TestCase):
    def test_fit_and_bands(self):
        self.assertEqual(probability.fit_score("30/25/20/5"), 80)
        self.assertEqual([probability.band(x) for x in (75, 74, 55, 54)], ["A", "B", "B", "C"])

    def test_component_above_its_limit_is_refused(self):
        with self.assertRaises(ValueError):
            probability.fit_score("40/25/20/5")

    def test_channel_dominates_fit(self):
        # A posting that fits worse, through a person, beats a perfect fit through a mass board.
        self.assertGreater(probability.at_submission("direct", 50), probability.at_submission("board", 95))

    def test_today_decays_after_the_window_and_is_capped(self):
        p = probability.at_submission("board", 80)
        self.assertEqual(probability.today_probability(p, 10), p)
        self.assertLess(probability.today_probability(p, 45), p)
        self.assertEqual(probability.today_probability(0.5, 1, "In process"), probability.CAP_TODAY)

    def test_a_rejection_after_an_interview_was_a_call(self):
        e = {"state": "rejected", "history": [{"date": D(2026, 9, 1), "type": "interview"}]}
        self.assertTrue(probability.was_called(e))
        self.assertFalse(probability.was_called({"state": "rejected"}))

    def test_brier(self):
        self.assertAlmostEqual(probability.brier([(0.5, True), (0.5, False)]), 0.25)
        self.assertEqual(probability.brier([(1.0, True), (0.0, False)]), 0.0)

    def test_example_fit_matches_its_detail(self):
        for e in ENTRIES:
            self.assertEqual(probability.fit_score(e["fit_detail"]), e["fit"], e["id"])


class Gate(unittest.TestCase):
    APPS = ROOT / "reference" / "fixtures" / "applications"

    def test_ready_application_passes(self):
        self.assertEqual(gate.run(self.APPS / "ready", gate.FACTS), [])

    def test_blocked_application_fails_G1_G4_G7_G12(self):
        checks = {c for c, _ in gate.run(self.APPS / "blocked", gate.FACTS)}
        self.assertEqual(checks, {"G1", "G4", "G7", "G12"})

    def test_any_edit_after_approval_voids_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = pathlib.Path(tmp) / "app"
            shutil.copytree(self.APPS / "ready", folder)
            cv = folder / "cv.txt"
            cv.write_text(cv.read_text().replace("two lines", "three lines"))
            self.assertEqual([c for c, _ in gate.run(folder, gate.FACTS)], ["G12"])

    def copy_ready(self, tmp):
        folder = pathlib.Path(tmp) / "app"
        shutil.copytree(self.APPS / "ready", folder)
        return folder

    def test_unreadable_characters_block_G2(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = self.copy_ready(tmp)
            cv = folder / "cv.txt"
            cv.write_text(cv.read_text().replace("Python", "Pyth\ufffdn", 1))
            self.assertIn("G2", {c for c, _ in gate.run(folder, gate.FACTS)})

    def test_G7_reads_month_ranges_and_open_ends(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = self.copy_ready(tmp)
            cv = folder / "cv.txt"
            text = cv.read_text().replace("2019–present", "Mar 2019 – now").replace("2013–2019", "Jan 2012 – Dec 2019")
            cv.write_text(text)
            problems = [p for c, p in gate.run(folder, gate.FACTS) if c == "G7"]
            self.assertEqual(problems, ["date range 2012–2019 does not exist in the master profile"])

    def test_approval_cannot_be_piped(self):
        import io
        from unittest import mock
        with mock.patch.object(gate.sys, "stdin", io.StringIO("APPROVE\n")):
            self.assertEqual(gate.approve(self.APPS / "ready"), 1)

    def test_whitespace_does_not_void_the_approval(self):
        self.assertEqual(gate.fingerprint("a  b\nc"), gate.fingerprint("a b c"))

    def test_retired_claim_is_found_without_accents_or_case(self):
        self.assertEqual(gate.fold("LIDERÉ  un equipo"), "lidere un equipo")


class AtsCoverage(unittest.TestCase):
    LATEX = ROOT / "examples" / "latex"
    APP = LATEX / "compositions" / "applications" / "2026-10-12-contoso-data-engineer"

    def pct(self, composition):
        posting = (self.APP / "posting.md").read_text()
        terms = ats_coverage.posting_terms(posting, ats_coverage.employer_of(posting))
        return ats_coverage.coverage(terms, ats_coverage.latex_text(composition, self.LATEX))[0]

    def test_tailored_cv_beats_both_showcases(self):
        tailored = self.pct(self.APP / "cv.tex")
        for showcase in ("showcase-ai-en.tex", "showcase-ops-en.tex"):
            self.assertGreater(tailored, self.pct(self.LATEX / "compositions" / showcase), showcase)

    def test_employer_name_is_not_a_term(self):
        posting = "## Text\nAcme Acme Acme needs Python and SQL. Python daily."
        self.assertNotIn("acme", ats_coverage.posting_terms(posting, "Acme"))

    def test_notes_after_the_text_are_not_requirements(self):
        posting = "## Text\nPython and SQL.\n## Notes\nKubernetes Kubernetes"
        self.assertNotIn("kubernetes", ats_coverage.posting_terms(posting))

    def test_plurals_meet_singulars(self):
        terms = ats_coverage.collections.Counter({"pipelines": 2, "processes": 1})
        self.assertEqual(ats_coverage.coverage(terms, "a pipeline and a process")[0], 100)

    def test_inputs_are_resolved(self):
        text = ats_coverage.latex_text(self.LATEX / "compositions" / "showcase-ai-en.tex", self.LATEX)
        self.assertIn("Example Research Institute", text)
        self.assertNotIn("\\input", text)


class MiniBoard(unittest.TestCase):
    def test_known_values_of_the_example(self):
        # Counted by hand in examples/data/pipeline.example.yaml: 20 sent, 3 answered, 11 discarded.
        exp = mini_board.expected(copy.deepcopy(ENTRIES), D(2026, 10, 13))
        self.assertEqual((exp["sent"], exp["response_rate"], exp["discarded"]), (20, "15%", 11))
        self.assertEqual(len(exp["due_today"]), len(set(exp["due_today"])))

    def test_rounding_matches_javascript(self):
        # Python's round() gives 12 for 12.5; Math.round in the page gives 13.
        self.assertEqual(mini_board.percent(1, 8), "13%")
        self.assertEqual(mini_board.percent(0, 0), "—")

    def test_an_answer_can_live_in_the_history(self):
        e = {"state": "rejected", "history": [{"date": "2026-09-01", "type": "interview"}]}
        self.assertTrue(mini_board.was_answered(e))


if __name__ == "__main__":
    unittest.main()
