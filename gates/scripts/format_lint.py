#!/usr/bin/env python3
"""
format_lint.py - The Agent Foundry format linter.

What it does
------------
Validates that contributed artifacts match the canonical schemas in the repo:

  * skills  : files under skills/ and community/*/skills/ must carry the
              required SKILL frontmatter keys and the required body headings.
  * agents  : files under agents/archetypes/ and community/*/agents/ must carry
              the required AGENT-SPEC frontmatter keys and headings.
  * tools   : files under tools/examples/ and community/*/tools/ must carry the
              required TOOL-SPEC frontmatter keys and headings.

It is pragmatic on purpose. It checks that required frontmatter keys exist and
that required section headings are present. It does not police prose. The point
is a consistent shape so a human or an agent can read any artifact in the repo
and know where to look.

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

# Schema files and README/template/schema files are not themselves artifacts.
EXEMPT_BASENAMES = {
    "README.md", "SKILL.schema.md", "SKILL.template.md",
    "AGENT-SPEC.schema.md", "AGENTS.template.md", "SOUL.template.md",
    "TOOL-SPEC.schema.md", "PRINCIPLES.template.md",
}

# Required frontmatter keys and required headings per artifact kind.
RULES = {
    "skill": {
        "frontmatter": ["name", "description", "version", "owner"],
        "headings": ["When to use", "Inputs", "Procedure",
                     "What good looks like", "Landmines"],
    },
    "agent": {
        "frontmatter": ["role", "mission", "reports_to"],
        "headings": ["Mission", "Scope", "Skills and tools",
                     "What good looks like", "Approval boundaries"],
    },
    "tool": {
        "frontmatter": ["name", "problem"],
        "headings": ["Problem", "Interface", "What good looks like"],
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
    # core locations
    if "agents/archetypes" in "/".join(parts):
        return "agent"
    if "tools/examples" in "/".join(parts):
        return "tool"
    if "skills/examples" in "/".join(parts):
        return "skill"
    # community namespace: community/<handle>/<kind>/...
    if "community" in parts:
        i = parts.index("community")
        if len(parts) > i + 2:
            kind_dir = parts[i + 2]
            return {"skills": "skill", "agents": "agent",
                    "tools": "tool"}.get(kind_dir)
    return None


def parse_frontmatter(text):
    """Return a set of top-level keys found in YAML-ish frontmatter, or None."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    keys = set()
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z0-9_-]+)\s*:", line)
        if km:
            keys.add(km.group(1).strip())
    return keys


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

    keys = parse_frontmatter(text)
    if keys is None:
        problems.append("missing YAML frontmatter block (--- ... ---)")
    else:
        for req in spec["frontmatter"]:
            if req not in keys:
                problems.append(f"missing frontmatter key: {req}")

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
    print(f"format_lint: FAILED. {total} violation(s) across "
          f"{checked} checked artifact(s).")
    print("Match the canonical schema in skills/, agents/, or tools/ and re-run.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
