"""Regression tests for the guide-content and sitemap strict audit."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT_SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "audit_content_quality.py"


class IndexedGuideSitemapRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "scripts").mkdir()
        (self.root / "guides").mkdir()
        (self.root / "scripts" / "audit_content_quality.py").write_text(
            SCRIPT_SOURCE.read_text(encoding="utf-8"), encoding="utf-8"
        )
        (self.root / "guides" / "index.html").write_text(
            "<html><body>Guide index</body></html>", encoding="utf-8"
        )
        self.write_guide("sample-guide.html", "index,follow", "Sample guide", "Original useful guidance.")
        self.write_sitemap(["https://pakistanfoodrecipes.top/"])

    def tearDown(self):
        self.temp.cleanup()

    def write_guide(self, filename, robots, heading, body):
        (self.root / "guides" / filename).write_text(
            f"<html><head><meta name='robots' content='{robots}'></head>"
            f"<body><h1>{heading}</h1><p>{body}</p></body></html>",
            encoding="utf-8",
        )

    def write_sitemap(self, urls):
        entries = "".join(f"<url><loc>{url}</loc></url>" for url in urls)
        (self.root / "sitemap-v2.xml").write_text(
            f"<?xml version='1.0' encoding='UTF-8'?><urlset>{entries}</urlset>",
            encoding="utf-8",
        )

    def run_audit(self, strict=True):
        command = [sys.executable, str(self.root / "scripts" / "audit_content_quality.py")]
        if strict:
            command.append("--strict")
        return subprocess.run(
            command, cwd=self.root, text=True, capture_output=True, check=False
        )

    def test_strict_audit_fails_when_indexable_guide_is_missing_from_sitemap(self):
        result = self.run_audit()

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("INDEXED GUIDES MISSING FROM SITEMAP", result.stdout)
        self.assertIn("sample-guide.html", result.stdout)

    def test_strict_audit_passes_when_indexable_guide_is_in_sitemap(self):
        self.write_sitemap([
            "https://pakistanfoodrecipes.top/",
            "https://pakistanfoodrecipes.top/guides/sample-guide.html",
        ])

        result = self.run_audit()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("INDEXED GUIDES MISSING FROM SITEMAP", result.stdout)

    def test_non_strict_audit_reports_missing_guide_without_failing(self):
        result = self.run_audit(strict=False)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("INDEXED GUIDES MISSING FROM SITEMAP", result.stdout)

    def test_strict_audit_fails_when_noindex_guide_is_in_sitemap(self):
        self.write_guide("sample-guide.html", "noindex,follow", "Sample guide", "Original useful guidance.")
        self.write_sitemap([
            "https://pakistanfoodrecipes.top/",
            "https://pakistanfoodrecipes.top/guides/sample-guide.html",
        ])

        result = self.run_audit()

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("NOINDEX URLS PRESENT IN SITEMAP", result.stdout)

    def test_strict_audit_fails_on_duplicate_visible_guide_bodies(self):
        self.write_guide("second-guide.html", "index,follow", "Sample guide", "Original useful guidance.")
        self.write_sitemap([
            "https://pakistanfoodrecipes.top/",
            "https://pakistanfoodrecipes.top/guides/sample-guide.html",
            "https://pakistanfoodrecipes.top/guides/second-guide.html",
        ])

        result = self.run_audit()

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("EXACT DUPLICATE BODY GROUPS", result.stdout)
        self.assertIn("sample-guide.html", result.stdout)
        self.assertIn("second-guide.html", result.stdout)

    def test_noindex_guide_missing_from_sitemap_is_not_reported_as_indexable_missing(self):
        self.write_guide("sample-guide.html", "noindex,follow", "Sample guide", "Useful consolidated guidance.")

        result = self.run_audit()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("INDEXED GUIDES MISSING FROM SITEMAP", result.stdout)
        self.assertNotIn("NOINDEX URLS PRESENT IN SITEMAP", result.stdout)

    def test_strict_audit_fails_when_indexable_guide_contains_generic_template_phrase(self):
        self.write_guide(
            "sample-guide.html",
            "index,follow",
            "Sample guide",
            "This step has the strongest effect on the final result.",
        )
        self.write_sitemap([
            "https://pakistanfoodrecipes.top/",
            "https://pakistanfoodrecipes.top/guides/sample-guide.html",
        ])

        result = self.run_audit()

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("GENERIC TEMPLATE PHRASE HITS", result.stdout)
        self.assertIn("sample-guide.html", result.stdout)


    def test_same_filename_outside_guides_directory_does_not_satisfy_sitemap_check(self):
        self.write_sitemap([
            "https://pakistanfoodrecipes.top/",
            "https://pakistanfoodrecipes.top/archive/sample-guide.html",
        ])

        result = self.run_audit()

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("INDEXED GUIDES MISSING FROM SITEMAP", result.stdout)
        self.assertIn("sample-guide.html", result.stdout)


    def test_foreign_host_guide_url_does_not_satisfy_sitemap_check(self):
        self.write_sitemap([
            "https://pakistanfoodrecipes.top/",
            "https://other.example/guides/sample-guide.html",
        ])

        result = self.run_audit()

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("INDEXED GUIDES MISSING FROM SITEMAP", result.stdout)
        self.assertIn("sample-guide.html", result.stdout)

    def test_query_string_guide_url_does_not_satisfy_canonical_sitemap_check(self):
        self.write_sitemap([
            "https://pakistanfoodrecipes.top/",
            "https://pakistanfoodrecipes.top/guides/sample-guide.html?ref=home",
        ])

        result = self.run_audit()

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("INDEXED GUIDES MISSING FROM SITEMAP", result.stdout)
        self.assertIn("sample-guide.html", result.stdout)


if __name__ == "__main__":
    unittest.main()
