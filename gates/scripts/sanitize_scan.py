#!/usr/bin/env python3
"""
sanitize_scan.py - The Agent Foundry fail-closed sanitization gate.

What it does
------------
Recursively scans a directory (or a single file) for things that must never
enter a public repo: credentials, private keys, .env-style secret assignments,
real absolute home paths, mesh/Tailscale hostnames, email addresses, phone
numbers, and long all-digit IDs that look like chat or user IDs.

It is pure Python 3 standard library. No dependencies, no network, no secrets
of its own. It is meant to run identically on a contributor's laptop and in CI
so the same answer comes back in both places.

Posture
-------
Fail closed. Exit code 0 means clean. Any finding returns a non-zero exit code
and prints a report with file:line for every hit. CI is wired to block a merge
on a non-zero exit, so nothing sensitive lands by accident.

This is a backstop, not a guarantee. It catches the common, high-signal
patterns. You are still responsible for scrubbing your own contribution before
you ever open a pull request.

Allowlisting
------------
Two mechanisms keep legitimate content passing without weakening the gate:

1. Built-in placeholder awareness. Obvious placeholders are ignored on every
   line: <YOUR_HANDLE>, <CHAT_ID>, <...> angle-bracket tokens generally,
   example.com / example.org / example.net, /path/to/..., 0000000000, and
   similar fill-in tokens used in templates and schemas.

2. A .sanitize-allow file at the scan root. One regex per line. Any line of any
   scanned file that matches an allow regex is skipped for that scan. Use it
   sparingly and comment why (lines starting with # are ignored).

Usage
-----
    python3 sanitize_scan.py [PATH]

    PATH   File or directory to scan. Defaults to the current directory.

Examples
--------
    python3 gates/scripts/sanitize_scan.py .
    python3 gates/scripts/sanitize_scan.py community/your-handle/

Exit codes
----------
    0   Clean. Nothing sensitive found.
    1   One or more findings. See the printed report.
    2   Usage / runtime error (bad path, etc.).
"""

import os
import re
import sys

# Directories we never descend into.
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    ".mypy_cache", ".pytest_cache", "dist", "build", ".idea", ".vscode",
}

# File extensions we treat as binary and skip outright.
BINARY_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip",
    ".gz", ".tar", ".tgz", ".woff", ".woff2", ".ttf", ".otf", ".eot",
    ".mp3", ".mp4", ".mov", ".ogg", ".wav", ".bin", ".so", ".dylib",
    ".dll", ".class", ".jar", ".pyc", ".lock",
}

# This scanner file and the allow file naturally contain pattern strings.
# We skip them so the gate does not flag its own definitions.
SELF_SKIP_NAMES = {"sanitize_scan.py", ".sanitize-allow"}

# Tokens that mark a line as an intentional placeholder. If a candidate match
# overlaps one of these on the same line, that match is excused.
PLACEHOLDER_TOKENS = [
    "example.com", "example.org", "example.net", "example.edu",
    "/path/to/", "/Users/<", "/home/<",
    "your-handle", "your_handle", "YOUR_HANDLE",
    "name@example", "user@example", "you@example",
]

# Regex placeholders: if a match string itself looks like one of these, excuse it.
PLACEHOLDER_MATCH_RES = [
    re.compile(r"^<[^>]+>$"),                 # <ANYTHING>
    re.compile(r"^0+$"),                      # 0000000000
    re.compile(r"^[Xx]+$"),                   # XXXXXXXX
    re.compile(r"^1234567890$"),
    re.compile(r"^(?:123)+$"),
    re.compile(r"(?i)^(your|my|the)[-_].+"),   # YOUR_TOKEN, my-handle, etc.
    re.compile(r"(?i)placeholder"),
    re.compile(r"(?i)example"),
    re.compile(r"(?i)redacted"),
    re.compile(r"(?i)changeme"),
    re.compile(r"(?i)dummy"),
    re.compile(r"(?i)^<.*>$"),
]

# (label, compiled regex). Order matters only for readability of the report.
RULES = [
    ("Private key block",
     re.compile(r"-----BEGIN(?: [A-Z0-9]+)* PRIVATE KEY-----")),
    ("OpenAI-style secret key (sk-)",
     re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b")),
    ("GitHub token (ghp_/gho_/ghu_/ghs_/ghr_)",
     re.compile(r"\bgh[posur]_[A-Za-z0-9]{20,}\b")),
    ("Slack token (xox...)",
     re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("Google API key (AIza...)",
     re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b")),
    ("AWS access key id (AKIA/ASIA...)",
     re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("Bearer token in header",
     re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._-]{20,}\b")),
    ("Generic API/secret/token assignment",
     re.compile(r"(?i)\b(?:api[_-]?key|secret|token|passwd|password|access[_-]?key)\b"
                r"\s*[:=]\s*['\"]?([A-Za-z0-9._/+-]{12,})['\"]?")),
    ("Long base64-ish secret (40+ chars)",
     re.compile(r"\b[A-Za-z0-9+/]{40,}={0,2}\b")),
    (".env-style KEY=VALUE secret",
     re.compile(r"(?m)^\s*[A-Z][A-Z0-9_]{2,}\s*=\s*['\"]?[^\s'\"#]{8,}['\"]?\s*$")),
    ("Absolute home path (/Users/<name> or /home/<name>)",
     re.compile(r"/(?:Users|home)/[A-Za-z0-9._-]+")),
    ("Tailscale / mesh hostname (*.ts.net)",
     re.compile(r"\b[A-Za-z0-9._-]+\.ts\.net\b")),
    ("Email address",
     re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("Phone number",
     re.compile(r"(?<![\w.])(?:\+?\d{1,3}[\s.-]?)?(?:\(\d{3}\)|\d{3})[\s.-]\d{3}[\s.-]\d{4}(?![\w])")),
    ("Long all-digit ID (>=9 digits, looks like a chat/user ID)",
     re.compile(r"(?<![\w.])-?\d{9,}(?![\w.])")),
]


def load_allowlist(root):
    """Read .sanitize-allow at the scan root: one regex per line, # for comments."""
    allow = []
    candidate = os.path.join(root, ".sanitize-allow") if os.path.isdir(root) \
        else os.path.join(os.path.dirname(root) or ".", ".sanitize-allow")
    if os.path.isfile(candidate):
        with open(candidate, "r", encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    allow.append(re.compile(line))
                except re.error:
                    # A bad allow regex must never silently weaken the gate.
                    sys.stderr.write(f"warning: bad allow regex skipped: {line}\n")
    return allow


def is_placeholder(matched_text, line_text):
    """True if a candidate match is clearly an intentional placeholder."""
    low_line = line_text.lower()
    for tok in PLACEHOLDER_TOKENS:
        if tok.lower() in low_line:
            return True
    for rx in PLACEHOLDER_MATCH_RES:
        if rx.search(matched_text):
            return True
    # Angle-bracket templating wrapping the match, e.g. <CHAT_ID>.
    if "<" in line_text and ">" in line_text:
        wrapped = re.search(r"<[^>]*" + re.escape(matched_text) + r"[^>]*>", line_text)
        if wrapped:
            return True
    return False


def iter_files(root):
    """Yield scannable file paths under root, skipping junk and binaries."""
    if os.path.isfile(root):
        yield root
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name in SELF_SKIP_NAMES:
                continue
            ext = os.path.splitext(name)[1].lower()
            if ext in BINARY_EXTS:
                continue
            yield os.path.join(dirpath, name)


def scan_file(path, allow):
    """Return a list of (lineno, label, snippet) findings for one file."""
    findings = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except (OSError, UnicodeError):
        return findings

    for lineno, line in enumerate(lines, start=1):
        if any(rx.search(line) for rx in allow):
            continue
        for label, rule in RULES:
            for m in rule.finditer(line):
                matched = m.group(0).strip()
                if not matched:
                    continue
                if is_placeholder(matched, line):
                    continue
                snippet = line.strip()
                if len(snippet) > 160:
                    snippet = snippet[:157] + "..."
                findings.append((lineno, label, snippet))
                break  # one finding per rule per line is enough signal
    return findings


def main(argv):
    target = argv[1] if len(argv) > 1 else "."
    if not os.path.exists(target):
        sys.stderr.write(f"error: path not found: {target}\n")
        return 2

    allow = load_allowlist(target)
    total = 0
    flagged_files = 0

    for path in sorted(iter_files(target)):
        findings = scan_file(path, allow)
        if findings:
            flagged_files += 1
            rel = os.path.relpath(path, target if os.path.isdir(target) else ".")
            for lineno, label, snippet in findings:
                print(f"{rel}:{lineno}: {label}")
                print(f"    | {snippet}")
                total += 1

    print()
    if total == 0:
        print("sanitize_scan: CLEAN. No sensitive patterns found.")
        return 0

    print(f"sanitize_scan: FAILED. {total} finding(s) in {flagged_files} file(s).")
    print("Scrub the items above before submitting. Use .sanitize-allow only for "
          "genuine placeholders, and document why.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
