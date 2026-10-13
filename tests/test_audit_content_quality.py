"""Regression tests for indexed-guide sitemap enforcement in strict mode."""

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
        (self.root / "guides" / "sample-guide.html").write_text(
            "<html><head><meta name='robots' content='index,follow'></head>"
            "<body><h1>Sample guide</h1><p>Original useful guidance.</p></body></html>",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp.cleanup()

    def run_strict_audit(self):
        return subprocess.run(
            [sys.executable, str(self.root / "scripts" / "audit_content_quality.py"), "--strict"],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=False,
        )

    def write_sitemap(self, include_sample_guide):
        urls = ["https://example.test/"]
        if include_sample_guide:
            urls.append("https://example.test/guides/sample-guide.html")
        entries = "".join(f"<url><loc>{url}</loc></url>" for url in urls)
        (self.root / "sitemap-v2.xml").write_text(
            f"<?xml version='1.0' encoding='UTF-8'?><urlset>{entries}</urlset>",
            encoding="utf-8",
        )

    def test_strict_audit_fails_when_indexable_guide_is_missing_from_sitemap(self):
        self.write_sitemap(include_sample_guide=False)

        result = self.run_strict_audit()

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("INDEXED GUIDES MISSING FROM SITEMAP", result.stdout)
        self.assertIn("sample-guide.html", result.stdout)

    def test_strict_audit_passes_when_indexable_guide_is_in_sitemap(self):
        self.write_sitemap(include_sample_guide=True)

        result = self.run_strict_audit()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("INDEXED GUIDES MISSING FROM SITEMAP", result.stdout)


if __name__ == "__main__":
    unittest.main()
