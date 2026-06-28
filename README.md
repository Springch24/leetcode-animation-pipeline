# 个人 IP 构建 — LeetCode 算法动画 + AI 科技媒体

> 抖音/B站算法动画教程 + 微信公众号 AI 科技深度内容的完整生产流水线。

## 📂 目录

```
├── AGENTS.md                # AI Agent 项目规范（Codex CLI 使用）
├── candidates.json          # 视频选题池
├── rubric_notes.md          # v2.1 视频评分规则
│
├── templates/               # HTML 动画模板 + 封面 prompt 模板
├── scripts/                 # LeetCode 视频脚本（Markdown）
├── covers/                  # 封面生成参考
│
├── wechat/                  # 公众号内容区
│   ├── candidates-wechat.md # 公众号选题池
│   ├── drafts/              # 文章草稿（Markdown）
│   └── images/              # 文章配图
│
├── predictions/             # 视频预测 + 复盘
├── shipped/                 # 发布记录
└── docs/                    # 产品方案文档
```

## 🎬 内容矩阵

| 平台 | 内容形态 | 定位 |
|------|---------|------|
| 抖音 | 75-85s 竖屏算法动画 | 面试焦虑 × 可视化教学 |
| B站 | 同上（同步） | 长尾流量 |
| 微信公众号 | 1500-3000 字技术深度 | AI/ML 前沿解读 |

## 🧠 AI 工作流

从选题到发布，全流程 AI Agent 驱动：

```
选题 → 脚本 → TTS → HTML动画 → 渲染 → 封面 → 发布
                                    ↓
                              公众号文章 → 发草稿箱
```

## 🛠 技术栈

- **动画**: GSAP + HyperFrames（HTML → MP4）
- **TTS**: edge-tts（zh-CN-YunyangNeural）
- **封面**: 豆包 Seedream 4.5 / Pillow
- **公众号**: 微信 API（draft/add）
- **Agent**: Codex CLI + AGENTS.md

## 📝 模板

- `templates/video-hook-first.html` — 钩子前置视频模板
- `templates/cover-prompt.md` — 封面生成 prompt 模板
- `wechat/candidates-wechat.md` — 公众号选题池

## 📄 许可证

MIT
