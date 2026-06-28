#!/bin/bash
# 用法: ./generate-cover.sh <题号> <标题> <难度> <描述> <标签>
# 示例: ./generate-cover.sh 1 "两数之和" easy "给定一个整数数组..." "哈希表"

NUM="$1"
TITLE="$2"
DIFF="$3"
DESC="$4"
TAG="$5"
OUTNAME="leetcode-${NUM}-cover.png"
OUTDIR="/Users/sring24/Desktop/个人ip构建/covers"

# 难度映射
case "$DIFF" in
  easy)   DIFF_CLASS="diff-easy"; DIFF_TEXT="简单" ;;
  medium) DIFF_CLASS="diff-medium"; DIFF_TEXT="中等" ;;
  hard)   DIFF_CLASS="diff-hard"; DIFF_TEXT="困难" ;;
  *)      DIFF_CLASS="diff-easy"; DIFF_TEXT="简单" ;;
esac

# 在标题中找中间字加橙色
TITLE_LEN=${#TITLE}
if [ "$TITLE_LEN" -ge 3 ]; then
  MID=$((TITLE_LEN / 2))
  BEFORE="${TITLE:0:$MID}"
  ACCENT="${TITLE:$MID:1}"
  AFTER="${TITLE:$((MID+1))}"
  TITLE_HTML="${BEFORE}<span class=\"accent-dot\">${ACCENT}</span>${AFTER}"
else
  TITLE_HTML="$TITLE"
fi

# 生成 HTML
cat > /tmp/cover-gen/index.html << HTMLEOF
<!doctype html>
<html lang="zh">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=1920, height=1080" />
  <title>Cover</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;700;900&family=JetBrains+Mono:wght@400;700&display=swap');
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      width: 1920px; height: 1080px; overflow: hidden;
      background: #080C14;
      font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
      position: relative;
    }
    .grid-overlay {
      position: absolute; inset: 0; z-index: 1;
      background-image:
        linear-gradient(rgba(30,60,100,0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(30,60,100,0.05) 1px, transparent 1px);
      background-size: 80px 80px;
    }
    .glow-right { position: absolute; top: -150px; right: -100px; width: 700px; height: 700px; background: radial-gradient(circle, rgba(252,163,17,0.06) 0%, transparent 70%); border-radius: 50%; z-index: 0; }
    .glow-left { position: absolute; bottom: -200px; left: -150px; width: 600px; height: 600px; background: radial-gradient(circle, rgba(30,100,200,0.07) 0%, transparent 70%); border-radius: 50%; z-index: 0; }
    .glow-center { position: absolute; top: 30%; left: 50%; transform: translate(-50%, -50%); width: 500px; height: 500px; background: radial-gradient(circle, rgba(252,163,17,0.04) 0%, transparent 70%); border-radius: 50%; z-index: 0; }
    .scanline { position: absolute; inset: 0; z-index: 50; pointer-events: none; background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.025) 2px, rgba(0,0,0,0.025) 4px); }
    .dot-pattern { position: absolute; z-index: 0; opacity: 0.06; top: 80px; right: 80px; font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #4A6FA5; line-height: 1.8; white-space: pre; }
    .corner-tl { position: absolute; top: 40px; left: 40px; width: 60px; height: 60px; border-top: 2px solid rgba(252,163,17,0.4); border-left: 2px solid rgba(252,163,17,0.4); z-index: 2; opacity: 0.3; }
    .corner-tr { position: absolute; top: 40px; right: 40px; width: 60px; height: 60px; border-top: 2px solid rgba(252,163,17,0.4); border-right: 2px solid rgba(252,163,17,0.4); z-index: 2; opacity: 0.3; }
    .corner-bl { position: absolute; bottom: 40px; left: 40px; width: 60px; height: 60px; border-bottom: 2px solid rgba(252,163,17,0.4); border-left: 2px solid rgba(252,163,17,0.4); z-index: 2; opacity: 0.3; }
    .corner-br { position: absolute; bottom: 40px; right: 40px; width: 60px; height: 60px; border-bottom: 2px solid rgba(252,163,17,0.4); border-right: 2px solid rgba(252,163,17,0.4); z-index: 2; opacity: 0.3; }
    .container { position: absolute; inset: 0; z-index: 10; display: flex; flex-direction: column; align-items: center; justify-content: center; }
    .top-bar { position: absolute; top: 60px; left: 0; right: 0; display: flex; justify-content: space-between; align-items: center; padding: 0 120px; }
    .series-tag { font-family: 'JetBrains Mono', monospace; font-size: 16px; letter-spacing: 0.22em; color: #4A6FA5; border: 1px solid rgba(74,111,165,0.3); padding: 10px 28px; border-radius: 2px; }
    .problem-number { font-family: 'JetBrains Mono', monospace; font-size: 22px; color: #FCA311; letter-spacing: 0.1em; font-weight: 700; }
    .center-content { text-align: center; }
    .difficulty-badge { display: inline-block; font-size: 16px; letter-spacing: 0.15em; padding: 10px 28px; border-radius: 3px; margin-bottom: 36px; font-weight: 500; }
    .diff-easy { color: #4ADE80; border: 1.5px solid rgba(74,222,128,0.4); }
    .diff-medium { color: #FBBF24; border: 1.5px solid rgba(251,191,36,0.4); }
    .diff-hard { color: #F87171; border: 1.5px solid rgba(248,113,113,0.4); }
    .main-title { font-size: 130px; font-weight: 900; color: #E8EDF2; letter-spacing: 0.03em; line-height: 1.1; }
    .accent-dot { color: #FCA311; }
    .subtitle-row { display: flex; gap: 28px; align-items: center; justify-content: center; margin-top: 32px; }
    .subtitle-tag { font-size: 19px; color: #5C7CA5; border: 1px solid rgba(92,124,165,0.3); padding: 9px 22px; border-radius: 3px; letter-spacing: 0.08em; }
    .subtitle-sep { width: 6px; height: 6px; background: #FCA311; border-radius: 50%; opacity: 0.5; }
    .divider-line { width: 100px; height: 2px; background: linear-gradient(90deg, transparent, #FCA311, transparent); margin: 44px auto; }
    .desc-text { font-size: 22px; color: #8899B4; letter-spacing: 0.06em; font-weight: 300; line-height: 1.6; max-width: 900px; }
    .bottom-bar { position: absolute; bottom: 60px; left: 0; right: 0; display: flex; justify-content: center; align-items: center; gap: 32px; }
    .channel-name { font-size: 19px; color: #4A6FA5; letter-spacing: 0.12em; font-weight: 500; }
    .bottom-dot { width: 4px; height: 4px; background: #FCA311; border-radius: 50%; opacity: 0.4; }
    .bottom-tagline { font-size: 15px; color: #3A5A80; letter-spacing: 0.1em; }
  </style>
</head>
<body data-composition-id="cover" data-width="1920" data-height="1080" data-duration="1">
  <div class="grid-overlay"></div>
  <div class="glow-right"></div>
  <div class="glow-left"></div>
  <div class="glow-center"></div>
  <div class="scanline"></div>
  <div class="dot-pattern">
def twoSum(nums, target):
    hashmap = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in hashmap:
            return [hashmap[complement], i]
        hashmap[num] = i
  </div>
  <div class="corner-tl"></div>
  <div class="corner-tr"></div>
  <div class="corner-bl"></div>
  <div class="corner-br"></div>
  <div class="container">
    <div class="top-bar">
      <div class="series-tag">LEETCODE HOT 100</div>
      <div class="problem-number">#${NUM}</div>
    </div>
    <div class="center-content">
      <div class="difficulty-badge ${DIFF_CLASS}">${DIFF_TEXT}</div>
      <div class="main-title">${TITLE_HTML}</div>
      <div class="subtitle-row">
        <span class="subtitle-tag">动画图解</span>
        <span class="subtitle-sep"></span>
        <span class="subtitle-tag">算法可视化</span>
        <span class="subtitle-sep"></span>
        <span class="subtitle-tag">${TAG}</span>
      </div>
      <div class="divider-line"></div>
      <div class="desc-text">${DESC}</div>
    </div>
    <div class="bottom-bar">
      <span class="channel-name">自学算法</span>
      <span class="bottom-dot"></span>
      <span class="bottom-tagline">每天一道算法题 · 面试不再怕</span>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <script>
    var tl = gsap.timeline();
    tl.set("body", { opacity: 1, duration: 0.01 });
    window.__timelines = { cover: tl };
  </script>
</body>
</html>
HTMLEOF

# 渲染
export PATH="$HOME/.local/bin:$PATH"
mkdir -p /tmp/cover-gen/renders
cd /tmp/cover-gen
rm -rf renders/*
npx hyperframes render . -o ./renders/cover.mp4 -f 2 -q high 2>&1 | tail -3

# 抽帧
ffmpeg -i ./renders/cover.mp4 -frames:v 1 -q:v 2 "${OUTDIR}/${OUTNAME}" -y 2>&1 | tail -1

echo "✅ Cover: ${OUTDIR}/${OUTNAME}"
