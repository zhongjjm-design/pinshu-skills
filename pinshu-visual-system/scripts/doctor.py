#!/usr/bin/env python3
"""Report planning prerequisites; unsupported Python is a failed check."""
import json,sys,shutil,importlib.util
from pathlib import Path
from select_styles import registry
def main():
    r = registry()
    ready = sys.version_info >= (3, 10)
    result = dict(python=sys.version.split()[0], minimum_python='3.10', planning_ready=ready,
        whole_article_dependencies={m:bool(importlib.util.find_spec(m)) for m in ['PIL','markdown_it','bs4']},
        layout_companion=(Path(__file__).resolve().parents[2]/'pinshu-wechat-layout/scripts/build.py').is_file(),
        imagemagick=shutil.which('magick'), bundled_modes=len(r['modes']),
        external_dependencies=sorted({x['external_skill'] for x in r['external_integrations']}),
        image_generation='provided by current agent; must verify actual tool', release=r['version'],
        scope='exit status checks planning Python; export and whole-article prerequisites are reported separately')
    if not ready:
        result['error'] = 'Python 3.10 or newer is required for planning'
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if ready else 1

if __name__ == '__main__':
    raise SystemExit(main())
