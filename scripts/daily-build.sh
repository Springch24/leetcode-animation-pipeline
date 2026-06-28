#!/bin/bash
# ============================================
# 自学算法 - 每日自动构建脚本
# 用法: ./daily-build.sh <题号>
# 示例: ./daily-build.sh 11
#
# 前提：题目的 index.html 和 narration.txt 已由 AI 提前生成
#       存放在 videos/leetcode-<题号>-<标题>/ 下
#
# 定时: 建议每天 17:00 由 launchd 触发
# ============================================
set -e

export PATH="$HOME/.local/bin:$PATH"
BASE="/Users/sring24/Desktop/个人ip构建"
COVER_SCRIPT="$BASE/cover-template/generate-cover.sh"
CANDIDATES="$BASE/candidates.json"

LEETCODE_NUM="$1"
if [ -z "$LEETCODE_NUM" ]; then
  echo "❌ 用法: $0 <LeetCode题号>"
  exit 1
fi

# ===== 1. 从 candidates.json 提取题目信息 =====
INFO=$(python3 -c "
import json, sys
with open('$CANDIDATES') as f:
    data = json.load(f)
for c in data:
    if c['id'] == $LEETCODE_NUM:
        print(f'{c[\"id\"]}|{c[\"title\"]}|{c[\"difficulty\"]}|{c[\"tag\"]}')
        break
")

if [ -z "$INFO" ]; then
  echo "❌ 题目 $LEETCODE_NUM 不在 candidates.json 中"
  exit 1
fi

TITLE=$(echo "$INFO" | cut -d'|' -f2)
DIFF=$(echo "$INFO" | cut -d'|' -f3)
TAG=$(echo "$INFO" | cut -d'|' -f4)

# 难度映射
case "$DIFF" in
  简单) DIFF_EN="easy" ;;
  中等) DIFF_EN="medium" ;;
  困难) DIFF_EN="hard" ;;
esac

# 目录名（用题号，标题可能有特殊字符）
VIDEO_DIR=$(ls -d "$BASE/videos/leetcode-$LEETCODE_NUM-"* 2>/dev/null | head -1)
if [ -z "$VIDEO_DIR" ]; then
  echo "❌ 视频目录不存在: $BASE/videos/leetcode-$LEETCODE_NUM-*"
  echo "   请先让 AI 生成 index.html 和 narration.txt"
  exit 1
fi

echo "📹 题目: #$LEETCODE_NUM $TITLE ($DIFF)"
echo "📂 目录: $VIDEO_DIR"

# ===== 2. TTS 合成配音 =====
echo ""
echo "🎙  TTS 合成中..."
if [ -f "$VIDEO_DIR/narration.txt" ]; then
  python3 -m edge_tts \
    --voice zh-CN-YunyangNeural \
    --file "$VIDEO_DIR/narration.txt" \
    --write-media "$VIDEO_DIR/narration.mp3" 2>/dev/null
  echo "   ✅ narration.mp3 完成 ($(du -h "$VIDEO_DIR/narration.mp3" | cut -f1))"
else
  echo "   ⚠️  narration.txt 不存在，跳过 TTS"
fi

# ===== 3. 生成封面 =====
echo ""
echo "🖼  封面生成中..."
# 从 narration.txt 提取描述（第一段）
DESC=""
if [ -f "$VIDEO_DIR/narration.txt" ]; then
  DESC=$(head -2 "$VIDEO_DIR/narration.txt" | tr '\n' ' ' | sed 's/,$//')
fi
if [ -z "$DESC" ]; then
  DESC="LeetCode $LEETCODE_NUM: $TITLE"
fi

bash "$COVER_SCRIPT" "$LEETCODE_NUM" "$TITLE" "$DIFF_EN" "$DESC" "$TAG" 2>&1 | tail -2

# ===== 4. 渲染视频 =====
echo ""
echo "🎬 渲染视频中..."
cd "$VIDEO_DIR"
rm -rf renders

npx hyperframes render . -o "./leetcode-$LEETCODE_NUM.mp4" -f 30 -q high 2>&1 | tail -3

# ===== 5. 合并音频 =====
OUTPUT_VIDEO="$BASE/videos/leetcode-$LEETCODE_NUM-$TITLE.mp4"
if [ -f "$VIDEO_DIR/narration.mp3" ] && [ -f "$VIDEO_DIR/leetcode-$LEETCODE_NUM.mp4" ]; then
  echo ""
  echo "🔊 合并音频..."
  ffmpeg -i "$VIDEO_DIR/leetcode-$LEETCODE_NUM.mp4" \
         -i "$VIDEO_DIR/narration.mp3" \
         -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 \
         -shortest -y "$OUTPUT_VIDEO" 2>&1 | tail -1
  echo "   ✅ $(du -h "$OUTPUT_VIDEO" | cut -f1)"
else
  echo "   ⚠️ 无音频，跳过合并"
  if [ -f "$VIDEO_DIR/leetcode-$LEETCODE_NUM.mp4" ]; then
    cp "$VIDEO_DIR/leetcode-$LEETCODE_NUM.mp4" "$OUTPUT_VIDEO"
  fi
fi

# ===== 6. 生成发布文案 =====
BILI_DESC="$BASE/data/bilibili-draft-$LEETCODE_NUM.txt"
cat > "$BILI_DESC" << DESC_END
【B站标题】$TITLE 这道题，你真的会了吗？

【简介】
$TITLE（LeetCode $LEETCODE_NUM）的动画讲解。

标签：#LeetCode #算法 #${TAG} #面试 #自学算法
DESC_END

echo ""
echo "========================================="
echo "✅ 全部完成！"
echo ""
echo "📺 视频: $OUTPUT_VIDEO"
echo "🖼  封面: $BASE/covers/leetcode-$LEETCODE_NUM-cover.png"
echo "📝 文案: $BILI_DESC"
echo "========================================="
