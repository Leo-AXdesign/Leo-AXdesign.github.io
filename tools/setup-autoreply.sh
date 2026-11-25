#!/bin/bash
# 인스타 댓글 자동 답장과 스레드 댓글 자동 답글을 5분마다 돌게 설치합니다 (이 맥이 켜져 있을 때만 돕니다).
#   설치:  bash tools/setup-autoreply.sh
#   제거:  bash tools/setup-autoreply.sh --remove
# 어떤 게시물에 켤지는 Claude 에서 ig_autoreply_on 으로 정합니다. 켜 둔 게시물이 없으면 아무것도 보내지 않습니다.
set -e
LABEL="com.designrefs.ig-autoreply"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
DIR="$HOME/.designhub"
RUNNER="$DIR/ig-autoreply.mjs"
HERE="$(cd "$(dirname "$0")/.." && pwd)"

if [ "$1" = "--remove" ]; then
  launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
  rm -f "$PLIST"
  echo "자동 답장 실행을 멈추고 지웠습니다. (켜 둔 게시물 목록과 기록은 $DIR 에 남아 있습니다)"
  exit 0
fi

NODE="$(command -v node || true)"
[ -z "$NODE" ] && { echo "Node.js 가 없습니다. https://nodejs.org 에서 설치한 뒤 다시 실행하세요."; exit 1; }

mkdir -p "$DIR" "$HOME/Library/LaunchAgents"
# 저장소에 있는 최신 파일을 씁니다 (Claude 연결 도구와 같은 폴더에 둬야 ig_autoreply_run 이 찾습니다)
cp "$HERE/mcp/ig-autoreply.mjs" "$RUNNER"
cp "$HERE/mcp/th-autoreply.mjs" "$DIR/th-autoreply.mjs"
cp "$HERE/mcp/designhub-social.mjs" "$DIR/designhub-social.mjs"

cat > "$PLIST" <<XML
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array><string>/bin/sh</string><string>-c</string><string>"$NODE" "$RUNNER"; "$NODE" "$DIR/th-autoreply.mjs"</string></array>
  <key>StartInterval</key><integer>300</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>$DIR/autoreply.out.log</string>
  <key>StandardErrorPath</key><string>$DIR/autoreply.out.log</string>
</dict>
</plist>
XML

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "설치 완료: 5분마다 켜 둔 게시물의 새 댓글을 확인합니다."
echo "실행 기록: $DIR/autoreply.out.log"
echo "Claude 데스크톱을 다시 열면 ig_autoreply_* · th_autoreply_* (켜기·끄기·상태·실행) 도구가 보입니다."
