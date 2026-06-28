# LeetCode 算法动画 + AI 科技媒体 — 模板仓库

> 个人 IP 内容生产的开源模板：视频脚本模板、HTML 动画模板、封面 prompt 模板、公众号选题池。

## 📂 目录

```
├── AGENTS.md                         # AI Agent 项目规范
├── templates/
│   ├── video-hook-first.html         # 钩子前置视频 HTML 模板
│   ├── video-template-vertical.html  # 竖屏通用模板
│   ├── cover-prompt.md               # 封面生成 prompt 模板
│   └── narration-template.txt        # 旁白脚本模板
├── scripts/
│   ├── leetcode-141-环形链表.md       # 3 个示例脚本（链表×简单）
│   ├── leetcode-206-反转链表.md
│   └── leetcode-021-合并两个有序链表.md
└── wechat/
    └── candidates-wechat.md          # 公众号选题池
```

## 🎯 用途

这些模板和规范用于驱动 AI Agent（如 Codex CLI）自动化生产内容：

```
选题 → 脚本 → TTS → HTML动画 → 渲染 → 封面 → 发布
```

## 🛠 使用的工具

- **动画**: GSAP + HyperFrames
- **TTS**: edge-tts
- **封面**: 豆包 Seedream / Python Pillow
- **Agent**: Codex CLI

## 📄 许可证

MIT
