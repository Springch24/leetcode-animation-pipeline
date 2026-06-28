#!/usr/bin/env python3
"""从 LeetcodeTop 仓库拉取高频面经题，构建结构化题库 JSON。
输出: miniprogram/utils/question_bank.json
"""

import json
import os
import re
import urllib.request
from pathlib import Path

COMPANIES = {
    "字节跳动": ["backend", "frontend", "algorithm", "client", "test", "data"],
    "腾讯": ["backend", "frontend", "algorithm", "client", "test"],
    "美团": ["backend", "frontend", "algorithm", "client", "test", "data"],
    "阿里巴巴": ["backend", "frontend", "algorithm", "client", "test", "data"],
    "快手": ["backend", "frontend", "algorithm", "client", "test"],
    "百度": ["backend", "frontend", "algorithm", "client", "test"],
    "虾皮": ["backend", "frontend", "algorithm", "client", "test", "data"],
    "网易": ["backend", "frontend", "algorithm", "client", "test"],
    "京东": ["backend", "frontend", "algorithm", "client", "test"],
    "拼多多": ["backend", "frontend", "algorithm"],
    "滴滴": ["backend", "frontend", "algorithm"],
    "华为": ["backend", "frontend", "algorithm", "test"],
    "微软中国": ["SDE"],
    "亚马逊中国": ["SDE"],
}

TAG_MAP = {
    "链表": ["链表", "linked-list", "reverse", "merge", "reorder", "cycle", "intersection", "palindrome"],
    "二叉树": ["树", "二叉树", "binary-tree", "bst", "traversal", "preorder", "inorder", "postorder", "zigzag", "ancestor", "diameter", "path-sum", "symmetric", "right-side"],
    "数组": ["数组", "array", "matrix", "spiral", "merge-intervals", "next-permutation"],
    "双指针": ["双指针", "two-pointer", "sliding-window", "三个数", "盛水", "移动零"],
    "哈希表": ["哈希", "hash", "两数之和", "最长连续", "异位词", "无重复字"],
    "动态规划": ["dp", "dynamic", "最大子", "上升子", "最长回文", "爬楼梯", "股票", "编辑距离", "正方形"],
    "栈": ["栈", "stack", "括号", "最小栈", "用栈实现队列"],
    "堆": ["堆", "heap", "top-k", "K个", "优先队列"],
    "二分查找": ["二分", "binary-search", "搜索旋转", "平方根"],
    "字符串": ["字符串", "string", "相加", "反转字符"],
    "回溯": ["回溯", "backtrack", "全排列", "组合", "子集"],
    "图": ["图", "graph", "岛屿", "课程表"],
    "设计": ["设计", "LRU", "LFU"],
}

GITHUB_RAW = "https://raw.githubusercontent.com/afatcoder/LeetcodeTop/master"

SHIPPED_VIDEOS = {
    1: "lc001-两数之和", 2: "lc002-两数相加", 3: "lc003-无重复最长子串",
    11: "lc011-盛最多水的容器", 15: "lc015-三数之和", 21: "lc021-合并两个有序链表",
    128: "lc128-最长连续序列", 141: "lc141-环形链表", 160: "lc160-相交链表",
    206: "lc206-反转链表", 234: "lc234-回文链表", 283: "lc283-移动零",
}

ROLE_CN = {"backend": "后端", "frontend": "前端", "algorithm": "算法",
           "client": "客户端", "test": "测试", "data": "数据开发", "SDE": "SDE"}

EN_MAP = {
    "字节跳动": "bytedance", "腾讯": "tencent", "美团": "meituan",
    "阿里巴巴": "alibaba", "快手": "kuaishou", "百度": "baidu",
    "虾皮": "shopee", "网易": "netease", "京东": "jd",
    "拼多多": "pinduoduo", "滴滴": "didi", "华为": "huawei",
    "微软中国": "microsoft", "亚马逊中国": "amazon",
}


def parse_line(line):
    m = re.match(r'\|\s*(?:补充题)?(\d+)\.?\s*(.+?)\s*\|\s*(\d+)\s*\|', line)
    if not m:
        return None
    return {"id": int(m.group(1)), "name": m.group(2).strip(), "count": int(m.group(3))}


def detect_tag(name):
    nl = name.lower()
    for tag, keywords in TAG_MAP.items():
        for kw in keywords:
            if kw.lower() in nl:
                return tag
    return "综合"


def estimate_difficulty(qid, name):
    hard_ids = {25, 42, 124, 239, 76, 84, 32, 72, 297, 23, 4, 10, 44, 128, 85, 51}
    if qid in hard_ids:
        return "困难"
    easy_kw = ["两数之和", "移动零", "合并两个有序", "反转链表", "环形链表",
               "最大深度", "对称", "爬楼梯", "多数元素", "用栈实现队列", "相同的树"]
    for kw in easy_kw:
        if kw in name:
            return "简单"
    return "中等"


def fetch_company(name_en, role):
    url = f"{GITHUB_RAW}/{name_en}/{role}.md"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            text = resp.read().decode("utf-8")
    except Exception as e:
        print(f"  ⚠ 无法拉取 {name_en}/{role}: {e}")
        return []
    questions = []
    for line in text.split("\n"):
        p = parse_line(line)
        if p:
            p["difficulty"] = estimate_difficulty(p["id"], p["name"])
            p["tag"] = detect_tag(p["name"])
            p["has_video"] = p["id"] in SHIPPED_VIDEOS
            if p["has_video"]:
                p["video_id"] = SHIPPED_VIDEOS[p["id"]]
            questions.append(p)
    return questions


def build():
    company_data = {}
    all_q = {}

    for cn, roles in COMPANIES.items():
        name_en = EN_MAP.get(cn, cn.lower())
        company_data[cn] = {}
        for role in roles:
            print(f"📡 拉取 {cn} / {role} ...")
            qs = fetch_company(name_en, role)
            rd = ROLE_CN.get(role, role)
            company_data[cn][rd] = qs
            for q in qs:
                qid = q["id"]
                if qid not in all_q:
                    all_q[qid] = {
                        "id": qid, "name": q["name"], "difficulty": q["difficulty"],
                        "tag": q["tag"], "has_video": q["has_video"],
                        "video_id": q.get("video_id"), "companies": [], "max_count": 0,
                    }
                all_q[qid]["companies"].append({"company": cn, "role": rd, "count": q["count"]})
                all_q[qid]["max_count"] = max(all_q[qid]["max_count"], q["count"])
            print(f"   ✅ {cn}/{rd}: {len(qs)} 题")

    sorted_q = sorted(all_q.values(), key=lambda x: x["max_count"], reverse=True)

    output = {
        "companies": company_data,
        "all_questions": sorted_q,
        "total_questions": len(sorted_q),
        "shipped_count": sum(1 for q in sorted_q if q["has_video"]),
        "company_list": [
            {"name": cn, "roles": [ROLE_CN.get(r, r) for r in rs]}
            for cn, rs in COMPANIES.items()
        ],
    }

    out_path = Path(__file__).parent.parent / "miniprogram" / "utils" / "question_bank.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n🎉 题库生成完毕 → {out_path}")
    print(f"   总题数: {len(sorted_q)} | 已有视频: {output['shipped_count']}")


if __name__ == "__main__":
    build()
