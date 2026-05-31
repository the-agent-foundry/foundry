#!/usr/bin/env python3
"""Regression tests for gates/scripts/sanitize_scan.py.

The test data constructs fake sensitive strings at runtime so the repository's
own sanitizer does not flag this file as a leak.
"""

import importlib.util
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCAN_PATH = ROOT / "gates" / "scripts" / "sanitize_scan.py"

spec = importlib.util.spec_from_file_location("sanitize_scan", SCAN_PATH)
sanitize_scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sanitize_scan)


class SanitizeScanTests(unittest.TestCase):
    def scan_text(self, text, suffix=".txt"):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / ("sample" + suffix)
            path.write_text(text, encoding="utf-8")
            return sanitize_scan.scan_file(str(path), [])

    def test_redacts_secret_value(self):
        secret = "sk-" + "A" * 24
        findings = self.scan_text("OPENAI_KEY=" + secret + "\n")
        self.assertTrue(findings)
        joined = "\n".join(f[2] for f in findings)
        self.assertIn("[REDACTED]", joined)
        self.assertNotIn(secret, joined)

    def test_placeholder_elsewhere_on_line_does_not_hide_secret(self):
        secret = "sk-" + "B" * 24
        findings = self.scan_text("docs at example.com OPENAI_KEY=" + secret + "\n")
        self.assertTrue(findings)
        joined = "\n".join(f[2] for f in findings)
        self.assertIn("[REDACTED]", joined)
        self.assertNotIn(secret, joined)

    def test_detects_connection_string(self):
        password = "fakepass" + "12345"
        uri = "postgres://user:" + password + "@db.internal/name"
        findings = self.scan_text("DATABASE_URL=" + uri + "\n")
        labels = {f[1] for f in findings}
        self.assertIn("Credential-bearing connection string", labels)

    def test_placeholders_are_allowed(self):
        findings = self.scan_text("contact: user@example.com\nchat: <CHAT_ID>\npath: /Users/<YOUR_NAME>/repo\n")
        self.assertEqual(findings, [])

    def test_sensitive_filename_is_flagged_and_redacted(self):
        with tempfile.TemporaryDirectory() as tmp:
            name = "person" + "@" + "private.biz-notes.txt"
            path = pathlib.Path(tmp) / name
            path.write_text("safe body\n", encoding="utf-8")
            findings = sanitize_scan.scan_file(str(path), [], root=tmp)
        self.assertTrue(findings)
        self.assertIn("Sensitive value in file path", findings[0][1])

    def test_risky_binary_artifact_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "slides.pdf"
            path.write_bytes(b"%PDF fake")
            findings = sanitize_scan.scan_file(str(path), [])
        self.assertTrue(findings)
        self.assertEqual(findings[0][1], "Risky binary/archive artifact requires explicit review")

    def test_path_allowlist_can_permit_reviewed_artifact_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "reviewed.pdf"
            path.write_bytes(b"%PDF fake")
            findings = sanitize_scan.scan_file(
                str(path), [], [sanitize_scan.re.compile(r"^reviewed\.pdf$")], root=tmp
            )
        self.assertEqual(findings, [])

    def test_broad_allowlist_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / ".sanitize-allow").write_text(".*\n", encoding="utf-8")
            _line, _path, errors = sanitize_scan.load_allowlist(str(root))
        self.assertTrue(errors)
        self.assertEqual(errors[0][2], "Dangerously broad sanitize allowlist regex")


if __name__ == "__main__":
    unittest.main()
