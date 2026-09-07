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
# 해시(#) 주소는 검색엔진이 별도 페이지로 보지 않으므로 대표 주소만 넣습니다.
sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{SITE}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
"""
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
e = html.escape
parts = ['  <noscript>', '    <div class="wrap noscript-seo">',
         '      <h2>디자인 레퍼런스 사이트 모음</h2>',
         f'      <p>자바스크립트가 꺼져 있어 목록만 표시합니다. 전체 {len(sites)}개 사이트와 검색·필터 기능은 자바스크립트를 켜면 사용할 수 있습니다.</p>']
for c in cats:
    items = [s for s in sites if s.get("cat") == c["id"]]
    if not items:
        continue
    parts.append(f'      <h3>{e(c["label"])} ({len(items)})</h3>')
    parts.append(f'      <p>{e(c.get("desc", ""))}</p>')
    parts.append("      <ul>")
    for s in items:
        parts.append(f'        <li><a href="{e(s["url"])}" rel="noopener nofollow">{e(s["name"])}</a> — {e(s.get("desc", ""))}</li>')
    parts.append("      </ul>")
parts.append(f'      <h3>디자인 스타일 사전 ({len(styles)})</h3>')
parts.append("      <ul>")
for s in styles:
    parts.append(f'        <li>{e(s["name"])} ({e(s.get("en", ""))}, {e(s.get("era", ""))})</li>')
parts.append("      </ul>")
parts.append(f'      <h3>디자인 용어 사전 ({len(terms)})</h3>')
parts.append("      <ul>")
for t in terms:
    parts.append(f'        <li>{e(t["term"])} — {e(t.get("en", ""))}</li>')
parts.append("      </ul>")
parts += ["    </div>", "  </noscript>"]
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
