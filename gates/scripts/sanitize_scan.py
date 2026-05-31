#!/usr/bin/env python3
"""
sanitize_scan.py - The Agent Foundry fail-closed sanitization gate.

Scans a directory or single file for things that must never enter a public repo:
credentials, private keys, secret assignments, credential-bearing connection
strings, package-registry auth residue, real absolute home paths, mesh/Tailscale
hostnames, email addresses, phone numbers, long all-digit IDs, sensitive path
names, and risky binary/archive artifacts that need human review.

Pure Python 3 standard library. No dependencies, no network, no secrets.

Posture: fail closed. Exit 0 means clean. Any finding returns non-zero and
prints path/line/rule with redacted snippets. This is a backstop, not a
complete DLP system.
"""

import os
import re
import sys

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    ".mypy_cache", ".pytest_cache", "dist", "build", ".idea", ".vscode",
}

RISKY_BINARY_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip",
    ".gz", ".tar", ".tgz", ".7z", ".rar", ".woff", ".woff2", ".ttf",
    ".otf", ".eot", ".mp3", ".mp4", ".mov", ".ogg", ".wav", ".bin",
    ".so", ".dylib", ".dll", ".class", ".jar", ".pyc", ".sqlite",
    ".sqlite3", ".db", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
}

MAX_TEXT_BYTES = 2_000_000
SELF_SKIP_NAMES = {"sanitize_scan.py", ".sanitize-allow"}

PLACEHOLDER_TOKENS = [
    "example.com", "example.org", "example.net", "example.edu",
    "/path/to/", "/Users/<", "/home/<",
    "your-handle", "your_handle", "YOUR_HANDLE",
    "name@example", "user@example", "you@example",
]

PLACEHOLDER_MATCH_RES = [
    re.compile(r"^<[^>]+>$"),
    re.compile(r"^0+$"),
    re.compile(r"^[Xx]+$"),
    re.compile(r"^1234567890$"),
    re.compile(r"^(?:123)+$"),
    re.compile(r"(?i)^(your|my|the)[-_].+"),
    re.compile(r"(?i)placeholder"),
    re.compile(r"(?i)example"),
    re.compile(r"(?i)redacted"),
    re.compile(r"(?i)changeme"),
    re.compile(r"(?i)dummy"),
    re.compile(r"(?i)^<.*>$"),
]

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
    ("Credential-bearing connection string",
     re.compile(r"(?i)\b(?:postgres(?:ql)?|mysql|mariadb|mongodb(?:\+srv)?|redis|amqps?|smtp|smtps)://[^\s:@/]+:[^\s@/]{8,}@[^\s]+")),
    ("JDBC credential-bearing URL",
     re.compile(r"(?i)\bjdbc:[A-Za-z0-9:+.-]+://[^\s;]+;[^\n]*(?:password|pwd)=[^\s;]{8,}")),
    ("Webhook URL with embedded secret",
     re.compile(r"https://(?:hooks\.slack\.com/services|discord(?:app)?\.com/api/webhooks|api\.telegram\.org/bot)[A-Za-z0-9_./:-]{20,}")),
    ("Package registry auth token",
     re.compile(r"(?i)\b(?:_authToken|npm_token|pypi_token|twine_password|poetry_pypi_token_[A-Za-z0-9_-]+)\b\s*[:=]\s*['\"]?([A-Za-z0-9._/+-]{12,})['\"]?")),
    ("netrc-style credential",
     re.compile(r"(?i)\bmachine\s+\S+\s+login\s+\S+\s+password\s+\S{8,}")),
    ("Cloud/service-account private key marker",
     re.compile(r"(?i)\b(?:private_key_id|client_secret|refresh_token)\b\s*[:=]\s*['\"]?([A-Za-z0-9._/+-]{12,})['\"]?")),
    ("Kubeconfig credential marker",
     re.compile(r"(?i)\b(?:client-certificate-data|client-key-data|token):\s*([A-Za-z0-9+/=._-]{20,})")),
    ("Generic API/secret/token assignment",
     re.compile(r"(?i)\b(?:api[_-]?key|secret|token|passwd|password|access[_-]?key)\b"
                r"\s*[:=]\s*['\"]?([A-Za-z0-9._/+-]{12,})['\"]?")),
    ("Long base64-ish secret (40+ chars)",
     re.compile(r"\b[A-Za-z0-9+/]{40,}={0,2}\b")),
    (".env-style sensitive KEY=VALUE secret",
     re.compile(r"(?m)^\s*[A-Z][A-Z0-9_]*(?:SECRET|TOKEN|KEY|PASSWORD|PASSWD|AUTH|CREDENTIAL|PRIVATE)[A-Z0-9_]*\s*=\s*['\"]?[^\s'\"#]{8,}['\"]?\s*$")),
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

BROAD_ALLOWLIST_PATTERNS = {".*", "^.*$", ".+", "^.+$", "(.*)", "^.*", ".*$"}


def is_broad_allow_pattern(pattern):
    stripped = pattern.strip()
    if stripped in BROAD_ALLOWLIST_PATTERNS:
        return True
    # Tiny unanchored fragments are usually lazy bypasses, not real exceptions.
    if len(stripped) < 4 and not stripped.startswith("^"):
        return True
    return False


def load_allowlist(root):
    """Read .sanitize-allow. Supports line:<regex> and path:<regex> entries."""
    line_allow = []
    path_allow = []
    errors = []
    candidate = os.path.join(root, ".sanitize-allow") if os.path.isdir(root) else os.path.join(os.path.dirname(root) or ".", ".sanitize-allow")
    if not os.path.isfile(candidate):
        return line_allow, path_allow, errors

    with open(candidate, "r", encoding="utf-8", errors="replace") as fh:
        for lineno, raw in enumerate(fh, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            kind = "line"
            pattern = line
            if line.startswith("line:"):
                pattern = line[len("line:"):].strip()
            elif line.startswith("path:"):
                kind = "path"
                pattern = line[len("path:"):].strip()

            if is_broad_allow_pattern(pattern):
                errors.append((candidate, lineno, "Dangerously broad sanitize allowlist regex", "[allowlist entry redacted]"))
                continue
            if kind == "path" and not (pattern.startswith("^") or "/" in pattern):
                errors.append((candidate, lineno, "Path allowlist entry must be anchored or repo-relative", "[allowlist entry redacted]"))
                continue
            try:
                compiled = re.compile(pattern)
            except re.error:
                errors.append((candidate, lineno, "Invalid sanitize allowlist regex", "[allowlist entry redacted]"))
                continue
            if kind == "path":
                path_allow.append(compiled)
            else:
                line_allow.append(compiled)
    return line_allow, path_allow, errors


def spans_overlap(a, b):
    return max(a[0], b[0]) < min(a[1], b[1])


def is_placeholder(matched_text, line_text, span=None):
    """True only when the matched value itself is a placeholder."""
    for rx in PLACEHOLDER_MATCH_RES:
        if rx.search(matched_text):
            return True

    if span is not None:
        low_line = line_text.lower()
        for tok in PLACEHOLDER_TOKENS:
            low_tok = tok.lower()
            start = 0
            while True:
                idx = low_line.find(low_tok, start)
                if idx == -1:
                    break
                if spans_overlap(span, (idx, idx + len(tok))):
                    return True
                start = idx + 1

    if "<" in line_text and ">" in line_text:
        wrapped = re.search(r"<[^>]*" + re.escape(matched_text) + r"[^>]*>", line_text)
        if wrapped:
            return True
    return False


def iter_files(root):
    if os.path.isfile(root):
        yield root
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name in SELF_SKIP_NAMES:
                continue
            yield os.path.join(dirpath, name)


def redacted_snippet(line, match):
    line = line.rstrip("\n")
    spans = []
    if match.lastindex:
        for i in range(1, match.lastindex + 1):
            span = match.span(i)
            if span != (-1, -1):
                spans.append(span)
    if not spans:
        spans = [match.span(0)]
    redacted = line
    for start, end in sorted(spans, reverse=True):
        redacted = redacted[:start] + "[REDACTED]" + redacted[end:]
    snippet = redacted.strip()
    return snippet[:157] + "..." if len(snippet) > 160 else snippet


def redact_text(text):
    redacted = text
    for label, rule in RULES:
        if label == "Long base64-ish secret (40+ chars)" and "://" in redacted:
            continue
        redacted = rule.sub("[REDACTED]", redacted)
    return redacted


def match_span(match):
    if match.lastindex and match.group(1):
        return match.span(1)
    return match.span(0)


def match_text(match):
    if match.lastindex and match.group(1):
        return match.group(1).strip()
    return match.group(0).strip()


def artifact_finding(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in RISKY_BINARY_EXTS:
        return (0, "Risky binary/archive artifact requires explicit review", "[artifact filename redacted]")
    try:
        size = os.path.getsize(path)
    except OSError:
        return None
    if size > MAX_TEXT_BYTES:
        return (0, "Large text artifact requires explicit review", "[large filename redacted]")
    return None


def path_findings(rel_path):
    findings = []
    for label, rule in RULES:
        if label == "Long base64-ish secret (40+ chars)" and "://" in rel_path:
            continue
        for m in rule.finditer(rel_path):
            matched = match_text(m)
            if not matched:
                continue
            if is_placeholder(matched, rel_path, match_span(m)):
                continue
            findings.append((0, f"Sensitive value in file path: {label}", "[path segment redacted]"))
            break
    return findings


def scan_file(path, line_allow, path_allow=None, root=None):
    path_allow = path_allow or []
    rel_path = os.path.relpath(path, root) if root else path
    rel_path = rel_path.replace(os.sep, "/")
    findings = []

    if any(rx.search(rel_path) for rx in path_allow):
        return findings

    findings.extend(path_findings(rel_path))

    artifact = artifact_finding(path)
    if artifact:
        findings.append(artifact)
        return findings

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except (OSError, UnicodeError):
        return findings

    for lineno, line in enumerate(lines, start=1):
        if any(rx.search(line) for rx in line_allow):
            continue
        for label, rule in RULES:
            if label == "Long base64-ish secret (40+ chars)" and "://" in line:
                continue
            for m in rule.finditer(line):
                matched = match_text(m)
                if not matched:
                    continue
                if is_placeholder(matched, line, match_span(m)):
                    continue
                findings.append((lineno, label, redacted_snippet(line, m)))
                break
    return findings


def main(argv):
    target = argv[1] if len(argv) > 1 else "."
    if not os.path.exists(target):
        sys.stderr.write(f"error: path not found: {target}\n")
        return 2

    line_allow, path_allow, allow_errors = load_allowlist(target)
    total = 0
    flagged_files = 0
    root = target if os.path.isdir(target) else "."

    for allow_path, lineno, label, snippet in allow_errors:
        rel = os.path.relpath(allow_path, root).replace(os.sep, "/")
        print(f"{redact_text(rel)}:{lineno}: {label}")
        print(f"    | {snippet}")
        total += 1
        flagged_files += 1

    for path in sorted(iter_files(target)):
        findings = scan_file(path, line_allow, path_allow, root=root)
        if findings:
            flagged_files += 1
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            safe_rel = redact_text(rel)
            for lineno, label, snippet in findings:
                loc = f"{safe_rel}:{lineno}" if lineno else safe_rel
                print(f"{loc}: {label}")
                print(f"    | {snippet}")
                total += 1

    print()
    if total == 0:
        print("sanitize_scan: CLEAN. No sensitive patterns found.")
        return 0

    print(f"sanitize_scan: FAILED. {total} finding(s) in {flagged_files} file(s).")
    print("Scrub the items above before submitting. Use .sanitize-allow only for narrow, documented placeholders or reviewed artifacts.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
