#!/bin/bash
# 스레드 계정을 하나 더 연결합니다 (예: 내 개인 계정).
#   bash <(curl -fsSL https://designrefs.com/tools/add-threads-account.sh)
#
# - 토큰은 화면에 보이지 않게 입력받고, 이 맥의 ~/.designhub/accounts.json 에만 저장합니다 (나만 읽기, 600).
# - 저장 전에 스레드 서버에 물어봐서 토큰이 맞는지, 어떤 계정인지 확인합니다.
# - 연결한 계정은 Claude 데스크톱(designhub)과 스튜디오에서 이름으로 고릅니다. 예: account "me"
set -e
say() { printf "\n\033[1m%s\033[0m\n" "$1"; }

say "스레드 계정 연결"
printf "이 계정을 부를 이름 (영문, 기본 me): "
read NAME
NAME=${NAME:-me}
case "$NAME" in
  designhub) echo "'designhub' 는 디자인 허브 계정 이름이라 쓸 수 없어요. 다른 이름을 골라 주세요."; exit 1 ;;
  *[!a-zA-Z0-9_-]*) echo "이름은 영문·숫자·_·- 만 쓸 수 있어요."; exit 1 ;;
esac

printf "스레드 토큰 붙여넣기 (화면에 안 보여요, 붙여넣고 Enter): "
read -s TOKEN
echo
[ -z "$TOKEN" ] && { echo "토큰이 비어 있어요."; exit 1; }

NAME="$NAME" TOKEN="$TOKEN" python3 - <<'PY'
import json, os, pathlib, urllib.parse, urllib.request, urllib.error
name, token = os.environ["NAME"], os.environ["TOKEN"].strip()
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
    print("스레드 토큰인지(THAA… 로 시작), 만료되지 않았는지 확인해 주세요.")
    raise SystemExit(1)
d = pathlib.Path.home() / ".designhub"
d.mkdir(exist_ok=True)
f = d / "accounts.json"
try:
    accs = json.loads(f.read_text())
except (OSError, ValueError):
    accs = {}
accs[name] = {"threads_token": token, "threads_user_id": me["id"], "username": me.get("username", "")}
f.write_text(json.dumps(accs, ensure_ascii=False, indent=2))
os.chmod(f, 0o600)
print(f"연결했습니다: @{me.get('username', '')} → 이름 '{name}'")
print("Claude 데스크톱: '내 스레드(" + name + ")에 …' 처럼 말하거나 + 메뉴의 write_chain 을 고르세요.")
print("스튜디오: 스레드 발행 화면의 '올릴 계정'에서 고르세요.")
PY
