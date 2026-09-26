#!/usr/bin/env python3
"""
content/articles/*.md 로 블로그 페이지를 만듭니다.

  python3 tools/build-articles.py

만들어지는 것
- /articles/            글 목록
- /articles/<slug>/     글 하나 (BlogPosting 구조화 데이터 포함)
- js/articles.js        메인 화면 '읽을거리' 목록용 데이터
- rss.xml               새 글 알림용 피드 (네이버 서치어드바이저·피드 구독기)
글별 공유 이미지(og/<slug>.png)는 tools/build-og.py 가 따로 만듭니다.

글을 추가하려면 content/articles/ 에 .md 파일을 하나 더 만들고 이 스크립트를 실행하세요.
그다음 tools/build-seo.py 를 돌려야 sitemap 과 llms.txt 에도 반영됩니다.
"""
import json, pathlib, datetime, email.utils

import articles as A
import sitedata as D
from nav import menu, footer_links
from shell import document, section_head, SITE, e

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


# 정적 페이지 슬러그 -> 메인 화면의 화면 이름 (#uiux 처럼)
APP_VIEW = {slug: cid for cid, slug in D.CAT_SLUG.items()}
APP_VIEW.update({"styles": "styles", "trends": "trends", "glossary": "glossary"})


def related_links(slugs):
    """글 아래 '이어서 볼 목록'. 사이트 안에서 움직일 때는 메인 화면의 같은 화면으로 보냅니다."""
    out = [f'<a href="{SITE}#{APP_VIEW.get(s, s)}">{e(A.RELATED_LABEL[s])}</a>'
           for s in slugs if s in A.RELATED_LABEL]
    if not out:
        return ""
    return ('<nav class="page__nav">\n      <h2 class="psub">이어서 볼 목록</h2>\n'
            f'      <div class="page__navlinks">{"".join(out)}</div>\n    </nav>')


def arow(x):
    """메인 화면 '읽을거리' 목록의 한 줄과 같은 모양 (js/app.js renderArticleRow)."""
    y, m, d = x["date"].split("-")
    return (f'        <a class="arow" href="{SITE}articles/{x["slug"]}/">\n'
            f'          <span class="arow__date">{y}. {m}. {d}</span>\n'
            f'          <span class="arow__main">\n'
            f'            <span class="arow__title">{e(x["title"])}</span>\n'
            f'            <p class="arow__desc">{e(x["desc"])}</p>\n'
            f'          </span>\n'
            f'          <span class="arow__tag">{e(x.get("tag", ""))} · {x["min"]}분</span>\n'
            f'        </a>')


def other_articles(items, slug):
    rest = [x for x in items if x["slug"] != slug]
    if not rest:
        return ""
    rows = "\n".join(arow(x) for x in rest)
    return (f'<section class="section">\n{section_head("다른 글", len(rest), level=2)}\n'
            f'      <div class="list list--insight">\n{rows}\n      </div>\n    </section>')


items = A.load()
if not items:
    raise SystemExit("content/articles/ 에 글이 없습니다")
fnav = footer_links()

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
      <h1 class="page__title">{A.nobreak(e(x["title"]))}</h1>
      <p class="page__intro">{e(x["desc"])}</p>
      <p class="art__meta"><time datetime="{x["date"]}">{kdate(x["date"])}</time> · 읽는 데 약 {x["min"]}분</p>
{x["body"]}
      <div class="share">
        <button class="share__btn" type="button" data-share>공유하기</button>
        <button class="share__btn" type="button" data-copy>링크 복사</button>
        <span class="share__msg" role="status"></span>
      </div>
    </article>

    {related_links(x.get("related", []))}

    {other_articles(items, x["slug"])}"""
    og = ROOT / "og" / f"{x['slug']}.png"
    doc = document(title=x["title"], desc=x["desc"], url=url, body=body, jsonld=jsonld,
                   og_type="article", menu=menu("articles"),
                   og_image=f"{SITE}og/{x['slug']}.png" if og.exists() else None,
                   main_class="page__main page__main--art", footer_nav=fnav)
    d = ROOT / "articles" / x["slug"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(doc, encoding="utf-8")

# ---------- 목록 페이지 ----------
LIST_TITLE = "읽을거리"
LIST_DESC = ("디자인하면서 생각한 것들을 적습니다. "
             "AI와 같이 일하는 법, 스타일을 말로 옮기는 법, 레퍼런스와 커뮤니티 이야기.")
list_body = f"""    <section class="section">
{section_head(LIST_TITLE, len(items), "디자인하면서 생각한 것들")}
      <div class="list list--insight">
{chr(10).join(arow(x) for x in items)}
      </div>
    </section>"""
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
               url=LIST_URL, body=list_body, jsonld=list_jsonld,
               footer_nav=fnav, menu=menu("articles"))
(ROOT / "articles").mkdir(exist_ok=True)
(ROOT / "articles" / "index.html").write_text(doc, encoding="utf-8")

# ---------- RSS ----------
KST = datetime.timezone(datetime.timedelta(hours=9))


def rfc822(d):
    y, m, day = (int(v) for v in d.split("-"))
    return email.utils.format_datetime(datetime.datetime(y, m, day, 9, 0, tzinfo=KST))


rss_items = []
for x in items:
    link = f"{SITE}articles/{x['slug']}/"
    rss_items.append(f"""    <item>
      <title>{e(x["title"])}</title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <pubDate>{rfc822(x["date"])}</pubDate>
      <category>{e(x.get("tag", ""))}</category>
      <description>{e(x["desc"])}</description>
      <content:encoded><![CDATA[{x["body"]}]]></content:encoded>
    </item>""")
rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>디자인 허브 읽을거리</title>
    <link>{LIST_URL}</link>
    <atom:link href="{SITE}rss.xml" rel="self" type="application/rss+xml" />
    <description>{e(LIST_DESC)}</description>
    <language>ko</language>
    <lastBuildDate>{rfc822(items[0]["date"])}</lastBuildDate>
{chr(10).join(rss_items)}
  </channel>
</rss>
"""
(ROOT / "rss.xml").write_text(rss, encoding="utf-8")

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
print(f"(오늘 {datetime.date.today().isoformat()} · js/articles.js, rss.xml 갱신)")
