# AGENTS.md — 个人ip构建 项目规范

## 项目概述

LeetCode 算法动画教程视频生产流水线。内容形态：竖屏 1080×1920，75-85 秒，旁白 + HTML 动画 → HyperFrames 渲染。

平台：抖音为主，B站同步。

## 目录结构

```
个人ip构建/
├── AGENTS.md                # 本文件
├── .cheat-state.json        # cheat-on-content 状态
├── rubric_notes.md          # v2.1 评分规则（白名单，不给 blind sub-agent）
├── rubric-memo.md           # 升级档案（含实绩数据）
├── candidates.json          # 选题池
│
├── scripts/                 # leetcode-NNN-题目.md
├── videos/lcNNN-题目/       # index.html + narration.txt + narration.mp3 + lcNNN-题目.mp4
├── predictions/lcNNN-题目.md # 预测 + 复盘
├── shipped/shipped.json     # 发布记录
│
├── covers/                  # 封面 png
├── data/douyin/             # 抖音发布文案
├── data/bilibili/           # B站发布文案
├── templates/               # HTML 模板
├── docs/                    # 产品方案文档
└── archive/                 # 废弃/旧版
```

## 视频生成标准流程

每次从零生成一个视频，严格按以下步骤：

### Step 1: 选题
- 从 `candidates.json` 选未 shipped 的题
- 优先级：链表 × 简单 > 链表 × 中等 > 二叉树 × 简单
- 选题后标记 candidates.json 状态

### Step 2: 脚本 (`scripts/leetcode-NNN-题目.md`)
- 标题用焦虑钩子公式："面试官让你…，90%的人…"
- 目标时长 75-82 秒
- 结构：开场钩子 → 题目描述 → 解法核心 → 动画描述 → 复杂度 → 金句收尾 → CTA
- 金句要求：一句话能记住的核心技巧

### Step 3: TTS (`videos/lcNNN-题目/narration.txt` + `narration.mp3`)
- 语音：zh-CN-YunyangNeural
- 命令：`python3 -m edge_tts --voice zh-CN-YunyangNeural --file narration.txt --write-media narration.mp3`

### Step 4: HTML 动画 (`videos/lcNNN-题目/index.html`)
- 竖屏 1080×1920
- 6 个场景：钩子(0-3s) → 标题(3-11s) → 题目可视化 → 解法动画 → 复杂度 → CTA
- **钩子前置**：第 0 帧必须有完整钩子文字（`hook-banner`），0.15s 闪现，不依赖飞入动画
- 钩子公式：`"面试官让你…，90%的人…。面试官说——能做到吗？"`
- 模板文件：`templates/video-hook-first.html`
- **重要**：后续所有视频必须用钩子前置模板，降低 2s 跳出率
- 使用 GSAP timeline，注册到 `window.__timelines`
- body 必须有 `data-composition-id`、`data-width`、`data-height`
- 字体用系统字体 fallback（PingFang SC → Noto Sans SC → sans-serif）
- 不依赖外部 CDN 字体（HyperFrames 离线渲染兼容）

### Step 5: 渲染 (`videos/lcNNN-题目/lcNNN-题目.mp4`)
- `npx hyperframes render . -o "lcNNN-题目.mp4" -f 30 -q high`
- 合并音频：`ffmpeg -i lcNNN-题目.mp4 -i narration.mp3 -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest -movflags +faststart -y lcNNN-题目-temp.mp4 && mv lcNNN-题目-temp.mp4 lcNNN-题目.mp4`

### Step 6: 预测 (`predictions/lcNNN-题目.md`)
- 用 v2.1 rubric blind predict
- 输出：8维度打分 + composite + bucket + 辅助信号（时长预警、赞播比、收藏）

### Step 7: 封面 (`covers/lcNNN-封面.png`)
- **每次生成视频时同步生成封面**，不后补
- 极简居中排版，无代码
- 结构：LeetCode 小标签 → 大字白色题号 → 中文题名 → 英文题名 → 橙色分割线 → 标签行 → 金句 → 橙序员署名
- 深色背景 `#060b14`，白色题号，橙色分割线和金句
- 代码是另一张图：`covers/lcNNN-code-card.png` 发评论区用

### Step 8: 发布
- 抖音简介含钩子 + 金句 + 标签
- 发布后更新 `shipped/shipped.json`

### Step 9: 复盘
- T+3d 收数据
- 更新 prediction 文件复盘段
- 更新 state baseline

## v2.1 Rubric 速查

| 维度 | 权重 | 0分 | 5分 |
|---|---|---|---|
| AC 动画清晰度 | ×2.0 | 纯静态 | 每个状态变化有视觉反馈 |
| HP 钩子力度 | ×2.0 | "大家好今天讲一道题" | "面试官…90%的人…" |
| TR 教学节奏 | ×1.5 | 严重脱节/>120s | 音画完美同步/75-85s |
| KI 关键洞察 | ×1.5 | 纯念代码 | "有环必相遇"级金句 |
| AB 受众广度 | ×1.2 | 冷门题 | 面试Top10/入门必刷 |
| ACT 可操作性 | ×1.2 | 看完不会写 | 步骤清晰能复现 |
| CR 代码可读性 | ×1.0 | 模糊无高亮 | 截图级美观 |
| VS 画面风格 | ×1.0 | 杂乱无设计 | 品牌辨识度 |

**公式**: `composite = (AC×2.0 + HP×2.0 + TR×1.5 + KI×1.5 + AB×1.2 + ACT×1.2 + CR×1.0 + VS×1.0) / 11.4 × 2.0`

**时长预警**: ≤85s🟢 86-100s🟡 101-120s🟠 >120s🔴

## 命名规范

- scripts: `leetcode-NNN-题目.md` (NNN 三位数补零)
- videos: `lcNNN-题目/`
- predictions: `lcNNN-题目.md`
- 最终视频: `videos/lcNNN-题目/lcNNN-题目.mp4`

## 已知高频模式

- 链表 × 简单题 = 黄金组合（4条 avg 3,266 播放）
- 焦虑钩子 "90%的人…" 持续有效
- 75-85s 最优时长
- 收藏由 ACT × KI 联合驱动
- lc1 (两数之和, 440播放) 是冷启动首条 + 深夜发布的异常值，不算内容问题

---

## LLM Wiki 维护规则

本项目的知识库位于 Obsidian vault: `/Users/sring24/Desktop/AI研究/个人知识库/spring的知识酷/`

### Wiki 目录结构

```
spring的知识酷/
├── index.md                     # 全局索引
├── log.md                       # 时间线日志，仅追加
│
├── 机器学习/                     # 面试知识库（核心）
│   ├── 机器学习.md               # 总入口
│   ├── 基础概念/                 # 监督/无监督/回归/正则/评估/偏差方差/生成判别
│   ├── 深度学习/                 # CNN/RNN/LSTM/Transformer/Attention/激活/优化器/归一化
│   ├── 大模型与LLM/              # DeepSeek-R1/训练流程/RLHF
│   └── 面试八股/                 # ML面试索引/推荐系统/强化学习
│
├── 算法知识/                     # 通用算法技巧
│   ├── 双指针.md
│   ├── 链表技巧.md
│   ├── 滑动窗口.md
│   ├── 哈希表.md
│   └── 排序与去重.md
│
├── 算法题/                       # 每题含：题目+解法+代码+演算+金句+视频
│   ├── 141-环形链表.md ...       # 已发布 10 题
│   └── 021-合并两个有序链表.md   # 待制作
│
└── 视频生产/
    ├── 视频发布记录.md
    ├── 选题策略与Rubric.md
    └── 视频生产复盘.md
```

### Wiki 维护工作流

**每发布一条新视频**，必须执行：

1. 更新 `shipped/shipped.json`（已有流程）
2. 同步到 Obsidian `视频生产/视频发布记录.md`：追加一行
3. 在 `算法题/` 下创建/更新题目页面，结构：
   - 题目描述 + 解法思路 + 完整代码 + 手动演算 + 复杂度
   - 金句 + 关联视频链接
   - 关联到对应的 `算法知识/` 页面
4. 更新 `index.md`：新页面加入对应分类
5. 追加 `log.md`

**每 T+3d 复盘后**：

1. 更新 `视频生产/视频生产复盘.md`
2. 如果 rubric 升级，同步更新 `视频生产/选题策略与Rubric.md`

**ML 知识摄入时**：

1. 在 `机器学习/` 对应子目录创建专题页面
2. 更新 `机器学习/机器学习.md` 目录索引
3. 在 `面试八股/ML 面试常见问题.md` 添加高频问题链接
4. 检查是否产生新的 ML ↔ 算法知识交叉引用
5. 更新 index.md + 追加 log.md

**定期检查（每周）**：

- Obsidian 图形视图巡览，检查孤立页面
- `视频发布记录.md` 与 `shipped.json` 数据一致性
- `ML 面试常见问题.md` 是否覆盖最新知识页

### 交叉引用规范

- 算法题页面 ↔ 算法知识页面（如 141-环形链表 ↔ 双指针）
- ML 知识 ↔ 算法知识（如 CNN 卷积核滑动 ↔ 滑动窗口）
- 面试八股页面汇总所有高频问题，链接到具体知识页
- 每个算法题页面底部标注来源路径（`个人ip构建/scripts/...`）
- ML 新知识摄入时：创建专题页面 → 更新 `机器学习/机器学习.md` 目录 → 更新 index.md → 追加 log.md

### Step 9: 代码卡片（评论区贴图）

每生成一条视频，生成两张图：封面（`lcNNN-封面.png`，极简排版）和评论区代码卡片（`lcNNN-code-card.png`，含完整代码）。两张图不要混淆。

**用途**：发到抖音评论区置顶，引导评论和收藏。

**规范**：
- 竖屏 1080×1920，深色背景 `#060b14`
- 标题：`LeetCode NNN · 题名 · Python` 橙色 `#FCA311`
- 副标题：标签 · 复杂度 灰色 `#4a6080`
- 代码正文：34px，`#dce4f0`
- 底部金句：`💡 金句` 橙色 22px
- 字体：STHeiti Medium（macOS 内置 CJK）
- 用 Python PIL 生成（`ImageDraw.rounded_rectangle` 做卡片背景）

**评论区话术模板**：配一句具体问题，引导二选一回答
- 格式：`代码在这 👇 你第一次做用了[方法A]还是[方法B]？`
- 杜绝"评论区见""欢迎点赞关注"等废话

**生成脚本参考**：`covers/` 目录下现有 14 张卡片，新卡片仿照格式生成。

---

## Agent 学习系列规范（HelloAgents）

### 目录结构
```
agent/
├── videos/agent-dayNN-章节名/    # 视频目录
├── covers/                       # 封面（竖屏 1080×1920）
├── scripts/                      # 脚本
├── predictions/                  # 预测
└── data/                         # 发布文案、小红书等
```

### 视频生产流程

#### Step 1: 录音
- Omi 屏幕录制，Mac 系统音频录制
- 文件命名：Screen-YYYY-MM-DD-HHmmss.mp4（Omi 自动生成）

#### Step 2: 合并
- 同一天多个录音按时间顺序 concat
- `ffmpeg -f concat -i list.txt -c copy raw.mp4`

#### Step 3: 字幕
- whisper medium 模型转写中文 SRT
- 先提取 16kHz WAV，再 `python3 -m whisper`

#### Step 4: 后期
- 缩放到 1920×1080（16:9 横屏，pad 黑边）
- 氛围电子 bgm（55Hz pulse + 粉噪，低频存在感低）
- bgm 音量 12%，人声 100%

#### Step 5: 发布
- 抖音 + B站同步
- 抖音创作者后台：上传 → 等转码 → 填标题简介 → 发布
- 标题格式：「章节名：一句话描述 🎙️ HelloAgents Day N」
- 简介：核心时间线 + 标签

#### Step 6: 小红书图文版
- 从 Obsidian hello-agents 课程提取精华
- 文案：一句话定义 + 对比表格 + 进化路径 + 思考题
- 配图：从章节 figures 提取 3-4 张

### 发布记录
- 抖音数据分析：播放、平均时长、赞播比、收藏率
- Agent 系列收藏率 > 1% 视为高质量内容
- 长视频（>30min）播放量偏低但精准，不做时长优化

---

## 公众号发布流程（AI 科技媒体）

### 定位
AI/科技媒体类公众号，类似机器之心、量子位。覆盖模型解读、技术深度解析、AI工具实操、行业趋势。

### 目录结构
```
wechat/
├── drafts/           # 草稿 Markdown
├── published/        # 已发布文章 + 备份
├── images/           # 文章配图（封面、插图）
```

### 发布流程

#### Step 1: 写稿
- Obsidian 或直接在 `wechat/drafts/` 下写 Markdown
- 标题用焦虑钩子或类比公式吸引点击
- 正文 1500-3000 字，适合 5-8 分钟阅读
- 配图放 `wechat/images/` 目录

#### Step 2: 发草稿
```bash
bun ~/.agents/skills/baoyu-post-to-wechat/scripts/wechat-api.ts wechat/drafts/文章.md --cover wechat/images/封面.png
```

#### Step 3: 发布
- 登录 https://mp.weixin.qq.com → 草稿箱
- 预览确认格式 → 群发

#### Step 4: 归档
- 文章移入 `wechat/published/`
- 更新 `shipped/shipped.json`（如适用）
