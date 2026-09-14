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


# ---------- 산문 페이지 (소개 · 개인정보처리방침) ----------
# 데이터가 아니라 글로 된 페이지입니다. 내용은 이 파일에서 고칩니다.
n_site, n_cat = len(sites), len(cats)
n_style, n_term, n_trend = len(styles), len(terms), len(trends)

ABOUT = f"""
    <h2 class="psub">무엇을 하는 곳인가요</h2>
    <p class="ptext">디자인 허브는 디자이너가 자주 찾는 사이트를 한곳에 모아 둔 주소록입니다.
    지금 {n_site}개 사이트를 {n_cat}개 분야로 나눠 정리했고, 각 사이트가 어떤 곳인지 한 줄로 설명해 두었습니다.
    검색창에서 이름·설명·주소·태그를 한 번에 찾을 수 있고, 자주 쓰는 곳은 즐겨찾기로 모아 둘 수 있습니다.</p>

    <h2 class="psub">직접 쓴 자료도 있습니다</h2>
    <p class="ptext">링크만 모으지 않았습니다. 실무에서 자주 부딪히는 내용을 따로 정리했습니다.</p>
    <ul class="ptext-list">
      <li><a href="{SITE}styles/">디자인 스타일 사전</a> — 아르누보부터 글래스모피즘까지 {n_style}가지 양식을 연대순으로. 시대, 특징, 대표 인물, 대표 이미지를 함께 실었습니다.</li>
      <li><a href="{SITE}glossary/">디자인 용어 사전</a> — 타이포그래피, 편집·인쇄, 컬러, UI 설계, UX 리서치, 개발 협업까지 {n_term}개 용어를 실무 기준으로 설명했습니다.</li>
      <li><a href="{SITE}trends/">2026 디자인 트렌드</a> — 업계 리포트와 커뮤니티에서 반복 언급되는 키워드 {n_trend}가지를 정리했습니다.</li>
    </ul>

    <h2 class="psub">어떤 기준으로 고르나요</h2>
    <ul class="ptext-list">
      <li>실무에서 실제로 쓰이는 곳만 넣습니다. 이름값보다 쓸모를 봅니다.</li>
      <li>분야마다 국내 사이트를 함께 담습니다. 한국에서 일하는 디자이너에게 맞춰야 하기 때문입니다.</li>
      <li>설명은 직접 씁니다. 사이트 소개 문구를 그대로 옮기지 않고, 무엇에 강한 곳인지 한 줄로 적습니다.</li>
      <li>무료·유료 여부를 태그로 표시해 들어가기 전에 알 수 있게 합니다.</li>
      <li>주소는 등록 전에 응답을 확인하고, 서비스가 바뀌거나 종료되면 갱신하거나 지웁니다.</li>
    </ul>

    <h2 class="psub">제안과 문의</h2>
    <p class="ptext">빠진 사이트나 잘못된 정보를 알려주시면 확인 후 반영하겠습니다.
    설명이 사실과 다르거나 서비스가 종료된 경우도 알려주세요.
    <a href="mailto:nisov0924@gmail.com">nisov0924@gmail.com</a> 으로 보내주시면 됩니다.</p>
"""

PRIVACY = f"""
    <p class="ptext">디자인 허브는 회원가입이나 로그인이 없고, 이름·연락처 같은 개인정보를 직접 수집하거나 저장하지 않습니다.
    다만 방문 분석과 일부 기능을 위해 아래와 같은 정보가 쓰입니다.</p>

    <h2 class="psub">1. 브라우저에만 저장되는 정보</h2>
    <p class="ptext">아래 세 가지는 보시는 기기의 브라우저 저장소에만 남고, 서버로 전송되지 않습니다.
    브라우저의 사이트 데이터 삭제 기능으로 언제든 지울 수 있습니다.</p>
    <ul class="ptext-list">
      <li>즐겨찾기로 표시한 사이트 목록</li>
      <li>라이트·다크 테마 선택</li>
      <li>목록·격자 보기 선택</li>
    </ul>

    <h2 class="psub">2. 방문 분석</h2>
    <p class="ptext">방문자 수와 어떤 페이지가 많이 읽히는지 파악하기 위해 Google Analytics를 사용합니다.
    이 과정에서 쿠키가 사용되며, 접속 기기·브라우저 종류, 대략적인 지역, 방문한 페이지, 머문 시간 같은 정보가 구글 서버에 수집됩니다.
    이 정보로 개인을 식별하지 않습니다.</p>
    <p class="ptext">수집을 원하지 않으시면
    <a href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="noopener">구글 애널리틱스 차단 확장 프로그램</a>을 설치하거나,
    브라우저 설정에서 쿠키를 차단하시면 됩니다.</p>

    <h2 class="psub">3. 광고</h2>
    <p class="ptext">향후 이 사이트에 구글 애드센스 광고가 게재될 수 있습니다.
    구글을 비롯한 제3자 광고 사업자는 쿠키를 사용해 이용자의 이전 방문 기록을 바탕으로 광고를 게재할 수 있습니다.
    맞춤 광고를 원하지 않으시면 <a href="https://myadcenter.google.com" target="_blank" rel="noopener">구글 광고 설정</a>에서 끌 수 있습니다.</p>

    <h2 class="psub">4. 외부 서비스</h2>
    <p class="ptext">화면을 구성하면서 아래 외부 서비스를 불러옵니다. 이 과정에서 해당 서비스에 접속 기록이 남을 수 있습니다.</p>
    <ul class="ptext-list">
      <li>구글 파비콘 서비스 — 목록에 표시되는 사이트 아이콘</li>
      <li>WordPress mShots, thum.io — 마우스를 올렸을 때 보이는 사이트 미리보기 이미지</li>
      <li>jsDelivr — 본문 글꼴(Pretendard)</li>
      <li>Wikimedia Commons — 스타일 사전의 대표 이미지</li>
    </ul>

    <h2 class="psub">5. 외부 링크</h2>
    <p class="ptext">이 사이트는 다른 사이트로 이동하는 링크를 모아 둔 곳입니다.
    링크를 눌러 이동한 뒤의 개인정보 처리는 해당 사이트의 방침을 따릅니다.
    이동한 사이트에서 일어나는 일에 대해 디자인 허브는 책임지지 않습니다.</p>

    <h2 class="psub">6. 문의</h2>
    <p class="ptext">이 방침에 대한 문의는 <a href="mailto:nisov0924@gmail.com">nisov0924@gmail.com</a> 으로 보내주세요.</p>

    <p class="ptext ptext--note">시행일 2026년 9월 14일</p>
"""

PROSE_PAGES = [
    ("about", "디자인 허브 소개",
     f"디자인 허브가 어떤 곳인지, 사이트를 어떤 기준으로 고르고 관리하는지 정리했습니다.", ABOUT),
    ("privacy", "개인정보처리방침",
     "디자인 허브의 개인정보 처리방침입니다. 수집 항목, 쿠키 사용, 외부 서비스, 광고에 대해 안내합니다.", PRIVACY),
]
for slug, title, intro, body in PROSE_PAGES:
    pages.append((slug, title, intro, body, 0, []))

# ---------- 페이지 파일 쓰기 ----------
nav_all = "".join(
    f'<a href="{SITE}{s}/">{e(t)}</a>' for s, t, *_ in pages
)

for slug, title, intro, body, n, names in pages:
    url = f"{SITE}{slug}/"
    PROSE_SLUGS = {sl for sl, *_ in PROSE_PAGES}
    others = "".join(f'<a href="{SITE}{s2}/">{e(t2)}</a>'
                     for s2, t2, *_ in pages if s2 != slug and s2 not in PROSE_SLUGS)
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
    }
    if n:
        jsonld["mainEntity"] = {
            "@type": "ItemList",
            "numberOfItems": n,
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": nm}
                for i, nm in enumerate(names[:100])
            ],
        }
    cta = ('<p class="page__cta"><a href="' + SITE + '">검색·필터가 되는 전체 목록 보기 →</a></p>'
           if n else '')
    nav_block = ('<nav class="page__nav">\n      <h2 class="psub">다른 목록</h2>\n'
                 f'      <div class="page__navlinks">{others}</div>\n    </nav>') if others else ''
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
  <!-- 구글 애드센스: 승인 신청 시 아래 주석을 풀고 ca-pub- 번호를 채우세요. -->
  <!-- <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX" crossorigin="anonymous"></script> -->

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
    {cta}

{body}

    {nav_block}
  </main>

  <footer class="footer">
    <div class="wrap footer__inner">
      <span>Copyright 2026. Design Hub. all rights reserved.</span>
      <a href="{SITE}about/">소개</a>
      <a href="{SITE}privacy/">개인정보처리방침</a>
      <a href="mailto:nisov0924@gmail.com">CONTACT : nisov0924@gmail.com</a>
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
_prose = {sl for sl, *_ in PROSE_PAGES}
links = "".join(f'<a href="{SITE}{s}/">{e(t.split(" ")[0])}</a>'
                for s, t, *_ in pages if s not in _prose)
pat = re.compile(r"<!-- SEO:PAGELINKS -->.*?<!-- /SEO:PAGELINKS -->", re.S)
if pat.search(doc):
    doc = pat.sub(f'<!-- SEO:PAGELINKS -->\n      <nav class="footer__nav">{links}</nav>\n      <!-- /SEO:PAGELINKS -->', doc)
    p.write_text(doc, encoding="utf-8")

print(f"페이지 {len(pages)}개 생성: " + ", ".join(f"/{s}/" for s, *_ in pages))
