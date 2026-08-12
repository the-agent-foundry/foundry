#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd -P)"
LABEL="org.agent-foundry.disk-guardian"
DEST="$HOME/.local/share/disk-guardian-community"
STATE="$HOME/.disk-guardian"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
DOMAIN="gui/$(id -u)"

case "${1:-}" in
  install)
    if launchctl print "$DOMAIN/$LABEL" >/dev/null 2>&1; then
      echo "Refusing to replace a loaded Guardian. Run '$0 uninstall' first." >&2
      exit 3
    fi
    stamp="$(date -u +%Y%m%dT%H%M%SZ)"
    backup="$STATE/install-backups/$stamp"
    mkdir -p "$DEST" "$STATE/logs" "$backup" "$(dirname "$PLIST")"
    chmod 700 "$DEST" "$STATE" "$STATE/logs" "$STATE/install-backups" "$backup"
    for path in "$DEST/disk_guardian.py" "$DEST/policy.json" "$PLIST"; do
      if [ -f "$path" ]; then
        cp -p "$path" "$backup/$(basename "$path")"
      fi
    done
    install -m 700 "$ROOT/disk_guardian.py" "$DEST/disk_guardian.py"
    install -m 600 "$ROOT/policy.example.json" "$DEST/policy.json"
    /usr/bin/python3 "$DEST/disk_guardian.py" --policy "$DEST/policy.json" self-test >/dev/null
    /usr/bin/python3 "$ROOT/render_launchd.py" \
      --script "$DEST/disk_guardian.py" \
      --policy "$DEST/policy.json" \
      --log "$STATE/logs/launchd.log" \
      --output "$PLIST" --label "$LABEL"
    plutil -lint "$PLIST" >/dev/null
    printf '%s\n' "$backup" > "$STATE/last-install-backup.txt"
    chmod 600 "$STATE/last-install-backup.txt"
    echo "Installed and staged. Review '$DEST/policy.json', then run '$0 enable'."
    ;;
  enable)
    test -f "$PLIST"
    /usr/bin/python3 "$DEST/disk_guardian.py" --policy "$DEST/policy.json" doctor
    launchctl bootstrap "$DOMAIN" "$PLIST"
    launchctl print "$DOMAIN/$LABEL" >/dev/null
    echo "Enabled $LABEL"
    ;;
  status)
    /usr/bin/python3 "$DEST/disk_guardian.py" --policy "$DEST/policy.json" status
    launchctl print "$DOMAIN/$LABEL"
    ;;
  uninstall)
    if launchctl print "$DOMAIN/$LABEL" >/dev/null 2>&1; then
      launchctl bootout "$DOMAIN/$LABEL"
    fi
    backup=""
    if [ -f "$STATE/last-install-backup.txt" ]; then
      backup="$(cat "$STATE/last-install-backup.txt")"
    fi
    rm -f "$PLIST" "$DEST/disk_guardian.py" "$DEST/policy.json"
    if [ -n "$backup" ] && [ -d "$backup" ]; then
      [ ! -f "$backup/disk_guardian.py" ] || install -m 700 "$backup/disk_guardian.py" "$DEST/disk_guardian.py"
      [ ! -f "$backup/policy.json" ] || install -m 600 "$backup/policy.json" "$DEST/policy.json"
      [ ! -f "$backup/$LABEL.plist" ] || install -m 600 "$backup/$LABEL.plist" "$PLIST"
    fi
    rmdir "$DEST" 2>/dev/null || true
    echo "Removed code and LaunchAgent; receipts and logs retained in $STATE."
    ;;
  *)
    echo "usage: $0 {install|enable|status|uninstall}" >&2
    exit 64
    ;;
esac
