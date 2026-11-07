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
from nav import menu, footer_links
from shell import document, section_head, SITE, e
import articles as A
import updates as U

HIST = U.history()
LAST = U.last_changed()


def related_articles(slug, n=4):
    """이 분야와 연결된 읽을거리 (글의 related 에 이 페이지 슬러그가 있는 것). 최신 글부터."""
    posts = [x for x in A.load() if slug in x.get("related", [])][:n]
    if not posts:
        return ""
    rows = []
    for x in posts:
        y, m, d = x["date"].split("-")
        rows.append(f'        <a class="arow" href="{SITE}articles/{x["slug"]}/">\n'
                    f'          <span class="arow__date">{y}. {m}. {d}</span>\n'
                    f'          <span class="arow__main">\n'
                    f'            <span class="arow__title">{e(x["title"])}</span>\n'
                    f'            <p class="arow__desc">{e(x["desc"])}</p>\n'
                    f'          </span>\n'
                    f'          <span class="arow__tag">{e(x.get("tag", ""))} · {x["min"]}분</span>\n'
                    f'        </a>')
    return (f'\n    <section class="section">\n{section_head("관련 읽을거리", len(posts), "이 분야를 다룬 글", level=2)}\n'
            f'      <div class="list list--insight">\n' + "\n".join(rows) + '\n      </div>\n    </section>')

ROOT = pathlib.Path(__file__).resolve().parent.parent

# 카테고리 id -> (주소 슬러그, 페이지 제목, 소개 문장)
PAGE_META = {
    "uiux":      ("ui-ux",     "UI/UX 레퍼런스 사이트 {n}곳",   "실제 앱·웹 화면과 유저 플로우, 랜딩페이지를 볼 수 있는 UI/UX 레퍼런스 사이트를 모았습니다."),
    "graphic":   ("graphic",   "그래픽·브랜딩 레퍼런스 {n}곳",  "포스터, 로고, 패키지, 편집 디자인 레퍼런스를 찾을 수 있는 사이트입니다."),
    "color":     ("color",     "컬러 팔레트 사이트 {n}곳",      "팔레트 생성기, 그라디언트 도구, 명도 대비 검사기를 모았습니다."),
    "typo":      ("font",      "무료 폰트·타이포그래피 사이트 {n}곳", "상업용 무료 한글 폰트부터 영문 파운드리, 폰트 조합 도구까지 정리했습니다."),
    "asset":     ("assets",    "아이콘·일러스트·에셋 사이트 {n}곳", "아이콘, 일러스트, 사진, 영상 등 디자인 에셋을 받을 수 있는 곳입니다."),
    "mockup":    ("mockups",   "디자인 목업 사이트 {n}곳",      "기기·인쇄물·패키지·의류 목업과 목업 생성기를 모았습니다. 무료 PSD부터 3D·영상 목업까지."),
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

def guide_parts(cat_id):
    """content/guides/<분야 id>.md 를 첫 문단(목록 위에 둠)과 나머지(목록 아래 '안내')로 나눕니다."""
    f = ROOT / "content" / "guides" / f"{cat_id}.md"
    if not f.exists():
        return "", ""
    md = f.read_text(encoding="utf-8").strip()
    first, _, rest = md.partition("\n\n")
    if first.startswith("#"):
        return "", md
    return " ".join(first.split("\n")), rest.strip()


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
            body.append(f'      <h2 class="psub psub--plain">{e(sb)} <span>{len(part)}</span></h2>')
            body.append(site_list(part))
        body_html = "\n".join(body)
    else:
        body_html = site_list(items)
    lead, guide = guide_parts(c["id"])
    y, m, d = LAST[c["id"]].split("-")
    meta = (f'      <p class="pmeta">마지막으로 고친 날 {y}. {int(m)}. {int(d)} · '
            f'<a href="{SITE}updates/">업데이트 기록</a>'
            + (' · <a href="#guide">이 분야 안내</a>' if guide else "") + '</p>\n')
    lead_html = f'      <p class="ptext guide-lead">{A.inline(lead)}</p>\n' if lead else ""
    guide_html = (f'\n      <section class="guide" id="guide">\n        <h2 class="guide__title">{e(c["label"])}, 이렇게 고릅니다</h2>\n'
                  f'{A.to_html(guide)}\n      </section>') if guide else ""
    body_html = lead_html + meta + body_html + guide_html
    pages.append((slug, title, intro, body_html, len(items), [s["name"] for s in items], c["label"]))

# 스타일 사전과 트렌드는 메인 화면과 같은 그림을 씁니다 (AI로 만든 예시 일러스트, assets/styles · assets/trends).
ILLUSTRATION_NOTE = '<p class="insight-note">썸네일은 각 양식과 흐름의 특징을 설명하기 위해 AI(GPT Image 2.5)로 만든 예시 일러스트입니다. 실제 작품이나 제품 화면이 아닙니다.</p>'
def study_image(item):
    return (f'<img class="plist__image" src="{e(item["img"])}" '
            f'alt="{e(item["name"])} — AI로 만든 예시 일러스트" width="640" height="480" loading="lazy" />')
# 스타일 현상소(/lab/)에 있는 양식. 아래 LAB_STYLES, js/lab.js 의 thumb, js/app.js 의 LAB_SLUGS 와 같아야 합니다
LAB_SLUGS = ["risograph", "pop-art", "pixel-art", "punk", "constructivism", "cyberpunk", "vaporwave", "psychedelic", "memphis"]
def lab_link(item):
    slug = item["img"].rsplit("/", 1)[-1].split(".")[0]
    return f' · <a href="{SITE}lab/#{slug}">내 사진으로 해 보기</a>' if slug in LAB_SLUGS else ""
sb = ['      <ul class="plist">']
for s in styles:
    sb.append('<li class="plist__item plist__item--illustrated">' + study_image(s) + '<div>'
              f'<span class="plist__name">{e(s["name"])}</span>'
              f'<span class="plist__host">{e(s.get("en",""))} · {e(s.get("era",""))}</span>'
              f'<p class="plist__desc">{e(s.get("desc",""))}</p>'
              f'<p class="plist__meta">{e(s.get("traits",""))}'
              + (f' · {e(s["people"])}' if s.get("people") else "") + lab_link(s) + "</p></div></li>")
sb.extend(["</ul>", ILLUSTRATION_NOTE])
pages.append(("styles", f"디자인 스타일 사전 {len(styles)}가지",
              "아르누보부터 바우하우스, 스위스 스타일, Y2K, 글래스모피즘까지 유명 그래픽 디자인 양식을 연대순으로 정리했습니다.",
              "\n".join(sb), len(styles), [s["name"] for s in styles], "스타일 사전"))

tb = ['      <ul class="plist">']
for i, t in enumerate(trends, 1):
    kind = "공식 리포트·발표" if t.get("kind") == "report" else "지속 흐름"
    source = (f'<p class="plist__meta"><a href="{e(t["link"])}" target="_blank" rel="noopener noreferrer">공식 출처 ↗</a></p>' if t.get("link") else "")
    tb.append('<li class="plist__item plist__item--illustrated">' + study_image(t) + '<div>'
              f'<span class="plist__name">{e(t["name"])}</span>'
              f'<span class="plist__host">{e(t.get("area",""))} · {kind}</span>'
              f'<p class="plist__desc">{e(t.get("desc",""))}</p>{source}</div></li>')
tb.extend(["</ul>", ILLUSTRATION_NOTE,
           '<p class="insight-note">2026-10-14 확인. 연간 리포트의 전망과 계속 쓰이는 표현을 함께 정리했습니다. 인기 순위가 아니며, 적용 조언은 디자인 허브의 편집 의견입니다.</p>'])
trend_sources = D.fields(D.block("TREND_SOURCES"), ["name", "url"])
tb.append('<div class="sources"><span class="sources__label">참고 리포트</span>' + ''.join(
    f'<a class="sources__link" href="{e(t["url"])}" target="_blank" rel="noopener noreferrer">{e(t["name"])} ↗</a>' for t in trend_sources) + '</div>')
pages.append(("trends", f"2026 디자인 트렌드 {len(trends)}가지",
              "Adobe·Canva의 2026 공식 리포트와 지속되는 디자인 흐름. 초현실적 유머, 로컬 문화, 시네마틱 연출부터 UI·타이포·컬러까지 직접 그린 예시로 살펴봅니다.",
              "\n".join(tb), len(trends), [t["name"] for t in trends], "2026 트렌드"))

# 용어 사전
gb = []
for g in groups:
    part = [t for t in terms if t.get("group") == g["id"]]
    if not part:
        continue
    gb.append(f'      <h2 class="psub psub--plain">{e(g["label"])} <span>{len(part)}</span></h2>')
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

    <h2 class="psub">누가 만드나</h2>
    <p class="ptext">8년 차 디자이너 한 명이 운영합니다. 일하면서 레퍼런스를 북마크에 모으던 습관이 이 사이트가 됐습니다. 어떤 사이트를 넣고 뺄지, 설명을 어떻게 쓸지는 직접 정합니다.</p>
    <p class="ptext">사이트를 만들고 고치는 일, 읽을거리의 자료 조사와 초안에는 클로드 코드 같은 AI 도구를 함께 씁니다.
    숫자와 사실은 공식 발표나 원문을 열어 확인하고, 글마다 출처를 적습니다. 틀린 곳이 있으면 고친 날과 함께 바로잡습니다.</p>

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
    <p class="ptext">언제 무엇을 넣고 뺐는지는 <a href="{SITE}updates/">업데이트 기록</a>에 날짜별로 남겨 둡니다.</p>

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
    <p class="ptext">이 사이트에는 구글 애드센스 광고가 게재됩니다.
    구글을 비롯한 제3자 광고 사업자는 쿠키를 사용해 이용자의 이전 방문 기록을 바탕으로 광고를 게재할 수 있습니다.
    맞춤 광고를 원하지 않으시면 <a href="https://myadcenter.google.com" target="_blank" rel="noopener">구글 광고 설정</a>에서 끌 수 있습니다.</p>

    <h2 class="psub">4. 이야기 페이지에 남긴 글</h2>
    <p class="ptext"><a href="{SITE}talk/">디자인 잡담</a> 페이지에 글을 남기면 적어 주신 이름과 내용이 그대로 공개되고,
    Cloudflare 가 운영하는 데이터베이스에 저장됩니다. 가입 절차가 없어 이메일이나 비밀번호는 받지 않습니다.</p>
    <p class="ptext">글을 지울 때 쓰는 비밀번호도 그대로 저장하지 않습니다. 글마다 다른 값을 섞어 되돌릴 수 없는 형태로 바꿔 두기 때문에,
    운영자도 어떤 비밀번호를 쓰셨는지 알 수 없습니다.</p>
    <p class="ptext">스팸을 막기 위해 접속 IP 를 그대로 저장하지 않고, 되돌릴 수 없는 형태로 바꾼 값만 남깁니다.
    이 값은 같은 사람이 짧은 시간에 여러 번 글을 올리는지 확인하는 데만 씁니다.</p>
    <p class="ptext"><a href="{SITE}articles/">읽을거리</a> 글의 조회수를 셀 때도 같은 방식으로 바꾼 값을 씁니다.
    같은 사람이 하루에 같은 글을 여러 번 열어도 한 번만 세기 위한 것이고, 이 기록은 이틀 뒤 지웁니다.
    글마다 몇 번 읽혔는지 외에는 아무것도 남기지 않습니다.</p>
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
      <li>YouTube(youtube-nocookie.com) — 읽을거리에 넣은 영상</li>
    </ul>
    <p class="ptext">스타일 현상소(/lab/)에 올린 사진은 브라우저 안에서만 처리되고, 어디에도 전송하거나 저장하지 않습니다.</p>

    <h2 class="psub">6. 외부 링크</h2>
    <p class="ptext">이 사이트는 다른 사이트로 이동하는 링크를 모아 둔 곳입니다.
    링크를 눌러 이동한 뒤의 개인정보 처리는 해당 사이트의 방침을 따릅니다.
    이동한 사이트에서 일어나는 일에 대해 디자인 허브는 책임지지 않습니다.</p>

    <h2 class="psub" id="instagram">7. 인스타그램·스레드 계정 운영</h2>
    <p class="ptext">디자인 허브는 메타(Meta)의 공식 API로 인스타그램(@design_refs_hub)과 스레드 계정에 글을 올리고,
    게시물에 달린 댓글에 답합니다. 일부 게시물은 댓글을 남긴 분께 안내 링크를 인스타그램 메시지(DM)로 한 번 보내 드립니다.</p>
    <ul class="ptext-list">
      <li>쓰는 정보: 댓글을 남긴 계정의 사용자 이름, 댓글 내용과 시각, 댓글 번호</li>
      <li>쓰는 목적: 같은 분께 메시지를 두 번 보내지 않도록 보낸 기록을 남기는 데에만 씁니다</li>
      <li>보관: 운영자의 컴퓨터에만 저장하고, 다른 곳에 넘기거나 광고에 쓰지 않습니다. 게시물 답장이 끝나고 90일이 지나면 지웁니다</li>
    </ul>
    <p class="ptext" id="delete">기록을 지우고 싶으시면 인스타그램 사용자 이름을 적어 <a href="mailto:nisov0924@gmail.com">nisov0924@gmail.com</a>으로 보내 주세요.
    확인 후 7일 안에 지우고 답장 드립니다. 댓글은 인스타그램에서 직접 지우실 수 있습니다.</p>

    <h2 class="psub">8. 문의</h2>
    <p class="ptext">이 방침에 대한 문의는 <a href="mailto:nisov0924@gmail.com">nisov0924@gmail.com</a> 으로 보내주세요.</p>

    <p class="ptext ptext--note">시행일 2026년 9월 14일 · 개정일 2026년 11월 4일</p>
"""

TALK = f"""
    <div id="talk"></div>

    <p class="ptext ptext--note">남긴 글은 이름과 내용이 그대로 공개됩니다. 연락처 같은 개인정보는 적지 마세요.
    광고나 욕설, 남의 개인정보가 담긴 글은 보이는 대로 지웁니다.</p>

    <script src="{SITE}js/talk.js" defer></script>
"""

# ---------- 업데이트 기록 (tools/updates.py 가 git 기록에서 읽어 옵니다) ----------
KIND = {"new": "새로", "add": "추가", "move": "이동", "edit": "수정", "del": "삭제", "post": "읽을거리"}


def updates_body():
    days = {d: [(k, e(t)) for k, t, _ in items] for d, items in HIST}
    for x in A.load():
        days.setdefault(x["date"], []).append(
            ("post", f'<a href="{SITE}articles/{x["slug"]}/">{e(x["title"])}</a>'))
    n_site = sum(1 for _, items in HIST for k, *_ in items if k == "add")
    out = [f'    <p class="ptext">사이트를 넣고, 옮기고, 고치고, 지운 기록입니다. 사이트 목록 파일이 바뀔 때마다 '
           f'바로 앞 상태와 비교해서 자동으로 적기 때문에 빠지는 것이 없습니다. 읽을거리를 올린 날도 함께 적었습니다.</p>',
           f'    <p class="ptext">공개한 뒤로 사이트 {n_site}곳을 새로 넣었고, 읽을거리 {len(A.load())}편을 올렸습니다.</p>']
    month = None
    for d in sorted(days, reverse=True):
        y, m, dd = d.split("-")
        if (y, m) != month:
            if month:
                out.append("    </div>")
            month = (y, m)
            out.append(f'    <h2 class="psub psub--plain">{y}년 {int(m)}월</h2>\n    <div class="ulog">')
        rows = "".join(f'<li><span class="ulog__k ulog__k--{k}">{KIND[k]}</span>{t}</li>' for k, t in days[d])
        out.append(f'      <div class="ulog__day"><time datetime="{d}">{int(m)}. {int(dd)}</time><ul>{rows}</ul></div>')
    if month:
        out.append("    </div>")
    return "\n".join(out)


UPDATES = updates_body()


# ---------- 스타일 현상소 (/lab/) : 화면 틀과 설명 글. 그리는 일은 js/lab.js ----------
LAB_STYLES = [
    ("risograph", "리소그래프", "1980년대 일본 인쇄기에서 시작해 2010년대 독립 출판에서 다시 유행한 인쇄 방식입니다. "
     "형광 잉크를 한 색씩 따로 찍기 때문에 색이 겹친 곳에 새 색이 생기고, 판이 조금씩 어긋나며, 굵은 망점과 종이의 흰 바탕이 그대로 보입니다. "
     "여기서는 밝은 잉크가 중간톤과 따뜻한 색을, 어두운 잉크가 그림자를 맡습니다. 윤곽이 또렷한 인물이나 정물 사진에 잘 어울립니다."),
    ("pop-art", "팝아트", "1950~60년대에 광고와 만화를 예술로 끌어온 흐름입니다. 평평하게 칠한 원색 면, 굵은 검정 윤곽, 만화 인쇄의 망점(벤데이 점)이 특징입니다. "
     "사진의 잡티를 먼저 지우고 면을 정리한 뒤 칠하기 때문에, '단순하게' 값을 올릴수록 손으로 그린 만화에 가까워집니다. 배경이 단순하고 피사체가 큰 사진이 좋습니다."),
    ("pixel-art", "픽셀 아트", "초기 컴퓨터와 게임기의 제약에서 나온 표현입니다. 화면이 거친 격자로 나뉘고, 몇 가지 색만 쓰고, 경계가 계단처럼 보입니다. "
     "기본값은 사진에서 대표 색을 뽑아 쓰고, 밝기가 확 바뀌는 경계를 한 단계 어둡게 칠해 픽셀 아트 특유의 윤곽을 만듭니다. 가로 칸 수를 줄이면 더 옛날 게임처럼 보입니다."),
    ("punk", "펑크 복사기", "1970년대 후반 펑크 공연 전단과 진(zine)은 복사기로 찍어 손으로 오려 붙여 만들었습니다. 거친 흑백, 토너 얼룩, 붙였다 뗀 테이프 자국이 그 흔적입니다. "
     "여기서는 사진을 복사기에 몇 번 돌린 것처럼 만든 뒤, 몇 조각으로 찢어 살짝 어긋나게 다시 붙이고 테이프로 고정합니다. 찢는 자리와 테이프 위치는 '배치 섞기'를 누를 때마다 새로 정해집니다."),
    ("constructivism", "구성주의", "1910~30년대 러시아에서 시작된 그래픽입니다. 사진을 잘라 붙이고(포토몽타주), 붉은색과 검정의 사선, 원과 막대 같은 단순한 도형으로 화면을 밀어붙입니다. "
     "여기서는 사진을 신문 인쇄처럼 망점으로 바꿔 사각형, 원, 반원 안에 넣고 붉은 띠와 원, 막대, 삼각형을 흩어 놓습니다. 모든 도형은 같은 사선 방향을 따르고, 위치는 '배치 섞기'를 누를 때마다 바뀝니다."),
    ("cyberpunk", "사이버펑크", "1980년대 SF 소설과 영화 「블레이드 러너」에서 굳어진 미래 도시의 그림입니다. 비 오는 밤거리, 네온사인, 고장 난 화면이 단골로 나옵니다. "
     "여기서는 사진의 밝기를 네온 그라데이션으로 바꾸고, 빨강과 파랑 채널을 좌우로 어긋나게 해 오래된 모니터처럼 만듭니다. 화면 몇 줄을 찢어 밀어내고 주사선을 얹습니다. 밤 사진이나 대비가 강한 인물 사진에 잘 어울립니다."),
    ("vaporwave", "바포웨이브", "2010년대 초 인터넷에서 생긴 흐름입니다. 90년대 광고 음악을 느리게 튼 음반 표지에서 시작해, 분홍과 하늘색 그라데이션, 줄무늬 태양, "
     "끝없는 격자 바닥, 옛날 컴퓨터 창이 상징이 됐습니다. 여기서는 사진을 그 색으로 물들이고, 빨강과 파랑이 옆으로 번지는 VHS 테이프 화면을 얹습니다. "
     "'태양과 격자'는 사진을 줄무늬 태양 안에 넣고, '옛날 창'은 90년대 컴퓨터 창 안에 넣습니다. 줄무늬는 얼굴 아래쪽만 지나가게 했습니다."),
    ("psychedelic", "사이키델릭", "1960년대 샌프란시스코 록 공연 포스터에서 꽃핀 양식입니다. 녹아 흐르는 듯한 형태, 서로 부딪히는 강한 색, 등고선처럼 겹친 띠가 특징입니다. "
     "여기서는 사진을 물결처럼 휘게 한 뒤 밝기를 색 띠로 나눠 칠합니다. 휘는 무늬는 '무늬 섞기'를 누를 때마다 바뀌고, "
     "'얼굴 살리기'를 켜 두면 가운데는 덜 휘어서 누구인지 알아볼 수 있게 남습니다. 대비가 뚜렷한 인물 사진이 가장 재미있게 나옵니다."),
    ("memphis", "멤피스", "1981년 밀라노에서 에토레 소트사스가 이끈 디자인 그룹 멤피스에서 이름을 땄습니다. 파스텔과 원색, 굵은 검정 테두리, 꼬불선과 지그재그, "
     "점무늬와 색종이 조각처럼 '진지하지 않은' 장식이 특징입니다. 여기서는 사진을 아치나 원, 사각형 틀에 넣고 어긋난 그림자를 준 뒤, 둘레에 무늬를 흩어 놓습니다. "
     "무늬는 사진을 가리지 않는 자리에만 놓이고, '배치 섞기'를 누를 때마다 새로 놓입니다."),
]
assert [sid for sid, _, _ in LAB_STYLES] == LAB_SLUGS


def lab_body():
    styles = "\n".join(
        f'      <div class="lab-style" id="style-{sid}">\n'
        f'        <img src="{SITE}assets/styles/{sid}.webp" alt="{e(name)} 예시 일러스트" width="640" height="480" loading="lazy" />\n'
        f'        <div><h3>{e(name)}</h3><p class="ptext">{e(desc)}</p>\n'
        f'        <p class="ptext"><a href="{SITE}styles/">스타일 사전에서 {e(name)} 더 보기</a></p></div>\n'
        f'      </div>' for sid, name, desc in LAB_STYLES)
    return LAB_HTML.replace("{SITE}", SITE).replace("{STYLES}", styles)


LAB_HTML = """

    <section class="lab" id="lab">
      <div class="lab__stage">
        <div class="lab__drop" id="lab-drop">
          <canvas class="lab__canvas" id="lab-canvas" aria-label="바뀐 사진 미리보기"></canvas>
          <div class="lab__empty" id="lab-empty">
            <p class="lab__empty-t">사진을 여기에 끌어 놓으세요</p>
            <p><label class="lab__btn">사진 고르기<input type="file" accept="image/*" id="lab-file" hidden /></label></p>
            <p class="lab__demo">데모 사진으로 해 보기 <span id="lab-demos"></span></p>
          </div>
        </div>
        <div class="lab__under"><button type="button" class="lab__btn lab__btn--sm" id="lab-compare">누르고 있으면 원본</button>
        <p class="lab__hint">사진은 기기 밖으로 나가지 않습니다</p></div>
      </div>
      <div class="lab__panel" id="lab-panel"></div>
    </section>

    <div class="lab-more">
    <details><summary><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/></svg>쓰는 법</summary>
    <ol class="ptext-list">
      <li>사진을 끌어 놓거나 '사진 고르기'로 엽니다. 휴대폰에서는 앨범에서 바로 고를 수 있습니다.</li>
      <li>양식을 고릅니다. 사진을 열면 양식 카드마다 내 사진이 그 양식으로 바뀐 작은 미리보기가 뜹니다.</li>
      <li>'다듬기'의 막대 두세 개와 색 조합으로 느낌을 맞춥니다. 펑크 복사기, 구성주의, 멤피스는 '배치 섞기'를 누를 때마다 조각과 도형이 새 자리로 옮겨 가고, 사이키델릭은 '무늬 섞기'로 휘는 모양이 바뀝니다. 마음에 드는 결과가 나올 때까지 눌러 보세요. 정해진 색 조합이 마음에 안 들면 '직접 고르기'로 색을 하나씩 바꿀 수 있습니다(픽셀 아트는 사진에서 색을 뽑아 쓰므로 제외).</li>
      <li>4:5(피드), 9:16(릴스·스토리), 1:1, 3:4, 16:9, 원본 가운데 비율을 고릅니다.</li>
      <li>더 만져 보고 싶다면 아래의 '더 다듬기'를 펼치세요. 망점 모양과 잉크 수 같은 양식 세부, 밝기·대비·채도, 확대와 위치, 필름 입자·종이 질감·비네팅·테두리, 저장 형식과 크기까지 바꿀 수 있습니다. '무작위'는 뜻밖의 조합을 찾을 때 좋습니다.</li>
      <li>'저장'을 누르면 긴 변 최대 3000픽셀로 저장됩니다. '더 다듬기'의 저장 형식에서 JPG와 인스타그램 크기(짧은 변 1080픽셀)도 고를 수 있습니다.</li>
    </ol>
    </details>
    <details><summary><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/></svg>양식 이야기</summary>
    <div class="lab-styles">
{STYLES}
    </div>
    </details>
    <details><summary><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/></svg>자주 묻는 질문</summary>
    <h3 class="art__h3">사진이 서버로 올라가나요?</h3>
    <p class="ptext">아니요. 모든 처리는 지금 보고 계신 브라우저 안에서 합니다. 사진과 결과물 모두 어디에도 보내지 않고 저장하지도 않습니다. 창을 닫으면 사라집니다.</p>
    <h3 class="art__h3">만든 이미지를 상업적으로 써도 되나요?</h3>
    <p class="ptext">직접 찍은 사진이라면 결과물도 자유롭게 쓰셔도 됩니다. 다른 사람이 찍은 사진이나 인물 사진은 원래의 저작권과 초상권이 그대로 남으니, 쓰기 전에 허락을 받으세요.</p>
    <h3 class="art__h3">휴대폰에서도 되나요?</h3>
    <p class="ptext">됩니다. 미리보기는 가볍게 줄여서 보여 주고, 저장할 때만 큰 크기로 다시 그립니다. 오래된 휴대폰에서는 저장에 몇 초가 걸릴 수 있습니다.</p>
    <h3 class="art__h3">사이트 표시를 빼고 저장할 수 있나요?</h3>
    <p class="ptext">네. 저장 버튼 위의 표시 항목을 끄면 됩니다. 켜 두시면 이 도구를 알리는 데 큰 도움이 됩니다.</p>
    <h3 class="art__h3">원하는 양식이 없어요</h3>
    <p class="ptext">양식은 반응을 보며 하나씩 늘려 갑니다. 써 보고 싶은 양식을 <a href="mailto:nisov0924@gmail.com">nisov0924@gmail.com</a>으로 알려 주세요.</p>
    </details>
    </div>

    <script src="{SITE}js/lab.js" defer></script>
"""

LAB = lab_body()


# ---------- 클로드 스킬 (/skills/) : 스킬 소개와 디자이너가 볼 만한 스킬 ----------
# 설치 수는 skills.sh 에서 확인한 날짜와 함께 적습니다. 고칠 때는 SKILLS_CHECKED 도 같이 바꾸세요.
SKILLS_CHECKED = "2026년 11월 4일"
SKILLS_PICK = [
    # (이름, 만든 곳, 하는 일, 설치 수)
    ("frontend-design", "anthropics/skills", "웹 화면을 만들 때 흔한 템플릿 느낌을 피하고 글꼴·색·여백을 의도를 갖고 고르게 합니다.", "110만"),
    ("canvas-design", "anthropics/skills", "포스터나 그래픽을 PDF·PNG 한 장으로 만듭니다. 먼저 디자인 방향을 글로 정한 뒤 그립니다.", "12.7만"),
    ("pptx", "anthropics/skills", "파워포인트 파일을 만들고 고칩니다.", "24.8만"),
    ("extract-design-system", "arvindrk/extract-design-system", "공개된 웹사이트 주소를 주면 색·글꼴·간격·모서리·그림자 값을 뽑아 토큰 파일로 정리합니다.", "13.1만"),
    ("tailwind-design-system", "wshobson/agents", "테일윈드 v4 기준으로 토큰과 컴포넌트, 다크 모드 구조를 잡습니다.", "7.2만"),
    ("accessibility", "addyosmani/web-quality-skills", "WCAG 2.2 기준으로 대비, 키보드 이동, 대체 텍스트 같은 접근성 문제를 점검합니다.", "6.7만"),
    ("review-animations", "emilkowalski/skills", "화면 전환과 모션 코드를 검토만 합니다. 새 기능을 만들지는 않습니다.", "27.9만"),
    ("remotion-best-practices", "remotion-dev/skills", "리모션(React로 영상을 만드는 도구)으로 영상을 만들 때의 규칙을 담았습니다.", "74.2만"),
    ("figma-use", "figma/mcp-server-guide", "피그마 MCP가 연결돼 있을 때 피그마 파일을 직접 읽고 고칩니다. 피그마가 만든 스킬입니다.", "9,500"),
    ("figma-generate-design", "figma/mcp-server-guide", "디자인 시스템에 올린 컴포넌트를 써서 피그마에 화면을 만듭니다. 이미지가 아니라 고칠 수 있는 레이어로 만듭니다.", "6,200"),
]
SKILLS_ASK = [
    "피그마 시안을 코드로 옮기는 스킬 찾아 줘",
    "이 사이트 주소에서 색이랑 글꼴 값을 뽑아 주는 스킬 있어?",
    "웹 접근성 점검하는 스킬 찾아 줘. 설치 수 1만 이상만",
    "포스터 한 장 만드는 스킬 있어?",
    "발표 자료(PPT) 만드는 스킬 찾아서 설치까지 해 줘",
    "테일윈드로 디자인 시스템 잡는 스킬 후보 3개 비교해 줘",
    "버튼 눌렀을 때 움직임이 어색한지 봐 주는 스킬 있어?",
    "리모션으로 짧은 소개 영상 만드는 스킬 찾아 줘",
]

# 검색·AI 답변용 스킬 (SEO·AEO·GEO). 따로 확인한 날짜를 씁니다.
SEO_CHECKED = "2026년 11월 5일"
SEO_PICK = [
    # (이름, 만든 곳, 하는 일, 설치 수, Snyk 점검)
    ("seo-audit", "coreyhaines31/marketingskills", "색인, 제목·설명 태그, 제목 구조, 내부 링크, 이미지를 차례로 보고 급한 것부터 고칠 목록으로 정리합니다.", "24.6만", "주의"),
    ("ai-seo", "coreyhaines31/marketingskills", "챗GPT, 퍼플렉시티, 구글 AI 개요에 인용되려면 글을 어떻게 쓸지 봅니다. 떼어 가기 좋은 문단, 숫자와 출처 넣기 같은 내용입니다.", "15.8만", "통과"),
    ("seo-geo", "resciencelab/opc-skills", "일반 검색과 AI 검색을 한 번에 봅니다. AI 봇이 사이트에 들어올 수 있는지도 확인합니다.", "5.5만", "주의"),
    ("seo", "addyosmani/web-quality-skills", "라이트하우스 SEO 점검 기준으로 봅니다. 순위 변화는 약속하지 않는다고 스킬 안에 적어 뒀습니다.", "5.4만", "주의"),
    ("seo-aeo-best-practices", "sanity-io/agent-toolkit", "메타 태그, 사이트맵, 구조화 데이터, 추천 스니펫 대비를 원칙 위주로 정리했습니다.", "7,500", "통과"),
]
SEO_ASK = [
    "이 사이트 SEO 점검해 줘. 급한 것부터",
    "챗GPT나 퍼플렉시티가 이 페이지를 출처로 쓰기 좋은지 봐 줘",
    "robots.txt에서 AI 봇을 막고 있는지 확인해 줘",
    "포트폴리오 페이지마다 제목이랑 설명 태그 다시 써 줘",
]


def skills_find_body():
    rows = "".join(
        f'<tr><td><code>{e(n)}</code></td><td>{e(d)}</td><td>{e(o)}</td><td class="nb">{e(c)}</td></tr>'
        for n, o, d, c in SKILLS_PICK)
    asks = "".join(f"<li>{e(q)}</li>" for q in SKILLS_ASK)
    return f"""
    <p class="ptext">스킬은 클로드 코드에게 특정한 일을 하는 방법을 적어 준 설명서입니다. 폴더 하나에 <code>SKILL.md</code> 파일이 들어 있고,
    클로드는 맡은 일이 그 설명과 맞을 때 꺼내 읽고 그대로 따릅니다. 한 번 설치해 두면 같은 부탁을 할 때마다 같은 방식으로 일합니다.</p>
    <p class="ptext">이 사이트도 클로드 코드로 만들고 있고, 디자인 작업에 쓸 만한 스킬을 찾다가 이 글을 정리했습니다.
    설치 수는 {SKILLS_CHECKED}에 <a href="https://skills.sh/" target="_blank" rel="noopener">skills.sh</a>에서 확인한 숫자입니다.</p>

    <h2 class="psub">스킬을 찾아 주는 스킬부터</h2>
    <p class="ptext">공개된 스킬은 수십만 개가 넘어서 직접 검색해 고르는 것부터 일입니다.
    <a href="https://skills.sh/vercel-labs/skills/find-skills" target="_blank" rel="noopener">find-skills</a>는 그 검색을 클로드가 대신 하게 만드는 스킬입니다.
    Next.js를 만든 회사 버셀(Vercel)의 실험용 저장소 vercel-labs에 들어 있고, 무료입니다(MIT).</p>
    <p class="ptext">스킬 안에 적힌 순서는 이렇습니다.</p>
    <ol class="ptext-list">
      <li>무슨 일을 하려는지 파악합니다.</li>
      <li>skills.sh 순위에서 설치 수가 많은 스킬이 있는지 먼저 봅니다.</li>
      <li>없으면 <code>npx skills find 검색어</code>로 찾습니다.</li>
      <li>설치 수 1천 이상, 공식 출처(vercel-labs, anthropics, microsoft 등), 저장소 별 100개 이상인지 확인합니다.</li>
      <li>후보를 이름·설치 수·출처·설치 명령과 함께 보여 줍니다.</li>
      <li>"설치해 줘"라고 하면 설치합니다.</li>
    </ol>

    <h2 class="psub">설치</h2>
    <p class="ptext">터미널에 아래 한 줄을 붙여 넣습니다. Node.js가 설치돼 있어야 합니다.</p>
    <pre class="pcode"><code>npx skills add vercel-labs/skills --skill find-skills -g -a claude-code -y</code></pre>
    <ul class="ptext-list">
      <li><code>-g</code>: 어느 폴더에서 클로드 코드를 열어도 쓰이게 전역으로 설치합니다(<code>~/.claude/skills</code>). 빼면 지금 폴더에만 설치됩니다.</li>
      <li><code>-a claude-code</code>: 클로드 코드에 설치합니다. 코덱스는 <code>-a codex</code>, 커서는 <code>-a cursor</code>입니다.</li>
      <li><code>-y</code>: 확인 질문을 건너뜁니다.</li>
    </ul>
    <p class="ptext">설치한 뒤에는 클로드 코드를 새로 열어야 목록에 나타납니다. 스킬은 세션을 시작할 때 읽기 때문입니다.
    클로드 앱의 채팅 창이 아니라 클로드 코드(터미널·데스크톱 앱의 Code 탭)에서 쓰는 방법입니다.</p>

    <h2 class="psub">이렇게 물어보면 됩니다</h2>
    <p class="ptext">평소 말투로 부탁하면 됩니다. 고르는 기준을 같이 말하면 결과가 더 좁혀집니다.</p>
    <ul class="ptext-list">{asks}</ul>

    <h2 class="psub">디자이너가 볼 만한 스킬 {len(SKILLS_PICK)}개</h2>
    <p class="ptext">디자인 작업과 가까운 것만 골랐습니다. 설치 명령은 <code>npx skills add 만든곳 --skill 이름 -g</code> 꼴입니다.</p>
    <div class="art__tablewrap"><table class="art__table">
      <thead><tr><th>이름</th><th>하는 일</th><th>만든 곳</th><th>설치 수</th></tr></thead>
      <tbody>{rows}</tbody>
    </table></div>
    <p class="art__note">※ 출처: 각 스킬의 skills.sh 페이지, {SKILLS_CHECKED} 확인. 설치 수는 매일 바뀝니다.</p>

    <h2 class="psub">설치 전에 볼 것</h2>
    <p class="ptext">스킬은 클로드에게 주는 지시문이라, 설치하면 클로드가 가진 권한 그대로 그 지시를 따릅니다.
    파일을 지우거나 외부로 보내라고 적혀 있어도 따를 수 있다는 뜻입니다. 그래서 아래를 확인하고 설치합니다.</p>
    <ul class="ptext-list">
      <li>설치 수가 100 아래인 스킬은 특히 조심합니다. 같은 이름을 베낀 저장소가 많습니다.</li>
      <li>만든 곳을 봅니다. 앤트로픽, 피그마, 리모션처럼 도구를 만든 회사가 직접 올린 스킬이 가장 안전합니다.</li>
      <li>설치할 때 나오는 보안 점검(Gen, Socket, Snyk)을 읽습니다. 위험 표시가 있으면 이유를 확인합니다.</li>
      <li>설치한 뒤 <code>SKILL.md</code>를 한 번 열어 봅니다. 긴 글이 아니라 몇 분이면 읽습니다.</li>
    </ul>

    <h2 class="psub">자주 쓰는 명령</h2>
    <ul class="ptext-list">
      <li><code>npx skills list</code>: 설치된 스킬 보기</li>
      <li><code>npx skills update</code>: 설치된 스킬을 최신으로</li>
      <li><code>npx skills remove 이름</code>: 스킬 지우기</li>
      <li><code>npx skills init 이름</code>: 내 스킬 만들기 (자주 하는 작업이 있다면)</li>
    </ul>

    <h2 class="psub">출처</h2>
    <ul class="ptext-list">
      <li><a href="https://skills.sh/vercel-labs/skills/find-skills" target="_blank" rel="noopener">find-skills — skills.sh</a></li>
      <li><a href="https://github.com/vercel-labs/skills" target="_blank" rel="noopener">vercel-labs/skills — GitHub</a></li>
      <li><a href="https://skills.sh/" target="_blank" rel="noopener">skills.sh 스킬 순위</a></li>
    </ul>
"""




def skills_seo_body():
    seo_rows = "".join(
        f'<tr><td><code>{e(n)}</code></td><td>{e(d)}</td><td>{e(o)}</td><td class="nb">{e(c)}</td><td class="nb">{e(k)}</td></tr>'
        for n, o, d, c, k in SEO_PICK)
    seo_asks = "".join(f"<li>{e(q)}</li>" for q in SEO_ASK)
    return f"""
    <p class="ptext">AI로 포트폴리오나 랜딩 페이지를 만드는 건 금방인데, 만든 다음에는 찾아오는 사람이 없습니다.
    구글에 검색해도 안 나오고, 챗GPT에 물어봐도 내 사이트는 답에 없습니다. 요즘은 이 문제를 세 갈래로 나눠 부릅니다.</p>
    <ul class="ptext-list">
      <li><b>SEO</b>: 검색 결과에서 위에 나오게 합니다.</li>
      <li><b>AEO</b>(답변 엔진 최적화): AI 답변이나 구글 AI 개요에 내 문장이 그대로 뽑히게 합니다.</li>
      <li><b>GEO</b>(생성형 엔진 최적화): 챗GPT, 퍼플렉시티 같은 생성형 AI가 내 사이트를 출처로 달게 합니다.</li>
    </ul>
    <p class="ptext">스킬이 처음이라면 <a href="{SITE}skills/find-skills/">1탄</a>에서 스킬이 무엇인지, 어떻게 까는지부터 보고 오면 됩니다.</p>
    <p class="ptext">사이트 폴더에서 클로드 코드를 열고 이런 스킬을 깔아 두면, "검색이랑 AI 답변에 잘 걸리게 봐 줘" 한마디로 고칠 목록이 나옵니다.
    터미널에서 <code>npx skills find seo</code>로 찾으면 아래처럼 설치 수와 함께 나옵니다.</p>
    <figure class="art__fig art__fig--shot">
      <img src="{SITE}assets/skills/find-seo-terminal.webp" width="1440" height="725" loading="lazy" decoding="async"
           alt="터미널에서 npx skills find seo를 실행한 결과. seo-audit 246.6K, ai-seo 158.4K, programmatic-seo 156.3K 같은 스킬이 설치 수와 함께 나온다">
      <figcaption><code>npx skills find seo</code> 결과 앞부분 ({SEO_CHECKED} 실행)</figcaption>
    </figure>
    <p class="ptext">설치 수가 많은 것 가운데 쓰임새가 겹치지 않게 다섯 개를 골랐습니다.</p>
    <div class="art__tablewrap"><table class="art__table">
      <thead><tr><th>이름</th><th>하는 일</th><th>만든 곳</th><th>설치 수</th><th>Snyk</th></tr></thead>
      <tbody>{seo_rows}</tbody>
    </table></div>
    <p class="art__note">※ 출처: 각 스킬의 skills.sh 페이지, {SEO_CHECKED} 확인. 'Snyk'은 skills.sh가 보여 주는 보안 점검 세 가지 중 하나입니다.</p>
    <p class="ptext">하나만 깐다면 설치 수가 가장 많은 <code>seo-audit</code>부터 보면 됩니다. 스킬 페이지 오른쪽에 설치 수, 깃허브 별, 보안 점검 결과가 있습니다.
    seo-audit은 세 점검 중 Snyk이 '주의(WARN)'로 떠 있습니다. 주의가 하나라도 있으면 설치한 뒤 <code>SKILL.md</code>를 열어 무엇을 시키는지 직접 확인하는 편이 좋습니다.</p>
    <figure class="art__fig art__fig--shot">
      <img src="{SITE}assets/skills/seo-audit-skillssh.webp" width="1440" height="1058" loading="lazy" decoding="async"
           alt="skills.sh의 seo-audit 페이지. 설치 246.5K, 깃허브 별 58.5K, 보안 점검은 Gen Agent Trust Hub와 Socket이 PASS, Snyk이 WARN으로 표시돼 있다">
      <figcaption>skills.sh의 seo-audit 페이지 ({SEO_CHECKED} 캡처)</figcaption>
    </figure>
    <pre class="pcode"><code>npx skills add coreyhaines31/marketingskills --skill seo-audit -g</code></pre>
    <p class="ptext">설치한 뒤에는 이렇게 부탁하면 됩니다.</p>
    <ul class="ptext-list">{seo_asks}</ul>
    <p class="ptext">이름에 seo, aeo, geo가 다 들어간 스킬도 많지만 설치 수가 수백 회인 것이 대부분입니다. 이름보다 설치 수와 만든 곳을 먼저 봅니다.
    그리고 어떤 스킬도 순위나 AI 인용을 보장하지는 않습니다. 놓친 기본기를 찾아 주는 점검표에 가깝습니다.</p>

    <p class="ptext">설치 전에 확인할 것과 자주 쓰는 명령은 <a href="{SITE}skills/find-skills/">1탄</a>에 정리해 뒀습니다.</p>

    <h2 class="psub">출처</h2>
    <ul class="ptext-list">
      <li><a href="https://skills.sh/coreyhaines31/marketingskills/seo-audit" target="_blank" rel="noopener">seo-audit — skills.sh</a></li>
      <li><a href="https://skills.sh/coreyhaines31/marketingskills/ai-seo" target="_blank" rel="noopener">ai-seo — skills.sh</a></li>
      <li><a href="https://skills.sh/resciencelab/opc-skills/seo-geo" target="_blank" rel="noopener">seo-geo — skills.sh</a></li>
      <li><a href="https://skills.sh/addyosmani/web-quality-skills/seo" target="_blank" rel="noopener">seo — skills.sh</a></li>
      <li><a href="https://skills.sh/sanity-io/agent-toolkit/seo-aeo-best-practices" target="_blank" rel="noopener">seo-aeo-best-practices — skills.sh</a></li>
    </ul>
"""


# hallmark (3탄). 저장소의 SKILL.md, references/gates.md, scripts/ 를 읽고 정리했습니다.
HM_CHECKED = "2026년 11월 7일"
HM_FLOOR = [
    "색과 글꼴은 모두 맨 위에 선언한 토큰으로만 씁니다. 중간에 색 코드를 직접 쓰지 않습니다.",
    "<code>transition: all</code>을 쓰지 않고, 너비·높이·위치를 움직이는 애니메이션도 쓰지 않습니다.",
    "제목 안에서 한 단어만 기울이지 않습니다.",
    "제목 위에 붙는 작은 라벨(아이브로우)을 쓰지 않고, 라벨을 자간 넓힌 대문자로 쓰지 않습니다.",
    "가운뎃점으로 이은 메타 줄, 링크 글자 끝에 붙인 화살표, 장식용 상태 점을 쓰지 않습니다.",
    "보라에서 파랑으로 가는 그라데이션, 카드 안의 카드, 아이콘 대신 쓴 이모지, 손으로 그린 브라우저 창을 쓰지 않습니다.",
    "숫자, 후기, 로고, 사례 수를 지어내지 않습니다.",
    "첫 화면(1280×800)에서 스크롤 없이 제목, 한 문장, 주요 버튼이 다 보여야 합니다.",
    "한 화면에 들어가는 글은 80단어 안팎까지입니다.",
    "모든 버튼과 링크에 키보드 포커스 표시가 있고, 움직임을 줄이는 설정을 켠 사람에게는 애니메이션을 끕니다.",
]
HM_STEPS = [
    ("미리 읽기", "묻기 전에 프로젝트부터 봅니다. <code>design.md</code>가 있으면 그게 모든 규칙보다 앞서고, 없으면 쓰던 글꼴, 색, 간격, 프레임워크를 읽어 둡니다."),
    ("한 번만 묻기", "보여 줄 재료(스크린샷, 사진, 실제 숫자), 누구를 위한 페이지인지, 페이지가 이끌어야 할 행동 하나, 톤을 한 메시지로 묻습니다. '깔끔하고 모던하게'는 톤이 아니라고 적혀 있고, 그냥 진행하라고 하면 알아서 정한 뒤 무엇을 골랐는지 알려 줍니다."),
    ("모양 잡기", "방문자가 와서 할 일(예약, 구매, 구독)을 먼저 정하고, 같은 업종의 실제 사이트가 그 버튼을 어디에 두는지에 맞춰 섹션을 짭니다. 페이지 구성은 21가지 틀 중에서 고릅니다."),
    ("방향 뽑기", "테마 50개 중 프롬프트에 맞는 3개를 뽑고 하나를 고릅니다. 지난 작업 기록(<code>.hallmark/log.json</code>)과 겹치는 조합은 피해서, 같은 부탁을 두 번 해도 다른 페이지가 나오게 합니다."),
    ("선택 정리", "모양, 테마, 첫 화면 구성, 기억에 남길 한 가지, 있는 재료와 없는 재료를 한 블록으로 보여 줍니다. 방향을 바꿀 마지막 기회입니다."),
    ("첫 화면부터", "메뉴와 첫 화면만 먼저 만들고 바로 검사합니다. 제목은 일곱 단어 이하, 문장 하나, 버튼 한두 개. 여기를 통과해야 아래 섹션을 만듭니다."),
    ("검사", "sloplint로 다시 검사하고, 작업 내용을 모르는 새 에이전트가 화면을 보고 판정합니다. 열린 실패가 하나라도 있으면 넘기지 않습니다."),
]


def skills_hallmark_body():
    floor = "".join(f"<li>{x}</li>" for x in HM_FLOOR)
    steps = "".join(f"<li><b>{e(a)}</b>: {b}</li>" for a, b in HM_STEPS)
    return f"""
    <p class="ptext"><a href="{SITE}skills/find-skills/">1탄</a>에서 스킬 까는 법을, <a href="{SITE}skills/seo/">2탄</a>에서 검색 점검 스킬을 다뤘습니다.
    이번에는 AI가 만든 화면에서 나는 '어디서 본 것 같은' 티를 막는 디자인 스킬입니다.</p>
    <p class="ptext"><a href="https://github.com/Nutlope/hallmark" target="_blank" rel="noopener">hallmark</a>는 AI 회사 투게더 AI(Together AI)가 만들어 무료(MIT)로 푼 스킬입니다.
    클로드 코드, 코덱스, 커서, 오픈코드에서 쓸 수 있습니다. {HM_CHECKED} 기준으로 깃허브 주간 트렌딩 5위에 올라 있었고, 그 주에만 별을 6,900개 받았습니다.</p>
    <figure class="art__fig art__fig--shot">
      <img src="{SITE}assets/skills/hallmark-trending.webp" width="1440" height="906" loading="lazy" decoding="async"
           alt="깃허브 주간 트렌딩 목록. Nutlope/hallmark가 worktrunk와 anthropics/skills 사이에 있고, 전체 별 49,675개, 이번 주 별 6,900개로 표시돼 있다">
      <figcaption>깃허브 주간 트렌딩 ({HM_CHECKED} 캡처). 테두리 친 줄이 hallmark</figcaption>
    </figure>

    <h2 class="psub">규칙을 세 단계로 나눈다</h2>
    <p class="ptext">스킬 안에는 AI가 습관처럼 내놓는 모양을 하나하나 번호를 붙여 적은 목록이 있고, 규칙마다 얼마나 엄격한지가 정해져 있습니다.</p>
    <ul class="ptext-list">
      <li><b>바닥</b>(Floor): 어떤 이유로도 넘어갈 수 없습니다. 명도 대비, 키보드 포커스, 휴대폰에서 깨지는 레이아웃, 지어낸 숫자 같은 것들입니다.</li>
      <li><b>습관</b>(Reflex): 모델이 기본값으로 빠지기 쉬운 모양입니다. 이 페이지에서 그렇게 해야 하는 이유를 적으면 넘어갈 수 있습니다.</li>
      <li><b>마감</b>(Finish): 멀리서는 안 보이는 디테일입니다. 알려 주기만 하고 막지는 않습니다.</li>
    </ul>

    <h2 class="psub">절대 못 넘기는 바닥 규칙</h2>
    <p class="ptext">SKILL.md 맨 앞에 16개가 적혀 있습니다. 디자이너 눈으로 볼 만한 것만 추렸습니다.</p>
    <ul class="ptext-list">{floor}</ul>
    <p class="ptext">라벨, 가운뎃점, 화살표는 원래 습관 정도로 볼 만한 것들인데 hallmark는 이걸 '집 규칙'이라 부르며 바닥으로 올려 뒀습니다.
    너무 확실하게 기계가 만든 티가 나서 다른 곳보다 엄격하게 본다는 설명입니다.</p>

    <h2 class="psub">돌아가는 순서</h2>
    <p class="ptext">클로드 코드에서 <code>/hallmark 랜딩 페이지 만들어 줘</code>처럼 부르면 아래 순서로 일합니다.</p>
    <ol class="ptext-list">{steps}</ol>

    <h2 class="psub">검사는 진짜 브라우저로 한다</h2>
    <p class="ptext">함께 들어 있는 <code>sloplint</code>는 만든 페이지를 크롬에 띄워 화면 폭 여덟 가지(320, 375, 414, 768, 1024, 1280, 1440, 1920)로 재 봅니다.
    가로 스크롤이 생기는지, 첫 화면에 제목과 버튼이 다 들어오는지, 한 화면에 글이 너무 많은지 같은 것을 숫자로 판정하고, 결과를 실패, 습관, 경고로 나눠 보여 줍니다.</p>
    <p class="ptext">그다음은 사람이 아니라 다른 에이전트가 봅니다. 페이지를 만든 대화 내용을 넘기지 않은 새 에이전트에게 스크린샷과 코드만 주고,
    첫 단어로 다시 찍기, 다시 만들기, 고치기, 내보내기 중 하나를 고르게 합니다. 만든 쪽이 자기 작업을 가장 너그럽게 본다는 이유에서입니다.</p>

    <h2 class="psub">습관 규칙은 이유를 적으면 넘어간다</h2>
    <p class="ptext">예외를 둘 때는 CSS 맨 위 주석에 규칙 번호, 근거, 이유를 적습니다. 이유가 너무 짧거나 다른 데서 복사한 문장이면 받아 주지 않고,
    같은 규칙을 세 번 연속 예외로 두면 예외가 아니라 그 브랜드의 스타일이니 <code>design.md</code>에 적으라고 합니다.</p>
    <p class="ptext">재미있는 건 hallmark 공식 사이트입니다. 크림색 바탕에 굵은 세리프 제목, 주황 포인트를 썼는데, 이 조합은 스킬 안에서 습관 규칙 65번 '이름 붙은 그 모양'으로 따로 적혀 있습니다.
    습관 규칙이니 이유가 있으면 써도 된다는 뜻이고, 금지 목록이라기보다 '알고 고르라'는 쪽에 가깝다는 걸 사이트가 직접 보여 줍니다.</p>
    <figure class="art__fig art__fig--shot">
      <img src="{SITE}assets/skills/hallmark-site.webp" width="1440" height="900" loading="lazy" decoding="async"
           alt="hallmark 공식 사이트 첫 화면. 크림색 바탕에 'The design skill that ends AI slop.'이라는 큰 세리프 제목과 설치 명령, 테마로 만든 페이지 예시들이 놓여 있다">
      <figcaption>usehallmark.com 첫 화면 ({HM_CHECKED} 캡처)</figcaption>
    </figure>

    <h2 class="psub">설치와 쓰는 법</h2>
    <pre class="pcode"><code>npx skills add nutlope/hallmark -g --agent claude-code</code></pre>
    <ul class="ptext-list">
      <li><code>/hallmark 만들 페이지 설명</code>: 새 페이지를 만듭니다. 테마 없이 프롬프트만으로 만들고 싶으면 '커스텀으로'라고 덧붙입니다.</li>
      <li><code>/hallmark redesign 경로</code>: 내용과 연결은 두고 디자인만 새로 만듭니다.</li>
      <li><code>/hallmark audit 경로</code>: 고치지 않고 점검 결과만 받습니다. 이미 만든 사이트라면 이것부터 해 보면 됩니다.</li>
    </ul>
    <p class="ptext">Node 18 이상이 필요하고, 브라우저 검사까지 하려면 크롬과 <code>puppeteer-core</code>가 있어야 합니다(<code>npm i -g puppeteer-core</code>). 없으면 코드만 보는 검사가 돕니다.
    이미 있는 디자인은 hallmark라고 이름을 불러야만 손댄다고 적혀 있어서, 설치해 둔다고 기존 작업이 갑자기 바뀌지는 않습니다.</p>

    <h2 class="psub">깔기 전에 볼 것</h2>
    <p class="ptext">skills.sh 설치 수는 {HM_CHECKED} 기준 9.4만 회입니다. 보안 점검 세 가지 중 Socket과 Snyk은 통과, Gen Agent Trust Hub는 '주의(WARN)'입니다.
    스크립트를 여럿 실행하는 스킬이라 그런 것으로 보이지만, 이유가 따로 적혀 있지는 않으니 <code>SKILL.md</code>와 <code>scripts</code> 폴더를 한 번 열어 보고 까는 편이 좋습니다.</p>
    <figure class="art__fig art__fig--shot">
      <img src="{SITE}assets/skills/hallmark-skillssh.webp" width="1440" height="997" loading="lazy" decoding="async"
           alt="skills.sh의 hallmark 페이지. 설치 94.5K, 깃허브 별 48.9K, 보안 점검은 Gen Agent Trust Hub WARN, Socket과 Snyk PASS로 표시돼 있다">
      <figcaption>skills.sh의 hallmark 페이지 ({HM_CHECKED} 캡처)</figcaption>
    </figure>
    <ul class="ptext-list">
      <li>파일을 저장할 때마다 자동으로 검사하는 훅은 기본 설치에 들어 있지 않습니다. 따로 <code>install-hook.mjs</code>를 실행해야 <code>.claude/settings.json</code>에 추가되고, 막지는 않고 조언만 합니다.</li>
      <li><code>TOGETHER_API_KEY</code>가 설정돼 있으면 코드를 짜기 전에 첫 화면 시안 이미지를 투게더 AI로 두세 장 생성해 봅니다. 키가 없으면 이 단계는 건너뜁니다.</li>
      <li>사진이 없으면 위키미디어 공용의 공개 라이선스 사진 755장 중에서 골라 넣고, 페이지 아래에 출처를 답니다. 나중에 내 사진으로 바꾸라는 자리 표시입니다.</li>
    </ul>
    <p class="ptext">설치 수 확인과 자주 쓰는 명령은 <a href="{SITE}skills/find-skills/">1탄</a>에 정리해 뒀습니다.</p>

    <h2 class="psub">출처</h2>
    <ul class="ptext-list">
      <li><a href="https://github.com/Nutlope/hallmark" target="_blank" rel="noopener">Nutlope/hallmark — GitHub</a> (SKILL.md, references/gates.md, scripts/)</li>
      <li><a href="https://skills.sh/nutlope/hallmark/hallmark" target="_blank" rel="noopener">hallmark — skills.sh</a></li>
      <li><a href="https://www.usehallmark.com" target="_blank" rel="noopener">usehallmark.com</a></li>
      <li><a href="https://github.com/trending?since=weekly" target="_blank" rel="noopener">GitHub 주간 트렌딩</a></li>
    </ul>
"""


# 클로드 스킬은 한 편씩 따로 봅니다 (/skills/ 는 목록, /skills/<slug>/ 가 글). 최신 글이 앞.
SKILL_POSTS = [
    {"slug": "hallmark", "no": 3, "date": "2026-11-07",
     "title": "AI 티 나는 디자인을 막는 스킬 hallmark, 어떻게 돌아가나",
     "desc": "깃허브 트렌딩에 오른 디자인 스킬 hallmark가 AI 화면의 습관을 어떤 규칙으로 막고, 어떤 순서로 만들고 검사하는지 저장소 원문을 읽고 정리했습니다.",
     "body": skills_hallmark_body()},
    {"slug": "seo", "no": 2, "date": "2026-11-05",
     "title": "SEO·AEO·GEO 스킬 5개, 검색과 AI 답변에 잡히는 사이트 만들기",
     "desc": "AI로 만든 사이트가 구글에도, 챗GPT 답변에도 안 나올 때 클로드 코드에 깔아 둘 스킬 5개를 설치 수와 보안 점검 결과와 함께 정리했습니다.",
     "body": skills_seo_body()},
    {"slug": "find-skills", "no": 1, "date": "2026-11-04",
     "title": "스킬을 찾아 주는 스킬 find-skills, 디자이너가 볼 만한 스킬 10개",
     "desc": "클로드 코드에 스킬을 설치하는 법과, 스킬 검색을 클로드에 맡기는 find-skills, 디자인 작업에 가까운 스킬 10개를 설치 수와 함께 정리했습니다.",
     "body": skills_find_body()},
]


def skills_index():
    rows = "\n".join(
        f'        <a class="arow" href="{SITE}skills/{x["slug"]}/">\n'
        f'          <span class="arow__date">{x["date"].replace("-", ". ")}</span>\n'
        f'          <span class="arow__main">\n'
        f'            <span class="arow__title">{e(x["title"])}</span>\n'
        f'            <p class="arow__desc">{e(x["desc"])}</p>\n'
        f'          </span>\n'
        f'          <span class="arow__tag">{x["no"]}탄</span>\n'
        f'        </a>' for x in SKILL_POSTS)
    return f"""
      <div class="list list--insight">
{rows}
      </div>
    <script>if (location.hash === "#seo") location.replace("{SITE}skills/seo/");</script>
"""


SKILLS = skills_index()

PROSE_PAGES = [
    ("talk", "디자인 잡담",
     "디자인 이야기를 편하게 나누는 공간입니다.", TALK),
    ("about", "디자인 허브 소개",
     "왜 만들었고 무엇이 들어 있는지, 사이트는 어떤 기준으로 고르는지 적어 뒀습니다.", ABOUT),
    ("lab", "스타일 현상소",
     "내 사진을 리소그래프, 팝아트, 픽셀 아트, 펑크 복사기, 구성주의, 사이버펑크, 바포웨이브, 사이키델릭, 멤피스로 바꿔 보는 무료 도구입니다. 가입이 필요 없고 사진은 기기 밖으로 나가지 않습니다.", LAB),
    ("skills", "클로드 스킬",
     "클로드 코드에 넣어 쓰는 스킬을 주제별로 한 편씩 정리합니다. 스킬 설치법과 find-skills(1탄), 검색과 AI 답변에 잡히게 하는 SEO·AEO·GEO 스킬(2탄), AI 티 나는 디자인을 막는 hallmark(3탄).", SKILLS),
    ("updates", "업데이트 기록",
     "디자인 허브에 사이트를 넣고, 옮기고, 고친 기록입니다. 날짜별로 자동으로 정리합니다.", UPDATES),
    ("privacy", "개인정보처리방침",
     "디자인 허브의 개인정보 처리방침입니다. 수집 항목, 쿠키 사용, 외부 서비스, 광고에 대해 안내합니다.", PRIVACY),
]
for slug, title, intro, body in PROSE_PAGES:
    pages.append((slug, title, intro, body, 0, [], title))

# ---------- 페이지 파일 쓰기 ----------
# 제목 오른쪽의 짧은 설명. 메인 화면에서 같은 화면을 볼 때와 똑같은 문구를 씁니다.
SHORT_DESC = {PAGE_META[c["id"]][0]: c.get("desc", "") for c in cats if c["id"] in PAGE_META}
SHORT_DESC.update({
    "styles": "유명 그래픽 디자인 양식과 흐름",
    "trends": "2026 공식 리포트와 지속 흐름 · 11월 4일 확인",
    "glossary": "디자인 · 편집/인쇄 · UI/UX 구축 시 자주 쓰는 용어",
    "talk": "디자인 이야기를 편하게 나누는 공간",
    "updates": "사이트를 넣고 옮기고 고친 날짜별 기록",
    "lab": "사진을 디자인 양식으로 바꾸는 도구",
    "skills": "클로드 코드에 일하는 방법을 더하는 설명서",
})
FOOTER = footer_links()
# 개수를 브라우저에서 채우는 페이지 (디자인 잡담의 글 수는 서버에서 받아 옵니다)
COUNT_BY_JS = {"talk"}
# 디자인 잡담은 영문판(/en/talk/)과 짝입니다
TALK_ALT = {"ko": f"{SITE}talk/", "en": f"{SITE}en/talk/"}
nav_all = "".join(
    f'<a href="{SITE}{s}/">{e(t)}</a>' for s, t, *_ in pages
)

for slug, title, intro, body, n, names, navlabel in pages:
    url = f"{SITE}{slug}/"
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
    # 제목 틀은 메인 화면과 같게: 제목 · 개수 · 오른쪽 짧은 설명 · 검은 줄.
    # 목록 페이지는 검색으로 들어온 사람을 위해 긴 소개를 한 줄 더 둡니다.
    intro_html = f'      <p class="page__intro">{e(intro)}</p>\n' if n else ""
    if slug == "jobs":   # 매주 모으는 채용 공고 (tools/build-jobs.py)
        intro_html += (f'      <p class="ptext"><a href="{SITE}jobs/weekly/">이번 주 디자이너 채용 공고 보기</a> '
                       '국내·해외 원격 공고를 매주 월요일 모아 둡니다.</p>\n')
    body_full = f"""    <section class="section">
{section_head(navlabel, n or ("" if slug in COUNT_BY_JS else None), SHORT_DESC.get(slug, ""))}
{intro_html}{body}
    </section>{related_articles(slug)}"""
    doc = document(title=title, desc=intro, url=url, body=body_full, jsonld=jsonld,
                   menu=menu(slug), footer_nav=FOOTER,
                   alternates=TALK_ALT if slug == "talk" else None,
                   # 디자인 잡담은 글이 쌓일 때까지 검색 결과에 내보내지 않습니다 (2026-10-26)
                   **({"robots": "noindex, follow"} if slug == "talk" else {}))
    d = ROOT / slug
    d.mkdir(exist_ok=True)
    (d / "index.html").write_text(doc, encoding="utf-8")

# ---------- 클로드 스킬 글 (/skills/<slug>/) ----------
# 목록(/skills/)은 위 PROSE_PAGES 가 만들고, 글은 읽을거리 글과 같은 틀로 한 편씩 씁니다.
SK_LIST = f"{SITE}skills/"
for i, x in enumerate(SKILL_POSTS):
    url = f"{SK_LIST}{x['slug']}/"
    y, m, d = (int(v) for v in x["date"].split("-"))
    newer = SKILL_POSTS[i - 1] if i > 0 else None
    older = SKILL_POSTS[i + 1] if i + 1 < len(SKILL_POSTS) else None
    cell = lambda o, label, cls: (f'<a class="art__pn-a {cls}" href="{SK_LIST}{o["slug"]}/" rel="{"prev" if cls == "is-prev" else "next"}">'
                                  f'<span class="art__pn-l">{label}</span><span class="art__pn-t">{o["no"]}탄 · {e(o["title"])}</span></a>'
                                  if o else '<span></span>')
    pn = f'      <nav class="art__pn">{cell(older, "← 이전 글", "is-prev")}{cell(newer, "다음 글 →", "is-next")}</nav>\n'
    body = f"""    <article class="art">
      <p class="art__kicker"><a href="{SK_LIST}">클로드 스킬</a> · {x["no"]}탄</p>
      <h1 class="page__title">{e(x["title"])}</h1>
      <p class="page__intro">{e(x["desc"])}</p>
      <p class="art__meta"><time datetime="{x["date"]}">{y}년 {m}월 {d}일</time></p>
{x["body"]}
    </article>
    <section class="section">
{pn}      <p class="art__all"><a href="{SK_LIST}">클로드 스킬 전체 {len(SKILL_POSTS)}편</a></p>
    </section>"""
    jsonld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Article", "headline": x["title"], "description": x["desc"], "url": url,
         "datePublished": x["date"], "dateModified": x["date"], "inLanguage": "ko",
         "author": {"@type": "Organization", "name": "디자인 허브", "url": SITE},
         "publisher": {"@type": "Organization", "name": "디자인 허브", "url": SITE}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "디자인 허브", "item": SITE},
            {"@type": "ListItem", "position": 2, "name": "클로드 스킬", "item": SK_LIST},
            {"@type": "ListItem", "position": 3, "name": x["title"], "item": url}]},
    ]}
    doc = document(title=x["title"], desc=x["desc"], url=url, body=body, jsonld=jsonld, og_type="article",
                   main_class="page__main page__main--art", menu=menu("skills"), footer_nav=FOOTER)
    out = ROOT / "skills" / x["slug"]
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(doc, encoding="utf-8")

# ---------- 404 (없는 주소) ----------
# GitHub Pages 는 없는 주소로 오면 /404.html 을 보여 줍니다. 한국어·영어를 같이 적고, 갈 곳을 안내합니다.
posts_404 = A.load()[:3]
rows_404 = "".join(f'<li><a href="{SITE}articles/{x["slug"]}/">{e(x["title"])}</a></li>' for x in posts_404)
body_404 = f"""    <section class="section">
{section_head("페이지를 찾을 수 없습니다", None, "Page not found")}
      <p class="ptext">주소가 바뀌었거나 없어진 페이지입니다. 아래에서 찾던 것을 다시 찾아보세요.</p>
      <form class="notfound__search" action="{SITE}" method="get" role="search">
        <input class="search__input" type="search" name="q" placeholder="사이트 검색 / Search sites" aria-label="검색" />
      </form>
      <div class="page__navlinks" style="margin-top:20px">
        <a href="{SITE}">디자인 허브 첫 화면</a><a href="{SITE}articles/">읽을거리</a><a href="{SITE}talk/">디자인 잡담</a>
        <a href="{SITE}en/" hreflang="en" lang="en">English</a>
      </div>
      <h2 class="psub">최근 읽을거리</h2>
      <ul class="ptext-list">{rows_404}</ul>
    </section>"""
doc = document(title="페이지를 찾을 수 없습니다", desc="찾는 페이지가 없습니다.", url=SITE + "404.html", body=body_404,
               jsonld={"@context": "https://schema.org", "@type": "WebPage", "name": "404"},
               menu=menu("404"), footer_nav=FOOTER, robots="noindex, follow")
(ROOT / "404.html").write_text(doc, encoding="utf-8")

# ---------- 영문 디자인 잡담 (/en/talk/) ----------
# 게시판은 한국어판과 하나를 같이 씁니다. 화면 문구는 js/talk.js 가 <html lang> 을 보고 바꿉니다.
TALK_EN_URL = TALK_ALT["en"]
TALK_EN_DESC = "A place to talk about design. Share what you're working on, the tools you use, or where you're stuck."
talk_en_body = f"""    <section class="section">
{section_head("Design Talk", "", "Talk about design, in Korean or English")}

    <div id="talk"></div>

    <p class="ptext ptext--note">Your name and post are shown publicly. Please don't include contact details or other personal information.
    Ads, abuse and posts containing other people's personal information are removed.
    This board is shared with the Korean site, so you'll see posts in Korean too.</p>

    <script src="{SITE}js/talk.js" defer></script>
    </section>"""
talk_en_jsonld = {
    "@context": "https://schema.org", "@type": "CollectionPage", "url": TALK_EN_URL, "name": "Design Talk",
    "description": TALK_EN_DESC, "inLanguage": "en",
    "isPartOf": {"@type": "WebSite", "url": SITE + "en/", "name": "Design Hub"},
}
doc = document(title="Design Talk", desc=TALK_EN_DESC, url=TALK_EN_URL, body=talk_en_body, jsonld=talk_en_jsonld,
               menu=menu("talk", "en"), footer_nav=footer_links("en"), lang="en", alternates=TALK_ALT,
               robots="noindex, follow")
(ROOT / "en" / "talk").mkdir(parents=True, exist_ok=True)
(ROOT / "en" / "talk" / "index.html").write_text(doc, encoding="utf-8")

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
         + f'<a href="{SITE}articles/">읽을거리</a>' + _group(INSIGHT)
         + f'<a href="{SITE}updates/">업데이트 기록</a>' + '</div>')
# 첫 화면 소개와 최근 글. 자바스크립트 없이도 보이게 index.html 에 직접 적습니다 (영문판은 build-en.py)
_posts = A.load()[:3]
_intro = (f'        <p class="hero__intro">디자이너가 실제로 자주 여는 사이트 {len(sites)}곳을 분야별로 모았습니다. '
          '설명은 직접 쓰고, 분야마다 고르는 법을 적어 두었습니다. '
          f'스타일 사전과 용어 사전, 읽을거리도 함께 냅니다.</p>\n'
          '        <ul class="hero__posts" aria-label="최근 읽을거리">'
          + "".join(f'<li><a href="{SITE}articles/{x["slug"]}/">{e(x["title"])}</a></li>' for x in _posts)
          + '</ul>')
doc = re.sub(r"<!-- HOME:INTRO -->.*?<!-- /HOME:INTRO -->",
             lambda m: f"<!-- HOME:INTRO -->\n{_intro}\n        <!-- /HOME:INTRO -->", doc, flags=re.S)
pat = re.compile(r"<!-- SEO:PAGELINKS -->.*?<!-- /SEO:PAGELINKS -->", re.S)
if pat.search(doc):
    doc = pat.sub(f'<!-- SEO:PAGELINKS -->\n      <nav class="footer__nav">{links}</nav>\n      <!-- /SEO:PAGELINKS -->', doc)
p.write_text(doc, encoding="utf-8")

print(f"페이지 {len(pages)}개 생성: " + ", ".join(f"/{s}/" for s, *_ in pages))
