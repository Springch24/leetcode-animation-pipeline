#!/usr/bin/env python3
"""
DeepSeek 聊天记录 → Obsidian Markdown 知识库
完全本地运行，不上传数据。

用法:
    python3 deepseek_to_obsidian.py <ZIP路径> [输出目录]

示例:
    python3 deepseek_to_obsidian.py ~/Desktop/deepseek_data.zip ./deepseek_obsidian
"""

import zipfile
import json
import os
import re
import sys
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# ── 配置 ──────────────────────────────────────────────

MAX_TITLE_LEN = 50          # 标题最大字数
FIRST_LINE_AS_TITLE = True  # 用用户第一句话做标题
TAGS_KEYWORDS = {
    "编程": ["代码", "python", "java", "c++", "编程", "api", "函数", "bug", "debug",
             "import", "def ", "class ", "docker", "git ", "算法", "leetcode", "前端",
             "后端", "react", "vue", "javascript", "typescript", "sql", "数据库"],
    "AI与大模型": ["模型", "训练", "transformer", "bert", "gpt", "llm", "大模型",
                  "深度学习", "机器学习", "微调", "token", "embedding", "神经网络",
                  "注意力", "attention", "rnn", "lstm", "cnn", "强化学习", "rlhf",
                  "deepseek", "chatgpt", "openai", "claude", "diffusion", "gan"],
    "面试与求职": ["面试", "简历", "实习", "校招", "社招", "offer", "薪资", "跳槽",
                  "八股", "刷题", "笔试", "hr", "内推", "大厂", "bat"],
    "产品与商业": ["产品", "运营", "用户", "增长", "变现", "商业模式", "创业",
                  "融资", "市场", "竞品", "需求", "mvp"],
    "写作与创作": ["写", "文章", "文案", "脚本", "视频", "抖音", "小红书", "公众号",
                  "自媒体", "标题", "内容", "爆款", "选题"],
    "学习与效率": ["笔记", "obsidian", "读书", "学习方法", "费曼", "番茄", "anki",
                  "专注", "效率", "工具", "工作流"],
    "个人成长": ["焦虑", "拖延", "习惯", "自律", "目标", "心态", "情绪", "迷茫",
                "方向", "成长", "改变", "反思", "心流", "冥想"],
    "医学与健康": ["医学", "医疗", "ct", "病历", "诊断", "vqa", "影像", "mri",
                  "病理", "临床", "疾病", "dicom"],
    "数据科学": ["数据", "pandas", "numpy", "分析", "可视化", "特征工程",
                "pipeline", "etl", "报表", "统计"],
}

# ── 辅助函数 ──────────────────────────────────────────

def extract_messages(mapping):
    """
    从树状 mapping 提取有序的消息序列。
    返回: [(time_str, role, content), ...]
    """
    root = mapping.get('root')
    if not root:
        return []
    
    messages = []
    visited = set()
    queue = list(root.get('children', []))
    
    while queue:
        nid = queue.pop(0)
        if nid in visited:
            continue
        visited.add(nid)
        
        node = mapping.get(nid)
        if not node:
            continue
        
        queue.extend(node.get('children', []))
        
        msg = node.get('message')
        if not msg:
            continue
        
        time_str = msg.get('inserted_at', '')
        for frag in msg.get('fragments', []):
            ftype = frag.get('type', '')
            content = frag.get('content', '').strip()
            if not content:
                continue
            
            if ftype == 'REQUEST':
                role = 'user'
            elif ftype == 'RESPONSE':
                role = 'deepseek'
            elif ftype == 'THINK':
                role = 'deepseek-think'
            else:
                role = ftype.lower()
            
            messages.append((time_str, role, content))
    
    return messages


def parse_conversation(conv):
    """解析单个对话，返回结构化数据"""
    conv_id = conv.get('id', 'unknown')
    title = conv.get('title', '').strip()
    inserted_at = conv.get('inserted_at', '')
    updated_at = conv.get('updated_at', '')
    
    mapping = conv.get('mapping', {})
    messages = extract_messages(mapping)
    
    return {
        'id': conv_id,
        'title': title,
        'inserted_at': inserted_at,
        'updated_at': updated_at,
        'messages': messages,
    }


def guess_title(messages, fallback_title, max_len=MAX_TITLE_LEN):
    """从用户第一条消息提取标题"""
    if fallback_title and fallback_title.strip():
        return fallback_title.strip()[:max_len]
    
    for _, role, content in messages:
        if role == 'user':
            # 去掉代码块
            cleaned = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
            cleaned = cleaned.strip()
            # 取第一行
            first_line = cleaned.split('\n')[0].strip()
            # 去掉常见前缀
            first_line = re.sub(r'^[#\->\s]+', '', first_line)
            if len(first_line) > max_len:
                first_line = first_line[:max_len] + '…'
            return first_line if first_line else '未命名对话'
    
    return '未命名对话'


def auto_tag(content, current_tags=None):
    """根据关键词自动打标签"""
    tags = set(current_tags or [])
    content_lower = content.lower()
    
    for tag, keywords in TAGS_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in content_lower:
                tags.add(tag)
                break
    
    return sorted(tags)


def sanitize_filename(name):
    """清理文件名中的非法字符"""
    name = re.sub(r'[<>:"/\\|?*]', '-', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def datetime_from_iso(iso_str):
    """安全解析 ISO 时间字符串"""
    try:
        # 处理时区后缀
        ts = iso_str.replace('+08:00', '').replace('Z', '')
        # 取前19字符: YYYY-MM-DDTHH:MM:SS
        ts = ts[:19]
        return datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S')
    except:
        return None


def generate_markdown(conv_data):
    """为单个对话生成 Markdown 内容"""
    title = conv_data['title']
    messages = conv_data['messages']
    dt = datetime_from_iso(conv_data['inserted_at']) or datetime_from_iso(conv_data['updated_at'])
    
    # 提取标题
    md_title = guess_title(messages, title)
    
    # 自动打标签 — 扫描所有消息内容
    all_text = ' '.join(c for _, _, c in messages[:10])  # 前10条足够判断
    tags = auto_tag(all_text)
    
    # 时间
    date_str = dt.strftime('%Y-%m-%d %H:%M') if dt else '未知时间'
    date_iso = dt.strftime('%Y-%m-%dT%H:%M:%S') if dt else ''
    
    # 构建 YAML Frontmatter
    frontmatter = f"""---
date: {date_iso}
title: "{md_title}"
tags: {json.dumps(tags, ensure_ascii=False)}
from: DeepSeek
conversation_id: "{conv_data['id']}"
---

"""
    
    # 正文
    body = f"# {md_title}\n\n"
    body += f"> 对话时间: {date_str} | 消息数: {len(messages)}\n\n"
    body += "---\n\n"
    
    for time_str, role, content in messages:
        if role == 'user':
            body += f"**🧑 我：**\n\n"
        elif role == 'deepseek':
            body += f"**🤖 DeepSeek：**\n\n"
        elif role == 'deepseek-think':
            body += f"**💭 DeepSeek 思考过程：**\n\n"
            content = f"> {content}"
        else:
            body += f"**{role}：**\n\n"
        
        # 保留原始换行，代码块保持缩进
        body += content + "\n\n"
    
    return frontmatter + body


def process_zip(zip_path, output_dir):
    """主流程"""
    output_dir = Path(output_dir)
    error_log_path = output_dir / 'error.log'
    index_path = output_dir / 'index.md'
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    errors = []
    index_entries = []
    stats = defaultdict(int)
    
    print(f"📂 读取 ZIP: {zip_path}")
    
    with zipfile.ZipFile(zip_path) as zf:
        # 找所有可能的对话文件
        conv_files = [f for f in zf.namelist() if f.endswith('.json') and not f.startswith('__MACOSX')]
        print(f"📄 找到 {len(conv_files)} 个 JSON 文件")
        
        all_convs = []
        for fname in conv_files:
            try:
                with zf.open(fname) as f:
                    raw = f.read()
                    # 尝试 UTF-8，失败则跳过
                    try:
                        text = raw.decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            text = raw.decode('gbk')
                        except:
                            errors.append(f"编码错误: {fname}, 跳过")
                            continue
                    
                    data = json.loads(text)
                    
                    if isinstance(data, list):
                        # conversations.json: 列表形式
                        for item in data:
                            if isinstance(item, dict) and 'mapping' in item:
                                all_convs.append(item)
                    elif isinstance(data, dict):
                        # 用户信息之类，跳过
                        if 'mapping' not in data:
                            continue
                        all_convs.append(data)
                    
            except Exception as e:
                errors.append(f"解析失败: {fname} - {e}")
                continue
        
        print(f"💬 共 {len(all_convs)} 条对话")
        
        # 按时间排序
        def sort_key(conv):
            dt = datetime_from_iso(conv.get('inserted_at', ''))
            return dt or datetime(2000, 1, 1)
        
        all_convs.sort(key=sort_key)
        
        # 逐个生成 Markdown
        for i, conv in enumerate(all_convs):
            try:
                conv_data = parse_conversation(conv)
                if not conv_data['messages']:
                    stats['skipped_empty'] += 1
                    continue
                
                dt = datetime_from_iso(conv_data['inserted_at']) or datetime_from_iso(conv_data['updated_at'])
                if not dt:
                    stats['skipped_no_date'] += 1
                    continue
                
                # 创建年份/月份子目录
                year_dir = output_dir / str(dt.year)
                month_dir = year_dir / f"{dt.month:02d}"
                month_dir.mkdir(parents=True, exist_ok=True)
                
                # 文件名
                title = guess_title(conv_data['messages'], conv_data['title'])
                safe_title = sanitize_filename(title)
                time_prefix = dt.strftime('%Y-%m-%d_%H%M')
                filename = f"{time_prefix}_{safe_title}.md"
                filepath = month_dir / filename
                
                # 生成内容
                md_content = generate_markdown(conv_data)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                
                # 收集索引
                tags = auto_tag(' '.join(c for _, _, c in conv_data['messages'][:10]))
                relative_path = filepath.relative_to(output_dir)
                index_entries.append({
                    'date': dt.strftime('%Y-%m-%d'),
                    'time': dt.strftime('%H:%M'),
                    'title': title,
                    'tags': tags,
                    'msg_count': len(conv_data['messages']),
                    'path': str(relative_path),
                })
                
                stats['success'] += 1
                
                if (i + 1) % 50 == 0:
                    print(f"   进度: {i+1}/{len(all_convs)}")
                    
            except Exception as e:
                conv_id = conv.get('id', '?')
                errors.append(f"生成失败: {conv_id} - {e}")
                stats['failed'] += 1
                continue
        
        # 生成 index.md
        print(f"\n📋 生成 index.md...")
        generate_index(index_entries, index_path)
        
        # 写入错误日志
        if errors:
            with open(error_log_path, 'w', encoding='utf-8') as f:
                f.write(f"# 转换错误日志\n\n")
                f.write(f"处理时间: {datetime.now()}\n\n")
                for err in errors:
                    f.write(f"- {err}\n")
            print(f"⚠️  {len(errors)} 个错误，详见 {error_log_path}")
        
        # 统计输出
        print(f"\n{'='*50}")
        print(f"✅ 转换完成！")
        print(f"   成功: {stats['success']} 条对话")
        print(f"   跳过(空): {stats.get('skipped_empty', 0)}")
        print(f"   跳过(无日期): {stats.get('skipped_no_date', 0)}")
        print(f"   失败: {stats.get('failed', 0)}")
        print(f"   输出: {output_dir.resolve()}")
        print(f"{'='*50}")


def generate_index(entries, index_path):
    """生成 index.md"""
    lines = []
    lines.append("# DeepSeek 对话索引\n")
    lines.append(f"> 共 {len(entries)} 条对话，最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    lines.append("---\n")
    
    # 按标签统计
    tag_count = defaultdict(int)
    for e in entries:
        for t in e['tags']:
            tag_count[t] += 1
    
    if tag_count:
        lines.append("## 标签分布\n")
        for tag in sorted(tag_count.keys(), key=lambda t: -tag_count[t]):
            lines.append(f"- #{tag} ({tag_count[tag]}条)")
        lines.append("")
    
    # 按月统计
    month_count = defaultdict(int)
    for e in entries:
        month = e['date'][:7]  # YYYY-MM
        month_count[month] += 1
    
    lines.append("## 月度分布\n")
    for month in sorted(month_count.keys()):
        bar = '█' * min(month_count[month], 50)
        lines.append(f"- {month}: {month_count[month]} 条 {bar}")
    
    lines.append("\n---\n")
    lines.append("## 全部对话\n")
    lines.append("| 日期 | 时间 | 对话 | 消息数 | 标签 |")
    lines.append("|------|------|------|--------|------|")
    
    for e in sorted(entries, key=lambda x: x['date'] + x['time'], reverse=True):
        tags_str = ' '.join(f'`{t}`' for t in e['tags']) if e['tags'] else '-'
        path = e['path'].replace(' ', '%20')
        lines.append(f"| {e['date']} | {e['time']} | [[{path}\\|{e['title']}]] | {e['msg_count']} | {tags_str} |")
    
    lines.append("")
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 deepseek_to_obsidian.py <ZIP路径> [输出目录]")
        sys.exit(1)
    
    zip_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './deepseek_obsidian'
    
    if not os.path.exists(zip_path):
        print(f"❌ 文件不存在: {zip_path}")
        sys.exit(1)
    
    process_zip(zip_path, output_dir)
