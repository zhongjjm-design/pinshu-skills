#!/usr/bin/env python3
"""Check the actual intended/saved image-tool prompt against its compiled plan. No API call."""
import argparse,json,hashlib
from pathlib import Path
def verify(plan,request):
 expected=plan.get('prompt','');actual=request.get('prompt','')
 if not expected or not isinstance(actual,str) or expected not in actual:raise ValueError('Full compiled prompt missing or shortened; preserve source and complete mode card before generating')
 return dict(status='PASS',compiled_prompt_sha256=hashlib.sha256(expected.encode()).hexdigest(),actual_prompt_sha256=hashlib.sha256(actual.encode()).hexdigest(),scope='prompt continuity only; does not prove tool execution, source truth, visual quality or user approval')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',required=True,type=Path);p.add_argument('--request',required=True,type=Path);a=p.parse_args()
 try:print(json.dumps(verify(json.loads(a.plan.read_text()),json.loads(a.request.read_text())),ensure_ascii=False,indent=2))
 except (OSError,ValueError,TypeError) as e:p.exit(1,'HARD_STOP: '+str(e)+'\n')
if __name__=='__main__':main()
