#!/usr/bin/env python3
"""
정적 페이지 왼쪽에 붙는 메뉴를 만듭니다.

메인 화면(index.html)은 자바스크립트가 같은 모양의 메뉴를 그립니다.
이 파일은 그 메뉴를 정적 페이지용으로, 진짜 주소를 건 형태로 다시 만듭니다.
보고 있는 페이지는 검게 표시됩니다.
"""
import html

import sitedata as D
import articles as A

SITE = "https://designrefs.com/"
e = html.escape


def _item(slug, label, count, active):
    """slug 가 '' 이면 메인 화면으로 갑니다."""
    url = SITE + (slug + "/" if slug else "")
    cls = "nav__item is-active" if slug == active else "nav__item"
    num = f'<span class="nav__count">{count}</span>' if count is not None else ""
    return f'<a class="{cls}" href="{url}"><span class="nav__label">{e(label)}</span>{num}</a>'


STAR = ('<svg viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1.8" '
        'stroke-linejoin="round"><path d="m12 2.5 2.9 6.1 6.6.8-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.3 '
        '1.3-6.6L2.5 9.4l6.6-.8Z"/></svg>')
SEP = '<hr class="nav__sep" />'


def menu(active=""):
    """메뉴 항목들. 왼쪽 사이드바와 모바일 메뉴가 같이 씁니다."""
    n = D.counts()
    parts = [_item("", "전체", len(D.sites), active),
             # 즐겨찾기는 브라우저에만 저장돼 있어서, 개수는 js/page.js 가 채웁니다
             f'<a class="nav__item" href="{SITE}#bookmarks">{STAR}'
             '<span class="nav__label">즐겨찾기</span><span class="nav__count" data-bm-count>0</span></a>',
             _item("talk", "디자인 잡담", None, active),
             SEP]
    for c in D.cats:
        slug = D.CAT_SLUG.get(c["id"])
        if slug and n.get(c["id"]):
            parts.append(_item(slug, c["label"], n[c["id"]], active))
    parts.append(SEP)
    posts = A.load()
    if posts:
        parts.append(_item("articles", "읽을거리", len(posts), active))
    parts.append(_item("styles", "스타일 사전", len(D.styles), active))
    parts.append(_item("trends", "2026 트렌드", len(D.trends), active))
    parts.append(_item("glossary", "용어 사전", len(D.terms), active))
    return "".join(parts)


def sidebar(active=""):
    """active: 지금 보고 있는 페이지의 슬러그 (예: 'talk', 'ai')"""
    return ('    <aside class="sidebar">\n      <nav class="nav" aria-label="메뉴">'
            + menu(active) + "</nav>\n    </aside>")
