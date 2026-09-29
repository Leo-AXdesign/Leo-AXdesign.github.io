#!/usr/bin/env python3
"""
영문판 첫 화면 en/index.html 을 만듭니다.

  python3 tools/build-en.py

- 한국어 index.html 을 그대로 가져와 화면에 박힌 한국어 문구만 영어로 바꿉니다.
  그래서 레이아웃은 한국어판과 늘 같습니다. 바꿀 문구를 못 찾으면 멈추고 알려 줍니다.
- 목록 내용(카테고리, 사이트 설명, 스타일, 용어)은 js/data.en.js 에서 앱이 바꿔 그립니다.
- js/data.en.js 에 번역이 빠진 사이트·용어가 있으면 목록을 보여 줍니다.
  (빠진 항목은 영문판에서 한국어로 보입니다)

build-seo.py 로 index.html 을 갱신한 다음에 돌리세요.
"""
import html, json, re, pathlib

import sitedata as D

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://designrefs.com/"
EN_URL = SITE + "en/"
e = html.escape

# ---------- data.en.js 읽기 ----------
sites_en = D.en_block("SITES_EN")
gloss_en = D.en_block("GLOSSARY_EN")
cat_en, cat_desc_en = D.cat_en, D.cat_desc_en

missing = [s["name"] for s in D.sites if s["url"] not in sites_en]
missing_terms = [t["term"] for t in D.terms if t["term"] not in gloss_en]


def site_name(s):
    x = sites_en.get(s["url"])
    return x[0] if x and x[0] else s["name"]


# ---------- 바꿀 문구 ----------
# (한국어판에 있는 그대로, 영어) 순서대로 한 번씩만 바꿉니다.
TEXT = [
    ('<html lang="ko">', '<html lang="en">'),
    ("<title>디자인 허브 — 디자인 레퍼런스 주소모음</title>",
     "<title>Design Hub — Design Reference Directory</title>"),
    ('<meta name="description" content="UI/UX, 그래픽, 컬러, 폰트, 디자인 개발, 외주, 채용, AI까지 디자이너에게 필요한 사이트를 한곳에 모았습니다." />',
     f'<meta name="description" content="{len(D.sites)} design reference sites in one place, each with a one-line description: UI/UX, graphic, color, fonts, mockups, design systems, tools and AI. Curated from Korea." />'),
    ('<meta property="og:title" content="디자인 허브 — 디자인 레퍼런스 주소모음" />',
     '<meta property="og:title" content="Design Hub — Design Reference Directory" />'),
    ('<meta property="og:description" content="디자이너를 위한 레퍼런스 사이트 모음. 스타일 사전, 2026 트렌드, 용어 사전까지." />',
     '<meta property="og:description" content="Reference sites for designers, plus a style guide, 2026 trends and a design glossary." />'),
    ('<meta property="og:url" content="https://designrefs.com/" />', f'<meta property="og:url" content="{EN_URL}" />'),
    ('href="favicon.ico"', 'href="../favicon.ico"'),
    ('href="favicon.svg"', 'href="../favicon.svg"'),
    ('href="css/style.css"', 'href="../css/style.css"'),
    ('<link rel="canonical" href="https://designrefs.com/" />', f'<link rel="canonical" href="{EN_URL}" />'),
    ('<meta name="keywords" content="디자인 레퍼런스, 디자인 사이트 모음, UI UX 레퍼런스, 그래픽 디자인, 컬러 팔레트, 무료 폰트, 디자인 외주, 디자이너 채용, AI 디자인 툴, 디자인 용어, 디자인 스타일, 2026 디자인 트렌드" />',
     '<meta name="keywords" content="design references, design resources, UI UX inspiration, graphic design, color palettes, free fonts, mockups, design systems, AI design tools, design glossary, design styles, 2026 design trends, Korean design" />'),
    # 머리글
    ('<a class="top__lang" href="/en/" hreflang="en" lang="en" title="English">EN</a>',
     '<a class="top__lang" href="/" hreflang="ko" lang="ko" title="한국어">KO</a>'),
    ('placeholder="사이트 검색"', 'placeholder="Search sites"'),
    ('aria-label="테마 전환" title="라이트 / 다크 전환"', 'aria-label="Toggle theme" title="Light / Dark"'),
    ('aria-label="메뉴 열기"', 'aria-label="Open menu"'),
    # 모바일 메뉴
    ('aria-label="전체 메뉴">', 'aria-label="Menu">'),
    ('<span class="drawer__title">전체 메뉴</span>', '<span class="drawer__title">Menu</span>'),
    ('aria-label="메뉴 닫기"', 'aria-label="Close menu"'),
    ('<nav class="nav" id="drawer-nav" aria-label="카테고리">', '<nav class="nav" id="drawer-nav" aria-label="Categories">'),
    ('<p class="nav__group">태그 필터</p>', '<p class="nav__group">Filter</p>'),
    ('<p class="nav__group">보기</p>', '<p class="nav__group">View</p>'),
    ('type="button">테마 전환</button>', 'type="button">Theme</button>'),
    ('data-view="list" type="button">목록</button>', 'data-view="list" type="button">List</button>'),
    ('data-view="grid" type="button">격자</button>', 'data-view="grid" type="button">Grid</button>'),
    ('<nav class="nav" id="nav" aria-label="카테고리">', '<nav class="nav" id="nav" aria-label="Categories">'),
    # 본문
    ('<p class="hero__sub">디자이너를 위한 레퍼런스 사이트 모음.</p>',
     '<p class="hero__sub">Reference sites for designers, curated in Korea.</p>'),
    ('aria-label="태그 필터"', 'aria-label="Filter"'),
    ('aria-label="보기 방식"', 'aria-label="View"'),
    ('aria-label="목록 보기" title="목록"', 'aria-label="List view" title="List"'),
    ('aria-label="격자 보기" title="격자"', 'aria-label="Grid view" title="Grid"'),
    # 맨 위로
    ('<button id="to-top" class="to-top" type="button" aria-label="맨 위로">',
     '<button id="to-top" class="to-top" type="button" aria-label="Back to top">'),
    # 스크립트: 한국어 글 목록 대신 영문 데이터
    ('<script src="js/data.js"></script>\n  <script src="js/articles.js"></script>\n  <script src="js/app.js"></script>',
     '<script src="../js/data.js"></script>\n  <script src="../js/data.en.js"></script>\n  <script src="../js/articles.en.js"></script>\n  <script src="../js/app.js"></script>'),
    ('<link rel="alternate" type="application/rss+xml" title="디자인 허브 읽을거리" href="https://designrefs.com/rss.xml" />',
     '<link rel="alternate" type="application/rss+xml" title="Design Hub Articles" href="https://designrefs.com/en/rss.xml" />'),
]

# 바닥글은 통째로 바꿉니다. 분야 링크는 한국어 정적 페이지 대신 영문판 화면으로.
FOOTER_RE = re.compile(r'<footer class="footer">.*?</footer>', re.S)
footer_links = "".join(f'<a href="#{c["id"]}">{e(cat_en.get(c["id"], c["label"]))}</a>' for c in D.cats)
FOOTER = f"""<footer class="footer">
    <div class="wrap">
      <nav class="footer__nav"><div class="footer__navgroup">{footer_links}</div><div class="footer__navgroup"><a href="{SITE}en/articles/">Articles</a><a href="#styles">Style Guide</a><a href="#trends">2026 Trends</a><a href="#glossary">Glossary</a></div></nav>
    </div>
    <div class="wrap footer__inner">
      <span>Copyright 2026. Design Hub. all rights reserved.</span>
      <a href="{SITE}en/articles/">Articles</a>
      <a href="{SITE}en/talk/">Design Talk</a>
      <a href="/" hreflang="ko" lang="ko">한국어</a>
      <a href="/privacy/">Privacy (Korean)</a>
      <a href="mailto:nisov0924@gmail.com">CONTACT : nisov0924@gmail.com</a>
      <a href="#" id="footer-top">Back to top ↑</a>
    </div>
  </footer>"""

# ---------- 구조화 데이터 ----------
items = [{"@type": "ListItem", "position": i + 1, "name": cat_en.get(c["id"], c["label"]),
          "description": cat_desc_en.get(c["id"], c.get("desc", "")), "url": f'{EN_URL}#{c["id"]}'}
         for i, c in enumerate(D.cats)]
jsonld = {
    "@context": "https://schema.org",
    "@graph": [
        {"@type": "WebSite", "@id": f"{EN_URL}#website", "url": EN_URL, "name": "Design Hub",
         "alternateName": "디자인 허브",
         "description": f"A directory of {len(D.sites)} reference sites for designers in {len(D.cats)} categories, "
                        f"with a style guide of {len(D.styles)} movements, 2026 trends and a glossary of {len(D.terms)} terms.",
         "inLanguage": "en"},
        {"@type": "CollectionPage", "@id": f"{EN_URL}#page", "url": EN_URL,
         "name": "Design Hub — Design Reference Directory", "inLanguage": "en",
         "isPartOf": {"@id": f"{EN_URL}#website"},
         "mainEntity": {"@type": "ItemList", "numberOfItems": len(items), "itemListElement": items}},
    ],
}
jsonld_html = ('  <script type="application/ld+json">\n'
               + json.dumps(jsonld, ensure_ascii=False, indent=2) + "\n  </script>")

# ---------- 자바스크립트 없이 보이는 목록 ----------
parts = ["  <noscript>", '    <div class="wrap noscript-seo">',
         "      <h2>Design Hub: reference sites for designers</h2>",
         f"      <p>A curated directory of {len(D.sites)} design sites in {len(D.cats)} categories, each with a one-line "
         f"description: UI/UX references, graphic design, color palettes, fonts, icons and mockups, design systems, "
         f"design tools, freelance and job boards, and AI design tools. Also a style guide of {len(D.styles)} movements, "
         f"{len(D.trends)} design trends for 2026 and a glossary of {len(D.terms)} design, print and UI/UX terms.</p>"]
for c in D.cats:
    cs = [s for s in D.sites if s.get("cat") == c["id"]]
    if not cs:
        continue
    names = ", ".join(e(site_name(s)) for s in cs[:8])
    more = f" and {len(cs) - 8} more" if len(cs) > 8 else ""
    parts.append(f'      <h3>{e(cat_en.get(c["id"], c["label"]))} ({len(cs)})</h3>')
    parts.append(f'      <p>{e(cat_desc_en.get(c["id"], ""))}. Including {names}{more}.</p>')
parts.append(f'      <p><a href="{SITE}">한국어</a></p>')
parts += ["    </div>", "  </noscript>"]
noscript_html = "\n".join(parts)


def build():
    doc = (ROOT / "index.html").read_text(encoding="utf-8")
    for ko, en in TEXT:
        assert doc.count(ko) == 1, f"index.html 에서 이 문구를 한 번만 찾아야 합니다: {ko[:70]}"
        doc = doc.replace(ko, en)
    assert FOOTER_RE.search(doc), "index.html 에 footer 가 없습니다"
    doc = FOOTER_RE.sub(lambda m: FOOTER, doc, count=1)
    for tag, body in (("JSONLD", jsonld_html), ("NOSCRIPT", noscript_html)):
        pat = re.compile(rf"<!-- SEO:{tag} -->.*?<!-- /SEO:{tag} -->", re.S)
        assert pat.search(doc), f"index.html 에 SEO:{tag} 표시가 없습니다"
        doc = pat.sub(lambda m: f"<!-- SEO:{tag} -->\n{body}\n  <!-- /SEO:{tag} -->", doc, count=1)
    # 한국어 주석은 남아도 되지만, 화면에 보이는 한국어가 남았는지 확인합니다
    visible = re.sub(r"<!--.*?-->|<script.*?</script>|<noscript>.*?</noscript>", "", doc, flags=re.S)
    left = sorted(set(re.findall(r"[가-힣][가-힣 ·/()]*", visible)) - {"한국어", "디자인 허브"})
    out = ROOT / "en" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    print(f"en/index.html 갱신 (사이트 {len(D.sites)} · 번역 빠짐 {len(missing)} · 용어 번역 빠짐 {len(missing_terms)})")
    if missing:
        print("  data.en.js SITES_EN 에 없는 사이트:", ", ".join(missing))
    if missing_terms:
        print("  data.en.js GLOSSARY_EN 에 없는 용어:", ", ".join(missing_terms))
    if left:
        print("  화면에 남은 한국어:", ", ".join(left))


if __name__ == "__main__":
    build()
