#!/usr/bin/env python3
"""
data.js 를 읽어 카테고리별 정적 페이지를 만듭니다.

  python3 tools/build-pages.py

- 해시(#ai) 주소는 검색엔진이 별도 페이지로 보지 않아 색인되는 주소가 하나뿐입니다.
  그래서 카테고리마다 진짜 주소(/ai/, /font/ ...)를 따로 만들어 검색 노출을 늘립니다.
- 메인 화면은 그대로 두고, 이 페이지들이 추가로 생깁니다.
- 사이트를 추가한 뒤 실행하면 페이지가 다시 만들어집니다.
"""
import json, re, pathlib

import sitedata as D
from nav import sidebar
from shell import document, SITE, e

ROOT = pathlib.Path(__file__).resolve().parent.parent

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

src    = D.SRC
cats   = D.cats
sites  = D.sites
styles = D.styles
trends = D.trends
terms  = D.terms
groups = D.gloss_groups

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
    pages.append((slug, title, intro, body_html, len(items), [s["name"] for s in items], c["label"]))

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
              "\n".join(sb), len(styles), [s["name"] for s in styles], "스타일 사전"))

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
              "\n".join(tb), len(trends), [t["name"] for t in trends], "2026 트렌드"))

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
              "\n".join(gb), len(terms), [t["term"] for t in terms], "용어 사전"))


# ---------- 산문 페이지 (소개 · 개인정보처리방침) ----------
# 데이터가 아니라 글로 된 페이지입니다. 내용은 이 파일에서 고칩니다.
n_site, n_cat = len(sites), len(cats)
n_style, n_term, n_trend = len(styles), len(terms), len(trends)

ABOUT = f"""
    <h2 class="psub">왜 만들었나</h2>
    <p class="ptext">북마크 폴더가 감당이 안 됐습니다. 폰트 사이트 하나 찾으려고 들어가 보면 몇 년 전에 저장해 둔 링크는 이미 없어진 도메인이고,
    괜찮은 레퍼런스를 봐도 어디에 넣어뒀는지 기억이 안 나고.</p>
    <p class="ptext">그래서 한 페이지에 다 모았습니다. 검색창에 단어 하나 치면 나오게.
    지금 {n_site}개가 들어 있고, 분야는 {n_cat}개로 나눠 뒀습니다.</p>

    <h2 class="psub">링크만 있는 건 아닙니다</h2>
    <p class="ptext">쓰다 보니 아쉬운 게 생겨서 몇 가지를 더 붙였습니다.</p>
    <ul class="ptext-list">
      <li><a href="{SITE}styles/">스타일 사전</a>은 클라이언트가 "바우하우스 느낌으로 가죠" 할 때 바로 열어볼 용도입니다.
      {n_style}가지 양식을 연대순으로 놓고, 시대와 특징, 대표 인물, 대표 이미지를 같이 넣었습니다.</li>
      <li><a href="{SITE}glossary/">용어 사전</a>은 인쇄소에서 도련이 어떻고 오시가 어떻고 하는 말을 들었을 때를 위한 것입니다.
      타이포그래피부터 UI 설계, 개발 협업 용어까지 {n_term}개.</li>
      <li><a href="{SITE}trends/">2026 트렌드</a>는 매년 리포트 찾아 헤매기가 번거로워서 정리해 둡니다. {n_trend}가지.</li>
    </ul>

    <h2 class="psub">고르는 기준</h2>
    <p class="ptext">처음부터 정해 놓은 건 아니고, 넣었다 뺐다 하면서 자연스럽게 생긴 기준입니다.</p>
    <ul class="ptext-list">
      <li>유명한 곳보다 실제로 자주 여는 곳</li>
      <li>분야마다 국내 사이트를 같이 넣습니다. 해외 것만 모아두면 반쪽짜리가 되더군요</li>
      <li>설명은 직접 씁니다. 사이트 소개 문구를 그대로 옮기면 전부 비슷해 보입니다</li>
      <li>무료인지 유료인지 태그로 먼저 표시. 들어갔다가 결제창 보면 맥이 빠지니까요</li>
      <li>주소는 넣기 전에 한 번씩 열어 보고, 서비스가 없어지면 지웁니다</li>
    </ul>

    <h2 class="psub">제안</h2>
    <p class="ptext">빠진 사이트를 알려주시면 확인하고 넣겠습니다. 링크가 죽었거나 설명이 틀린 것도 알려주세요.
    <a href="mailto:nisov0924@gmail.com">nisov0924@gmail.com</a></p>
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

    <h2 class="psub">4. 이야기 페이지에 남긴 글</h2>
    <p class="ptext"><a href="{SITE}talk/">디자인 이야기</a> 페이지에 글을 남기면 적어 주신 이름과 내용이 그대로 공개되고,
    Cloudflare 가 운영하는 데이터베이스에 저장됩니다. 가입 절차가 없어 이메일이나 비밀번호는 받지 않습니다.</p>
    <p class="ptext">글을 지울 때 쓰는 비밀번호도 그대로 저장하지 않습니다. 글마다 다른 값을 섞어 되돌릴 수 없는 형태로 바꿔 두기 때문에,
    운영자도 어떤 비밀번호를 쓰셨는지 알 수 없습니다.</p>
    <p class="ptext">스팸을 막기 위해 접속 IP 를 그대로 저장하지 않고, 되돌릴 수 없는 형태로 바꾼 값만 남깁니다.
    이 값은 같은 사람이 짧은 시간에 여러 번 글을 올리는지 확인하는 데만 씁니다.</p>
    <p class="ptext">남긴 글을 지우고 싶으시면 <a href="mailto:nisov0924@gmail.com">nisov0924@gmail.com</a> 으로 알려 주세요.
    광고, 욕설, 타인의 개인정보가 담긴 글은 예고 없이 지웁니다.</p>

    <h2 class="psub">5. 외부 서비스</h2>
    <p class="ptext">화면을 구성하면서 아래 외부 서비스를 불러옵니다. 이 과정에서 해당 서비스에 접속 기록이 남을 수 있습니다.</p>
    <ul class="ptext-list">
      <li>구글 파비콘 서비스 — 목록에 표시되는 사이트 아이콘</li>
      <li>WordPress mShots, thum.io — 마우스를 올렸을 때 보이는 사이트 미리보기 이미지</li>
      <li>jsDelivr — 본문 글꼴(Pretendard)</li>
      <li>Wikimedia Commons — 스타일 사전의 대표 이미지</li>
      <li>Cloudflare — 이야기 페이지의 글 저장</li>
    </ul>

    <h2 class="psub">6. 외부 링크</h2>
    <p class="ptext">이 사이트는 다른 사이트로 이동하는 링크를 모아 둔 곳입니다.
    링크를 눌러 이동한 뒤의 개인정보 처리는 해당 사이트의 방침을 따릅니다.
    이동한 사이트에서 일어나는 일에 대해 디자인 허브는 책임지지 않습니다.</p>

    <h2 class="psub">7. 문의</h2>
    <p class="ptext">이 방침에 대한 문의는 <a href="mailto:nisov0924@gmail.com">nisov0924@gmail.com</a> 으로 보내주세요.</p>

    <p class="ptext ptext--note">시행일 2026년 9월 14일 · 개정일 2026년 9월 25일</p>
"""

TALK = f"""
    <h2 class="psub">이런 이야기를 나눕니다</h2>
    <ul class="ptext-list">
      <li>작업하다 막힌 것. 인쇄 사양, 폰트 라이선스, 클라이언트 대응처럼 검색해도 잘 안 나오는 것들</li>
      <li>요즘 쓰는 툴과 방식. 특히 AI 툴은 쓰는 방식이 제각각이라 서로 물어볼 게 많습니다</li>
      <li>알게 된 사이트나 레퍼런스. <a href="{SITE}">목록</a>에 없는 곳은 알려주시면 확인하고 넣겠습니다</li>
      <li><a href="{SITE}articles/">읽을거리</a>에 쓴 글에 대한 의견이나 반론</li>
    </ul>

    <div id="talk"></div>

    <h2 class="psub">남기기 전에</h2>
    <ul class="ptext-list">
      <li>비밀번호는 나중에 본인 글을 지울 때 씁니다. 4~12자로 정하시면 됩니다.</li>
      <li>남긴 글은 이름과 내용이 그대로 공개됩니다. 연락처나 개인정보는 적지 마세요.</li>
      <li>광고, 욕설, 남의 개인정보가 담긴 글은 보이는 대로 지웁니다.</li>
    </ul>

    <script src="{SITE}js/talk.js" defer></script>
"""

PROSE_PAGES = [
    ("talk", "디자인 이야기",
     "디자이너들이 작업하면서 생기는 이야기를 나누는 공간입니다. 막힌 작업, 요즘 쓰는 툴, 찾은 레퍼런스를 서로 묻고 답합니다.", TALK),
    ("about", "디자인 허브 소개",
     "왜 만들었고 무엇이 들어 있는지, 사이트는 어떤 기준으로 고르는지 적어 뒀습니다.", ABOUT),
    ("privacy", "개인정보처리방침",
     "디자인 허브의 개인정보 처리방침입니다. 수집 항목, 쿠키 사용, 외부 서비스, 광고에 대해 안내합니다.", PRIVACY),
]
for slug, title, intro, body in PROSE_PAGES:
    pages.append((slug, title, intro, body, 0, [], title))

# ---------- 페이지 파일 쓰기 ----------
nav_all = "".join(
    f'<a href="{SITE}{s}/">{e(t)}</a>' for s, t, *_ in pages
)

for slug, title, intro, body, n, names, navlabel in pages:
    url = f"{SITE}{slug}/"
    PROSE_SLUGS = {sl for sl, *_ in PROSE_PAGES}
    others = f'<a href="{SITE}articles/">읽을거리</a>' + "".join(
        f'<a href="{SITE}{s2}/">{e(t2)}</a>'
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
    if slug == "glossary":
        # 용어 사전은 schema.org 의 DefinedTermSet 으로 표시해
        # 검색엔진과 AI 가 '용어 → 정의' 짝을 그대로 읽을 수 있게 합니다.
        jsonld["mainEntity"] = {
            "@type": "DefinedTermSet",
            "@id": url + "#terms",
            "name": "디자인 용어 사전",
            "inLanguage": "ko",
            "hasDefinedTerm": [
                {
                    "@type": "DefinedTerm",
                    "name": t["term"],
                    **({"alternateName": t["en"]} if t.get("en") else {}),
                    "description": t.get("desc", ""),
                    "inDefinedTermSet": url + "#terms",
                }
                for t in terms
            ],
        }
    elif n:
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
    body_full = f"""    <h1 class="page__title">{e(title)}</h1>
    <p class="page__intro">{e(intro)}</p>
    {cta}

{body}

    {nav_block}"""
    doc = document(title=title, desc=intro, url=url, body=body_full, jsonld=jsonld,
                   crumb=e(title), sidebar=sidebar(slug))
    d = ROOT / slug
    d.mkdir(exist_ok=True)
    (d / "index.html").write_text(doc, encoding="utf-8")

# ---------- 메인 index.html 의 푸터 링크 갱신 ----------
p = ROOT / "index.html"
doc = p.read_text(encoding="utf-8")
_prose = {sl for sl, *_ in PROSE_PAGES}
INSIGHT = {"styles", "trends", "glossary"}

def _group(slugs):
    return "".join(f'<a href="{SITE}{pg[0]}/">{e(pg[6])}</a>'
                   for pg in pages if pg[0] in slugs)

_cat_slugs = [pg[0] for pg in pages if pg[0] not in _prose and pg[0] not in INSIGHT]
links = ('<div class="footer__navgroup">' + _group(_cat_slugs) + '</div>'
         '<div class="footer__navgroup">'
         + f'<a href="{SITE}articles/">읽을거리</a>' + _group(INSIGHT) + '</div>')
pat = re.compile(r"<!-- SEO:PAGELINKS -->.*?<!-- /SEO:PAGELINKS -->", re.S)
if pat.search(doc):
    doc = pat.sub(f'<!-- SEO:PAGELINKS -->\n      <nav class="footer__nav">{links}</nav>\n      <!-- /SEO:PAGELINKS -->', doc)
    p.write_text(doc, encoding="utf-8")

print(f"페이지 {len(pages)}개 생성: " + ", ".join(f"/{s}/" for s, *_ in pages))
