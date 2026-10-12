"""Separate the opening YAML file-information block without changing body bytes.

The ready-folder contract uses a flat mapping of string scalars; no YAML runtime
is needed. General layout stripping does not interpret arbitrary YAML values.
"""
import json


def split_header(data):
    clean = data[3:] if data.startswith(b'\xef\xbb\xbf') else data
    lines = clean.splitlines(keepends=True)
    if not lines or lines[0].rstrip(b'\r\n') != b'---':
        return b'', data
    for i, line in enumerate(lines[1:], 1):
        if line.rstrip(b'\r\n') in {b'---', b'...'}:
            return b''.join(lines[1:i]), b''.join(lines[i + 1:])
    raise ValueError('Unclosed Markdown frontmatter')


def read_metadata(data):
    header, body = split_header(data)
    if not header:
        raise ValueError('Ready article/publishing kit needs opening YAML file information')
    result = {}
    for line in header.decode('utf-8').splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if line[:1].isspace() or ':' not in line:
            raise ValueError('File information must be flat YAML string fields')
        key, value = line.split(':', 1)
        key, value = key.strip(), value.strip()
        if key in result:
            raise ValueError('Duplicate file-information field: ' + key)
        if not key or not value.startswith('"'):
            raise ValueError('Use a double-quoted YAML string for ' + key)
        value = json.loads(value)
        if not isinstance(value, str):
            raise ValueError('File-information values must be strings')
        result[key] = value
    return result, body
