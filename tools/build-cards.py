#!/usr/bin/env python3
"""
인스타그램 카드뉴스(1080×1350)를 사이트 데이터로 만듭니다.

  python3 tools/build-cards.py                     # 아래 SETS 전부 + 읽을거리 최신 글
  python3 tools/build-cards.py fonts-pick          # 한 묶음만
  python3 tools/build-cards.py article:<slug>      # 읽을거리 한 편을 캐러셀로 (자동)

- 결과는 social/cards/<묶음>/01.jpg ... 로 저장되고, 사이트에 함께 배포됩니다.
  인스타그램 게시 API 는 공개 주소의 JPEG 만 받기 때문입니다.
  → https://designrefs.com/social/cards/<묶음>/01.jpg
- 묶음마다 caption.txt(캡션 초안)를 만들고, social/cards/index.json 에 목록을 모아 둡니다.
  Claude 데스크톱의 designhub MCP 가 이 목록을 읽어 게시합니다.
- 사이트 이름·주소·설명, 용어 설명은 js/data.js 에서 그대로 가져옵니다.

묶음 종류 (인스타 기획의 콘텐츠 기둥)
  A. 레퍼런스 소개   SETS 에 사이트 이름을 적어 직접 고릅니다
  B. AI 인사이트     article:<slug> 로 읽을거리에서 자동으로 만듭니다
  D. 용어 사전       SETS 에 term 카드로 적습니다

카드 종류
  cover   표지      title, sub
  site    사이트    name (data.js 의 사이트 이름), when (선택: "이럴 때 좋아요" 한 줄),
                    tour (선택: "card" 면 릴스 투어에서 화면 대신 카드를 보여 줌)
  lead    요약      label, text
  figure  그림      src (articles/img 의 SVG 이름)
  term    용어      name (data.js 의 용어 이름)
  tip     정보      title, points
  outro   마무리    title, url, sub
"""
import html, json, pathlib, re, sys, tempfile

from PIL import Image

import sitedata as D
from snap import shoot

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "social" / "cards"
SITE = "https://designrefs.com/"
SIZE = (1080, 1350)
CNT = D.counts()  # 카테고리별 사이트 수
e = html.escape

SETS = {
    # 한글날(10/9) 특집
    "fonts-hangul": {
        "title": "상업용 무료 한글 폰트, 여기서 받으세요",
        "cards": [
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
        "tags": ["디자인레퍼런스", "디자이너", "한글폰트", "무료폰트", "폰트추천"],
    },

    # A. 레퍼런스 소개: 폰트 고르는 과정 순서대로
    "fonts-pick": {
        "title": "폰트 고를 때 북마크해 둘 사이트 5",
        "cards": [
            {"kind": "cover", "title": "폰트 고를 때\n북마크해 둘\n사이트 5", "sub": "찾고, 맞춰 보고, 크기 정하는 순서대로"},
            # 사이트에 큰 할인 팝업이 떠서 릴스 투어에서는 카드로 보여 줍니다
            {"kind": "site", "name": "WhatTheFont", "when": "레퍼런스 이미지 속 폰트가 궁금할 때", "tour": "card"},
            {"kind": "site", "name": "Fonts In Use", "when": "이 폰트가 실제로 어디에 쓰였는지 보고 싶을 때"},
            {"kind": "site", "name": "Typewolf", "when": "비싼 폰트의 무료 대체재, 어울리는 조합을 찾을 때"},
            {"kind": "site", "name": "Wordmark", "when": "내 컴퓨터 폰트로 문구를 한 번에 비교할 때"},
            {"kind": "site", "name": "Type Scale", "when": "제목·본문 크기 체계를 숫자로 정할 때"},
            {"kind": "outro", "title": "폰트 사이트 23곳,\n한 페이지에 모아 뒀어요", "url": "designrefs.com/font",
             "sub": "저장해 두면 필요할 때 바로 꺼내 볼 수 있어요"},
        ],
        "tags": ["디자인레퍼런스", "디자이너", "폰트추천", "타이포그래피", "그래픽디자인"],
    },

    "colors-pick": {
        "title": "컬러 막힐 때 열어 볼 사이트 5",
        "cards": [
            {"kind": "cover", "title": "컬러 막힐 때\n열어 볼\n사이트 5", "sub": "뽑고, 입혀 보고, 단계 만들고, 검사까지"},
            {"kind": "site", "name": "Coolors", "when": "일단 팔레트를 빠르게 여러 개 뽑아 볼 때"},
            {"kind": "site", "name": "Realtime Colors", "when": "고른 색을 실제 웹 화면에 입혀 보고 싶을 때"},
            {"kind": "site", "name": "UI Colors", "when": "브랜드 색 하나로 50~950 단계를 만들 때"},
            {"kind": "site", "name": "WebAIM Contrast Checker", "when": "글자색과 배경색 대비가 충분한지 확인할 때"},
            {"kind": "site", "name": "Color Leap", "when": "시대 분위기가 나는 색 조합이 필요할 때"},
            {"kind": "outro", "title": f"컬러 사이트 {CNT['color']}곳,\n한 페이지에 모아 뒀어요", "url": "designrefs.com/color",
             "sub": "저장해 두면 필요할 때 바로 꺼내 볼 수 있어요"},
        ],
        "tags": ["디자인레퍼런스", "디자이너", "컬러팔레트", "배색", "UI디자인"],
    },

    "mockups-pick": {
        "title": "포트폴리오 목업, 이 다섯 곳이면 충분해요",
        "cards": [
            {"kind": "cover", "title": "포트폴리오 목업,\n이 다섯 곳이면\n충분해요", "sub": "이미지부터 영상, 앱스토어 이미지까지"},
            {"kind": "site", "name": "Shots", "when": "스크린샷 한 장을 바로 목업으로 만들 때"},
            {"kind": "site", "name": "Mockuuups Studio", "when": "여러 장면에 한 번에 입혀 보고 싶을 때"},
            {"kind": "site", "name": "Rotato", "when": "기기가 돌아가는 목업 영상이 필요할 때"},
            {"kind": "site", "name": "Previewed", "when": "앱스토어용 소개 이미지를 만들 때"},
            {"kind": "site", "name": "Mockups-Design", "when": "포토샵으로 직접 다듬을 무료 PSD가 필요할 때"},
            {"kind": "outro", "title": f"목업 사이트 {CNT['mockup']}곳,\n한 페이지에 모아 뒀어요", "url": "designrefs.com/mockups",
             "sub": "저장해 두면 필요할 때 바로 꺼내 볼 수 있어요"},
        ],
        "tags": ["디자인레퍼런스", "디자이너", "목업", "포트폴리오", "UXUI"],
    },

    "ai-ui-tools": {
        "title": "프롬프트로 화면 시안 뽑는 AI 툴 5",
        "cards": [
            {"kind": "cover", "title": "프롬프트로\n화면 시안 뽑는\nAI 툴 5", "sub": "어디까지 되는지, 언제 쓰면 좋은지"},
            {"kind": "site", "name": "Google Stitch", "when": "말로 설명한 화면을 피그마로 가져가고 싶을 때"},
            {"kind": "site", "name": "Figma Make", "when": "피그마 안에서 눌러 볼 수 있는 시안이 필요할 때"},
            {"kind": "site", "name": "Relume", "when": "사이트맵과 와이어프레임부터 잡을 때"},
            {"kind": "site", "name": "v0", "when": "개발자에게 넘길 컴포넌트 코드까지 보고 싶을 때"},
            {"kind": "site", "name": "Uizard", "when": "손 스케치를 화면 초안으로 바꿀 때"},
            {"kind": "outro", "title": f"AI 디자인 툴 {CNT['ai']}곳,\n쓰임새별로 모아 뒀어요", "url": "designrefs.com/ai",
             "sub": "이미지·영상·UI·코드까지 한 페이지에"},
        ],
        "tags": ["디자인레퍼런스", "디자이너", "AI디자인", "UIUX", "AI툴"],
    },

    # D. 용어 사전: 타이포 기본 넷
    "terms-typo-basic": {
        "title": "디자이너가 매일 쓰는 타이포 용어 4",
        "cards": [
            {"kind": "cover", "title": "디자이너가\n매일 쓰는\n타이포 용어 4", "sub": "헷갈릴 때 꺼내 보는 용어 사전"},
            {"kind": "term", "name": "위계"},
            {"kind": "term", "name": "행간"},
            {"kind": "term", "name": "커닝"},
            {"kind": "term", "name": "그리드"},
            {"kind": "outro", "title": "디자인 용어 155개,\n한 페이지에 모아 뒀어요", "url": "designrefs.com/glossary",
             "sub": "실무에서 헷갈리는 말을 쉽게 풀었어요"},
        ],
        "tags": ["디자인레퍼런스", "디자이너", "타이포그래피", "디자인용어", "디자인공부"],
    },
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
.label { font-size: 30px; font-weight: 700; color: #8A8A8A; }

/* 표지 */
.cover .label { margin-top: auto; }
.cover .title { margin-top: 24px; font-size: 104px; line-height: 1.16; font-weight: 800; letter-spacing: -0.045em;
                white-space: pre-line; word-break: keep-all; }
.cover .sub { margin-top: 36px; font-size: 38px; color: #6B6B6B; letter-spacing: -0.02em; word-break: keep-all; }

/* 사이트 */
.site .num { margin-top: auto; font-size: 30px; font-weight: 700; color: #8A8A8A; }
.site .name { margin-top: 18px; font-size: 104px; line-height: 1.1; font-weight: 800; letter-spacing: -0.045em;
              word-break: keep-all; text-wrap: balance; }
.site .host { margin-top: 22px; font-size: 34px; color: #8A8A8A; }
.site .when { font-size: 30px; font-weight: 700; color: #8A8A8A; margin-bottom: 14px; }
.site .whentext { font-size: 50px; line-height: 1.4; font-weight: 700; letter-spacing: -0.03em; word-break: keep-all; text-wrap: balance; }
.site .desc { margin-top: 28px; font-size: 38px; line-height: 1.55; letter-spacing: -0.02em; color: #444; word-break: keep-all; }
.site .tags { display: flex; gap: 14px; margin: 40px 0 72px; }
.site .tag { font-size: 28px; font-weight: 600; padding: 10px 26px; border: 2px solid #111; border-radius: 999px; }

/* 요약 */
.lead .label { margin-top: 120px; }
.lead .text { margin-top: 36px; font-size: 52px; line-height: 1.5; font-weight: 600; letter-spacing: -0.03em;
              word-break: keep-all; text-wrap: pretty; }

/* 그림: 글자가 읽히도록 여백을 줄이고 그림을 최대한 크게 */
.card.figure { padding: 40px 36px 36px; }
.figure .top { padding: 0 20px; }
.figure .logo { font-size: 40px; }
.figure .fig { flex: 1; min-height: 0; margin-top: 16px; display: flex; align-items: center; justify-content: center; }
.figure .fig img { width: 100%; height: 100%; object-fit: contain; }

/* 용어 */
.term .num { margin-top: auto; font-size: 30px; font-weight: 700; color: #8A8A8A; }
.term .name { margin-top: 18px; font-size: 120px; line-height: 1.1; font-weight: 800; letter-spacing: -0.045em; word-break: keep-all; }
.term .en { margin-top: 22px; font-size: 38px; color: #8A8A8A; }
.term .desc { font-size: 46px; line-height: 1.55; letter-spacing: -0.02em; word-break: keep-all; text-wrap: pretty; margin-bottom: 72px; }

/* 정보 */
.tip .title { margin-top: 120px; font-size: 76px; font-weight: 800; letter-spacing: -0.04em; word-break: keep-all; }
.tip ol { list-style: none; margin: 64px 0 0; padding: 0; counter-reset: n; }
.tip li { counter-increment: n; position: relative; padding: 36px 0 36px 96px; border-top: 2px solid #E2E2E2;
          font-size: 42px; line-height: 1.5; letter-spacing: -0.02em; word-break: keep-all; text-wrap: pretty; }
.tip li b { display: block; font-weight: 800; }
.tip li span { display: block; margin-top: 8px; font-size: 34px; color: #555; }
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


# ---------- 데이터 ----------

def site_tags(name):
    m = re.search(r"\{[^{}]*name: '" + re.escape(name) + r"'[^{}]*\}", D.SRC)
    t = re.search(r"tags: \[([^\]]*)\]", m.group(0)) if m else None
    return re.findall(r"'([^']+)'", t.group(1)) if t else []


def host(url):
    return re.sub(r"^https?://(www\.)?", "", url).split("/")[0]


def find_site(name):
    s = next((x for x in D.sites if x["name"] == name), None)
    if not s:
        raise SystemExit(f"data.js 에 없는 사이트입니다: {name}")
    return s


def find_term(name):
    t = next((x for x in D.terms if x["term"] == name), None)
    if not t:
        raise SystemExit(f"data.js 에 없는 용어입니다: {name}")
    return t


def plain(md):
    """마크다운 한 줄을 글자만 남깁니다."""
    md = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)
    return re.sub(r"[*_`]", "", md).strip()


def first_sentence(text, limit=48):
    """첫 문장. 너무 길면 짧은 문장을 고르고, 그것도 길면 비워 둡니다 (중간에서 자르지 않음)."""
    sents = [x.strip() for x in re.findall(r"[^.?!]+[.?!]", plain(text))] or [plain(text)]
    if len(sents[0]) <= limit:
        return sents[0]
    short = [x for x in sents if len(x) <= limit]
    return min(short, key=len) if short else ""


def article_set(slug):
    """읽을거리 한 편 → AI 인사이트 캐러셀 (B)."""
    path = ROOT / "content" / "articles" / f"{slug}.md"
    if not path.exists():
        raise SystemExit(f"없는 글입니다: {slug}")
    text = path.read_text(encoding="utf-8")
    head, body = text.split("---", 2)[1:]
    meta = dict(re.findall(r"^(\w+):\s*(.*)$", head, re.M))
    cards = [{"kind": "cover", "label": "읽을거리 · AI 디자인", "title": meta["title"], "sub": ""}]
    cards.append({"kind": "lead", "label": "무슨 일이 있었나", "text": meta["desc"]})
    for m in re.finditer(r"!\[([^\]]*)\]\(https://designrefs\.com/articles/img/([\w-]+)\.svg\)", body):
        cards.append({"kind": "figure", "src": m.group(2)})
    now = re.search(r"## 그래서 지금은\n(.*?)(\n\n[^\d]|\Z)", body, re.S)
    if now:
        points = []
        for m in re.finditer(r"^\d+\.\s+(.*)$", now.group(1), re.M):
            b = re.match(r"\*\*(.+?)\*\*\s*(.*)$", m.group(1))
            if b:   # "1. **굵은 제목.** 설명" 꼴
                points.append((b.group(1).rstrip(".").strip(), first_sentence(b.group(2))))
            else:   # 굵은 제목 없이 문장만 있는 순서 목록
                points.append((first_sentence(m.group(1), 40) or plain(m.group(1))[:40], ""))
        if points:
            cards.append({"kind": "tip", "title": "그래서 지금은", "points": points[:3]})
    cards.append({"kind": "outro", "title": "전문은 프로필 링크에서\n읽을 수 있어요", "url": "designrefs.com",
                  "sub": "출처와 표는 본문에 함께 정리해 뒀어요"})
    return {"title": meta["title"], "cards": cards[:10],
            "tags": ["디자인레퍼런스", "디자이너", "AI디자인", "디자인인사이트", "UXUI"],
            "lead": meta["desc"], "url": f"{SITE}articles/{slug}/"}


# ---------- 그리기 ----------

def render(card, i, total, n):
    top = (f'<div class="top"><div class="logo">d<span>.</span></div>'
           f'<div class="page">{i} / {total}</div></div>')
    foot = ('<div class="bottom"><span><b>디자인 허브</b> · 디자이너를 위한 레퍼런스 모음</span>'
            '<span>designrefs.com</span></div>')
    k = card["kind"]
    if k == "cover":
        label = f'<div class="label">{e(card["label"])}</div>' if card.get("label") else '<div style="margin-top:auto"></div>'
        sub = f'<div class="sub">{e(card["sub"])}</div>' if card.get("sub") else ""
        mid = f'{label}<div class="title">{e(card["title"])}</div>{sub}<div class="rule"></div>'
        foot = '<div class="bottom"><span><b>디자인 허브</b></span><span>넘겨서 보기 →</span></div>'
    elif k == "site":
        s = find_site(card["name"])
        tags = "".join(f'<span class="tag">{e(t)}</span>' for t in site_tags(s["name"]))
        if card.get("when"):
            body = (f'<div class="when">이럴 때 좋아요</div><div class="whentext">{e(card["when"])}</div>'
                    f'<div class="desc">{e(s["desc"])}</div>')
        else:
            body = f'<div class="desc" style="margin-top:0;font-size:44px;color:#111">{e(s["desc"])}</div>'
        mid = (f'<div class="num">{n:02d}</div><div class="name">{e(s["name"])}</div>'
               f'<div class="host">{e(host(s["url"]))}</div><div class="rule"></div>'
               f'{body}<div class="tags">{tags}</div>')
    elif k == "lead":
        mid = (f'<div class="label">{e(card["label"])}</div><div class="text">{e(card["text"])}</div>'
               '<div style="margin-top:auto"></div><div class="rule"></div>')
    elif k == "figure":
        src = ROOT / "articles" / "img" / f'{card["src"]}-m.svg'
        if not src.exists():
            src = ROOT / "articles" / "img" / f'{card["src"]}.svg'
        mid = f'<div class="fig"><img src="{src.as_uri()}"></div>'
    elif k == "term":
        t = find_term(card["name"])
        mid = (f'<div class="num">용어 {n:02d}</div><div class="name">{e(t["term"])}</div>'
               f'<div class="en">{e(t.get("en", ""))}</div><div class="rule"></div>'
               f'<div class="desc">{e(t["desc"])}</div>')
    elif k == "tip":
        items = ""
        for p in card["points"]:
            items += ((f"<li><b>{e(p[0])}</b><span>{e(p[1])}</span></li>" if p[1] else f"<li><b>{e(p[0])}</b></li>") if isinstance(p, (list, tuple))
                      else f"<li>{e(p)}</li>")
        mid = f'<div class="title">{e(card["title"])}</div><ol>{items}</ol><div style="margin-top:auto"></div><div class="rule"></div>'
    elif k == "outro":
        mid = (f'<div class="title">{e(card["title"])}</div><div class="url">{e(card["url"])}</div>'
               f'<div class="sub">{e(card["sub"])}</div><div class="rule"></div>')
    else:
        raise SystemExit(f"모르는 카드 종류: {k}")
    if k == "figure":
        foot = ""
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/'
            'dist/web/variable/pretendardvariable-dynamic-subset.min.css">'
            f'<style>{CSS}</style></head><body><div class="card {k}">{top}{mid}{foot}</div></body></html>')


def caption(set_id, spec):
    """인스타 캡션 초안. 첫 줄은 저장할 이유, 본문은 장마다 한 줄, 끝은 저장 유도."""
    tags = " ".join("#" + t for t in spec.get("tags", []))
    cards = spec["cards"]
    if set_id.startswith("article-"):
        lines = [spec["title"], "", spec["lead"], ""]
        tip = next((c for c in cards if c["kind"] == "tip"), None)
        if tip:
            lines.append("그래서 지금은")
            lines += [f"{i}. {p[0]}" for i, p in enumerate(tip["points"], 1)]
            lines.append("")
        lines += ["📌 저장해 두고 필요할 때 꺼내 보세요", "전문과 출처는 프로필 링크(designrefs.com)에 있어요.", "", tags]
        return "\n".join(lines)
    lines = [spec["title"], ""]
    n = 0
    for c in cards:
        if c["kind"] == "site":
            n += 1
            s = find_site(c["name"])
            lines.append(f"{n}. {s['name']} — {c.get('when') or s['desc']}")
        elif c["kind"] == "term":
            n += 1
            t = find_term(c["name"])
            lines.append(f"{n}. {t['term']} — {first_sentence(t['desc'], 80)}")
    lines += ["", "📌 저장해 두고 필요할 때 꺼내 보세요", "전체 목록은 프로필 링크(designrefs.com)에 있어요.", "", tags]
    return "\n".join(lines)


def build(set_id, spec):
    cards = spec["cards"]
    out = OUT / set_id
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.jpg"):
        old.unlink()
    n = 0
    with tempfile.TemporaryDirectory() as tmp:
        for i, card in enumerate(cards, 1):
            if card["kind"] in ("site", "term"):
                n += 1
            page = pathlib.Path(tmp) / f"{i:02d}.html"
            png = pathlib.Path(tmp) / f"{i:02d}.png"
            page.write_text(render(card, i, len(cards), n), encoding="utf-8")
            shoot(page, png, size=SIZE)
            Image.open(png).convert("RGB").save(out / f"{i:02d}.jpg", "JPEG", quality=90, optimize=True)
    cap = caption(set_id, spec)
    (out / "caption.txt").write_text(cap + "\n", encoding="utf-8")
    print(f"{set_id}: {len(cards)}장 → {out.relative_to(ROOT)}")
    return {"id": set_id, "title": spec["title"], "count": len(cards),
            "images": [f"{SITE}social/cards/{set_id}/{i:02d}.jpg" for i in range(1, len(cards) + 1)],
            "caption": cap, **({"article": spec["url"]} if "url" in spec else {})}


def write_index(built):
    """social/cards/index.json 에 묶음 목록을 모읍니다. 이미 있는 묶음은 그대로 두고 갱신만 합니다."""
    path = OUT / "index.json"
    sets = {s["id"]: s for s in (json.loads(path.read_text(encoding="utf-8"))["sets"] if path.exists() else [])}
    sets.update({s["id"]: s for s in built})
    sets = {k: v for k, v in sets.items() if (OUT / k).exists()}
    path.write_text(json.dumps({"sets": sorted(sets.values(), key=lambda s: s["id"])}, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


def latest_article():
    import articles as A
    return sorted(A.load(), key=lambda a: a["date"], reverse=True)[0]["slug"]


if __name__ == "__main__":
    targets = sys.argv[1:] or [*SETS, f"article:{latest_article()}"]
    built = []
    for t in targets:
        if t.startswith("article:"):
            slug = t.split(":", 1)[1]
            built.append(build(f"article-{slug}", article_set(slug)))
        elif t in SETS:
            built.append(build(t, SETS[t]))
        else:
            raise SystemExit(f"없는 묶음입니다: {t} (있는 것: {', '.join(SETS)}, article:<slug>)")
    write_index(built)
