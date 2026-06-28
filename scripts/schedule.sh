#!/bin/bash
# ============================================
# 定时任务管理脚本
#
# 用法:
#   ./schedule.sh on <题号>    # 注册定时任务（明天 17:00 执行）
#   ./schedule.sh off          # 取消定时任务
#   ./schedule.sh status       # 查看状态
#   ./schedule.sh now <题号>   # 立即执行
# ============================================

PLIST="$HOME/Library/LaunchAgents/com.zixue-suanfa.daily-build.plist"
BUILD_SCRIPT="/Users/sring24/Desktop/个人ip构建/scripts/daily-build.sh"
PLIST_TEMPLATE="$PLIST"
LOGS="/Users/sring24/Desktop/个人ip构建/logs"

cmd="${1:-status}"
arg="${2:-}"

case "$cmd" in
  on)
    if [ -z "$arg" ]; then
      echo "❌ 用法: $0 on <LeetCode题号>"
      exit 1
    fi
    mkdir -p "$LOGS"

    # 替换题号
    sed "s/__LEETCODE_NUM__/$arg/g" "$PLIST_TEMPLATE" > "$PLIST"

    # 卸载旧的
    launchctl unload "$PLIST" 2>/dev/null || true
    # 加载新的
    launchctl load "$PLIST"

    echo "✅ 定时任务已注册！"
    echo "   题目: LeetCode #$arg"
    echo "   时间: 每天 17:00"
    echo "   日志: $LOGS/daily-build.log"
    ;;

  off)
    launchctl unload "$PLIST" 2>/dev/null && echo "✅ 定时任务已取消" || echo "⚠️ 没有运行中的任务"
    ;;

  status)
    if launchctl list | grep -q "com.zixue-suanfa.daily-build"; then
      echo "✅ 定时任务运行中"
      echo ""
      echo "最近日志:"
      tail -20 "$LOGS/daily-build.log" 2>/dev/null || echo "(暂无日志)"
    else
      echo "⏸  定时任务未运行"
    fi
    ;;

  now)
    if [ -z "$arg" ]; then
      echo "❌ 用法: $0 now <LeetCode题号>"
      exit 1
    fi
    echo "🚀 立即执行构建..."
    bash "$BUILD_SCRIPT" "$arg"
    ;;

  *)
    echo "用法: $0 {on|off|status|now} [题号]"
    echo ""
    echo "  on <题号>   注册定时任务，每天 17:00 自动构建"
    echo "  off          取消定时任务"
    echo "  status       查看状态和最近日志"
    echo "  now <题号>   立即执行构建"
    ;;
esac
