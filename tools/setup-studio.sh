#!/bin/bash
# 디자인 허브 스튜디오를 맥에 한 번에 준비합니다.
#   bash <(curl -fsSL https://designrefs.com/tools/setup-studio.sh)
#
# 하는 일
#   1. 이 맥에서 사이트 저장소 폴더를 찾습니다 (tools/admin.py 가 있는 폴더)
#   2. GitHub 의 최신 내용을 받아 옵니다
#   3. 필요한 것을 설치합니다: Pillow(이미지), Anthropic SDK(AI 편집장), ffmpeg(릴스 영상, Homebrew 가 있을 때)
#   4. 바탕화면에 '디자인허브 스튜디오.command' 아이콘을 만듭니다
#   5. 스튜디오를 엽니다
set -e
say() { printf "\n\033[1m%s\033[0m\n" "$1"; }

say "1/5 저장소 폴더 찾는 중…"
REPO=""
for d in "$PWD" "$HOME/Desktop/클로드코드/Leo-AXdesign.github.io" "$HOME/Leo-AXdesign.github.io"; do
  [ -f "$d/tools/admin.py" ] && REPO="$d" && break
done
if [ -z "$REPO" ]; then
  HIT=$(find "$HOME" -maxdepth 6 -path "*/tools/admin.py" -not -path "*/Library/*" -not -path "*/.Trash/*" 2>/dev/null | head -1)
  [ -n "$HIT" ] && REPO=$(cd "$(dirname "$HIT")/.." && pwd)
fi
if [ -z "$REPO" ]; then
  echo "사이트 저장소 폴더를 찾지 못했습니다. 관리자를 여는 폴더에서 이 명령을 다시 실행해 주세요."
  exit 1
fi
echo "찾았습니다: $REPO"
cd "$REPO"

say "2/5 최신 내용 받는 중…"
git pull -q --rebase --autostash origin main && echo "완료"

say "3/5 필요한 것 설치 중…"
if python3 -c "import PIL" 2>/dev/null; then
  echo "Pillow: 이미 있음"
else
  python3 -m pip install --user -q pillow && echo "Pillow: 설치함"
fi
if python3 -c "import anthropic" 2>/dev/null; then
  python3 -m pip install --user -q --upgrade anthropic && echo "Anthropic SDK(AI 편집장): 최신으로 맞춤"
else
  python3 -m pip install --user -q anthropic && echo "Anthropic SDK(AI 편집장): 설치함"
fi
if command -v ffmpeg >/dev/null; then
  echo "ffmpeg: 이미 있음"
elif command -v brew >/dev/null; then
  echo "ffmpeg 설치 중 (몇 분 걸릴 수 있어요)…"
  brew install -q ffmpeg && echo "ffmpeg: 설치함"
else
  echo "ffmpeg: Homebrew 가 없어 건너뜁니다. 이미 만들어 둔 릴스 발행에는 필요 없고, 새 릴스를 만들 때만 필요합니다."
fi

say "4/5 바탕화면 아이콘 만드는 중…"
LAUNCHER="$HOME/Desktop/디자인허브 스튜디오.command"
cat > "$LAUNCHER" <<EOF
#!/bin/zsh
cd "$REPO"
git pull -q --rebase --autostash origin main
python3 tools/studio.py
EOF
chmod +x "$LAUNCHER"
echo "만들었습니다: 바탕화면 > 디자인허브 스튜디오.command (두 번 누르면 열려요)"

say "5/5 스튜디오 여는 중…"
echo "브라우저가 열립니다. 다 쓰면 이 창에서 Ctrl+C 를 누르거나 창을 닫으세요."
python3 tools/studio.py
