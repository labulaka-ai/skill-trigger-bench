#!/usr/bin/env python3
"""Skill trigger bench runner.

A router LLM sees ONLY name+description per skill (the same information a
real agent routes on) and single-picks one skill (or none) per battery
utterance, temperature 0.

Router backends:
  --backend cli    : any CLI accepting  chat --model M --system S --prompt P
                     --temperature 0 --max-tokens N  and printing the reply
                     (reference: our local beeapi.py; set --router-cli PATH).
                     This is the backend used for the published results.
  --backend openai : any OpenAI-compatible endpoint. Set OPENAI_BASE_URL and
                     OPENAI_API_KEY in the environment; --model names the model.

Usage: run_bench.py catalog.json battery.json results.json [--model M]
                     [--backend cli|openai] [--router-cli PATH]"""
import json, os, re, subprocess, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
args = sys.argv[1:]
pos = [a for a in args if not a.startswith('--')]
def opt(name, default=None):
    return args[args.index(name) + 1] if name in args else default
MODEL = opt('--model', 'gpt-6-sol'); BACKEND = opt('--backend', 'cli')
ROUTER_CLI = opt('--router-cli', os.path.expanduser('~/workspace/skills/beeapi/bin/beeapi.py'))
cat = json.load(open(pos[0])); bat = json.load(open(pos[1])); out_path = pos[2]
catalog_txt = '\n'.join(f"- {s['name']}: {s['description']}" for s in cat)
SYS = ("You are the skill router of an AI assistant. Below is the skill catalog the assistant can load. "
       "Given a user request, choose the ONE skill the assistant should load for it. If no skill clearly applies, choose none. "
       "Judge only from the catalog text. Reply with JSON only, no other words: {\"choice\": \"<exact skill name or none>\"}\n\nCATALOG:\n" + catalog_txt)
def call_cli(system, prompt):
    r = subprocess.run(['python3', ROUTER_CLI, 'chat', '--model', MODEL, '--system', system,
                        '--prompt', prompt, '--temperature', '0', '--max-tokens', '60'],
                       capture_output=True, text=True, timeout=240)
    return (r.stdout or '') + (r.stderr or '')
def call_openai(system, prompt):
    base = os.environ['OPENAI_BASE_URL'].rstrip('/'); key = os.environ['OPENAI_API_KEY']
    body = json.dumps({'model': MODEL, 'temperature': 0, 'max_tokens': 60,
                       'messages': [{'role': 'system', 'content': system},
                                    {'role': 'user', 'content': prompt}]}).encode()
    req = urllib.request.Request(base + '/v1/chat/completions', data=body,
                                 headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=240) as resp:
        data = json.loads(resp.read())
    return data['choices'][0]['message']['content']
CALL = call_cli if BACKEND == 'cli' else call_openai
def route(item):
    out = ''
    for _ in range(3):
        try: out = CALL(SYS, 'User request: ' + item['q'])
        except Exception as e: out = 'error: ' + str(e)
        m = re.search(r'"choice"\s*:\s*"([^"]+)"', out or '')
        if m: return {**item, 'choice': m.group(1).strip()}
    return {**item, 'choice': 'ERROR:' + (out or '').strip()[-80:]}
if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=6) as ex:
        res = list(ex.map(route, bat))
    json.dump(res, open(out_path, 'w'), ensure_ascii=False, indent=1)
    hit = sum(1 for x in res if x['choice'] == x['gold'])
    print(f"routed {len(res)} items, exact-match {hit} ({hit/len(res):.1%})")
    for x in res:
        if x['choice'] != x['gold']: print('MISS gold=', x['gold'], '| got=', x['choice'], '| q=', x['q'][:40])
