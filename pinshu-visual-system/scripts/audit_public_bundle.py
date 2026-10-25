#!/usr/bin/env python3
"""Scan text members including hidden/extensionless files; report locations only."""
import argparse
import json
from pathlib import Path
import re
import zipfile

PATTERNS = {
    'user_home': re.compile(re.escape('/' + 'Users' + '/')),
    'linux_home': re.compile(re.escape('/' + 'home' + '/')),
    'codex_documents': re.compile(re.escape('Documents' + '/' + 'Codex')),
    'vault_documents': re.compile(re.escape('Documents' + '/' + 'MyAIClone')),
    'api_secret': re.compile(r'\bsk-[A-Za-z0-9_-]{20,}'),
    'github_secret': re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})'),
    'bearer_secret': re.compile(r'(?i)\bBearer\s+[A-Za-z0-9_.~+/-]{20,}'),
    'jwt': re.compile(r'\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}'),
    'private_key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'assigned_secret': re.compile(r'''(?i)["']?(?:api[_-]?key|access[_-]?token|secret[_-]?key|password)["']?\s*[:=]\s*["'][A-Za-z0-9_/+=.-]{16,}["']'''),
    'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'),
    'private_identity': re.compile(r'(?:\.codex/(?:attachments|generated_images)/|' + 'pinshu' + '-mature|' + 'heguang' + '-xiansheng)'),
}

def inspect_members(members):
    hits, files, text_files = [], 0, 0
    for name, data in members:
        files += 1
        if '.video_agent' in Path(name).parts:
            hits.append(dict(file=name, category='private_plugin_directory', line=0))
        try:
            if data.startswith((b'\xff\xfe\x00\x00', b'\x00\x00\xfe\xff')):
                text = data.decode('utf-32')
            elif data.startswith((b'\xff\xfe', b'\xfe\xff')):
                text = data.decode('utf-16')
            else:
                text = data.decode('utf-8-sig')
        except UnicodeDecodeError:
            continue
        text_files += 1
        for category, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                hits.append(dict(file=name, category=category,
                                 line=text.count('\n', 0, match.start()) + 1))
    counts = {c: sum(h['category'] == c for h in hits)
              for c in list(PATTERNS) + ['private_plugin_directory']}
    return dict(status='PASS' if not hits else 'FAIL', files=files, text_files=text_files,
                counts=counts, hits=hits,
                scope='all UTF-8 and BOM-marked UTF-16/32 text members including hidden/extensionless; pattern scan, not proof of all possible secrets')

def audit_root(root):
    root = Path(root)
    # rglob includes dot-directories; never filter by extension.
    return inspect_members((str(p.relative_to(root)), p.read_bytes())
                           for p in sorted(root.rglob('*')) if p.is_file())

def audit_zip(archive):
    with zipfile.ZipFile(archive) as z:
        return inspect_members((i.filename, z.read(i)) for i in z.infolist())

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--root', type=Path)
    source.add_argument('--zip', type=Path)
    args = parser.parse_args()
    result = audit_zip(args.zip) if args.zip else audit_root(args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
