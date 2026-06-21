#!/usr/bin/env python3
"""Tiny synthetic health-check fixture used by the public Auto-buildroom example."""
from __future__ import annotations
import json
import pathlib
import sys

def main(argv):
    if len(argv) != 2:
        print("usage: check_fixture_health.py <fixture.json>", file=sys.stderr)
        return 64
    data = json.loads(pathlib.Path(argv[1]).read_text())
    status = data.get("source_status")
    if status == "fresh_source":
        print("status=healthy reason=fresh_source")
        return 0
    print("status=unhealthy reason=stale_source")
    return 2

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
