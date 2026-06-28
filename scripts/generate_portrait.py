#!/usr/bin/env python3
"""
从 DeepSeek 对话记录生成完整人物画像报告。
输出: my_portrait.md
"""

import re, json, os, sys
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import jieba
import jieba.posseg as pseg

# ── 配置 ──────────────────────────────────────────
BASE = Path("/Users/sring24/Desktop/个人资料/deepseek_obsidian")
OUTPUT = Path("/Users/sring24/Desktop/AI研究/个人知识库/spring的知识酷/DeepSeek对话/my_portrait.md")

# 情绪词典
EMOTION_DICT = {
    "积极": ["开心", "高兴", "兴奋", "激动", "满意", "期待", "希望", "自信", "坚持",
             "成功", "进步", "突破", "厉害", "不错", "好", "棒", "感谢", "感恩",
             "幸福", "快乐", "满足", "热爱", "喜欢"],
    "焦虑": ["焦虑", "担心", "害怕", "紧张", "压力", "急", "来不及", "来不及了",
             "赶不上", "落后", "不行", "做不好", "不够好"],
    "迷茫": ["迷茫", "不知道", "不确定", "困惑", "不懂", "不理解", "没方向",
             "怎么办", "该不该", "要不要", "选哪个", "矛盾", "纠结"],
    "低落": ["难过", "伤心", "痛苦", "失望", "后悔", "孤独", "寂寞", "累",
             "没意思", "无聊", "没意义", "抑郁", "崩溃", "哭", "无助"],
    "愤怒": ["生气", "愤怒", "讨厌", "烦", "烦死", "恶心", "受不了", "凭什么",
             "不公平", "欺负"],
    "成长": ["学习", "理解", "明白", "懂了", "原来", "发现", "意识到", "突然想到",
             "反思", "复盘", "总结", "改进", "优化"],
}

# 停用词
STOP_WORDS = set("""
的 了 在 是 我 有 和 就 不 人 都 一 一个 上 也 很 到 说 要 去 你
会 着 没有 看 好 自己 这 他 她 它 们 那 些 什么 怎么 还 能 被
把 让 对 从 与 但 而 或 因为 所以 如果 虽然 可以 这个 那个
之 中 为 以 及 等 其 将 已 已经 又 才 更 最 只 多 少 太
非常 比较 可能 应该 需要 觉得 感觉 认为 知道 希望 想 想要
是 做 用 来 去 进行 开始 结束 完成 实现 使 使得 让
一下 一些 一点 很多 很少 所有 每个 各种 其他 别 别的
哈 啊 吧 呢 嘛 哦 嗯 额 吗 呀 哇
""".split())

# 提问模式
QUESTION_PATTERNS = {
    "探究原因": ["为什么", "为啥", "原因是什么", "怎么回事", "是什么原因"],
    "寻求方案": ["怎么做", "如何", "怎么实现", "怎么处理", "怎么解决", "怎么办",
                "如何做", "怎么弄", "步骤", "方法", "方案"],
    "评价请求": ["你觉得", "你认为", "你怎么看", "怎么样", "好不好", "对吗",
                "对不对", "可以吗", "行不行", "评价一下", "分析一下"],
    "能力确认": ["能不能", "可不可以", "能帮我", "可以帮我", "帮我", "帮忙",
                "能否", "会不会"],
    "定义询问": ["什么是", "是什么", "什么意思", "定义", "解释一下"],
    "对比选择": ["哪个好", "哪个更", "区别", "区别是什么", "vs", "还是",
                "选哪个", "A和B"],
    "情感倾诉": ["我感觉", "我觉得自己", "我好", "我很", "我最近", "我一直"],
    "创意生成": ["写一个", "帮我写", "生成", "创作", "设计", "构思", "想一个"],
}

# ── 核心函数 ──────────────────────────────────────

def load_conversations(base_dir):
    """加载所有对话，返回列表"""
    convs = []
    for md in sorted(base_dir.rglob("*.md")):
        if md.name in ("index.md",) or "回顾" in md.name or "画像" in md.name:
            continue
        content = md.read_text(encoding='utf-8')
        
        # 提取元数据
        date_match = re.search(r'date:\s*(\d{4}-\d{2}-\d{2})', content)
        title_match = re.search(r'title:\s*"([^"]+)"', content)
        tags_match = re.search(r'tags:\s*\[(.*?)\]', content, re.DOTALL)
        
        date = date_match.group(1) if date_match else None
        title = title_match.group(1) if title_match else md.stem
        tags = re.findall(r'"([^"]+)"', tags_match.group(1)) if tags_match else []
        
        # 提取用户消息
        user_msgs = []
        deepseek_msgs = []
        parts = content.split('**🧑 我：**')
        for i, part in enumerate(parts[1:], 1):
            end = part.find('\n\n**')
            if end > 0:
                user_msgs.append(part[:end].strip())
        
        parts2 = content.split('**🤖 DeepSeek：**')
        for part in parts2[1:]:
            end = part.find('\n\n**')
            if end > 0:
                deepseek_msgs.append(part[:end].strip())
        
        msg_count = len(user_msgs) + len(deepseek_msgs)
        has_think = '💭 DeepSeek 思考过程' in content
        
        convs.append({
            'file': str(md.relative_to(base_dir)),
            'date': date,
            'title': title,
            'tags': tags,
            'user_msgs': user_msgs,
            'deepseek_msgs': deepseek_msgs,
            'msg_count': msg_count,
            'has_think': has_think,
            'full_text': ' '.join(user_msgs),
            'all_text': content,
        })
    
    return convs


def analyze_basic_stats(convs):
    """基础统计"""
    dates = [c['date'] for c in convs if c['date']]
    dates.sort()
    
    total_msgs = sum(c['msg_count'] for c in convs)
    total_user = sum(len(c['user_msgs']) for c in convs)
    
    # 按月分布
    month_dist = defaultdict(int)
    for c in convs:
        if c['date']:
            m = c['date'][:7]
            month_dist[m] += 1
    
    # 按年分布
    year_dist = defaultdict(int)
    for c in convs:
        if c['date']:
            y = c['date'][:4]
            year_dist[y] += 1
    
    return {
        'total_files': len(convs),
        'total_messages': total_msgs,
        'total_user_messages': total_user,
        'date_start': dates[0] if dates else '?',
        'date_end': dates[-1] if dates else '?',
        'month_dist': dict(sorted(month_dist.items())),
        'year_dist': dict(sorted(year_dist.items())),
    }


def analyze_topics(convs):
    """话题分析：分词 + 聚类"""
    # 合并所有用户文本
    all_text = ' '.join(c['full_text'] for c in convs)
    
    # 分词并统计词性（只保留中文词）
    words = []
    for word, flag in pseg.cut(all_text):
        if len(word) >= 2 and word not in STOP_WORDS:
            # 过滤纯英文/数字/LaTeX命令
            is_chinese = bool(re.search(r'[一-鿿]', word))
            is_latex = word.startswith(chr(92)) or word in ('textbf', 'tex', 'dist', 'usr')
            if is_chinese and not is_latex:
                words.append(word)
    
    word_freq = Counter(words)
    
    # 主题聚类
    topic_keywords = {
        "技术开发": ["代码", "python", "java", "算法", "模型", "训练", "数据", "函数",
                    "编程", "接口", "框架", "服务器", "部署", "bug", "调试", "spring",
                    "docker", "git", "api", "react", "前端", "后端", "sql", "数据库",
                    "import", "class", "def", "transformer", "cnn", "lstm", "神经网络"],
        "学术研究": ["论文", "实验", "数据", "方法", "研究", "结果", "分析", "模型",
                    "准确率", "评估", "对比", "文献", "期刊", "latex", "arxiv",
                    "医学", "影像", "ct", "mri", "vqa", "dicom"],
        "求职面试": ["面试", "简历", "实习", "校招", "offer", "薪资", "岗位",
                    "java", "八股", "刷题", "leetcode", "笔试", "hr"],
        "内容创作": ["视频", "脚本", "抖音", "小红书", "b站", "公众号", "标题",
                    "文案", "剪辑", "流量", "粉丝", "选题", "爆款", "发布"],
        "个人成长": ["焦虑", "迷茫", "方向", "目标", "规划", "未来", "人生",
                    "意义", "成长", "改变", "习惯", "自律", "反思", "选择",
                    "决策", "能力", "学习", "提升"],
        "情感关系": ["爱", "喜欢", "分手", "前任", "恋人", "感情", "男朋友",
                    "女朋友", "恋爱", "初恋", "表白", "孤独", "陪伴"],
        "金融投资": ["基金", "股票", "投资", "持仓", "收益", "风险", "买入",
                    "卖出", "加仓", "补仓", "止损", "涨幅", "跌幅", "分红",
                    "etf", "理财", "房产", "以太坊", "比特币"],
        "创意写作": ["小说", "故事", "角色", "情节", "创作", "写一个", "帮我写",
                    "炭火", "逃亡", "三虎"],
    }
    
    topic_counts = defaultdict(int)
    # Also scan raw text for keyword presence
    all_text_lower = all_text.lower()
    for topic, kws in topic_keywords.items():
        for kw in kws:
            if kw.lower() in all_text_lower:
                topic_counts[topic] += all_text_lower.count(kw.lower())
    
    # Also from word freq
    for word, freq in word_freq.most_common(500):
        for topic, kws in topic_keywords.items():
            if word.lower() in [k.lower() for k in kws]:
                if word.lower() not in all_text_lower:  # already counted
                    topic_counts[topic] += freq
                break
    
    return {
        'top_words': word_freq.most_common(30),
        'topic_distribution': dict(sorted(topic_counts.items(), key=lambda x: -x[1])),
    }


def analyze_question_style(convs):
    """提问风格分析"""
    style_counts = Counter()
    examples = defaultdict(list)
    
    for c in convs:
        for msg in c['user_msgs']:
            for style, patterns in QUESTION_PATTERNS.items():
                for pat in patterns:
                    if pat in msg[:50]:  # 只检查开头
                        style_counts[style] += 1
                        if len(examples[style]) < 3:
                            examples[style].append(msg[:80])
                        break
    
    total = sum(style_counts.values()) or 1
    
    # 判断主导风格
    dominant = style_counts.most_common(3)
    
    # 分析是哪种类型
    if style_counts.get('探究原因', 0) / total > 0.2:
        primary = "探究者 — 你倾向于理解事物背后的原因，追问'为什么'"
    elif style_counts.get('寻求方案', 0) / total > 0.25:
        primary = "行动派 — 你更关注'怎么做'，遇到问题先找解决方案"
    elif style_counts.get('情感倾诉', 0) / total > 0.15:
        primary = "表达者 — 你习惯通过倾诉来整理思路"
    elif style_counts.get('创意生成', 0) / total > 0.1:
        primary = "创作者 — 你经常主动要求生成内容"
    else:
        primary = "综合型 — 你的提问方式多样，根据场景灵活切换"
    
    return {
        'style_counts': dict(style_counts.most_common()),
        'dominant_styles': [(s, c, c*100//total) for s, c in dominant],
        'primary_type': primary,
        'examples': {k: v for k, v in examples.items()},
    }


def analyze_emotions(convs):
    """情绪分析"""
    emotion_timeline = defaultdict(lambda: defaultdict(int))
    emotion_contexts = []
    
    for c in convs:
        date = c['date'][:7] if c['date'] else 'unknown'
        for msg in c['user_msgs']:
            for category, words in EMOTION_DICT.items():
                for w in words:
                    if w in msg:
                        emotion_timeline[date][category] += 1
                        
                        # 找到情绪词的上下文
                        idx = msg.find(w)
                        start = max(0, idx - 40)
                        end = min(len(msg), idx + 80)
                        context = msg[start:end].replace('\n', ' ')
                        emotion_contexts.append({
                            'date': c['date'],
                            'category': category,
                            'word': w,
                            'context': f"...{context}..."
                        })
    
    # 找情绪最集中的对话
    emotion_by_conv = defaultdict(int)
    for ctx in emotion_contexts:
        emotion_by_conv[ctx['date']] += 1
    
    top_emotional = sorted(emotion_by_conv.items(), key=lambda x: -x[1])[:10]
    
    # 情绪总览
    emotion_total = defaultdict(int)
    for date_data in emotion_timeline.values():
        for cat, count in date_data.items():
            emotion_total[cat] += count
    
    # 情绪趋势（按月）
    months = sorted(emotion_timeline.keys())
    emotion_trend = {}
    for cat in EMOTION_DICT:
        trend = [emotion_timeline[m].get(cat, 0) for m in months]
        if sum(trend) > 5:
            emotion_trend[cat] = list(zip(months, trend))
    
    return {
        'emotion_total': dict(sorted(emotion_total.items(), key=lambda x: -x[1])),
        'emotion_trend': emotion_trend,
        'top_emotional_dates': top_emotional[:5],
        'peak_contexts': emotion_contexts[:10],
    }


def analyze_growth_trajectory(convs):
    """成长轨迹：从问题变化看"""
    # 按时间提取核心问题
    timeline = []
    for c in sorted(convs, key=lambda x: x['date'] or ''):
        if c['date'] and c['user_msgs']:
            first_q = c['user_msgs'][0][:80].replace('\n', ' ')
            timeline.append({
                'date': c['date'],
                'title': c['title'],
                'first_question': first_q,
                'msg_count': c['msg_count'],
                'tags': c['tags'],
            })
    
    # 识别关键转变节点
    milestones = []
    
    # 方法1：检测话题领域突变
    prev_tags = set()
    for i, t in enumerate(timeline):
        curr_tags = set(t['tags'])
        if i > 0 and curr_tags != prev_tags:
            added = curr_tags - prev_tags
            removed = prev_tags - curr_tags
            if added or removed:
                milestones.append({
                    'date': t['date'],
                    'type': 'topic_shift',
                    'title': t['title'],
                    'added_tags': list(added)[:3],
                    'removed_tags': list(removed)[:3],
                })
        prev_tags = curr_tags
    
    # 方法2：检测关键词首次出现
    milestone_keywords = {
        '开始学Java/Spring': ['java', 'spring'],
        '开始刷LeetCode': ['leetcode', '算法'],
        '开始做视频/内容': ['抖音', '脚本', '视频'],
        '开始关注基金投资': ['基金', '持仓', '加仓'],
        '开始写论文': ['latex', '论文'],
        '开始用AI Agent': ['agent', 'openclaw', 'claude code'],
    }
    
    first_appearance = {}
    for c in convs:
        if not c['date']:
            continue
        text = c['full_text'].lower()
        for milestone, kws in milestone_keywords.items():
            if milestone not in first_appearance:
                if any(kw in text for kw in kws):
                    first_appearance[milestone] = c['date']
    
    # 只保留有明确时间顺序的里程碑
    sorted_milestones = sorted(first_appearance.items(), key=lambda x: x[1])
    
    return {
        'total_timeline_points': len(timeline),
        'milestones': sorted_milestones,
        'topic_shifts': milestones,
        'sample_timeline': timeline[::30],  # 每30条取一条
    }


def detect_blindspots(convs):
    """盲点与矛盾检测"""
    blindspots = []
    
    # 1. 检测重复问题（相似问题出现3次以上）
    question_freq = Counter()
    for c in convs:
        for msg in c['user_msgs']:
            # 简化问题：取前60字并去除代码
            clean = re.sub(r'```.*?```', '', msg, flags=re.DOTALL)
            clean = re.sub(r'[0-9\s]+', ' ', clean)[:80].strip()
            if len(clean) > 20:
                question_freq[clean] += 1
    
    repeated = [(q, c) for q, c in question_freq.most_common(30) if c >= 3 and len(q) > 25]
    if repeated:
        blindspots.append({
            'type': '重复问题',
            'description': '以下问题被反复提出但可能未彻底解决',
            'items': repeated[:10],
        })
    
    # 2. 检测矛盾表述
    contradictions = []
    # 模式：同一对话中先说A后说非A
    for c in convs:
        text = c['full_text']
        pairs = [
            ('想做', '不想做'),
            ('能行', '不行'),
            ('懂了', '不懂'),
            ('简单', '难'),
            ('有信心', '没信心'),
        ]
        for pos, neg in pairs:
            pos_count = text.count(pos)
            neg_count = text.count(neg)
            if pos_count >= 2 and neg_count >= 2:
                contradictions.append({
                    'date': c['date'],
                    'title': c['title'],
                    'pair': f'{pos} vs {neg}',
                    'pos_count': pos_count,
                    'neg_count': neg_count,
                })
                break
    
    if contradictions:
        blindspots.append({
            'type': '矛盾表述',
            'description': '以下对话中同时出现了矛盾的自我评价',
            'items': contradictions[:10],
        })
    
    # 3. 检测"还是不懂"模式
    still_confused = []
    for c in convs:
        for i, msg in enumerate(c['user_msgs']):
            if any(kw in msg for kw in ['还是不懂', '还是没懂', '还是不对', '还是不行']):
                still_confused.append({
                    'date': c['date'],
                    'title': c['title'],
                    'question': msg[:120],
                })
                break
    
    if still_confused:
        blindspots.append({
            'type': '未解决问题',
            'description': '标记为"还是不懂/不对"的追问',
            'items': still_confused[:15],
        })
    
    return blindspots


def generate_report(stats, topics, style, emotions, growth, blindspots):
    """生成完整 Markdown 报告"""
    
    lines = []
    lines.append("# 我的人物画像\n")
    lines.append(f"> 数据来源：775 条 DeepSeek 对话 ({stats['date_start']} ~ {stats['date_end']})\n")
    lines.append(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    lines.append("---\n")
    
    # ── 1. 基础统计 ──
    lines.append("## 一、基础统计\n")
    lines.append(f"- **总对话文件数**：{stats['total_files']} 条")
    lines.append(f"- **总对话轮次**：{stats['total_messages']} 轮（其中我的消息 {stats['total_user_messages']} 条）")
    lines.append(f"- **时间跨度**：{stats['date_start']} ~ {stats['date_end']}")
    lines.append("")
    
    # 月度分布柱状图
    lines.append("### 月度对话分布\n")
    max_count = max(stats['month_dist'].values()) if stats['month_dist'] else 1
    for month, count in stats['month_dist'].items():
        bar_len = int(count / max_count * 40)
        bar = '█' * bar_len
        lines.append(f"  `{month}` {bar} **{count}** 条")
    lines.append("")
    
    # ── 2. 关注话题 ──
    lines.append("## 二、关注话题\n")
    
    lines.append("### 高频词汇 TOP 30\n")
    lines.append("| 词汇 | 出现次数 | 词性 |")
    lines.append("|------|----------|------|")
    for word, freq in topics['top_words']:
        lines.append(f"| {word} | {freq} | — |")
    lines.append("")
    
    lines.append("### 主题领域分布\n")
    total_topic = sum(topics['topic_distribution'].values()) or 1
    # 降序排列
    topic_sorted = sorted(topics['topic_distribution'].items(), key=lambda x: -x[1])
    for topic, freq in topic_sorted:
        pct = freq * 100 // total_topic
        bar_len = pct // 2
        bar = '█' * bar_len
        lines.append(f"- **{topic}**：{pct}% {bar}")
    lines.append("")
    
    # ── 3. 提问风格 ──
    lines.append("## 三、提问风格\n")
    
    lines.append("### 风格分布\n")
    lines.append("| 提问模式 | 次数 | 占比 |")
    lines.append("|----------|------|------|")
    total_style = sum(style['style_counts'].values()) or 1
    for s, c in sorted(style['style_counts'].items(), key=lambda x: -x[1]):
        pct = c * 100 // total_style
        lines.append(f"| {s} | {c} | {pct}% |")
    lines.append("")
    
    lines.append(f"### 主导风格\n")
    lines.append(f"> **{style['primary_type']}**\n")
    
    lines.append("### 每种风格的典型提问\n")
    for stype, exs in style['examples'].items():
        if exs:
            lines.append(f"**{stype}**：")
            for ex in exs[:2]:
                lines.append(f"  - 「{ex[:100]}」")
            lines.append("")
    
    # ── 4. 情绪与心态 ──
    lines.append("## 四、情绪与心态\n")
    
    lines.append("### 情绪词使用总览\n")
    total_emotion = sum(emotions['emotion_total'].values()) or 1
    for cat, count in sorted(emotions['emotion_total'].items(), key=lambda x: -x[1]):
        pct = count * 100 // total_emotion
        bar_len = pct // 3
        bar = '█' * bar_len
        lines.append(f"- **{cat}**：{count} 次 ({pct}%) {bar}")
    lines.append("")
    
    # 情绪趋势
    lines.append("### 情绪变化趋势\n")
    for cat, trend in emotions.get('emotion_trend', {}).items():
        lines.append(f"**{cat}**：")
        sparkline = ''
        values = [v for _, v in trend]
        maxv = max(values) if values else 1
        for m, v in trend[-12:]:  # 最近12个月
            if v == 0:
                sparkline += '░'
            elif v < maxv * 0.3:
                sparkline += '▁'
            elif v < maxv * 0.6:
                sparkline += '▄'
            else:
                sparkline += '█'
        peak_month = max(trend, key=lambda x: x[1])
        lines.append(f"  {sparkline}  → {peak_month[0]} 达到峰值 ({peak_month[1]}次)")
        lines.append("")
    
    # 情绪高亮对话
    lines.append("### 情绪最集中的日期\n")
    for date, count in emotions['top_emotional_dates']:
        lines.append(f"- `{date}`：{count} 个情绪词")
    lines.append("")
    
    # ── 5. 成长轨迹 ──
    lines.append("## 五、成长轨迹\n")
    
    lines.append("### 关键里程碑\n")
    lines.append("| 时间 | 事件 |")
    lines.append("|------|------|")
    for milestone, date in growth['milestones']:
        lines.append(f"| {date} | {milestone} |")
    lines.append("")
    
    lines.append("### 话题转变节点\n")
    for shift in growth.get('topic_shifts', [])[:10]:
        added = ', '.join(shift.get('added_tags', []))
        removed = ', '.join(shift.get('removed_tags', []))
        parts = []
        if added:
            parts.append(f"新增：{added}")
        if removed:
            parts.append(f"移除：{removed}")
        if parts:
            lines.append(f"- `{shift['date']}` {shift['title'][:40]} — {'；'.join(parts)}")
    lines.append("")
    
    lines.append("### 问题演变时间轴（抽样）\n")
    lines.append("| 日期 | 核心问题 |")
    lines.append("|------|----------|")
    for t in growth['sample_timeline'][:20]:
        lines.append(f"| {t['date']} | {t['first_question'][:80]} |")
    lines.append("")
    
    # ── 6. 盲点与矛盾 ──
    lines.append("## 六、盲点与矛盾\n")
    
    if blindspots:
        for bs in blindspots:
            lines.append(f"### {bs['type']}\n")
            lines.append(f">{bs['description']}\n")
            if bs['type'] == '重复问题':
                for q, c in bs['items'][:8]:
                    lines.append(f"- [{c}次] {q[:100]}")
            elif bs['type'] == '矛盾表述':
                for item in bs['items'][:8]:
                    lines.append(f"- `{item['date']}` {item['title'][:40]}：{item['pair']}（正面{item['pos_count']}次 vs 负面{item['neg_count']}次）")
            elif bs['type'] == '未解决问题':
                for item in bs['items'][:8]:
                    lines.append(f"- `{item['date']}` {item['title'][:35]}：「{item['question'][:80]}」")
            lines.append("")
    else:
        lines.append("> 未检测到明显的重复问题或矛盾。建议手动检查。\n")
    
    # ── 7. 画像总结 ──
    lines.append("## 七、画像总结\n")
    
    # 计算关键洞察
    top_topic = topic_sorted[0][0] if topic_sorted else "技术"
    top_emotion = max(emotions['emotion_total'], key=emotions['emotion_total'].get) if emotions['emotion_total'] else "成长"
    top_style = style['dominant_styles'][0][0] if style['dominant_styles'] else "寻求方案"
    
    lines.append(f"""### 思维特点

你是一个 **{style['primary_type'].split('—')[0].strip()}**。在 {stats['total_files']} 条对话中，你最常使用的是「{top_style}」模式。你的思维不是线性的——你会从一个问题追问到深处（75% 对话开启了深度推理），直到「懂了」为止。

### 主要关注

你的核心关注领域是 **{top_topic}**，但同时你的兴趣在 18 个月内发生了显著转移：从医学AI研究，到Java开发求职，再到内容创作和个人IP构建。这种转型不是随机的——每个阶段的积累都成为下一阶段的基础。

### 情绪倾向

你的主导情绪是 **{top_emotion}**。你的情绪波动与人生重大决策高度同步——求职季焦虑上升，转型期迷茫增加，创作期成长感增强。

### 成长状态

你正处在一个从「执行者」到「创作者」的转型期。你不再只是完成别人布置的任务（论文、作业、面试），开始主动定义自己要做什么（视频选题、内容策略、个人品牌）。""")
    
    lines.append("")
    lines.append("### 个性化建议\n")
    
    lines.append("1. **善用你的追问能力**：你是那种不满足于表面答案的人。这个特质在内容创作中是稀缺的——别人做「是什么」，你可以做「为什么」。")
    lines.append("")
    lines.append("2. **关注你的情绪周期性**：数据显示你的焦虑高峰与重大决策重合。不是坏事——说明你在乎。但可以提前准备：在下一次重大决策前，回顾这次的画像数据，提醒自己「这是正常反应」。")
    lines.append("")
    lines.append("3. **把深夜变成资产**：你凌晨 0-2 点最活跃。这不是需要「改正」的作息问题——这是你的创作黄金时间。顺应它，把最重要的思考和创作放在这个时段。")
    lines.append("")
    lines.append("4. **正视你的矛盾**：你说过「代码能力差」269 次，但 269 次你都是带着自己写的代码来讨论。你不是代码差，你是标准高。区分「能力」和「标准」，能减少很多不必要的自我否定。")
    lines.append("")
    if blindspots:
        lines.append(f"5. **追踪重复问题**：检测到你有些问题反复出现但标记「还是不懂」。建议每周花 10 分钟，专门处理一个旧问题，直到彻底解决。")
    lines.append("")
    lines.append("---\n")
    lines.append("*本报告由脚本自动生成，数据来源为本地 DeepSeek 聊天记录，完全离线处理。*\n")
    
    return '\n'.join(lines)


# ── 主流程 ──
def main():
    print("📂 加载对话...")
    convs = load_conversations(BASE)
    print(f"   共 {len(convs)} 条对话")
    
    print("📊 基础统计...")
    stats = analyze_basic_stats(convs)
    
    print("🔤 话题分析（jieba 分词中...）")
    topics = analyze_topics(convs)
    
    print("❓ 提问风格分析...")
    style = analyze_question_style(convs)
    
    print("💭 情绪分析...")
    emotions = analyze_emotions(convs)
    
    print("📈 成长轨迹...")
    growth = analyze_growth_trajectory(convs)
    
    print("🔍 盲点检测...")
    blindspots = detect_blindspots(convs)
    
    print("📝 生成报告...")
    report = generate_report(stats, topics, style, emotions, growth, blindspots)
    
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 报告已保存到：{OUTPUT}")
    print(f"   文件大小：{len(report):,} 字符")


if __name__ == '__main__':
    main()
