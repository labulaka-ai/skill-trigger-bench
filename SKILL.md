# Skill 触发率实测器（skill-trigger-bench）

测一个 skill 库里每个 skill 的**触发命中率、误触发与撞车**：agent 选 skill 时只看名称＋描述，描述写得好不好决定它会不会被用起来。这个工具把「晒 skill 要晒触发率」变成可复跑的体检。

## 原理

把「名称＋描述目录」和一条用户说法交给一个路由器模型（temperature 0、单选、最多选 1 个或 none），条件与真实 agent 路由一致。统计：正例命中率（recall）、误触发（被选去答别人的题）、撞车对（gold → 被谁抢走）、全局负例的乱触发率。

## 流程

1. **收割目录**：`python3 scripts/harvest_catalog.py [skills目录] [输出json]`
   描述来源：各 skill 文件夹 `skill.yaml` 的 `description:` 字段；无 skill.yaml 时读 SKILL.md 的 YAML frontmatter。带 `include_in_prompt: false` 或两者都没有的文件夹会被单独列出——它们进不了路由目录，这本身就是体检结果。注意：个别无 skill.yaml 的 skill，运行时目录给的描述可能与文件 frontmatter 不一致，此时以运行时实际下发的描述为准。
2. **编题库**：按 `templates/battery-notes.md` 的规矩写 battery.json（每 skill 3 条场景化正例＋邻近防抢题＋10 条全局负例）。
3. **跑测**：`python3 scripts/run_bench.py catalog.json battery.json results.json --model <模型> [--backend cli|openai]`
   cli 后端接任何 `chat --model/--system/--prompt` 形态的命令行工具；openai 后端接任何 OpenAI 兼容端点（环境变量 OPENAI_BASE_URL / OPENAI_API_KEY）。80 余条一轮通常要数分钟到数十分钟（取决于服务商响应），请用能等它跑完的方式执行；失败条目重试 3 次后记为 ERROR 并如实出现在结果里，不冒充分数。
4. **分析**：`python3 scripts/analyze.py results.json [第二轮results.json]`
   出每 skill 命中/误触发、混淆对；给两轮结果时另出重复性（共享题目的翻转数）。
5. **（可选）修复复测**：给最差的 skill 按**真实内容**改描述，同题库全量复测，重点看两件事：目标涨回来没有、邻居有没有被反抢。

## 硬规矩

- **gold 必须读过 skill 真实内容才能标**（SKILL.md 本体／README／子目录结构）。凭名称推断的 gold 打 `"gold_basis": "inferred"` 并排除出头条分数。教训（2026-10-19 实测）：一个名为 punk 的视觉生成 skill 被凭名字当成 X 起号 playbook，描述与题库同按错误前提写成，互相对出 3/3 假成绩——评审读了 README 才发现张冠李戴。
- **分数必须带重复性**：同一题库至少留两轮结果，报翻转数当噪声底；描述没变而选择翻转的题目要逐条列出。临界题（两个 skill 描述都沾边）天然会翻，±1 条不作结论。
- **绝对分数只看大概，相对排名与失败形态才是结论**：路由器是单个模型模拟，与真实 agent 的选择可能有系统差；每 skill n=3 样本小。
- **触发≠交付**：描述修好只解决「被认出来」。若 skill 顶层 SKILL.md 是空壳、真内容埋在子目录且不指路，先补入口再改描述，不然触发率涨了、agent 进门照样找不到活干。

## 局限

- 只测「名称＋描述」这一层路由，不测 agent 读完 SKILL.md 后的执行质量（那是交付演练的事，要另做真请求全程测试）。
- 题库由人编写，口语化程度与场景覆盖会影响绝对值；换题库必须重新基线。
- 路由模型更换（或服务商后端漂移）会改变基线，报告必须注明模型与日期。
