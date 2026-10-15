#!/bin/zsh
# 예약 실행용 (launchd 가 호출). 수동 실행도 가능: ./run.sh --dry-run
# 로그: ~/Library/Logs/ai-hanip-autopost.log
cd "${0:A:h}" || exit 1
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
export PYTHONWARNINGS=ignore PYTHONUNBUFFERED=1  # 로그에 진행 상황이 바로 찍히도록
echo "===== $(date '+%Y-%m-%d %H:%M:%S') 시작 $*"
# 인자가 없으면 시간대로 슬롯 결정: 14시 전 = morning, 이후 = evening
if [ $# -eq 0 ]; then
  if [ $(date +%H) -lt 14 ]; then set -- --slot morning; else set -- --slot evening; fi
fi
caffeinate -i .venv/bin/python -m autopost.main "$@"
code=$?
echo "===== $(date '+%Y-%m-%d %H:%M:%S') 종료 (code $code)"
if [ $code -ne 0 ]; then
  osascript -e 'display notification "로그: ~/Library/Logs/ai-hanip-autopost.log" with title "AI 한입 자동 포스팅 실패"' 2>/dev/null
fi
exit $code
