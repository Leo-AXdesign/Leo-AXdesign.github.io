#!/usr/bin/env python3
"""
인스타그램 카드뉴스(1080×1350)를 사이트 데이터로 만듭니다.

  python3 tools/build-cards.py              # 모든 묶음
  python3 tools/build-cards.py fonts-hangul # 한 묶음만

- 결과는 저장소 밖 홍보자료/cards/<묶음>/01.png ... 에 저장됩니다. (사이트에는 올라가지 않음)
- 사이트 이름·주소·설명은 js/data.js 에서 그대로 가져옵니다. 설명을 고치려면 data.js 를 고치세요.
- 새 묶음은 아래 SETS 에 하나 추가하면 됩니다.

카드 종류
  cover  표지      title, sub
  site   사이트    name (data.js 의 사이트 이름)
  tip    정보      title, points
  outro  마무리    title, url, sub
"""
import html, pathlib, re, sys, tempfile

import sitedata as D
from snap import shoot

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT.parent / "홍보자료" / "cards"
SIZE = (1080, 1350)
e = html.escape

SETS = {
    # 한글날(10/9) 특집
    "fonts-hangul": [
        {"kind": "cover", "title": "상업용 무료 한글 폰트,\n여기서 받으세요", "sub": "한글날에 저장해 두는 폰트 사이트 4곳"},
        {"kind": "site", "name": "눈누"},
        {"kind": "site", "name": "Pretendard"},
        {"kind": "site", "name": "네이버 한글한글 아름답게"},
        {"kind": "site", "name": "Google Fonts"},
        {"kind": "tip", "title": "받기 전에 확인할 것",
         "points": ["‘상업용 무료’여도 로고·BI에는 못 쓰는 폰트가 있어요",
                    "폰트 파일을 그대로 다시 배포하는 건 대부분 안 돼요",
                    "웹폰트로 써도 되는지, 영상·인쇄물 범위는 어디까지인지 라이선스 문서를 한 번 열어 보세요"]},
        {"kind": "outro", "title": "폰트 사이트 23곳,\n한 페이지에 모아 뒀어요", "url": "designrefs.com/font",
         "sub": "저장해 두면 필요할 때 바로 꺼내 볼 수 있어요"},
    ],
}

CSS = """
html, body { margin: 0; width: 1080px; height: 1350px; overflow: hidden; background: #fff; }
body { font-family: "Pretendard Variable", Pretendard, "Apple SD Gothic Neo", sans-serif; color: #111;
       -webkit-font-smoothing: antialiased; }
.card { box-sizing: border-box; width: 1080px; height: 1350px; padding: 88px 88px 80px; display: flex; flex-direction: column; }
.top { display: flex; justify-content: space-between; align-items: baseline; }
.logo { font-size: 56px; font-weight: 800; letter-spacing: -0.04em; }
.logo span { color: #A3A3A3; }
.page { font-size: 28px; color: #8A8A8A; font-variant-numeric: tabular-nums; }
.bottom { display: flex; justify-content: space-between; align-items: baseline; font-size: 28px; color: #6B6B6B; }
.bottom b { color: #111; }
.rule { height: 5px; background: #111; margin: 48px 0 28px; }

/* 표지 */
.cover .title { margin-top: auto; font-size: 104px; line-height: 1.16; font-weight: 800; letter-spacing: -0.045em;
                white-space: pre-line; word-break: keep-all; }
.cover .sub { margin-top: 36px; font-size: 38px; color: #6B6B6B; letter-spacing: -0.02em; }

/* 사이트 */
.site .num { margin-top: auto; font-size: 30px; font-weight: 700; color: #8A8A8A; }
.site .name { margin-top: 18px; font-size: 104px; line-height: 1.1; font-weight: 800; letter-spacing: -0.045em;
              word-break: keep-all; text-wrap: balance; }
.site .host { margin-top: 22px; font-size: 34px; color: #8A8A8A; }
.site .desc { font-size: 44px; line-height: 1.55; letter-spacing: -0.02em; word-break: keep-all; }
.site .tags { display: flex; gap: 14px; margin: 40px 0 88px; }
.site .tag { font-size: 28px; font-weight: 600; padding: 10px 26px; border: 2px solid #111; border-radius: 999px; }

/* 정보 */
.tip .title { margin-top: 120px; font-size: 76px; font-weight: 800; letter-spacing: -0.04em; }
.tip ol { list-style: none; margin: 64px 0 0; padding: 0; counter-reset: n; }
.tip li { counter-increment: n; position: relative; padding: 36px 0 36px 96px; border-top: 2px solid #E2E2E2;
          font-size: 42px; line-height: 1.5; letter-spacing: -0.02em; word-break: keep-all; text-wrap: pretty; }
.tip li:last-child { border-bottom: 2px solid #E2E2E2; }
.tip li::before { content: counter(n, decimal-leading-zero); position: absolute; left: 0; top: 40px;
                  font-size: 32px; font-weight: 700; color: #8A8A8A; }

/* 마무리 */
.outro { background: #111; color: #fff; }
.outro .logo span { color: #6B6B6B; }
.outro .title { margin-top: auto; font-size: 92px; line-height: 1.18; font-weight: 800; letter-spacing: -0.045em;
                white-space: pre-line; word-break: keep-all; }
.outro .url { margin-top: 56px; display: inline-block; align-self: flex-start; font-size: 44px; font-weight: 700;
              padding: 22px 40px; border-radius: 999px; background: #fff; color: #111; }
.outro .sub { margin-top: 36px; font-size: 34px; color: #A3A3A3; }
.outro .rule { background: #fff; }
.outro .bottom, .outro .bottom b { color: #A3A3A3; }
"""


def site_tags(name):
    m = re.search(r"\{[^{}]*name: '" + re.escape(name) + r"'[^{}]*\}", D.SRC)
    t = re.search(r"tags: \[([^\]]*)\]", m.group(0)) if m else None
    return re.findall(r"'([^']+)'", t.group(1)) if t else []


def host(url):
    return re.sub(r"^https?://(www\.)?", "", url).split("/")[0]


def render(card, i, total, n_site):
    top = (f'<div class="top"><div class="logo">d<span>.</span></div>'
           f'<div class="page">{i} / {total}</div></div>')
    foot = ('<div class="bottom"><span><b>디자인 허브</b> · 디자이너를 위한 레퍼런스 모음</span>'
            '<span>designrefs.com</span></div>')
    k = card["kind"]
    if k == "cover":
        mid = (f'<div class="title">{e(card["title"])}</div><div class="sub">{e(card["sub"])}</div>'
               '<div class="rule"></div>')
        foot = '<div class="bottom"><span><b>디자인 허브</b></span><span>넘겨서 보기 →</span></div>'
    elif k == "site":
        s = next((x for x in D.sites if x["name"] == card["name"]), None)
        if not s:
            raise SystemExit(f"data.js 에 없는 사이트입니다: {card['name']}")
        tags = "".join(f'<span class="tag">{e(t)}</span>' for t in site_tags(s["name"]))
        mid = (f'<div class="num">{n_site:02d}</div><div class="name">{e(s["name"])}</div>'
               f'<div class="host">{e(host(s["url"]))}</div><div class="rule"></div>'
               f'<div class="desc">{e(s["desc"])}</div><div class="tags">{tags}</div>')
    elif k == "tip":
        items = "".join(f"<li>{e(p)}</li>" for p in card["points"])
        mid = f'<div class="title">{e(card["title"])}</div><ol>{items}</ol><div style="margin-top:auto"></div><div class="rule"></div>'
    elif k == "outro":
        mid = (f'<div class="title">{e(card["title"])}</div><div class="url">{e(card["url"])}</div>'
               f'<div class="sub">{e(card["sub"])}</div><div class="rule"></div>')
    else:
        raise SystemExit(f"모르는 카드 종류: {k}")
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/'
            'dist/web/variable/pretendardvariable-dynamic-subset.min.css">'
            f'<style>{CSS}</style></head><body><div class="card {k}">{top}{mid}{foot}</div></body></html>')


def build(set_id):
    cards = SETS[set_id]
    out = OUT / set_id
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.png"):
        old.unlink()
    n_site = 0
    with tempfile.TemporaryDirectory() as tmp:
        for i, card in enumerate(cards, 1):
            if card["kind"] == "site":
                n_site += 1
            page = pathlib.Path(tmp) / f"{i:02d}.html"
            page.write_text(render(card, i, len(cards), n_site), encoding="utf-8")
            shoot(page, out / f"{i:02d}.png", size=SIZE)
    print(f"{set_id}: {len(cards)}장 → {out}")


if __name__ == "__main__":
    for sid in (sys.argv[1:] or SETS):
        if sid not in SETS:
            raise SystemExit(f"없는 묶음입니다: {sid} (있는 것: {', '.join(SETS)})")
        build(sid)
