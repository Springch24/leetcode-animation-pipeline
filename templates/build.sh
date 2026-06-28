#!/bin/bash
# LeetCode 视频批量生成脚本
# 用法: ./build.sh <题号> <题名> <难度> <描述>
# 示例: ./build.sh 1 "Two Sum" Easy "nums=[2,7,11,15], target=9"

set -e
export PATH="$HOME/.local/bin:$HOME/.nvm/versions/node/v24.14.0/bin:$PATH"

NUM="${1:-1}"
NAME="${2:-Two Sum}"
DIFF="${3:-Easy}"

echo ">>> 生成 LeetCode $NUM. $NAME ($DIFF) 视频"

# 渲染
cd "$(dirname "$0")"
hyperframes render --quality standard --workers 1

# 找到最新 mp4
latest=$(ls -t renders/leetcode-video_*.mp4 2>/dev/null | head -1)
if [ -z "$latest" ]; then
  echo "ERROR: 渲染失败"
  exit 1
fi

# 合成音频（如果有 narration.wav）
if [ -f narration.wav ]; then
  output="renders/leetcode-${NUM}-${NAME// /_}.mp4"
  ffmpeg -y -i "$latest" -i narration.wav \
    -c:v copy -c:a aac -shortest -map 0:v:0 -map 1:a:0 \
    "$output" 2>/dev/null
  rm -f renders/leetcode-video_*.mp4
  echo ">>> 完成: $output"
else
  mv "$latest" "renders/leetcode-${NUM}-${NAME// /_}.mp4"
  echo ">>> 完成 (无音频)"
fi
