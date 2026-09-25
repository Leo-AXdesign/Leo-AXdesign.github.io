#!/usr/bin/env python3
"""
content/articles/*.md 로 블로그 페이지를 만듭니다.

  python3 tools/build-articles.py

만들어지는 것
- /articles/            글 목록
- /articles/<slug>/     글 하나 (BlogPosting 구조화 데이터 포함)
- js/articles.js        메인 화면 '읽을거리' 목록용 데이터

글을 추가하려면 content/articles/ 에 .md 파일을 하나 더 만들고 이 스크립트를 실행하세요.
그다음 tools/build-seo.py 를 돌려야 sitemap 과 llms.txt 에도 반영됩니다.
"""
import json, pathlib, datetime

import articles as A
from nav import menu
from shell import document, SITE, e

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIST_URL = SITE + "articles/"


def kdate(d):
    """2026-09-25 -> 2026년 9월 25일"""
    y, m, day = (int(x) for x in d.split("-"))
    return f"{y}년 {m}월 {day}일"


def crumbs(items):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": u}
            for i, (n, u) in enumerate(items)
        ],
    }


def related_links(slugs):
    out = [f'<a href="{SITE}{s}/">{e(A.RELATED_LABEL[s])}</a>'
           for s in slugs if s in A.RELATED_LABEL]
    if not out:
        return ""
    return ('<nav class="page__nav">\n      <h2 class="psub">이어서 볼 목록</h2>\n'
            f'      <div class="page__navlinks">{"".join(out)}</div>\n    </nav>')


def other_articles(items, slug):
    rest = [x for x in items if x["slug"] != slug]
    if not rest:
        return ""
    rows = "\n".join(
        '        <li class="plist__item">'
        f'<a class="plist__name" href="{SITE}articles/{x["slug"]}/">{e(x["title"])}</a>'
        f'<span class="plist__host">{e(x.get("tag", ""))}</span>'
        f'<p class="plist__desc">{e(x["desc"])}</p></li>'
        for x in rest)
    return ('<nav class="page__nav">\n      <h2 class="psub">다른 글</h2>\n'
            f'      <ul class="plist">\n{rows}\n      </ul>\n    </nav>')


def footer_nav(items):
    """푸터 위에 붙는 글 목록. 모든 글에서 모든 글로 연결되게 둡니다."""
    links = "".join(f'<a href="{SITE}articles/{x["slug"]}/">{e(x["title"])}</a>' for x in items)
    return ('    <div class="wrap">\n'
            f'      <nav class="footer__nav"><div class="footer__navgroup">{links}</div></nav>\n'
            '    </div>\n')


items = A.load()
if not items:
    raise SystemExit("content/articles/ 에 글이 없습니다")
fnav = footer_nav(items)

# ---------- 글 하나씩 ----------
for x in items:
    url = f"{SITE}articles/{x['slug']}/"
    jsonld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BlogPosting",
                "@id": url + "#post",
                "url": url,
                "mainEntityOfPage": url,
                "headline": x["title"],
                "description": x["desc"],
                "articleSection": x.get("tag", ""),
                "datePublished": x["date"],
                "dateModified": x["date"],
                "inLanguage": "ko",
                "wordCount": x["chars"],
                "timeRequired": f"PT{x['min']}M",
                "image": SITE + "og-image.png",
                "author": {"@type": "Organization", "name": "디자인 허브", "url": SITE},
                "publisher": {"@type": "Organization", "name": "디자인 허브", "url": SITE},
                "isPartOf": {"@type": "Blog", "@id": LIST_URL + "#blog", "name": "디자인 허브 읽을거리"},
            },
            crumbs([("디자인 허브", SITE), ("읽을거리", LIST_URL), (x["title"], url)]),
        ],
    }
    body = f"""    <article class="art">
      <p class="art__kicker"><a href="{LIST_URL}">읽을거리</a>{f' · {e(x["tag"])}' if x.get("tag") else ''}</p>
      <h1 class="page__title">{e(x["title"])}</h1>
      <p class="page__intro">{e(x["desc"])}</p>
      <p class="art__meta"><time datetime="{x["date"]}">{kdate(x["date"])}</time> · 읽는 데 약 {x["min"]}분</p>
{x["body"]}
    </article>

    {related_links(x.get("related", []))}

    {other_articles(items, x["slug"])}"""
    doc = document(title=x["title"], desc=x["desc"], url=url, body=body, jsonld=jsonld,
                   og_type="article", menu=menu("articles"),
                   crumb=f'<a href="{LIST_URL}">읽을거리</a> / {e(x["title"])}',
                   main_class="page__main page__main--art", footer_nav=fnav)
    d = ROOT / "articles" / x["slug"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(doc, encoding="utf-8")

# ---------- 목록 페이지 ----------
LIST_TITLE = "읽을거리"
LIST_DESC = ("디자인하면서 생각한 것들을 적습니다. "
             "AI와 같이 일하는 법, 스타일을 말로 옮기는 법, 레퍼런스와 커뮤니티 이야기.")
rows = []
for x in items:
    rows.append(
        '        <li class="plist__item">'
        f'<a class="plist__name" href="{SITE}articles/{x["slug"]}/">{e(x["title"])}</a>'
        f'<span class="plist__host">{e(x.get("tag", ""))}</span>'
        f'<p class="plist__desc">{e(x["desc"])}</p>'
        f'<p class="plist__meta"><time datetime="{x["date"]}">{kdate(x["date"])}</time> · 약 {x["min"]}분</p></li>')
list_body = f"""    <h1 class="page__title">{LIST_TITLE}</h1>
    <p class="page__intro">{e(LIST_DESC)}</p>
    <p class="page__cta"><a href="{SITE}">디자인 레퍼런스 사이트 목록 보기 →</a></p>

      <ul class="plist">
{chr(10).join(rows)}
      </ul>"""
list_jsonld = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "Blog",
            "@id": LIST_URL + "#blog",
            "url": LIST_URL,
            "name": "디자인 허브 읽을거리",
            "description": LIST_DESC,
            "inLanguage": "ko",
            "isPartOf": {"@type": "WebSite", "url": SITE, "name": "디자인 허브"},
            "blogPost": [
                {
                    "@type": "BlogPosting",
                    "@id": f"{SITE}articles/{x['slug']}/#post",
                    "url": f"{SITE}articles/{x['slug']}/",
                    "headline": x["title"],
                    "description": x["desc"],
                    "datePublished": x["date"],
                    "author": {"@type": "Organization", "name": "디자인 허브"},
                }
                for x in items
            ],
        },
        crumbs([("디자인 허브", SITE), ("읽을거리", LIST_URL)]),
    ],
}
doc = document(title=f"{LIST_TITLE} — 디자인·AI 디자인 글 {len(items)}편", desc=LIST_DESC,
               url=LIST_URL, body=list_body, jsonld=list_jsonld, crumb=LIST_TITLE,
               footer_nav=fnav, menu=menu("articles"))
(ROOT / "articles").mkdir(exist_ok=True)
(ROOT / "articles" / "index.html").write_text(doc, encoding="utf-8")

# ---------- 메인 화면용 데이터 ----------
js = ["// 이 파일은 tools/build-articles.py 가 만듭니다. 직접 고치지 마세요.",
      "// 글은 content/articles/*.md 에서 고칩니다.",
      "const ARTICLES = ["]
for x in items:
    js.append("  { " + ", ".join([
        f"slug: {json.dumps(x['slug'], ensure_ascii=False)}",
        f"title: {json.dumps(x['title'], ensure_ascii=False)}",
        f"desc: {json.dumps(x['desc'], ensure_ascii=False)}",
        f"date: {json.dumps(x['date'], ensure_ascii=False)}",
        f"tag: {json.dumps(x.get('tag', ''), ensure_ascii=False)}",
        f"min: {x['min']}",
    ]) + " },")
js += ["];", ""]
(ROOT / "js" / "articles.js").write_text("\n".join(js), encoding="utf-8")

print(f"글 {len(items)}편: /articles/ + " + ", ".join(f"/articles/{x['slug']}/" for x in items))
print(f"(오늘 {datetime.date.today().isoformat()} · js/articles.js 갱신)")
