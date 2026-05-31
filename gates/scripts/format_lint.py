#!/usr/bin/env python3
"""
format_lint.py - The Agent Foundry format linter.

What it does
------------
Validates that contributed artifacts match the canonical schemas in the repo:

  * skills  : files under skills/ and community/*/skills/ must carry the
              required SKILL frontmatter keys and required body headings.
  * agents  : files under agents/archetypes/ and community/*/agents/ must carry
              the required AGENT-SPEC frontmatter keys and headings.
  * tools   : files under tools/examples/ and community/*/tools/ must carry the
              required TOOL-SPEC frontmatter keys and headings.

It is pragmatic on purpose. It checks the contract shape, not prose quality.
The point is a consistent shape so a human or an agent can read any artifact in
this repo and know where to look.

Pure Python 3 standard library. No dependencies. Designed to run identically on
a laptop and in CI.

Usage
-----
    python3 format_lint.py [PATH]

    PATH   Repo root to lint. Defaults to the current directory.

Exit codes
----------
    0   All artifacts conform.
    1   One or more violations. See the printed report.
    2   Usage / runtime error.
"""
import os
import re
import sys

EXEMPT_BASENAMES = {
    "README.md", "SKILL.schema.md", "SKILL.template.md",
    "AGENT-SPEC.schema.md", "AGENTS.template.md", "SOUL.template.md",
    "TOOL-SPEC.schema.md", "TOOL.template.md", "PRINCIPLES.template.md",
}

RULES = {
    "skill": {
        "frontmatter": [
            "name", "description", "version", "owner",
            "data_sensitivity", "approval_required",
        ],
        "headings": [
            "When to use", "Inputs", "Procedure", "What good looks like",
            "Output contract", "Privacy and approval", "Verification",
            "Maintenance", "Landmines",
        ],
        "allowed_values": {
            "data_sensitivity": {"public", "internal", "confidential", "restricted"},
            "approval_required": {"none", "before_write", "before_external_send", "before_live_change"},
        },
    },
    "agent": {
        "frontmatter": ["role", "mission", "reports_to"],
        "headings": ["Mission", "Scope", "Skills and tools",
                     "What good looks like", "Approval boundaries"],
        "allowed_values": {},
    },
    "tool": {
        "frontmatter": ["name", "problem"],
        "headings": ["Problem", "Interface", "What good looks like",
                     "Failure modes", "Privacy notes",
                     "Approval boundaries", "Freshness and state",
                     "Observability"],
        "allowed_values": {},
    },
}

FRONTMATTER_RE = re.compile(r"^\s*---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def classify(path):
    """Return 'skill' | 'agent' | 'tool' | None for a markdown file path."""
    parts = path.replace(os.sep, "/").split("/")
    if os.path.basename(path) in EXEMPT_BASENAMES:
        return None
    if not path.endswith(".md"):
        return None
    joined = "/".join(parts)
    if "agents/archetypes" in joined:
        return "agent"
    if "tools/examples" in joined:
        return "tool"
    if "skills/examples" in joined:
        return "skill"
    if "community" in parts:
        i = parts.index("community")
        if len(parts) > i + 2:
            kind_dir = parts[i + 2]
            return {"skills": "skill", "agents": "agent", "tools": "tool"}.get(kind_dir)
    return None


def parse_frontmatter(text):
    """Return a dict of top-level YAML-ish frontmatter keys to scalar values."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    values = {}
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*?)\s*$", line)
        if km:
            key = km.group(1).strip()
            value = km.group(2).strip().strip('"\'')
            values[key] = value
    return values


def find_headings(text):
    """Return lowercased heading texts found in the document."""
    heads = []
    for line in text.splitlines():
        hm = re.match(r"^#{1,6}\s+(.*\S)\s*$", line)
        if hm:
            heads.append(hm.group(1).strip().lower())
    return heads


def lint_file(path, kind):
    """Return a list of problem strings for one artifact file."""
    problems = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError as exc:
        return [f"cannot read file: {exc}"]

    spec = RULES[kind]

    fm = parse_frontmatter(text)
    if fm is None:
        problems.append("missing YAML frontmatter block (--- ... ---)")
    else:
        for req in spec["frontmatter"]:
            if req not in fm:
                problems.append(f"missing frontmatter key: {req}")
        for key, allowed in spec.get("allowed_values", {}).items():
            if key in fm and fm[key] not in allowed:
                allowed_list = ", ".join(sorted(allowed))
                problems.append(
                    f"invalid frontmatter value for {key}: {fm[key]!r} "
                    f"(allowed: {allowed_list})"
                )

    heads = find_headings(text)
    for req in spec["headings"]:
        if req.lower() not in heads:
            problems.append(f"missing required section heading: {req}")

    return problems


def iter_markdown(root):
    skip = {".git", "node_modules", "__pycache__"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for name in filenames:
            if name.endswith(".md"):
                yield os.path.join(dirpath, name)


def main(argv):
    root = argv[1] if len(argv) > 1 else "."
    if not os.path.exists(root):
        sys.stderr.write(f"error: path not found: {root}\n")
        return 2

    total = 0
    checked = 0
    for path in sorted(iter_markdown(root)):
        kind = classify(path)
        if kind is None:
            continue
        checked += 1
        problems = lint_file(path, kind)
        if problems:
            rel = os.path.relpath(path, root)
            for p in problems:
                print(f"{rel}: [{kind}] {p}")
                total += 1

    print()
    if total == 0:
        print(f"format_lint: CLEAN. {checked} artifact(s) conform to schema.")
        return 0
    print(f"format_lint: FAILED. {total} violation(s) across {checked} checked artifact(s).")
    print("Match the canonical schema in skills/, agents/, or tools/ and re-run.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
