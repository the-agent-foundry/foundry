#!/usr/bin/env python3
"""Render a user-specific launchd plist without storing private paths in Git."""
import argparse
import os
import plistlib
from pathlib import Path


def render(script, policy, stdout_path, label="org.agent-foundry.disk-guardian"):
    script = str(Path(script).resolve())
    policy = str(Path(policy).resolve())
    stdout_path = str(Path(stdout_path).resolve())
    return {
        "Label": label,
        "ProgramArguments": [
            "/usr/bin/python3", script, "--policy", policy,
            "cleanup", "--scheduled",
        ],
        "StartInterval": 900,
        "RunAtLoad": True,
        "KeepAlive": False,
        "ProcessType": "Background",
        "LowPriorityIO": True,
        "StandardOutPath": stdout_path,
        "StandardErrorPath": stdout_path,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--log", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--label", default="org.agent-foundry.disk-guardian")
    args = parser.parse_args()
    payload = plistlib.dumps(render(args.script, args.policy, args.log, args.label), sort_keys=True)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name("." + output.name + ".candidate")
    temporary.write_bytes(payload)
    os.chmod(temporary, 0o600)
    os.replace(temporary, output)


if __name__ == "__main__":
    main()
