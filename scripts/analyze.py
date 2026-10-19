#!/usr/bin/env python3
"""Analyze bench results: per-skill recall, false triggers, confusion pairs.
Optionally compare two runs for repeatability (flips on shared items).
Usage: analyze.py results.json [results_run2.json]"""
import json, sys, collections
def load(fn): return json.load(open(fn))
res = load(sys.argv[1])
names = sorted({x['gold'] for x in res if x['gold'] != 'none'} | {x['choice'] for x in res if x['choice'] not in ('none',) and not x['choice'].startswith('ERROR')})
per = {n: [0, 0, 0] for n in names}  # hit, gold, false_triggers
conf = collections.Counter()
for x in res:
    if x['gold'] != 'none':
        per[x['gold']][1] += 1
        if x['choice'] == x['gold']: per[x['gold']][0] += 1
    if x['choice'] in per and x['choice'] != x['gold']: per[x['choice']][2] += 1
    if x['choice'] != x['gold']: conf[(x['gold'], x['choice'])] += 1
print(f"{'skill':46s} recall  false_trig")
for n in names: print(f"{n:46s} {per[n][0]}/{per[n][1]}     {per[n][2]}")
neg = [x for x in res if x['gold'] == 'none']
print('global negatives correct:', sum(1 for x in neg if x['choice'] == 'none'), '/', len(neg))
print('confusion pairs:', dict(conf))
if len(sys.argv) > 2:
    r2 = {(x['q'], x['gold']): x['choice'] for x in load(sys.argv[2])}
    shared = [(x, r2[(x['q'], x['gold'])]) for x in res if (x['q'], x['gold']) in r2]
    flips = [(x['gold'], x['choice'], c2, x['q'][:30]) for x, c2 in shared if c2 != x['choice']]
    print(f'repeatability: {len(shared)} shared items, {len(flips)} flipped')
    for f in flips: print('FLIP', f)
