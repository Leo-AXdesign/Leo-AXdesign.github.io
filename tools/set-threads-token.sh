#!/bin/bash
# 디자인 허브 스레드 토큰을 새 토큰으로 바꿉니다 (권한을 더 켜고 다시 받았을 때).
#   bash <(curl -fsSL https://designrefs.com/tools/set-threads-token.sh)
#
# - 토큰은 화면에 보이지 않게 입력받습니다.
# - 스레드 서버에 물어 토큰이 맞는지, 어느 계정인지 확인한 뒤 Claude 데스크톱 설정에 저장합니다.
#   (스튜디오도 같은 설정에서 토큰을 읽습니다. 저장 전 설정 파일은 .bak 으로 백업)
# - Claude 데스크톱이 켜져 있으면 설정을 덮어쓸 수 있어서, 먼저 Cmd+Q 로 꺼 주세요.
set -e
printf "\n\033[1m디자인 허브 스레드 토큰 바꾸기\033[0m\n"
if pgrep -x "Claude" >/dev/null 2>&1; then
  echo "Claude 데스크톱이 켜져 있어요. Cmd+Q 로 끈 뒤 다시 실행해 주세요."
  exit 1
fi
printf "새 스레드 토큰 붙여넣기 (화면에 안 보여요, 붙여넣고 Enter): "
read -s TOKEN
echo
[ -z "$TOKEN" ] && { echo "토큰이 비어 있어요."; exit 1; }

TOKEN="$TOKEN" python3 - <<'PY'
import json, os, pathlib, shutil, urllib.parse, urllib.request, urllib.error
token = os.environ["TOKEN"].strip()
q = urllib.parse.urlencode({"fields": "id,username", "access_token": token})
try:
    with urllib.request.urlopen("https://graph.threads.net/v1.0/me?" + q, timeout=30) as r:
        me = json.loads(r.read())
except urllib.error.HTTPError as e:
    try:
        msg = json.loads(e.read()).get("error", {}).get("message", "")
    except ValueError:
        msg = ""
    print(f"토큰을 확인하지 못했습니다 ({e.code}). {msg.replace(token, '[토큰]')}")
    print("스레드 토큰인지(THAA… 로 시작), 복사가 잘렸는지 확인해 주세요.")
    raise SystemExit(1)
p = pathlib.Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
try:
    conf = json.loads(p.read_text())
except (OSError, ValueError):
    print("Claude 데스크톱 설정 파일을 찾지 못했습니다.")
    raise SystemExit(1)
server = next((s for s in (conf.get("mcpServers") or {}).values()
               if any("designhub-social" in str(a) for a in s.get("args", []))), None)
if not server:
    print("설정에 designhub 서버가 없습니다. 설치 한 줄(setup-studio.sh)을 먼저 실행해 주세요.")
    raise SystemExit(1)
shutil.copyfile(p, str(p) + ".bak")
env = server.setdefault("env", {})
env["THREADS_ACCESS_TOKEN"] = token
env["THREADS_USER_ID"] = me["id"]
p.write_text(json.dumps(conf, ensure_ascii=False, indent=2))
print(f"바꿨습니다: @{me.get('username', '')} 의 새 토큰을 저장했어요.")
print("이제 Claude 데스크톱을 켜고, 스튜디오는 새로 열면 새 토큰으로 올립니다.")
PY
