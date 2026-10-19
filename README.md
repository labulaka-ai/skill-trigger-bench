# skill-trigger-bench

**Don't just ship the SKILL.md. Ship its trigger rate.**

An agent chooses a skill from its name + description alone. If the description is vague, missing, or a placeholder, the skill silently never fires — or a better-described neighbor steals its jobs. This bench measures that: it harvests the runtime descriptions of a skill library, feeds scenario-style user utterances to a router model that sees *only* the catalog, and reports per-skill trigger recall, false triggers, and collision pairs — plus run-to-run repeatability, so a score is never reported without its noise floor.

中文：给 skill 库做触发率体检的工具。自动收割每个 skill 的运行时描述组成目录，让路由器模型只看名称＋描述对口语化说法做单选，统计每个 skill 的触发命中率、误触发（被邻居抢活）和撞车，并附失败原话与重复性。方法、硬规矩与局限见 [SKILL.md](SKILL.md)，完整实测报告见 [evidence/REPORT.md](evidence/REPORT.md)。

## What we found in our own library (24 skills, 84 utterances)

| Round | Setup | Score |
| --- | --- | --- |
| v1 | Original descriptions | 74/82 (90.2%) — positives 64/72, global negatives 10/10 |
| v2 | 4 placeholder descriptions rewritten from the skills' real contents (sandbox catalog) | 80/82 headline — **but see the correction below** |
| v3 | Two fixes actually landed in the live registry; battery corrected | 78/84 (92.9%) |

Three lessons worth stealing:

1. **Placeholder descriptions get robbed.** Six of our skills carried the same placeholder line ("Local skill notes preserved from the previous layout and awaiting review."). The worst scored **0/3** — a neighbor with a rich, domain-claiming description took all three of its utterances (and racked up 3 false triggers doing it). Fixing the victims' descriptions also cured the thief's false triggers: clear boundaries help both sides.
2. **A stub is not fatal — unless a rich neighbor wants your turf.** Two placeholder skills still scored 3/3 on name recognition alone, because nobody else claimed their domain.
3. **A wrong gold + a wrong description can fake a perfect score.** One skill's rewrite scored 3/3 — because both the description and the test battery had been written from the same wrong guess about what the skill does (its name suggested an X-growth playbook; its README says it generates cover and avatar images). An adversarial review that actually read the folder caught it. Hence the bench's hardest rule: **gold labels must be grounded in the skill's real contents; name-inferred gold is flagged and excluded from headline scores.** With that item removed, the honest v1→v2 comparison is 73/79 → 77/79.

**Repeatability:** across two full runs sharing 79 utterances, every flip was explained by a deliberate description change; on the 67 utterances whose descriptions did not change, the router's choices were **67/67 identical**. The bench tracks description changes, not luck — at least within one router model.

## Quick start

```bash
# 1. Harvest the catalog (skill.yaml description, else SKILL.md frontmatter)
python3 scripts/harvest_catalog.py ~/path/to/custom-skills catalog.json

# 2. Write your battery (rules in templates/battery-notes.md)
#    [{"q": "user-style utterance", "gold": "skill_name_or_none", "kind": "pos|neg"}]

# 3. Run (any chat CLI, or any OpenAI-compatible endpoint)
python3 scripts/run_bench.py catalog.json battery.json results.json --model gpt-6-sol --backend cli
# or: OPENAI_BASE_URL=... OPENAI_API_KEY=... python3 scripts/run_bench.py ... --backend openai

# 4. Analyze (add a second results file to get repeatability flips)
python3 scripts/analyze.py results.json
```

The published results were produced with the `cli` backend (an OpenAI-compatible relay, model `gpt-6-sol`, temperature 0, single pick). Raw batteries, catalogs and per-item results for all three rounds are in [`evidence/`](evidence/).

## Layout

- `SKILL.md` — the skill itself (method, hard rules, limitations), in Chinese
- `scripts/` — harvest / run / analyze
- `templates/battery-notes.md` — battery authoring rules, incl. the gold-grounding rule
- `evidence/` — full report (Chinese) + raw data of the three rounds on our library

## Limitations

- The router is a single LLM simulating agent routing; absolute scores are approximate — relative rankings and failure shapes are the trustworthy output.
- n=3 utterances per skill is small; borderline utterances flip when neighboring descriptions change. That's sensitivity, and the report format forces you to disclose it.
- The bench measures discoverability (name + description), not execution quality after the skill is opened. A skill can trigger perfectly and still be an empty shell inside — we found that too, and it needs a separate delivery rehearsal.

## License

MIT. By [Labulaka](https://github.com/labulaka-ai). Sibling project: [video-prompt-verifier](https://github.com/labulaka-ai/video-prompt-verifier) — same philosophy for video prompts: don't claim it, measure it.
