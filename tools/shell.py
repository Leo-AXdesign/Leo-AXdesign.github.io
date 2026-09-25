#!/usr/bin/env python3
"""
정적 페이지의 공통 껍데기(head, 상단바, 푸터)를 한곳에서 만듭니다.

build-pages.py 와 build-articles.py 가 같이 씁니다.
애널리틱스 ID, 애드센스 코드, 푸터 문구는 이 파일만 고치면 모든 페이지에 반영됩니다.
"""
import json, html

SITE = "https://designrefs.com/"
GA_ID = "G-Q7QVVHSLQ6"
CONTACT = "nisov0924@gmail.com"
e = html.escape


MENU_ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
             'stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>')
# 메인 화면의 태그 필터와 같은 순서 (js/app.js 의 TAG_FILTERS)
TAGS = [("", "전체"), ("한국", "한국"), ("무료", "무료"), ("유료", "유료"), ("AI", "AI")]


def drawer_extras():
    """메인 화면 모바일 메뉴의 아래쪽 두 묶음을 정적 페이지에도 똑같이 둡니다.
    태그를 누르면 메인 화면으로 가서 그 필터가 걸린 채로 열립니다."""
    from urllib.parse import quote
    pills = "".join(
        f'<a class="pill{" is-active" if not tid else ""}" href="{SITE}{"?tag=" + quote(tid) if tid else ""}">{label}</a>'
        for tid, label in TAGS)
    return ('        <div class="drawer__section">\n'
            '          <p class="nav__group">태그 필터</p>\n'
            f'          <div class="pills pills--tags">{pills}</div>\n'
            '        </div>\n'
            '        <div class="drawer__section">\n'
            '          <p class="nav__group">보기</p>\n'
            '          <div class="drawer__row">\n'
            '            <button class="drawer__opt" id="drawer-theme" type="button">테마 전환</button>\n'
            '            <button class="drawer__opt" data-view="list" type="button">목록</button>\n'
            '            <button class="drawer__opt" data-view="grid" type="button">격자</button>\n'
            '          </div>\n'
            '        </div>\n')


CLOSE_ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
              'stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>')


def document(*, title, desc, url, body, jsonld, crumb, og_type="website",
             head_extra="", main_class="page__main", footer_nav="", menu=""):
    """페이지 하나의 HTML 전체를 돌려줍니다.

    title      : <title> 과 og:title 에 쓰는 제목 (사이트 이름은 여기서 붙입니다)
    desc       : meta description
    url        : canonical 주소 (끝에 / 포함)
    body       : <main> 안에 들어갈 HTML
    jsonld     : 구조화 데이터 dict
    crumb      : 상단바에 보이는 현재 위치 문구 (HTML 허용)
    footer_nav : 푸터 위에 붙일 링크 묶음 HTML
    menu       : 메뉴 항목 HTML (tools/nav.py 의 menu()). 넓은 화면에서는 왼쪽에,
                 좁은 화면에서는 햄버거 버튼을 누르면 서랍으로 나옵니다. 비우면 메뉴 없이 나옵니다.
    """
    menu_btn = drawer = aside = ""
    if menu:
        menu_btn = ('<div class="top__actions">\n'
                    '        <button id="menu-open" class="top__btn top__btn--menu" type="button" '
                    'aria-label="메뉴 열기" aria-expanded="false" aria-controls="drawer">'
                    + MENU_ICON + '</button>\n      </div>')
        drawer = ('\n  <!-- 모바일 전체 메뉴 -->\n'
                  '  <div class="drawer" id="drawer" hidden>\n'
                  '    <div class="drawer__backdrop" id="drawer-backdrop"></div>\n'
                  '    <aside class="drawer__panel" role="dialog" aria-modal="true" aria-label="전체 메뉴">\n'
                  '      <header class="drawer__head">\n'
                  '        <span class="drawer__title">전체 메뉴</span>\n'
                  '        <button id="menu-close" class="drawer__close" type="button" aria-label="메뉴 닫기">'
                  + CLOSE_ICON + '</button>\n'
                  '      </header>\n'
                  '      <div class="drawer__body">\n'
                  '        <nav class="nav" aria-label="메뉴">' + menu + '</nav>\n'
                  + drawer_extras() +
                  '      </div>\n'
                  '    </aside>\n'
                  '  </div>\n')
        aside = ('    <aside class="sidebar">\n'
                 '      <nav class="nav" aria-label="메뉴">' + menu + '</nav>\n'
                 '    </aside>')
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{e(title)} | 디자인 허브</title>
  <meta name="description" content="{e(desc)}" />
  <link rel="canonical" href="{url}" />
  <meta name="robots" content="index, follow, max-image-preview:large" />
  <meta property="og:type" content="{og_type}" />
  <meta property="og:title" content="{e(title)} | 디자인 허브" />
  <meta property="og:description" content="{e(desc)}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{SITE}og-image.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="icon" href="{SITE}favicon.ico" sizes="32x32" />
  <link rel="icon" type="image/svg+xml" href="{SITE}favicon.svg" />
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css" />
  <link rel="stylesheet" href="{SITE}css/style.css" />
  <!-- 구글 애드센스: 승인 신청 시 아래 주석을 풀고 ca-pub- 번호를 채우세요. -->
  <!-- <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX" crossorigin="anonymous"></script> -->

  <!-- Google Analytics (GA4) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{GA_ID}');
  </script>
  <script>
    // 메인에서 고른 테마를 그대로 따릅니다.
    try {{
      var t = localStorage.getItem('designhub:theme') || 'light';
      if (t === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
    }} catch (e) {{}}
  </script>
  <script type="application/ld+json">
{json.dumps(jsonld, ensure_ascii=False, indent=2)}
  </script>{head_extra}
</head>
<body class="page">
  <header class="top">
    <div class="wrap top__inner">
      <a class="logo" href="{SITE}">d<span>.</span></a>
      <span class="page__crumb"><a href="{SITE}">디자인 허브</a> / {crumb}</span>
      {menu_btn}
    </div>
  </header>
{drawer}
  <div class="wrap layout">
{aside}
    <main class="{main_class}">
{body}
    </main>
  </div>

  <footer class="footer">
{footer_nav}    <div class="wrap footer__inner">
      <span>Copyright 2026. Design Hub. all rights reserved.</span>
      <a href="{SITE}about/">소개</a>
      <a href="{SITE}articles/">읽을거리</a>
      <a href="{SITE}talk/">디자인 잡담</a>
      <a href="{SITE}privacy/">개인정보처리방침</a>
      <a href="mailto:{CONTACT}">CONTACT : {CONTACT}</a>
    </div>
  </footer>
  <script src="{SITE}js/page.js" defer></script>
</body>
</html>
"""
