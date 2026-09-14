#!/usr/bin/env python3
"""
data.js 를 읽어 검색엔진용 파일을 다시 만듭니다.

  python3 tools/build-seo.py

- sitemap.xml           : 검색엔진에 알릴 주소 목록
- index.html 의 두 블록 : 구조화 데이터(JSON-LD)와 자바스크립트 미실행 시 보이는 목록
  (<!-- SEO:JSONLD --> ~ <!-- /SEO:JSONLD -->,
   <!-- SEO:NOSCRIPT --> ~ <!-- /SEO:NOSCRIPT --> 사이만 교체합니다)

사이트를 추가한 뒤 실행하면 됩니다.
"""
import json, re, html, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://leo-axdesign.github.io/"

src = (ROOT / "js" / "data.js").read_text(encoding="utf-8")

def block(name):
    i = src.index(f"const {name} = [")
    return src[i:src.index("\n];", i)]

def fields(chunk, keys):
    out = []
    for m in re.finditer(r"\{[^{}]*\}", chunk):
        row = m.group(0)
        item = {}
        for k in keys:
            # 값이 작은따옴표 또는 큰따옴표로 감싸인 두 경우를 모두 처리
            v = (re.search(rf"\b{k}: '((?:[^'\\]|\\.)*)'", row)
                 or re.search(rf'\b{k}: "((?:[^"\\]|\\.)*)"', row))
            if v:
                item[k] = v.group(1).replace("\\'", "'").replace('\\"', '"')
        if item.get(keys[0]):
            out.append(item)
    return out

cats = fields(block("CATEGORIES"), ["id", "label", "desc"])
sites = fields(block("SITES"), ["name", "url", "desc", "cat"])
styles = fields(block("STYLES"), ["name", "en", "era"])
terms = fields(block("GLOSSARY"), ["term", "en"])
today = datetime.date.today().isoformat()

# ---------- sitemap.xml ----------
# 해시(#) 주소는 검색엔진이 별도 페이지로 보지 않으므로, 실제 파일이 있는 주소만 넣습니다.
PAGE_SLUGS = ["ui-ux", "graphic", "color", "font", "assets", "dev", "tools",
              "freelance", "jobs", "ai", "community", "creators",
              "styles", "trends", "glossary", "about", "privacy"]
urls = [(SITE, "1.0")] + [(SITE + s + "/", "0.8") for s in PAGE_SLUGS]
body = "\n".join(
    f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{today}</lastmod>\n"
    f"    <changefreq>weekly</changefreq>\n    <priority>{pr}</priority>\n  </url>"
    for u, pr in urls
)
sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + body + "\n</urlset>\n")
(ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")

# ---------- JSON-LD ----------
jsonld = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "WebSite",
            "@id": SITE + "#website",
            "url": SITE,
            "name": "디자인 허브",
            "alternateName": "Design Hub",
            "description": f"디자이너를 위한 레퍼런스 사이트 {len(sites)}개를 카테고리별로 모은 주소록. "
                           f"디자인 스타일 사전 {len(styles)}개, 2026 트렌드, 용어 사전 {len(terms)}개 제공.",
            "inLanguage": "ko",
        },
        {
            "@type": "CollectionPage",
            "@id": SITE + "#page",
            "url": SITE,
            "name": "디자인 허브 — 디자인 레퍼런스 주소모음",
            "isPartOf": {"@id": SITE + "#website"},
            "about": [c["label"] for c in cats],
            "mainEntity": {
                "@type": "ItemList",
                "numberOfItems": len(cats),
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": i + 1,
                        "name": c["label"],
                        "description": c.get("desc", ""),
                        "url": SITE + "#" + c["id"],
                    }
                    for i, c in enumerate(cats)
                ],
            },
        },
    ],
}
jsonld_html = ('  <script type="application/ld+json">\n'
               + json.dumps(jsonld, ensure_ascii=False, indent=2)
               + "\n  </script>")

# ---------- noscript ----------
# 전체 목록은 카테고리 페이지가 담당합니다. 여기서는 중복을 피해 안내와 링크만 둡니다.
PAGE_TITLES = [
    ("ui-ux", "UI/UX 레퍼런스"), ("graphic", "그래픽 · 브랜딩"), ("color", "컬러 가이드"),
    ("font", "타이포 · 폰트"), ("assets", "아이콘 · 에셋"), ("dev", "디자인 개발"),
    ("tools", "디자인 툴"), ("freelance", "외주 · 프리랜서"), ("jobs", "채용공고"),
    ("ai", "AI 툴"), ("community", "커뮤니티 · 매거진"), ("creators", "크리에이터 · 채널"),
    ("styles", "디자인 스타일 사전"), ("trends", "2026 디자인 트렌드"), ("glossary", "디자인 용어 사전"),
    ("about", "사이트 소개"), ("privacy", "개인정보처리방침"),
]
e = html.escape
parts = ["  <noscript>", '    <div class="wrap noscript-seo">',
         "      <h2>디자인 레퍼런스 사이트 모음</h2>",
         f"      <p>디자이너를 위한 사이트 {len(sites)}개를 {len(cats)}개 카테고리로 정리했습니다. "
         f"디자인 스타일 사전 {len(styles)}가지, 2026 트렌드, 용어 사전 {len(terms)}개도 함께 제공합니다. "
         "검색과 필터 기능은 자바스크립트를 켜면 사용할 수 있습니다.</p>",
         "      <h3>목록 바로가기</h3>", "      <ul>"]
for slug, label in PAGE_TITLES:
    parts.append(f'        <li><a href="{SITE}{slug}/">{e(label)}</a></li>')
parts += ["      </ul>", "    </div>", "  </noscript>"]
noscript_html = "\n".join(parts)

# ---------- index.html 교체 ----------
p = ROOT / "index.html"
doc = p.read_text(encoding="utf-8")
def replace(doc, tag, body):
    pat = re.compile(rf"<!-- SEO:{tag} -->.*?<!-- /SEO:{tag} -->", re.S)
    assert pat.search(doc), f"index.html 에 SEO:{tag} 표시가 없습니다"
    return pat.sub(lambda m: f"<!-- SEO:{tag} -->\n{body}\n  <!-- /SEO:{tag} -->", doc, count=1)
doc = replace(doc, "JSONLD", jsonld_html)
doc = replace(doc, "NOSCRIPT", noscript_html)
p.write_text(doc, encoding="utf-8")

print(f"sitemap.xml, JSON-LD, noscript 갱신 완료 "
      f"(사이트 {len(sites)} · 카테고리 {len(cats)} · 스타일 {len(styles)} · 용어 {len(terms)})")
