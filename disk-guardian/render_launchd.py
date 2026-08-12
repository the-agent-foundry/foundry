#!/usr/bin/env python3
"""Render a user-specific launchd plist without storing private paths in Git."""
import argparse
import os
import plistlib
from pathlib import Path


def assert_no_symlink_components(path):
    path = Path(path).absolute()
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        if (current.exists() or current.is_symlink()) and current.is_symlink():
            raise SystemExit("refusing symlinked plist destination")
    return path


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
    output = assert_no_symlink_components(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name("." + output.name + ".candidate")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        os.write(fd, payload)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(temporary, output)
    directory_fd = os.open(output.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


if __name__ == "__main__":
    main()
