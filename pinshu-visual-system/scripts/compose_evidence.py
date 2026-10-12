#!/usr/bin/env python3
"""Compose disclosed, unscaled source-image details and update one article asset."""
import argparse
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
from PIL import Image
from capture_evidence import sha


def is_montage(asset):
    return 'montage' in asset.get('capture_receipt', {}).get('capture_method', '')


def compose_pixels(original, recipe):
    size = recipe.get('delivery_size', [])
    regions = recipe.get('regions_native_pixels', [])
    if (len(size) != 2 or any(type(v) is not int or v <= 0 for v in size)
            or size[0] * size[1] > 40_000_000 or not regions):
        raise ValueError('Montage needs bounded delivery_size and native regions')
    with Image.open(original) as image:
        source = image.convert('RGB')
    canvas = Image.new('RGB', tuple(size), 'white')
    occupied = []
    for region in regions:
        box, target = region.get('source_box', []), region.get('paste_xy', [])
        if (not region.get('role') or len(box) != 4 or len(target) != 2
                or any(type(v) is not int for v in box + target)):
            raise ValueError('Each region needs role, integer source_box and paste_xy')
        x1, y1, x2, y2 = box
        x, y = target
        if not (0 <= x1 < x2 <= source.width and 0 <= y1 < y2 <= source.height):
            raise ValueError('Native region outside original pixels')
        end_x, end_y = x + x2 - x1, y + y2 - y1
        if not (0 <= x < end_x <= canvas.width and 0 <= y < end_y <= canvas.height):
            raise ValueError('Pasted region outside montage canvas')
        if any(x < b[2] and end_x > b[0] and y < b[3] and end_y > b[1] for b in occupied):
            raise ValueError('Montage regions overlap; source evidence must not be covered')
        occupied.append((x, y, end_x, end_y))
        canvas.paste(source.crop(tuple(box)), (x, y))
    return canvas


def validate_montage(asset, delivered, original):
    if not is_montage(asset):
        return
    receipt = asset['capture_receipt']
    if receipt.get('original_sha256') != sha(original) or receipt.get('delivery_sha256') != sha(delivered):
        raise ValueError('Montage receipt must bind original and delivery hashes')
    if asset.get('frame_baked', False):
        raise ValueError('New montage must be unframed; layout adds its frame')
    expected = compose_pixels(original, receipt)
    with Image.open(delivered) as image:
        actual = image.convert('RGB')
    if actual.size != expected.size or actual.tobytes() != expected.tobytes():
        raise ValueError('Montage pixels differ from native crop recipe')


def disclosed_caption(asset):
    caption = asset.get('caption') or ('截图来源：' + asset.get('attribution', ''))
    if '局部拼接' not in caption:
        caption += '｜局部拼接'
    return caption


def compose(plan_path, filename, recipe_path, out):
    plan_path, out = plan_path.resolve(), out.resolve()
    if out.exists():
        raise FileExistsError(out)
    before = plan_path.read_bytes()
    plan = json.loads(before)
    def locate(value):
        path = Path(value)
        return (path if path.is_absolute() else plan_path.parent / path).resolve()
    if sha(locate(plan['source_md'])) != plan['article_sha256']:
        raise ValueError('Article changed; review anchors before composition')
    matches = [a for a in plan['assets'] if (a.get('filename') or Path(a.get('file', '')).name) == filename]
    if len(matches) != 1 or Path(filename).name != filename or Path(filename).suffix.lower() != '.png':
        raise ValueError('Select one existing PNG evidence asset by its handoff filename')
    asset = matches[0]
    if asset['asset_kind'] != 'evidence-screenshot':
        raise ValueError('Only evidence screenshots use native detail montage')
    original = locate(asset['original_file'])
    receipt = copy.deepcopy(asset.get('capture_receipt', {}))
    if (receipt.get('original_sha256', receipt.get('raw_sha256')) != sha(original)
            or receipt.get('source_url') != asset.get('source_url')
            or not receipt.get('captured_at') or receipt['captured_at'] != asset.get('captured_at')):
        raise ValueError('Need an original/source/date-bound capture receipt')
    recipe = json.loads(recipe_path.read_text())
    caption = recipe.get('caption', '').strip()
    if '局部拼接' not in caption:
        raise ValueError('Recipe caption must disclose 局部拼接 and describe the selected evidence')
    canvas = compose_pixels(original, recipe)
    if plan_path.read_bytes() != before:
        raise ValueError('Plan changed during composition')
    out.mkdir(parents=True)
    (out/'输入配图任务.json').write_bytes(before)
    (out/'拼接取景.json').write_bytes(recipe_path.read_bytes())
    target = out/filename
    canvas.save(target)
    receipt.update(capture_method='native-source-image-detail-montage',
        delivery_size=list(canvas.size), regions_native_pixels=recipe['regions_native_pixels'],
        delivery_sha256=sha(target), original_file=str(original), original_sha256=sha(original),
        frame_baked=False, composition_disclosure=caption,
        processed_at=datetime.now(timezone.utc).isoformat(), exact_region_pixels_verified=True,
        mobile_review={'state':'pending','reason':'原生局部拼接后须重新看整篇手机图'})
    asset.update(file=str(target), original_file=str(original), filename=filename,
        capture_receipt=receipt, caption=caption, frame_baked=False,
        mobile_review=receipt['mobile_review'], review_state='局部拼接已生成；当前图意与手机审看待核')
    asset.setdefault('processing', []).append('原图局部仅裁切平移；不重画、不放大；图注明示局部拼接')
    validate_montage(asset, target, original)
    (out/'截图回执.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
    if plan_path.read_bytes() != before:
        raise ValueError('Plan changed; output kept but input plan was not replaced')
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2)+'\n')
    return target


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--filename', required=True)
    p.add_argument('--recipe', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    a=p.parse_args()
    print(compose(a.plan, a.filename, a.recipe, a.output_dir))
