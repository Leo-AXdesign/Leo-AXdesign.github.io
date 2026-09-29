#!/usr/bin/env python3
"""
content/articles/*.md 와 content/articles-en/*.md 로 블로그 페이지를 만듭니다.

  python3 tools/build-articles.py

만들어지는 것 (한국어)
- /articles/            글 목록
- /articles/<slug>/     글 하나 (BlogPosting 구조화 데이터 포함)
- js/articles.js        메인 화면 '읽을거리' 목록용 데이터
- rss.xml               새 글 알림용 피드 (네이버 서치어드바이저·피드 구독기)

만들어지는 것 (영문판, content/articles-en/ 에 번역이 있는 글만)
- /en/articles/, /en/articles/<slug>/, js/articles.en.js, en/rss.xml
  한국어 글과 영문 글은 서로 hreflang 으로 이어지고, 머리글의 EN/KO 버튼이 짝 글로 갑니다.

글별 공유 이미지(og/<slug>.png, og/en/<slug>.png)는 tools/build-og.py 가 따로 만듭니다.

글을 추가하려면 content/articles/ 에 .md 파일을 하나 더 만들고 이 스크립트를 실행하세요.
그다음 tools/build-seo.py 를 돌려야 sitemap 과 llms.txt 에도 반영됩니다.
"""
import json, pathlib, datetime, email.utils

import articles as A
import sitedata as D
from nav import menu, footer_links
from shell import document, section_head, SITE, e

ROOT = pathlib.Path(__file__).resolve().parent.parent
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

# 언어마다 다른 것들
LANG = {
    "ko": {
        "base": SITE, "dir": ROOT, "og": ROOT / "og", "og_url": SITE + "og/",
        "brand": "디자인 허브", "blog": "디자인 허브 읽을거리", "list": "읽을거리",
        "list_title": lambda n: f"읽을거리 — 디자인·AI 디자인 글 {n}편",
        "list_head": "디자인하면서 생각한 것들",
        "list_desc": ("디자인하면서 생각한 것들을 적습니다. "
                      "AI와 같이 일하는 법, 스타일을 말로 옮기는 법, 레퍼런스와 커뮤니티 이야기."),
        "date": lambda y, m, d: f"{y}년 {m}월 {d}일",
        "read": lambda n: f"읽는 데 약 {n}분", "min": "분",
        "share": "공유하기", "copy": "링크 복사", "more": "다른 글", "related": "이어서 볼 목록",
        "labels": A.RELATED_LABEL, "js": "articles.js", "rss": "rss.xml", "rss_lang": "ko",
        "note": "",
    },
    "en": {
        "base": SITE + "en/", "dir": ROOT / "en", "og": ROOT / "og" / "en", "og_url": SITE + "og/en/",
        "brand": "Design Hub", "blog": "Design Hub Articles", "list": "Articles",
        "list_title": lambda n: f"Articles — {n} pieces on design and AI design",
        "list_head": "Notes from designing, translated from Korean",
        "list_desc": ("Notes from a designer in Korea: working with AI, putting style into words, "
                      "collecting references and design communities. Translated from Korean."),
        "date": lambda y, m, d: f"{MONTHS[m - 1]} {d}, {y}",
        "read": lambda n: f"{n} min read", "min": " min",
        "share": "Share", "copy": "Copy link", "more": "More articles", "related": "Keep exploring",
        "labels": A.RELATED_LABEL_EN, "js": "articles.en.js", "rss": "en/rss.xml", "rss_lang": "en",
        "note": '      <p class="art__note">Translated from the Korean original. '
                '<a href="{ko}" hreflang="ko" lang="ko">Read in Korean</a></p>\n',
    },
}

# 정적 페이지 슬러그 -> 메인 화면의 화면 이름 (#uiux 처럼)
APP_VIEW = {slug: cid for cid, slug in D.CAT_SLUG.items()}
APP_VIEW.update({"styles": "styles", "trends": "trends", "glossary": "glossary"})

KST = datetime.timezone(datetime.timedelta(hours=9))


def crumbs(items):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": u}
            for i, (n, u) in enumerate(items)
        ],
    }


def rfc822(d):
    y, m, day = (int(v) for v in d.split("-"))
    return email.utils.format_datetime(datetime.datetime(y, m, day, 9, 0, tzinfo=KST))


def build(lang, ko_slugs, en_slugs):
    L = LANG[lang]
    items = A.load(lang)
    if not items:
        if lang == "ko":
            raise SystemExit("content/articles/ 에 글이 없습니다")
        return items
    base = L["base"]
    list_url = base + "articles/"
    fnav = footer_links(lang)

    def art_url(slug, lg=lang):
        return LANG[lg]["base"] + f"articles/{slug}/"

    def alternates(slug):
        """같은 글의 한국어판·영문판 주소. 짝이 없으면 비워 둡니다."""
        if slug in ko_slugs and slug in en_slugs:
            return {"ko": art_url(slug, "ko"), "en": art_url(slug, "en")}
        return None

    def related_links(slugs):
        """글 아래 '이어서 볼 목록'. 사이트 안에서 움직일 때는 메인 화면의 같은 화면으로 보냅니다."""
        out = [f'<a href="{base}#{APP_VIEW.get(s, s)}">{e(L["labels"][s])}</a>'
               for s in slugs if s in L["labels"]]
        if not out:
            return ""
        return (f'<nav class="page__nav">\n      <h2 class="psub">{L["related"]}</h2>\n'
                f'      <div class="page__navlinks">{"".join(out)}</div>\n    </nav>')

    def arow(x):
        """메인 화면 '읽을거리' 목록의 한 줄과 같은 모양 (js/app.js renderArticleRow)."""
        y, m, d = x["date"].split("-")
        return (f'        <a class="arow" href="{art_url(x["slug"])}">\n'
                f'          <span class="arow__date">{y}. {m}. {d}</span>\n'
                f'          <span class="arow__main">\n'
                f'            <span class="arow__title">{e(x["title"])}</span>\n'
                f'            <p class="arow__desc">{e(x["desc"])}</p>\n'
                f'          </span>\n'
                f'          <span class="arow__tag">{e(x.get("tag", ""))} · {x["min"]}{L["min"]}</span>\n'
                f'        </a>')

    def other_articles(slug):
        rest = [x for x in items if x["slug"] != slug]
        if not rest:
            return ""
        rows = "\n".join(arow(x) for x in rest)
        return (f'<section class="section">\n{section_head(L["more"], len(rest), level=2)}\n'
                f'      <div class="list list--insight">\n{rows}\n      </div>\n    </section>')

    # ---------- 글 하나씩 ----------
    for x in items:
        url = art_url(x["slug"])
        og = L["og"] / f"{x['slug']}.png"
        og_url = f'{L["og_url"]}{x["slug"]}.png' if og.exists() else None
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
                    "inLanguage": lang,
                    "wordCount": x["words"] if lang == "en" else x["chars"],
                    "timeRequired": f"PT{x['min']}M",
                    "image": og_url or SITE + "og-image.png",
                    "author": {"@type": "Organization", "name": L["brand"], "url": base},
                    "publisher": {"@type": "Organization", "name": L["brand"], "url": base},
                    "isPartOf": {"@type": "Blog", "@id": list_url + "#blog", "name": L["blog"]},
                },
                crumbs([(L["brand"], base), (L["list"], list_url), (x["title"], url)]),
            ],
        }
        if lang == "en":
            jsonld["@graph"][0]["translationOfWork"] = {"@id": art_url(x["slug"], "ko") + "#post"}
        y, m, d = (int(v) for v in x["date"].split("-"))
        note = L["note"].format(ko=art_url(x["slug"], "ko")) if L["note"] else ""
        body = f"""    <article class="art">
      <p class="art__kicker"><a href="{list_url}">{L["list"]}</a>{f' · {e(x["tag"])}' if x.get("tag") else ''}</p>
      <h1 class="page__title">{A.nobreak(e(x["title"]))}</h1>
      <p class="page__intro">{e(x["desc"])}</p>
      <p class="art__meta"><time datetime="{x["date"]}">{L["date"](y, m, d)}</time> · {L["read"](x["min"])}</p>
{note}{x["body"]}
      <div class="share">
        <button class="share__btn" type="button" data-share>{L["share"]}</button>
        <button class="share__btn" type="button" data-copy>{L["copy"]}</button>
        <span class="share__msg" role="status"></span>
      </div>
    </article>

    {related_links(x.get("related", []))}

    {other_articles(x["slug"])}"""
        doc = document(title=x["title"], desc=x["desc"], url=url, body=body, jsonld=jsonld,
                       og_type="article", menu=menu("articles", lang), og_image=og_url,
                       main_class="page__main page__main--art", footer_nav=fnav,
                       lang=lang, alternates=alternates(x["slug"]))
        out = L["dir"] / "articles" / x["slug"]
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(doc, encoding="utf-8")

    # ---------- 목록 페이지 ----------
    list_body = f"""    <section class="section">
{section_head(L["list"], len(items), L["list_head"])}
      <div class="list list--insight">
{chr(10).join(arow(x) for x in items)}
      </div>
    </section>"""
    list_jsonld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Blog",
                "@id": list_url + "#blog",
                "url": list_url,
                "name": L["blog"],
                "description": L["list_desc"],
                "inLanguage": lang,
                "isPartOf": {"@type": "WebSite", "url": base, "name": L["brand"]},
                "blogPost": [
                    {
                        "@type": "BlogPosting",
                        "@id": f"{art_url(x['slug'])}#post",
                        "url": art_url(x["slug"]),
                        "headline": x["title"],
                        "description": x["desc"],
                        "datePublished": x["date"],
                        "author": {"@type": "Organization", "name": L["brand"]},
                    }
                    for x in items
                ],
            },
            crumbs([(L["brand"], base), (L["list"], list_url)]),
        ],
    }
    both = {"ko": SITE + "articles/", "en": SITE + "en/articles/"} if en_slugs else None
    doc = document(title=L["list_title"](len(items)), desc=L["list_desc"],
                   url=list_url, body=list_body, jsonld=list_jsonld,
                   footer_nav=fnav, menu=menu("articles", lang), lang=lang, alternates=both)
    (L["dir"] / "articles").mkdir(parents=True, exist_ok=True)
    (L["dir"] / "articles" / "index.html").write_text(doc, encoding="utf-8")

    # ---------- RSS ----------
    rss_items = []
    for x in items:
        link = art_url(x["slug"])
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
    <title>{e(L["blog"])}</title>
    <link>{list_url}</link>
    <atom:link href="{SITE}{L["rss"]}" rel="self" type="application/rss+xml" />
    <description>{e(L["list_desc"])}</description>
    <language>{L["rss_lang"]}</language>
    <lastBuildDate>{rfc822(items[0]["date"])}</lastBuildDate>
{chr(10).join(rss_items)}
  </channel>
</rss>
"""
    (ROOT / L["rss"]).write_text(rss, encoding="utf-8")

    # ---------- 메인 화면용 데이터 ----------
    js = ["// 이 파일은 tools/build-articles.py 가 만듭니다. 직접 고치지 마세요.",
          f"// 글은 content/{'articles-en' if lang == 'en' else 'articles'}/*.md 에서 고칩니다.",
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
    (ROOT / "js" / L["js"]).write_text("\n".join(js), encoding="utf-8")
    return items


ko_slugs = {x["slug"] for x in A.load("ko")}
en_slugs = {x["slug"] for x in A.load("en")}
ko = build("ko", ko_slugs, en_slugs)
en = build("en", ko_slugs, en_slugs)

print(f"글 {len(ko)}편: /articles/ + " + ", ".join(f"/articles/{x['slug']}/" for x in ko))
if en:
    print(f"영문 {len(en)}편: /en/articles/ + " + ", ".join(f"/en/articles/{x['slug']}/" for x in en))
missing = sorted(ko_slugs - en_slugs)
if missing:
    print("  영문 번역이 없는 글 (content/articles-en/ 에 같은 이름으로 만들면 됩니다):", ", ".join(missing))
print(f"(오늘 {datetime.date.today().isoformat()} · js/articles.js, rss.xml 갱신)")
