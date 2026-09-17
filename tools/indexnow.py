#!/usr/bin/env python3
"""
사이트맵의 주소를 IndexNow 로 제출합니다.
IndexNow 에 참여하는 검색엔진(Bing, 네이버, Yandex 등)에 한 번에 전달됩니다.

  python3 tools/indexnow.py

배포(push)가 끝나 사이트에 반영된 뒤에 실행하세요.
키 파일(fac1ebe51d5f2cbef4f356705c5fc430.txt)은 저장소 루트에 있어야 하며 지우면 안 됩니다.
"""
import json, re, pathlib, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
HOST = "designrefs.com"
KEY = "fac1ebe51d5f2cbef4f356705c5fc430"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"

urls = re.findall(r"<loc>([^<]+)</loc>", (ROOT / "sitemap.xml").read_text(encoding="utf-8"))
extra = [f"https://{HOST}/llms.txt", f"https://{HOST}/llms-full.txt"]
url_list = list(dict.fromkeys(urls + extra))

# 제출 전에 키 파일이 실제로 열리는지 확인 (없으면 검색엔진이 거부합니다)
with urllib.request.urlopen(KEY_LOCATION, timeout=20) as r:
    live_key = r.read().decode().strip()
if live_key != KEY:
    raise SystemExit(f"키 파일 내용이 다릅니다: {KEY_LOCATION}")

payload = json.dumps({
    "host": HOST,
    "key": KEY,
    "keyLocation": KEY_LOCATION,
    "urlList": url_list,
}).encode()
req = urllib.request.Request(
    "https://api.indexnow.org/indexnow",
    data=payload,
    headers={"Content-Type": "application/json; charset=utf-8"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f"제출 완료: 주소 {len(url_list)}개, 응답 {r.status}")
except urllib.error.HTTPError as err:
    msg = {400: "요청 형식 오류", 403: "키 확인 실패", 422: "주소와 호스트 불일치",
           429: "요청이 너무 잦음. 잠시 후 다시"}.get(err.code, "")
    print(f"제출 실패: {err.code} {msg}")
    raise SystemExit(1)
