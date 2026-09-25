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

import articles as A

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://designrefs.com/"
posts = A.load()          # content/articles/*.md

import sitedata as D

src = D.SRC
cats = D.cats
sites = D.sites
styles = D.styles
trends = D.trends
terms = D.terms
gloss_groups = D.gloss_groups

# 카테고리 id -> 정적 페이지 주소
CAT_SLUG = D.CAT_SLUG
today = datetime.date.today().isoformat()

# ---------- sitemap.xml ----------
# 해시(#) 주소는 검색엔진이 별도 페이지로 보지 않으므로, 실제 파일이 있는 주소만 넣습니다.
PAGE_SLUGS = ["ui-ux", "graphic", "color", "font", "assets", "dev", "tools",
              "freelance", "jobs", "ai", "community", "creators",
              "styles", "trends", "glossary", "talk", "about", "privacy"]
urls = [(SITE, "1.0", today)] + [(SITE + s + "/", "0.8", today) for s in PAGE_SLUGS]
urls.append((SITE + "articles/", "0.8", posts[0]["date"] if posts else today))
# 글은 고칠 때마다 날짜가 바뀌므로 각 글의 작성일을 lastmod 로 넣습니다
urls += [(f'{SITE}articles/{x["slug"]}/', "0.7", x["date"]) for x in posts]
body = "\n".join(
    f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{lm}</lastmod>\n"
    f"    <changefreq>weekly</changefreq>\n    <priority>{pr}</priority>\n  </url>"
    for u, pr, lm in urls
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
            "hasPart": {
                "@type": "Blog",
                "@id": SITE + "articles/#blog",
                "url": SITE + "articles/",
                "name": "디자인 허브 읽을거리",
                "description": "디자인·AI 디자인·커뮤니티에 대해 운영자가 직접 쓴 글",
            },
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
# AI 크롤러와 검색엔진은 대부분 자바스크립트를 실행하지 않습니다.
# 메인에서 이 블록이 사실상 유일한 본문이므로, 카테고리마다 설명과 대표 사이트를 적어 둡니다.
# 사이트 전체 목록은 카테고리 페이지와 llms-full.txt 가 맡아 중복을 줄입니다.
e = html.escape
REPRESENTATIVE = 8   # 카테고리마다 이름을 드러낼 사이트 수
parts = ["  <noscript>", '    <div class="wrap noscript-seo">',
         "      <h2>디자인 허브: 디자이너를 위한 레퍼런스 사이트 모음</h2>",
         f"      <p>UI/UX 레퍼런스, 그래픽 디자인, 컬러 팔레트, 무료 폰트, 아이콘과 목업, 디자인 시스템, "
         f"디자인 툴, 외주 플랫폼, 디자이너 채용, AI 디자인 툴까지 {len(sites)}개 사이트를 "
         f"{len(cats)}개 분야로 나눠 한 줄 설명과 함께 정리한 한국어 디렉터리입니다. "
         f"디자인 스타일 사전 {len(styles)}가지, 2026 디자인 트렌드 {len(trends)}가지, "
         f"디자인·편집·UI/UX 용어 사전 {len(terms)}개도 제공합니다.</p>"]
for c in cats:
    items = [x for x in sites if x.get("cat") == c["id"]]
    if not items:
        continue
    slug = CAT_SLUG.get(c["id"], c["id"])
    names = ", ".join(e(x["name"]) for x in items[:REPRESENTATIVE])
    more = f" 외 {len(items) - REPRESENTATIVE}곳" if len(items) > REPRESENTATIVE else ""
    parts.append(f'      <h3><a href="{SITE}{slug}/">{e(c["label"])}</a> ({len(items)})</h3>')
    parts.append(f'      <p>{e(c.get("desc", ""))}. 대표 사이트: {names}{more}.</p>')
parts.append(f'      <h3><a href="{SITE}styles/">디자인 스타일 사전</a> ({len(styles)})</h3>')
parts.append("      <p>" + ", ".join(e(f'{x["name"]}({x.get("en","")})') for x in styles) + ".</p>")
parts.append(f'      <h3><a href="{SITE}trends/">2026 디자인 트렌드</a> ({len(trends)})</h3>')
parts.append("      <p>" + ", ".join(e(x["name"]) for x in trends) + ".</p>")
parts.append(f'      <h3><a href="{SITE}glossary/">디자인 용어 사전</a> ({len(terms)})</h3>')
parts.append("      <p>" + " · ".join(
    f'{e(g["label"])} {sum(1 for t in terms if t.get("group") == g["id"])}개' for g in gloss_groups) + ".</p>")
if posts:
    parts.append(f'      <h3><a href="{SITE}articles/">읽을거리</a> ({len(posts)})</h3>')
    parts.append(f'      <p>디자인과 AI 디자인, 커뮤니티를 다룬 직접 쓴 글 {len(posts)}편입니다.</p>')
    parts.append("      <ul>")
    for x in posts:
        parts.append(f'        <li><a href="{SITE}articles/{x["slug"]}/">{e(x["title"])}</a> — {e(x["desc"])}</li>')
    parts.append("      </ul>")
parts.append(f'      <p><a href="{SITE}talk/">디자인 잡담</a> · <a href="{SITE}about/">사이트 소개</a> · <a href="{SITE}llms.txt">llms.txt</a></p>')
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

# ---------- llms.txt ----------
# 규격: https://llmstxt.org  (H1 → 인용 요약 → 본문 → H2 링크 목록 → Optional)
def md(t):
    return (t or "").replace("\n", " ").strip()

L = ["# 디자인 허브 (Design Hub)", "",
     f"> 디자이너를 위한 한국어 레퍼런스 사이트 디렉터리. {len(sites)}개 사이트를 {len(cats)}개 분야로 나누고 "
     f"각각 한 줄 설명과 무료·유료·국내 여부를 적어 두었습니다. "
     f"디자인 스타일 사전 {len(styles)}가지, 2026 디자인 트렌드 {len(trends)}가지, 디자인 용어 사전 {len(terms)}개를 함께 제공합니다.", "",
     "각 분야 페이지는 자바스크립트 없이 읽을 수 있는 정적 HTML입니다. "
     "전체 내용을 한 번에 읽으려면 llms-full.txt 를 보세요. "
     "사이트 설명은 운영자가 직접 작성했고, 등록 전에 주소가 살아 있는지 확인합니다.", "",
     "## 분야별 사이트 목록", ""]
for c in cats:
    n = sum(1 for x in sites if x.get("cat") == c["id"])
    if n:
        L.append(f'- [{c["label"]}]({SITE}{CAT_SLUG.get(c["id"], c["id"])}/): {md(c.get("desc"))}. {n}곳')
if posts:
    L += ["", "## 읽을거리 (직접 쓴 글)", ""]
    L += [f'- [{x["title"]}]({SITE}articles/{x["slug"]}/): {md(x["desc"])} ({x["date"]}, 약 {x["min"]}분)'
          for x in posts]
L += ["", "## 자료", "",
      f"- [디자인 스타일 사전]({SITE}styles/): 아르누보부터 글래스모피즘까지 {len(styles)}가지 그래픽 디자인 양식. 시대, 특징, 대표 인물",
      f"- [디자인 용어 사전]({SITE}glossary/): 타이포그래피, 편집·인쇄, 컬러, UI 설계, UX 리서치, 개발 협업 용어 {len(terms)}개",
      f"- [2026 디자인 트렌드]({SITE}trends/): 올해 디자인 트렌드 키워드 {len(trends)}가지",
      f"- [읽을거리 목록]({SITE}articles/): 디자인·AI 디자인·커뮤니티에 대해 직접 쓴 글 {len(posts)}편",
      f"- [전체 내용]({SITE}llms-full.txt): 위의 모든 목록과 설명, 글 본문을 마크다운 한 파일로",
      "", "## Optional", "",
      f"- [디자인 잡담]({SITE}talk/): 디자인 이야기를 편하게 나누는 게시판",
      f"- [사이트 소개]({SITE}about/): 운영 목적과 사이트 선정 기준",
      f"- [개인정보처리방침]({SITE}privacy/)",
      f"- [사이트맵]({SITE}sitemap.xml)", ""]
(ROOT / "llms.txt").write_text("\n".join(L), encoding="utf-8")

# ---------- llms-full.txt ----------
F = ["# 디자인 허브 (Design Hub) 전체 내용", "",
     f"> 출처: {SITE} · 사이트 {len(sites)}개, 스타일 {len(styles)}가지, 트렌드 {len(trends)}가지, 용어 {len(terms)}개", ""]
for c in cats:
    items = [x for x in sites if x.get("cat") == c["id"]]
    if not items:
        continue
    F += [f'## {c["label"]}', "", md(c.get("desc")) + ".", ""]
    ai_order = re.findall(r"'([^']+)'", re.search(r"const AI_SUBS = \[(.*?)\]", src, re.S).group(1)) \
        if "const AI_SUBS" in src else []
    present = [x for x in dict.fromkeys(i.get("sub", "") for i in items) if x]
    subs = [x for x in ai_order if x in present] + [x for x in present if x not in ai_order]
    if subs:
        for sb in subs:
            F += [f"### {sb}", ""]
            F += [f'- [{i["name"]}]({i["url"]}): {md(i.get("desc"))}' for i in items if i.get("sub") == sb]
            F.append("")
    else:
        F += [f'- [{i["name"]}]({i["url"]}): {md(i.get("desc"))}' for i in items]
        F.append("")
F += ["## 디자인 스타일 사전", ""]
for x in styles:
    line = f'- **{x["name"]}** ({x.get("en","")}, {x.get("era","")}): {md(x.get("desc"))}'
    if x.get("traits"): line += f' 특징: {md(x["traits"])}.'
    if x.get("people"): line += f' 대표 인물: {md(x["people"])}.'
    F.append(line)
F += ["", "## 2026 디자인 트렌드", ""]
F += [f'- **{x["name"]}** ({x.get("area","")}): {md(x.get("desc"))}' for x in trends]
F += ["", "## 디자인 용어 사전", ""]
for g in gloss_groups:
    part = [t for t in terms if t.get("group") == g["id"]]
    if not part:
        continue
    F += [f'### {g["label"]}', ""]
    F += [f'- **{t["term"]}** ({t.get("en","")}): {md(t.get("desc"))}' for t in part]
    F.append("")
if posts:
    F += ["", "## 읽을거리 (직접 쓴 글)", ""]
    for x in posts:
        F += [f'### {x["title"]}', "",
              f'출처: {SITE}articles/{x["slug"]}/ · {x["date"]} · {x.get("tag","")}', "",
              x["text"], ""]
(ROOT / "llms-full.txt").write_text("\n".join(F), encoding="utf-8")

print(f"sitemap.xml, JSON-LD, noscript, llms.txt, llms-full.txt 갱신 완료 "
      f"(사이트 {len(sites)} · 카테고리 {len(cats)} · 스타일 {len(styles)} · 용어 {len(terms)})")
