#!/usr/bin/env python3
"""
정적 페이지 왼쪽에 붙는 메뉴와 푸터 링크를 만듭니다.

메인 화면(index.html)은 자바스크립트가 같은 모양의 메뉴를 그립니다.
정적 페이지의 메뉴를 누르면 메인 화면의 같은 화면(#ai, #articles ...)으로 갑니다.
카테고리별 정적 페이지(/ai/ 등)는 검색엔진이 들어오는 입구로 두고,
사이트 안에서 돌아다닐 때는 늘 메인 화면과 똑같은 모습을 보게 하려는 것입니다.
디자인 잡담만은 메인 화면에 없는 페이지라 /talk/ 로 갑니다.
보고 있는 페이지는 검게 표시됩니다.
"""
import html

import sitedata as D
import articles as A

SITE = "https://designrefs.com/"
e = html.escape


def _item(key, label, count, active, href):
    cls = "nav__item is-active" if key == active else "nav__item"
    num = f'<span class="nav__count">{count}</span>' if count is not None else ""
    return f'<a class="{cls}" href="{href}"><span class="nav__label">{e(label)}</span>{num}</a>'


def _app(view=""):
    """메인 화면의 한 화면으로 가는 주소 (#ai 처럼)"""
    return SITE + ("#" + view if view else "")


STAR = ('<svg viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1.8" '
        'stroke-linejoin="round"><path d="m12 2.5 2.9 6.1 6.6.8-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.3 '
        '1.3-6.6L2.5 9.4l6.6-.8Z"/></svg>')
SEP = '<hr class="nav__sep" />'


def menu(active=""):
    """메뉴 항목들. 왼쪽 사이드바와 모바일 메뉴가 같이 씁니다.
    active: 지금 보고 있는 페이지의 슬러그 (예: 'talk', 'ai', 'articles')"""
    n = D.counts()
    parts = [_item("", "전체", len(D.sites), active, _app()),
             # 즐겨찾기는 브라우저에만 저장돼 있어서, 개수는 js/page.js 가 채웁니다
             f'<a class="nav__item" href="{_app("bookmarks")}">{STAR}'
             '<span class="nav__label">즐겨찾기</span><span class="nav__count" data-bm-count>0</span></a>',
             SEP]
    for c in D.cats:
        slug = D.CAT_SLUG.get(c["id"])
        if slug and n.get(c["id"]):
            parts.append(_item(slug, c["label"], n[c["id"]], active, _app(c["id"])))
    parts.append(SEP)
    posts = A.load()
    if posts:
        parts.append(_item("articles", "읽을거리", len(posts), active, _app("articles")))
    parts.append(_item("styles", "스타일 사전", len(D.styles), active, _app("styles")))
    parts.append(_item("trends", "2026 트렌드", len(D.trends), active, _app("trends")))
    parts.append(_item("glossary", "용어 사전", len(D.terms), active, _app("glossary")))
    parts.append(SEP)
    parts.append(_item("talk", "디자인 잡담", None, active, SITE + "talk/"))
    return "".join(parts)


def footer_links():
    """메인 화면 푸터의 링크 묶음(카테고리 / 인사이트)과 같은 것.
    여기는 검색엔진이 따라가도록 정적 페이지 주소를 겁니다."""
    n = D.counts()
    cats = "".join(f'<a href="{SITE}{D.CAT_SLUG[c["id"]]}/">{e(c["label"])}</a>'
                   for c in D.cats if D.CAT_SLUG.get(c["id"]) and n.get(c["id"]))
    ins = (f'<a href="{SITE}articles/">읽을거리</a><a href="{SITE}styles/">스타일 사전</a>'
           f'<a href="{SITE}trends/">2026 트렌드</a><a href="{SITE}glossary/">용어 사전</a>')
    return ('    <div class="wrap">\n'
            f'      <nav class="footer__nav"><div class="footer__navgroup">{cats}</div>'
            f'<div class="footer__navgroup">{ins}</div></nav>\n'
            '    </div>\n')


def sidebar(active=""):
    """active: 지금 보고 있는 페이지의 슬러그 (예: 'talk', 'ai')"""
    return ('    <aside class="sidebar">\n      <nav class="nav" aria-label="메뉴">'
            + menu(active) + "</nav>\n    </aside>")
