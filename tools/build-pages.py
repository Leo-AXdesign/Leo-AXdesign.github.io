#!/usr/bin/env python3
"""
data.js 를 읽어 카테고리별 정적 페이지를 만듭니다.

  python3 tools/build-pages.py

- 해시(#ai) 주소는 검색엔진이 별도 페이지로 보지 않아 색인되는 주소가 하나뿐입니다.
  그래서 카테고리마다 진짜 주소(/ai/, /font/ ...)를 따로 만들어 검색 노출을 늘립니다.
- 메인 화면은 그대로 두고, 이 페이지들이 추가로 생깁니다.
- 사이트를 추가한 뒤 실행하면 페이지가 다시 만들어집니다.
"""
import json, re, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://leo-axdesign.github.io/"
e = html.escape

# 카테고리 id -> (주소 슬러그, 페이지 제목, 소개 문장)
PAGE_META = {
    "uiux":      ("ui-ux",     "UI/UX 레퍼런스 사이트 {n}곳",   "실제 앱·웹 화면과 유저 플로우, 랜딩페이지를 볼 수 있는 UI/UX 레퍼런스 사이트를 모았습니다."),
    "graphic":   ("graphic",   "그래픽·브랜딩 레퍼런스 {n}곳",  "포스터, 로고, 패키지, 편집 디자인 레퍼런스를 찾을 수 있는 사이트입니다."),
    "color":     ("color",     "컬러 팔레트 사이트 {n}곳",      "팔레트 생성기, 그라디언트 도구, 명도 대비 검사기를 모았습니다."),
    "typo":      ("font",      "무료 폰트·타이포그래피 사이트 {n}곳", "상업용 무료 한글 폰트부터 영문 파운드리, 폰트 조합 도구까지 정리했습니다."),
    "asset":     ("assets",    "아이콘·일러스트·목업 사이트 {n}곳", "아이콘, 일러스트, 사진, 영상, 목업 등 디자인 에셋을 받을 수 있는 곳입니다."),
    "dev":       ("dev",       "디자인 시스템·개발 참고 사이트 {n}곳", "디자인 시스템과 플랫폼 가이드라인, 인터랙션 구현에 필요한 자료를 모았습니다."),
    "tool":      ("tools",     "디자인 툴 {n}가지",             "제작, 협업, 프로토타이핑, 이미지 최적화까지 실무에 쓰는 도구입니다."),
    "freelance": ("freelance", "디자인 외주·프리랜서 플랫폼 {n}곳", "국내외 외주 매칭 플랫폼과 표준 계약·대가 기준 자료입니다."),
    "job":       ("jobs",      "디자이너 채용 사이트 {n}곳",    "국내외 디자이너 채용 공고와 기업 정보를 볼 수 있는 곳입니다."),
    "ai":        ("ai",        "AI 디자인 툴 {n}가지",          "LLM, 이미지·영상 생성, 업스케일, UI·코드 생성까지 종류별로 정리했습니다."),
    "community": ("community", "디자인 매거진·커뮤니티 {n}곳",  "아티클, 뉴스레터, 강의, 디자이너 커뮤니티를 모았습니다."),
    "creator":   ("creators",  "디자인 유튜버·크리에이터 {n}명", "디자인 유튜브 채널과 인스타그램 큐레이션 계정, 팟캐스트입니다."),
}

src = (ROOT / "js" / "data.js").read_text(encoding="utf-8")

def block(name):
    i = src.index(f"const {name} = [")
    return src[i:src.index("\n];", i)]

def fields(chunk, keys):
    out = []
    for m in re.finditer(r"\{[^{}]*\}", chunk):
        row, item = m.group(0), {}
        for k in keys:
            v = (re.search(rf"\b{k}: '((?:[^'\\]|\\.)*)'", row)
                 or re.search(rf'\b{k}: "((?:[^"\\]|\\.)*)"', row))
            if v:
                item[k] = v.group(1).replace("\\'", "'").replace('\\"', '"')
        if item.get(keys[0]):
            out.append(item)
    return out

cats   = fields(block("CATEGORIES"), ["id", "label", "desc"])
sites  = fields(block("SITES"), ["name", "url", "desc", "cat", "sub"])
styles = fields(block("STYLES"), ["name", "en", "era", "desc", "traits", "people"])
trends = fields(block("TRENDS"), ["name", "area", "desc"])
terms  = fields(block("GLOSSARY"), ["term", "en", "group", "desc"])
groups = fields(block("GLOSSARY_GROUPS"), ["id", "label"])

def host(u):
    return re.sub(r"^https?://(www\.)?", "", u).split("/")[0]

# 만들 페이지 목록: (슬러그, 제목, 설명, 본문 HTML 생성 함수, 항목 수)
pages = []

def site_list(items, show_sub=False):
    out = ['      <ul class="plist">']
    for s in items:
        sub = f'<span class="plist__sub">{e(s["sub"])}</span>' if show_sub and s.get("sub") else ""
        out.append(
            '        <li class="plist__item">'
            f'<a class="plist__name" href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["name"])}</a>'
            f'<span class="plist__host">{e(host(s["url"]))}</span>{sub}'
            f'<p class="plist__desc">{e(s.get("desc",""))}</p></li>'
        )
    out.append("      </ul>")
    return "\n".join(out)

for c in cats:
    if c["id"] not in PAGE_META:
        continue
    slug, title_t, intro = PAGE_META[c["id"]]
    items = [s for s in sites if s.get("cat") == c["id"]]
    if not items:
        continue
    title = title_t.format(n=len(items))
    # 소분류 순서는 data.js 의 AI_SUBS 를 따릅니다 (메인 화면과 동일)
    order = re.findall(r"'([^']+)'", re.search(r"const AI_SUBS = \[(.*?)\]", src, re.S).group(1)) \
        if "const AI_SUBS" in src else []
    present = {s.get("sub", "") for s in items} - {""}
    subs = [x for x in order if x in present] + [x for x in dict.fromkeys(s.get("sub", "") for s in items) if x and x not in order]
    if subs:
        body = []
        for sb in subs:
            part = [s for s in items if s.get("sub") == sb]
            body.append(f'      <h2 class="psub">{e(sb)} <span>{len(part)}</span></h2>')
            body.append(site_list(part))
        body_html = "\n".join(body)
    else:
        body_html = site_list(items)
    pages.append((slug, title, intro, body_html, len(items), [s["name"] for s in items]))

# 스타일 사전
sb = ['      <ul class="plist">']
for s in styles:
    sb.append('        <li class="plist__item">'
              f'<span class="plist__name">{e(s["name"])}</span>'
              f'<span class="plist__host">{e(s.get("en",""))} · {e(s.get("era",""))}</span>'
              f'<p class="plist__desc">{e(s.get("desc",""))}</p>'
              f'<p class="plist__meta">{e(s.get("traits",""))}'
              + (f' · {e(s["people"])}' if s.get("people") else "") + "</p></li>")
sb.append("      </ul>")
pages.append(("styles", f"디자인 스타일 사전 {len(styles)}가지",
              "아르누보부터 바우하우스, 스위스 스타일, Y2K, 글래스모피즘까지 유명 그래픽 디자인 양식을 연대순으로 정리했습니다.",
              "\n".join(sb), len(styles), [s["name"] for s in styles]))

# 트렌드
tb = ['      <ul class="plist">']
for i, t in enumerate(trends, 1):
    tb.append('        <li class="plist__item">'
              f'<span class="plist__name">{i:02d}. {e(t["name"])}</span>'
              f'<span class="plist__host">{e(t.get("area",""))}</span>'
              f'<p class="plist__desc">{e(t.get("desc",""))}</p></li>')
tb.append("      </ul>")
pages.append(("trends", f"2026 디자인 트렌드 {len(trends)}가지",
              "리퀴드 글래스, 팬톤 올해의 컬러, 벤토 그리드 등 2026년 디자인 트렌드 키워드를 정리했습니다.",
              "\n".join(tb), len(trends), [t["name"] for t in trends]))

# 용어 사전
gb = []
for g in groups:
    part = [t for t in terms if t.get("group") == g["id"]]
    if not part:
        continue
    gb.append(f'      <h2 class="psub">{e(g["label"])} <span>{len(part)}</span></h2>')
    gb.append('      <ul class="plist">')
    for t in part:
        gb.append('        <li class="plist__item">'
                  f'<span class="plist__name">{e(t["term"])}</span>'
                  f'<span class="plist__host">{e(t.get("en",""))}</span>'
                  f'<p class="plist__desc">{e(t.get("desc",""))}</p></li>')
    gb.append("      </ul>")
pages.append(("glossary", f"디자인 용어 사전 {len(terms)}개",
              "타이포그래피, 편집·인쇄, 컬러, UI 설계, UX 리서치, 개발 협업까지 실무에서 자주 쓰는 디자인 용어를 정리했습니다.",
              "\n".join(gb), len(terms), [t["term"] for t in terms]))

# ---------- 페이지 파일 쓰기 ----------
nav_all = "".join(
    f'<a href="{SITE}{s}/">{e(t)}</a>' for s, t, *_ in pages
)

for slug, title, intro, body, n, names in pages:
    url = f"{SITE}{slug}/"
    others = "".join(f'<a href="{SITE}{s}/">{e(t)}</a>' for s, t, *_ in pages if s != slug)
    jsonld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "url": url,
        "name": title,
        "description": intro,
        "inLanguage": "ko",
        "isPartOf": {"@type": "WebSite", "url": SITE, "name": "디자인 허브"},
        "breadcrumb": {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "디자인 허브", "item": SITE},
                {"@type": "ListItem", "position": 2, "name": title, "item": url},
            ],
        },
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": n,
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": nm}
                for i, nm in enumerate(names[:100])
            ],
        },
    }
    doc = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{e(title)} | 디자인 허브</title>
  <meta name="description" content="{e(intro)}" />
  <link rel="canonical" href="{url}" />
  <meta name="robots" content="index, follow, max-image-preview:large" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="{e(title)} | 디자인 허브" />
  <meta property="og:description" content="{e(intro)}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{SITE}og-image.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="icon" href="../favicon.ico" sizes="32x32" />
  <link rel="icon" type="image/svg+xml" href="../favicon.svg" />
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css" />
  <link rel="stylesheet" href="../css/style.css" />

  <!-- Google Analytics (GA4) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-Q7QVVHSLQ6"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-Q7QVVHSLQ6');
  </script>
  <script>
    // 메인에서 고른 테마를 그대로 따릅니다.
    try {{
      var t = localStorage.getItem('designhub:theme')
        || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
      if (t === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
    }} catch (e) {{}}
  </script>
  <script type="application/ld+json">
{json.dumps(jsonld, ensure_ascii=False, indent=2)}
  </script>
</head>
<body class="page">
  <header class="top">
    <div class="wrap top__inner">
      <a class="logo" href="{SITE}">d<span>.</span></a>
      <span class="page__crumb"><a href="{SITE}">디자인 허브</a> / {e(title)}</span>
    </div>
  </header>

  <main class="wrap page__main">
    <h1 class="page__title">{e(title)}</h1>
    <p class="page__intro">{e(intro)}</p>
    <p class="page__cta"><a href="{SITE}">검색·필터가 되는 전체 목록 보기 →</a></p>

{body}

    <nav class="page__nav">
      <h2 class="psub">다른 목록</h2>
      <div class="page__navlinks">{others}</div>
    </nav>
  </main>

  <footer class="footer">
    <div class="wrap footer__inner">
      <span>Copyright 2026. Design Hub. all rights reserved.</span>
      <a href="mailto:nisov0924@gmail.com">CONTACT : nisov0924@gmail.com</a>
      <a href="{SITE}">홈으로</a>
    </div>
  </footer>
</body>
</html>
"""
    d = ROOT / slug
    d.mkdir(exist_ok=True)
    (d / "index.html").write_text(doc, encoding="utf-8")

# ---------- 메인 index.html 의 푸터 링크 갱신 ----------
p = ROOT / "index.html"
doc = p.read_text(encoding="utf-8")
links = "".join(f'<a href="{SITE}{s}/">{e(t.split(" ")[0])}</a>' for s, t, *_ in pages)
pat = re.compile(r"<!-- SEO:PAGELINKS -->.*?<!-- /SEO:PAGELINKS -->", re.S)
if pat.search(doc):
    doc = pat.sub(f'<!-- SEO:PAGELINKS -->\n      <nav class="footer__nav">{links}</nav>\n      <!-- /SEO:PAGELINKS -->', doc)
    p.write_text(doc, encoding="utf-8")

print(f"페이지 {len(pages)}개 생성: " + ", ".join(f"/{s}/" for s, *_ in pages))
