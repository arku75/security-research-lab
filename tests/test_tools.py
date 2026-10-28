import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


BASE = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, BASE / "tools" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


inventory = load("safe_inventory")
audit = load("auth_response_audit")


class InventoryTests(unittest.TestCase):
    def test_report_has_no_names_paths_or_unknown_suffixes(self):
        with tempfile.TemporaryDirectory(prefix="private-root-") as directory:
            root = Path(directory)
            (root / "private-user@invalid.test@synthetic-secret.tokenvalue").write_text("private file contents")
            (root / "module.py").write_text("raise RuntimeError('never execute')")
            report = inventory.inventory(root)
            text = json.dumps(report)
            for private in (directory, "private-user", "synthetic-secret", "tokenvalue", "module.py", "private file contents"):
                self.assertNotIn(private, text)
            self.assertEqual(report["regular_files"], 2)
            self.assertEqual(report["extension_counts"], {".py": 1, "other_or_none": 1})

    def test_symlinks_and_dependency_trees_are_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "source.py").write_text("pass")
            (root / ".git").mkdir()
            (root / ".git" / "private.txt").write_text("private")
            (root / "loop").symlink_to(root, target_is_directory=True)
            report = inventory.inventory(root)
            self.assertEqual(report["regular_files"], 1)
            self.assertEqual(report["symlinks_skipped"], 1)
            self.assertEqual(report["excluded_directory_counts"], {".git": 1})

    def test_file_limit_marks_partial_results(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("a.py", "b.py", "c.py"):
                (root / name).write_text("pass")
            report = inventory.inventory(root, max_files=2)
            self.assertEqual(report["regular_files"], 2)
            self.assertEqual(report["status"], "limited")
            self.assertEqual(report["stop_reason"], "file_limit")

    def test_depth_limit_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "child").mkdir()
            (root / "child" / "source.py").write_text("pass")
            report = inventory.inventory(root, max_depth=0)
            self.assertEqual(report["regular_files"], 0)
            self.assertEqual(report["status"], "partial")

    def test_unavailable_root_does_not_echo_path(self):
        report = inventory.inventory("/does-not-exist/private-example")
        self.assertEqual(report["status"], "unavailable")
        self.assertNotIn("private-example", json.dumps(report))


class ResponseAuditTests(unittest.TestCase):
    def parse_text(self, content):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "observations.csv"
            path.write_text(content)
            return audit.read_observations(path)

    def test_consistent_fixture(self):
        report = audit.analyze(audit.read_observations(BASE / "examples" / "consistent.csv"))
        self.assertEqual(report["sample_status"], "sufficient_for_summary")
        self.assertEqual(set(report["comparison"].values()), {0})

    def test_discrepant_fixture(self):
        report = audit.analyze(audit.read_observations(BASE / "examples" / "discrepant.csv"))
        self.assertEqual(report["comparison"]["status_distribution_distance"], 1)
        self.assertEqual(report["comparison"]["absolute_median_size_gap_bytes"], 600)
        self.assertEqual(report["comparison"]["absolute_median_latency_gap_ms"], 80)

    def test_personal_data_columns_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "four documented columns"):
            self.parse_text("cohort,status_code,response_bytes,latency_ms,email\nknown,200,100,25,private@example.invalid\n")

    def test_duplicate_headers_are_rejected(self):
        with self.assertRaises(ValueError):
            self.parse_text("cohort,status_code,response_bytes,cohort\nknown,200,100,known\n")

    def test_non_regular_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "regular CSV file"):
                audit.read_observations(directory)

    def test_invalid_values_are_not_echoed(self):
        for bad in ("NaN", "inf", "-1", "private@example.invalid"):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, "Invalid observation on CSV line 2") as error:
                self.parse_text("cohort,status_code,response_bytes,latency_ms\nknown,200,100," + bad + "\n")
            self.assertNotIn(bad, str(error.exception))

    def test_empty_and_small_samples_are_inconclusive(self):
        empty = audit.analyze(self.parse_text("cohort,status_code,response_bytes,latency_ms\n"))
        self.assertEqual(empty["sample_status"], "insufficient")
        self.assertIsNone(empty["comparison"])
        small = audit.analyze(self.parse_text("cohort,status_code,response_bytes,latency_ms\nknown,200,100,25\nunknown,200,100,25\n"))
        self.assertEqual(small["sample_status"], "insufficient")


if __name__ == "__main__":
    unittest.main()
