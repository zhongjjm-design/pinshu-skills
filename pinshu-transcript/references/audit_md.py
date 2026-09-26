#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pre-delivery audit for edited transcripts (supports pinshu-transcript production guardrails).

Usage:
  python3 audit_md.py file1.md [file2.md ...] [--dict glossary.md]

Checks: frontmatter structure, body H1 (optional), missing blank lines between adjacent body lines,
leading punctuation, overlong paragraphs (>180 characters), consecutive spaces/trailing whitespace,
duplicate punctuation, em dashes, consistent table column counts, balanced quotation marks and
parentheses, existing images and local links, and residual glossary patterns.

Exit codes: 0 = pass (or warnings only), 1 = errors found.
"""
import os, re, sys, glob


def load_dict_patterns(dict_path):
    pats = []
    if not dict_path or not os.path.exists(dict_path):
        return pats
    text = open(dict_path, encoding='utf-8').read()
    for m in re.finditer(r'^\|([^|\n]+)\|', text, re.M):
        cell = m.group(1).strip()
        if cell and not cell.startswith(('-', ':')) and len(cell) <= 24 and re.search(r'[\u4e00-\u9fffA-Za-z]', cell):
            pats.append(cell)
    return pats


def audit(F, dict_patterns, require_no_h1=True, raw=False):
    errs, warns = [], []
    s = open(F, encoding='utf-8').read()
    lines = s.split('\n')
    if lines[0] != '---':
        errs.append('Missing frontmatter (the file must begin with ---)')
        end = -1
    else:
        if '---' not in lines[1:]:
            errs.append('Unclosed frontmatter')
            end = len(lines)
        else:
            end = lines.index('---', 1)
            for l in lines[1:end]:
                if l.strip() == '':
                    errs.append('Blank line between frontmatter fields')
                    break
            if end + 1 < len(lines) and lines[end + 1].strip() == '---':
                errs.append('Separator --- immediately follows the frontmatter closing line')
    body_start = end + 1
    body = lines[body_start:] if end >= 0 else lines

    def is_q(l): return l.startswith('>')
    def is_t(l): return l.startswith('|')
    def is_l(l): return bool(re.match(r'\s*(?:[-*+]|\d+[.\u3001)])\s', l))

    if require_no_h1 and any(re.match(r'# ', l) for l in body):
        warns.append('Body contains an H1 (treat this as an error when the library standard forbids H1 headings)')

    # Adjacent body lines (excluding frontmatter; consecutive quote, table, and list lines are valid).
    bad = sum(1 for a, b in zip(body, body[1:])
              if a.strip() and b.strip() and not ((is_q(a) and is_q(b)) or (is_t(a) and is_t(b)) or (is_l(a) and is_l(b))))
    if bad:
        errs.append(f'Missing blank line between adjacent body lines: {bad} occurrence(s)')

    # Leading punctuation.
    for i, l in enumerate(body):
        if l.strip() and not l.startswith(('>', '|', '#', '!', '-')) and not re.match(r'\d', l):
            if l.lstrip() and l.lstrip()[0] in '\uff0c\u3002\uff1b\uff1a\u3001\uff09\u300d\u3011\uff05%':
                errs.append(f'Leading punctuation (body line {i+1}): {l[:24]}')
                break

    # Overlong paragraphs.
    if not raw:
        for l in body:
            if l.strip() and not l.startswith(('>', '|', '#', '!', '-')) and not re.match(r'\d+\.\s', l) and len(l) > 180:
                errs.append(f'Paragraph exceeds 180 characters: {l[:28]}...')
                break

    # Punctuation and whitespace.
    if re.search('——', s):
        errs.append('Contains an em dash sequence: ——')
    for pat, label in ([(r'——', 'em dash')] if not raw else []) + [
        (r'\uff0c\uff0c|\u3002\u3002|\uff1b\uff1b|\uff1a\uff0c', 'punctuation error'),
        (r'[ \t]+$', 'trailing whitespace'),
        (r'\S  +\S', 'consecutive spaces within a line'),
    ]:
        if re.search(pat, s, re.M):
            errs.append(label)

    # Residual glossary forms.
    for p in dict_patterns:
        if p and p in s:
            warns.append(f'Residual glossary form: {p}')

    # Consistent table column counts.
    block = []
    tables = []
    for l in body:
        if l.startswith('|'):
            block.append(l)
        else:
            if block:
                tables.append(block)
                block = []
    if block:
        tables.append(block)
    for t in tables:
        cols = {r.count('|') for r in t}
        if len(cols) != 1:
            if any('\\|' in r for r in t):
                cols = {r.replace('\\|', '').count('|') for r in t}
            if len(cols) != 1:
                errs.append(f'Inconsistent table column count: {t[0][:24]}... pipe counts {sorted(cols)}')

    # Paired emphasis markers and emphasis length (check each line to prevent markers spanning paragraphs).
    for li, ll in enumerate(lines):
        if ll.count('**') % 2:
            errs.append(f'Line {li+1} has an odd number of ** markers (unpaired or spanning paragraphs): {ll[:24]}')
            break
    long_bolds = re.findall(r'\*\*([^*\n]{17,})\*\*', s)
    if long_bolds:
        warns.append(
            f'{len(long_bolds)} long emphasized passage(s) '
            f'(the library standard allows emphasis only for short phrases); example: {long_bolds[0][:20]}'
        )

    # Balanced quotation marks and parentheses.
    for a, b, label in [('\u201c', '\u201d', 'double quotation marks'), ('\uff08', '\uff09', 'full-width parentheses'), ('\u300c', '\u300d', 'corner brackets')]:
        if s.count(a) != s.count(b):
            warns.append(f'Unbalanced {label}: {s.count(a)} vs {s.count(b)} (may be source quotation; review manually)')

    # Existing images and local relative links.
    base = os.path.dirname(F)
    for m in re.finditer(r'\]\(([^)#h][^)]*)\)', s):
        p = os.path.normpath(os.path.join(base, m.group(1).strip()))
        if not os.path.exists(p):
            errs.append(f'Missing local link or image: {m.group(1)}')

    return errs, warns


def main():
    args = sys.argv[1:]
    if '-h' in args or '--help' in args:
        print(__doc__)
        sys.exit(0)
    dict_path = None
    raw_mode = '--raw' in args
    if '--raw' in args:
        args.remove('--raw')
    if '--dict' in args:
        i = args.index('--dict')
        dict_path = args[i + 1]
        del args[i:i + 2]
    files = []
    for a in args:
        files.extend(sorted(glob.glob(a)) if any(c in a for c in '*?') else [a])
    if not files:
        print(__doc__)
        sys.exit(2)
    pats = load_dict_patterns(dict_path)
    rc = 0
    for F in files:
        errs, warns = audit(F, pats, raw=raw_mode)
        status = 'PASS' if not errs else 'FAIL'
        print(f'[{status}] {os.path.basename(F)}  errors={len(errs)} warnings={len(warns)}')
        for e in errs:
            print('   x', e)
        for w in warns:
            print('   !', w)
        if errs:
            rc = 1
    sys.exit(rc)


if __name__ == '__main__':
    main()
