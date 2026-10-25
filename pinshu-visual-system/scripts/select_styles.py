#!/usr/bin/env python3
"""Filter compatible styles and resolve short names; the agent judges actual source meaning."""
import argparse,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def registry():return json.loads((ROOT/'references/system-registry.json').read_text())
def select(platform,structure,character=False,skills_dir=None):
 r=registry();out=[]
 for x in r['modes']:
  if platform in x['blocked_platforms'] or (x.get('allowed_platforms') and platform not in x['allowed_platforms']):continue
  if structure not in x['supported_structures']:continue
  if not character and x['character_policy']=='required':continue
  if character and x['character_policy']=='none-only':continue
  out.append(dict(id=x['id'],name=x['short_name'],kind='mode',available=True,uses=x['uses'],card=x['mode_card'],grammar=x['grammar'],requires_direction_confirmation=False))
 roots=[Path(skills_dir)] if skills_dir else [Path.home()/'.agents/skills',Path.home()/'.codex/skills']
 for x in r['external_integrations']:
  if platform not in x['allowed_platforms'] or structure not in x.get('supported_structures',[]) or character:continue
  full=next((root/x['external_skill']/'SKILL.md' for root in roots if (root/x['external_skill']/'SKILL.md').is_file()),None)
  out.append(dict(x,name=x['short_name'],kind='external',available=bool(full),dependency_entry=str(full) if full else None,dependency_sha256=hashlib.sha256(full.read_bytes()).hexdigest() if full else None,requires_direction_confirmation=False,next_step='read full installed dependency and check its terms/tools' if full else 'dependency missing; explain installation option, then offer a compatible bundled style'))
 return dict(version=r['version'],platform=platform,structure=structure,options=out,scope='compatible choices, not semantic ranking or generated images; final image review required')
def handoff(name,content,platform,structure,skills_dir=None,source_image=None):
 r=registry();rid=r.get('aliases',{}).get(name,name)
 if rid in r['held_routes'] or rid in r['retired_routes']:raise ValueError('direction held, frozen or retired')
 choices=select(platform,structure,skills_dir=skills_dir)['options'];x=next((i for i in choices if i['id']==rid),None)
 if not x:raise ValueError('unknown or incompatible style')
 if x['kind']!='external':raise ValueError('use visual_compiler.py for bundled modes')
 if not x['available']:raise ValueError('dependency missing: '+x['external_skill'])
 if x.get('requires_source_image'):
  if not source_image or not Path(source_image).is_file():raise ValueError('source image required')
 if not content.strip():raise ValueError('empty source')
 profiles_path=ROOT/'references/platform-profiles.json'
 profiles=json.loads(profiles_path.read_text())['profiles'];profile=next(p for p in profiles if p['id']==platform)
 return dict(kind='external-handoff',platform=platform,structure=structure,platform_profile=profile,platform_profiles_sha256=hashlib.sha256(profiles_path.read_bytes()).hexdigest(),output_requirement='Return actual image dimensions and inspect exported platform image before review',style=x,source_sha256=hashlib.sha256(content.encode()).hexdigest(),source=content,source_image=str(Path(source_image).resolve()) if source_image else None,source_image_sha256=hashlib.sha256(Path(source_image).read_bytes()).hexdigest() if source_image else None,status='pending-dependency-execution',actual_model=None,instruction='Read the complete dependency entry; preserve source facts and IP=none. Check tool availability and permission before generation. Return actual images, prompts and review evidence. This handoff is not a rendered image.')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--platform',required=True);p.add_argument('--structure',default='single-claim');p.add_argument('--skills-dir',type=Path);p.add_argument('--character',action='store_true');p.add_argument('--style');p.add_argument('--content-file',type=Path);p.add_argument('--source-image',type=Path);a=p.parse_args()
 try:
  r=registry()
  if a.platform not in {i['id'] for i in json.loads((ROOT/'references/platform-profiles.json').read_text())['profiles']} or a.structure not in r['structures']:raise ValueError('unknown platform or structure')
  if a.style:
   if not a.content_file:raise ValueError('handoff requires source content')
   result=handoff(a.style,a.content_file.read_text(),a.platform,a.structure,a.skills_dir,a.source_image)
  else:result=select(a.platform,a.structure,a.character,a.skills_dir)
  print(json.dumps(result,ensure_ascii=False,indent=2))
 except (OSError,ValueError) as e:p.exit(1,'HARD_STOP: '+str(e)+'\n')
if __name__=='__main__':main()
