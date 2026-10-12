import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from export_share import export

class SharingTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.image = self.root/'final.png'
        Image.new('RGB',(80,40),'navy').save(self.image)
    def test_share_manifest_has_only_names_and_hashes(self):
        (self.root/'render-receipt.json').write_text(json.dumps({'source':str(self.image)}))
        result = export([self.image], self.root/'share')
        text = result.read_text()
        self.assertNotIn(str(self.root), text)
        item = json.loads(text)['files'][0]
        self.assertEqual('final.png', item['filename'])
        self.assertFalse(Path(item['filename']).is_absolute())
        self.assertEqual(self.image.read_bytes(), (result.parent/item['filename']).read_bytes())
        self.assertEqual(hashlib.sha256(self.image.read_bytes()).hexdigest(), item['sha256'])
        self.assertEqual({'final.png','share-manifest.json'}, {p.name for p in result.parent.iterdir()})
    def test_metadata_rejection_keeps_original_and_no_output(self):
        info=PngInfo();info.add_text('Comment','Private client event')
        Image.new('RGB',(80,40),'navy').save(self.image,pnginfo=info)
        before=self.image.read_bytes()
        with self.assertRaises(ValueError):export([self.image],self.root/'share')
        self.assertEqual(before,self.image.read_bytes());self.assertFalse((self.root/'share').exists())
    def test_alias_and_duplicate_rejected(self):
        alias=self.root/'alias.png';alias.symlink_to(self.image)
        with self.assertRaises(ValueError):export([alias],self.root/'share')
        with self.assertRaises(ValueError):export([self.image,self.image],self.root/'share')

    def test_publish_clean_to_share_preserves_pixels_and_relative_manifest(self):
        import struct, zlib
        from prepare_publish_images import prepare_one, require_magick, png_chunk_types, pixel_difference, is_zero_pixel_difference
        # These are valid metadata chunks, not a private real image.
        data=self.image.read_bytes()
        def chunk(kind, payload):
            return struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(kind+payload))
        extras=chunk(b'tIME',struct.pack('>H5B',2026,10,11,12,0,0))+chunk(b'orNT',b'\x01')
        self.image.write_bytes(data[:-12]+extras+data[-12:])
        before=self.image.read_bytes();prepared=self.root/'prepared';prepared.mkdir()
        magick=require_magick()  # Required integration dependency: no skipped PASS.
        result=prepare_one(magick,self.image,prepared)
        clean=Path(result['publish_copy']);self.assertEqual(result['status'],'PASS')
        self.assertEqual(hashlib.sha256(before).hexdigest(),result['source_sha256'])
        self.assertEqual(hashlib.sha256(clean.read_bytes()).hexdigest(),result['publish_copy_sha256'])
        self.assertNotIn(b'tIME',png_chunk_types(clean.read_bytes()));self.assertNotIn(b'orNT',png_chunk_types(clean.read_bytes()))
        shared=export([clean],self.root/'share');manifest=json.loads(shared.read_text());item=manifest['files'][0]
        self.assertEqual(clean.name,item['filename']);self.assertFalse(Path(item['filename']).is_absolute())
        self.assertNotIn(str(self.root),shared.read_text())
        delivered=shared.parent/item['filename'];self.assertEqual(hashlib.sha256(delivered.read_bytes()).hexdigest(),item['sha256'])
        self.assertEqual(result['publish_copy_sha256'],item['sha256'])
        self.assertEqual(before,self.image.read_bytes());self.assertTrue(is_zero_pixel_difference(pixel_difference(magick,self.image,delivered)))
        with Image.open(self.image) as original, Image.open(delivered) as final:
            self.assertEqual(original.size,final.size);self.assertEqual(original.convert('RGBA').tobytes(),final.convert('RGBA').tobytes())

if __name__=='__main__':unittest.main()
