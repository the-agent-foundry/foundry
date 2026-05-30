#!/usr/bin/env python3
"""
Content QA Gate — Mechanical anti-slop checker.
Run against any draft before sending to Darryl.
Returns non-zero exit code if violations found.
"""

import sys
import re

BANNED_CHARS = {
    '—': 'Em dash (ZERO TOLERANCE)',
    '–': 'En dash (use hyphen or rewrite)',
}

BANNED_WORDS = [
    'synergy', 'game-changer', 'game changer', 'north star', 'delight',
    'world-class', 'world class', 'stakeholder', 'best practices',
    'unprecedented', 'pivotal', 'groundbreaking', 'landmark',
    'rapidly evolving', 'in today\'s', 'it could be argued',
    'nestled', 'breathtaking', 'vibrant', 'dynamic', 'thriving',
    'cutting-edge', 'cutting edge', 'state-of-the-art',
    'experts believe', 'analysts say', 'studies show',
    'research suggests', 'industry leaders note',
]

BANNED_STARTERS = [
    'Additionally,', 'Furthermore,', 'Moreover,',
    'Great question', 'I\'d be happy to', 'Absolutely,',
]

WARN_PATTERNS = [
    (r'\b(showcasing|highlighting|demonstrating|illustrating|signaling|symbolizing|reflecting)\b',
     'Superficial -ing analysis chain'),
    (r'It\'s not just .+, it\'s',
     'Faux-depth "not just X, it\'s Y" formula'),
    (r'(?:agree|thoughts)\s*[?]?\s*[👇💬🔥]',
     'LinkedIn bro-post ending'),
]


def check_content(text):
    violations = []
    warnings = []
    lines = text.split('\n')

    # Check banned characters
    for char, desc in BANNED_CHARS.items():
        count = text.count(char)
        if count > 0:
            violations.append(f'🚨 FAIL: {desc} — found {count} instance(s)')

    # Check banned words (case-insensitive)
    text_lower = text.lower()
    for word in BANNED_WORDS:
        if word.lower() in text_lower:
            violations.append(f'🚨 FAIL: Banned word/phrase: "{word}"')

    # Check banned starters
    for starter in BANNED_STARTERS:
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(starter):
                violations.append(f'🚨 FAIL: Banned paragraph starter "{starter}" on line {i+1}')

    # Check warning patterns
    for pattern, desc in WARN_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            warnings.append(f'⚠️  WARN: {desc} — {len(matches)} instance(s)')

    # Exclamation mark count
    excl_count = text.count('!')
    if excl_count > 1:
        warnings.append(f'⚠️  WARN: {excl_count} exclamation marks (max 1 per piece)')

    # Emoji check
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U0001f900-\U0001f9FF"
        "]+", flags=re.UNICODE
    )
    emojis = emoji_pattern.findall(text)
    if emojis:
        warnings.append(f'⚠️  WARN: Emojis found: {emojis[:5]}')

    return violations, warnings


def main():
    if len(sys.argv) < 2:
        # Read from stdin
        text = sys.stdin.read()
        source = 'stdin'
    else:
        filepath = sys.argv[1]
        with open(filepath, 'r') as f:
            text = f.read()
        source = filepath

    violations, warnings = check_content(text)

    print(f'📋 Content QA Gate — checking {source}')
    print(f'   Word count: {len(text.split())}')
    print()

    if violations:
        print('🚨 VIOLATIONS (must fix before sending):')
        for v in violations:
            print(f'   {v}')
        print()

    if warnings:
        print('⚠️  WARNINGS (review before sending):')
        for w in warnings:
            print(f'   {w}')
        print()

    if not violations and not warnings:
        print('✅ PASSED — No violations or warnings found.')
    elif not violations:
        print('✅ PASSED with warnings — No hard violations.')
    else:
        print(f'❌ FAILED — {len(violations)} violation(s) found. Fix before sending.')
        sys.exit(1)


if __name__ == '__main__':
    main()
