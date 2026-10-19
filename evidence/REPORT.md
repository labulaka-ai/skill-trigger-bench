# Skill 触发率实测报告（第一轮）

日期：2026-10-19　执行：Labulaka

## 方法（口径先行）
- 路由器：路由器模型 gpt-6-sol（OpenAI 兼容中转），temperature 0，单选（最多选 1 个 skill，或 none）。它只能看到每个 skill 的**名称＋运行时描述**——与真实 agent 触发 skill 时看到的信息一致（多数 SKILL.md 没有 frontmatter 描述，运行时目录描述才是 agent 实际依据；描述取自运行时注册口径，非文件原文）。
- 目录：custom-skills 里已注册的 24 个自家 skill。另有 2 个目录（codebase_index_before_writing、recovered-skill-notes）未注册、无描述，路由器根本看不见，未纳入。
- 题库：82 条。每 skill 3 条正例（共 72），按真实使用场景写成口语化说法，**刻意不照抄描述关键词**；另 10 条与任何 skill 无关的日常请求作全局负例（天气、翻译、订机票、数学题等）。每条题有唯一标准答案。题库在 battery.json，结果在 results.json / results_v2.json。
- 指标：正例命中率（recall）、误触发（被选去答别人的题）、撞车对（gold→被抢去的 skill）。

## v1 结果（原描述）：74/82（90.2%）
- 正例命中 64/72（88.9%）；全局负例 10/10 全部正确拒绝——**没有乱触发**。
- 19/24 个 skill 满分 3/3。
- 全部 8 条失败：
  1. local_figures4papers 0/3，三条全被 local_plot_is_all_you_need 抢走（原话：「按顶刊的绘图规范帮我把这组实验数据图重做一下」「figures4papers那套matplotlib规范，套到我这张消融图上」「投稿用的图要符合顶会风格，你按那个绘图库的规范来」）。
  2. local_punk_xhs_cards 1/3，两条被 local_guizang_social_card_skill 抢走（「做一套小红书卡片，要punk一点的风格」「小红书图文卡换个更抓眼的版式，用之前收的那套」）。
  3. local_punk_skill 1/3：一条被 local_creator_buddy 抢走（「按Adrian Punk那套打法，我的X账号冷启动该怎么排帖」），一条无人接（「X起号的playbook你按我们装的那套来执行一遍」→ none）。
  4. local_seedance_prompt_skill 2/3：一条无人接（「即梦上跑视频，提示词怎么写才稳」→ none）。
- 「小偷」榜（被选次数 − 本分）：plot_is_all_you_need 被选 6 次（3 真 + 3 误）、guizang 5 次（3 + 2）、creator_buddy 4 次（3 + 1）。**描述写得最全的 skill 会把邻居的活也揽走。**

## 根因
6 个 skill 的运行时描述是同一句占位符「Local skill notes preserved from the previous layout and awaiting review.」，其 SKILL.md 打开只有「回收的旧笔记」套话、没写自己是谁（figures4papers、punk-skill、punk-xhs-cards、seedance-prompt、video-publisher、yichen-skills）；xilo 的描述只有「用代码做视频」一句。但占位符≠必死：video_publisher、yichen 同为占位符却 3/3——**没有富邻居抢领域时，光靠名字能活；有富邻居时必死**。这是本轮测出的规律。

## 修复轮 v2：80/82（97.6%）
按 4 个失败 skill 文件夹里的**真实内容**重写描述（全文在 catalog_v2.json；每条都写了与富邻居的分界句），同题库全量复测：
- figures4papers 0/3 → **3/3**；punk_skill 1/3 → **3/3**；seedance 2/3 → **3/3**；punk_xhs_cards 1/3 → **2/3**。
- 误触发同步清零方向：plot 3 → 0，creator_buddy 1 → 0，guizang 2 → 1。**给受害者补描述，顺带治好了小偷的误报**（领域边界一清楚，两边都受益）。
- 剩余 2 条未中：
  1. knowledge_explainer 的「把这篇文档转成带动画的讲解片，Remotion渲染」被 anything2explainer 拿走——真撞车：anything 的描述里明写「document turned into a video」，而 knowledge 的描述只有一行、没写清「markdown/笔记输入、本地跑、不依赖云 API」的分界。此条 v1 曾答对、v2 翻转，说明临界题有跑次波动，±1 条属正常噪声。修复建议已备（扩写其描述），本轮未复测。
  2. punk_xhs 的「用之前收的那套」靠内部指代，任何目录都解析不了，且「小红书图文卡」是 guizang 的原词触发语——一半是题目artifact，一半是残余重叠。

## 局限（不许当没说）
- 路由器是单个模型（gpt-6-sol）模拟，与真实 agent 的选择可能有系统差；绝对分数看个大概，**跨 skill 相对比较与失败形态比绝对值可信**。
- 每 skill n=3，样本小；正例由执行者撰写，口语化程度影响绝对值。
- 占位符 skill 的正例标准答案是按文件夹名称与实际内容推断的用户意图——测的正是「没描述就没法被认出来」这一失败模式本身。
- 描述若落地到真实注册（SKILL.md/skill.yaml），运行时目录会重新生成，本 bench 的 catalog 需随之更新再复测。

## 文件清单
catalog.json（v1 目录）/ catalog_v2.json（修复后）/ battery.json / run_bench.py / results.json / results_v2.json / stats.json / compare.py / REPORT.md

## 订正与写回讨论（2026-10-19 下午，两个 subagent 分工复核后追加）

### 订正：punk_skill 的 v2 成绩作废（执行者错误）
- v2 给 local_punk_skill 写的描述（「Adrian Punk's X growth playbook…冷启动/发帖节奏」）是**张冠李戴**：执行者凭名称与运营手册里的同名概念推断、没读文件夹 README。该 skill 真身（README 原文）是一组**视觉生成** skill：`skills/punk-cover/`（给小红书/公众号/X 生成封面图）＋`skills/punk-avatar/`（生成头像图）＋25+ 封面风格库。与 X 起号毫无关系（X 运营 playbook 在运营手册里，不在这个 skill 里）。
- 题库里 punk_skill 的 3 条正例按同一错误前提标注 gold，故其 v1 1/3、v2 3/3 均**不计分**。剔除这 3 条无效题后的修正口径：79 条有效题，v1 73/79 → v2 77/79；figures4papers 0→3、seedance 2→3、punk_xhs 1→2 的结论不受影响。97.6% 的原标题数字自此作废，引用以本节为准。

### 机制查明（subagent A，只读实查）
- 运行时描述的事实源＝每个 skill 的 `skill.yaml` 的 `description:` 字段（有 skill.yaml 时以它为准；无 skill.yaml 的两个 skill 才读 SKILL.md frontmatter）。`~/config/skills.yaml` 是连接器状态表、与此无关。占位符就写在这 6 个 skill.yaml 里。改进回路会写 skill.yaml 的元数据字段，未见其重置 description 的证据；手改风险低，备份＋复核可兜底。

### 对抗评审（subagent B）与最终处置
- 共同真问题：这批 skill 顶层 SKILL.md 是空壳套话，真内容埋在子目录且顶层不指路（seedance 在 `.claude/skills/seedance/`、punk-xhs 真身在内层 `punk-xhs-cards/SKILL.md`、figures4papers 规范在 `scientific-figure-making/`）。**只改描述＝门牌擦亮、屋里没路牌，触发涨了交付仍断链。**正确顺序：先补顶层入口 → 描述从入口长出来 → 修正题库 → 复测。
- local_knowledge_explainer_skill：本体完整、只差描述，**已按评审成稿写回 skill.yaml 并验证运行时索引已生效**（skill_search 回读为新描述；原文件备份在 skill-yaml-backup-20261019/）。
- 其余处置：punk_skill 描述须按真身重写且题库 gold 同步修正（新领域与 guizang/punk-xhs 相邻，整组复测）；figures4papers 现稿措辞偏满（本体是已发表顶会图的脚本示例库＋一处 house style 规范子目录），降格后再落地；punk_xhs 应让顶层入口指向内层真 SKILL.md、描述须含「个人 IP 前置＋三道人工确认门」；seedance 描述基本属实，与「顶层 SKILL.md 补一行指路」同批落地才放行。

## v3 复测与检测器自身验证（2026-10-19 傍晚）

### v3 口径
catalog_v3 = v1 目录，仅两处换成已写回真实注册的现行描述（knowledge 扩写版、punk 真身版）；其余 22 家与 v1 相同（含 figures/seedance/punk-xhs 仍为占位符——它们的改稿只在 v2 沙盒目录里验过、未写回）。题库 battery_v3：punk 3 条无效题按真身重写＋新增像素头像题（共 4 条），归藏新增 1 条成套卡片防抢题，总 84 条。

### v3 结果：78/84（92.9%）
- local_punk_skill（真身题＋真身描述）：**4/4**；且未反抢——归藏 4/4（含其公众号成对封面题与新增成套卡片题），单张封面归 punk、成套/成对归归藏，分界成立。
- local_knowledge_explainer_skill（扩写描述已落地）：**3/3**，v2 里被 anything 抢走的那条已回收。
- 未落地的三家与 v1 完全一致（预期内）：figures4papers 0/3（仍被 plot 抢）、punk_xhs 1/3（仍被归藏抢 2）、seedance 2/3（即梦一条仍 none）。证明分数跟踪的是描述状态、不是随机漂移。
- 全局负例仍 10/10。

### 检测器重复性（噪声底）
v2 与 v3 两轮共享 79 条题目，共 6 条选择翻转，**全部可由两轮间故意的描述变更解释**（figures/v2 改稿→v3 占位符 ×3、punk_xhs 改稿→占位符 ×1、seedance 改稿→占位符 ×1、knowledge 旧→扩写 ×1）。描述未变更的 67 条共享题，两轮选择 **67/67 完全一致**。即本检测器在同模型、同题库下的跑次噪声底为 0/67（本轮样本）；临界翻转只发生在描述被改动的邻域——这是灵敏度，不是噪声。口径限制：仅两轮、同一路由器模型（gpt-6-sol）。

### 机制订正（打包收割时查明）
- codebase_index_before_writing 并非「无描述未注册」：它有完整 skill.yaml 描述，但 `include_in_prompt: false`，是被开关排除在路由目录外。此前「没有描述、路由器看不见」的说法修正为「有描述、被 include_in_prompt 关掉」。
- recovered-skill-notes 有 skill.yaml、描述同为占位符句，属元条目；收割脚本默认收录，操作者可剔除。
- 收割以文件为准与以运行时 skill_search 为准有一处分歧：local_xilo_opus_video 无 skill.yaml，其 SKILL.md frontmatter 是完整英文长描述，但运行时目录给它的描述只有「用代码做视频」一行——无 skill.yaml 的文件夹，运行时描述可能另有来源（未查明），以运行时口径为准。本报告 v1–v3 的 xilo 条目用的是运行时短描述。
- 手工目录另有一处截断：video-prompt-verifier 描述手工版 462 字、frontmatter 全文 576 字；三轮均 3/3，无结论影响。打包后的 harvest_catalog.py 为今后正源。

### 成品
检测器已打包为 skill：~/workspace/custom-skills/local-skill-trigger-bench/（SKILL.md＋skill.yaml＋scripts/harvest_catalog.py、run_bench.py、analyze.py＋templates/battery-notes.md）。收割脚本已自验（26 条入目录、codebase 按开关排除并报告）；跑测脚本与今日所用为同一代码路径。
