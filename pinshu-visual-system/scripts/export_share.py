"""Export explicitly selected, reviewed PNGs; all audit receipts stay local."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import shutil
import struct
import tempfile
import zlib
from PIL import Image

SAFE_CHUNKS = {b'IHDR', b'PLTE', b'IDAT', b'IEND', b'tRNS', b'gAMA', b'cHRM', b'sRGB', b'pHYs'}

def inspect(path):
    if path.is_symlink() or any(p.is_symlink() for p in path.parents):
        raise ValueError('Symlink input is not shareable')
    data = path.read_bytes()
    if len(data) > 30_000_000 or not data.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('Expected a PNG under 30 MB')
    offset = 8
    ended = False
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError('Truncated PNG')
        size = struct.unpack_from('>I', data, offset)[0]
        kind = data[offset+4:offset+8]
        end = offset + 12 + size
        if end > len(data) or kind not in SAFE_CHUNKS:
            raise ValueError('Unapproved PNG metadata or malformed chunk')
        payload = data[offset+8:end-4]
        crc = struct.unpack_from('>I', data, end-4)[0]
        if zlib.crc32(kind+payload) != crc:
            raise ValueError('PNG checksum mismatch')
        offset = end
        if kind == b'IEND':
            ended = True
            break
    if not ended or offset != len(data):
        raise ValueError('Missing end or unapproved trailing data')
    with Image.open(path) as image:
        if image.width * image.height > 20_000_000:
            raise ValueError('Image exceeds 20 million pixels')
        image.load()
    return data

def export(images, output):
    output = Path(output)
    if output.exists():
        raise FileExistsError(output)
    names = set()
    files = []
    for image in images:
        image = Path(image)
        if re.search(r"[\\/:]", image.name):
            raise ValueError("Share filenames must be simple relative names")
        if image.name in names or image.name == 'share-manifest.json':
            raise ValueError('Duplicate filename')
        names.add(image.name)
        files.append((image.name, inspect(image)))
    if not files:
        raise ValueError('Select at least one reviewed final PNG')
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.share-stage-', dir=output.parent))
    try:
        manifest = {'scope':'explicitly-selected-final-images', 'local_receipts_included':False,
                    'rights_and_human_acceptance':'requires-author-review', 'files':[]}
        for name, data in files:
            (stage/name).write_bytes(data)
            manifest['files'].append({'filename':name, 'sha256':hashlib.sha256(data).hexdigest()})
        (stage/'share-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
        if output.exists():
            raise FileExistsError(output)
        stage.rename(output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return output/'share-manifest.json'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', type=Path, action='append', required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    print(export(args.image, args.output_dir))
