#!/usr/bin/env python3
"""Harvest the runtime skill catalog from a custom-skills directory.

Descriptor source of truth (verified 2026-10-19): each skill folder's
skill.yaml `description:` field; folders without skill.yaml fall back to the
SKILL.md YAML frontmatter `description:`. Folders with neither are reported
as UNREGISTERED (the router never sees them).
Usage: harvest_catalog.py [skills_dir] [out_json]"""
import json, os, re, sys
import yaml

def from_frontmatter(md_path):
    try: txt = open(md_path, encoding='utf-8').read(6000)
    except OSError: return None
    if not txt.startswith('---'): return None
    end = txt.find('\n---', 3)
    if end < 0: return None
    try: fm = yaml.safe_load(txt[3:end])
    except Exception: return None
    return (fm or {}).get('description')

def main():
    skills_dir = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else '~/workspace/custom-skills')
    out = sys.argv[2] if len(sys.argv) > 2 else 'catalog.json'
    catalog, missing = [], []
    for name in sorted(os.listdir(skills_dir)):
        d = os.path.join(skills_dir, name)
        if not os.path.isdir(d): continue
        desc, src = None, None
        y = os.path.join(d, 'skill.yaml')
        excluded = False
        if os.path.exists(y):
            try:
                data = yaml.safe_load(open(y, encoding='utf-8')) or {}
                desc, src = data.get('description'), 'skill.yaml'
                reg_name = data.get('name') or name.replace('-', '_')
                excluded = data.get('include_in_prompt') is False
            except Exception:
                reg_name = name.replace('-', '_')
        if excluded:
            missing.append(name + ' (include_in_prompt: false)')
            continue
        else:
            reg_name = name.replace('-', '_')
        if not desc:
            desc, src = from_frontmatter(os.path.join(d, 'SKILL.md')), 'SKILL.md frontmatter'
        if desc: catalog.append({'name': reg_name, 'folder': name, 'description': str(desc).strip(), 'source': src})
        else: missing.append(name)
    json.dump(catalog, open(out, 'w'), ensure_ascii=False, indent=1)
    print(f'harvested {len(catalog)} skills -> {out}')
    if missing: print('NOT IN CATALOG (no description, or include_in_prompt: false):', ', '.join(missing))

if __name__ == '__main__': main()
