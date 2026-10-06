#!/usr/bin/env python3
"""
읽을거리에 넣는 도식(SVG)을 만듭니다. 막대 차트는 charts.py, 그 밖의 그림은 여기서.

  python3 tools/figures.py

- 넓은 화면용(articles/img/<이름>.svg)과 폰용(<이름>-m.svg)을 같이 만듭니다.
- 한국어판과 영문판(<이름>-en)을 같은 틀에서 문구만 바꿔 만듭니다.
- 색은 사이트와 같은 흑백. 강조는 굵기와 채움으로만 합니다.
"""
import html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "articles" / "img"
e = html.escape

INK, BODY, MUTED, RULE, SOFT, BG = "#111111", "#444444", "#6B6B6B", "#D9D9D9", "#F2F2F2", "#FFFFFF"
FONT = "Pretendard, 'Apple SD Gothic Neo', 'Malgun Gothic', 'Noto Sans KR', sans-serif"


def wrap(W, H, title, desc, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">\n'
            f'  <title id="t">{e(title)}</title>\n  <desc id="d">{e(desc)}</desc>\n'
            f'  <rect width="{W}" height="{H}" rx="20" fill="{BG}"/>\n'
            f'  <g font-family="{FONT}">\n    ' + "\n    ".join(body) + "\n  </g>\n</svg>\n")


def text(x, y, s, size, fill=INK, weight=400, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}">{e(s)}</text>')


# =========================================================
# 1. 오픈AI 앱 플랫폼 타임라인 (2026-09-30 데브데이 글)
# =========================================================
TIMELINE = {
    "ko": {
        "title": "챗GPT 앱 플랫폼, 3년 동안 네 번",
        "sub": "시작한 때부터 닫은(닫을) 때까지",
        "rows": [
            ("플러그인", "2023. 3 → 2024. 4 종료", 2023 + 2 / 12, 2024 + 3 / 12, "end"),
            ("GPTs · GPT 스토어", "2023. 11 → 2026. 12. 11 종료 예정", 2023 + 10 / 12, 2026 + 11.35 / 12, "planned"),
            ("Apps SDK", "2025. 10 →", 2025 + 9 / 12, None, "live"),
            ("플러그인 익스텐션", "2026. 9 새로", 2026 + 8.95 / 12, None, "new"),
        ],
        "now": "지금",
        "legend": ["운영 중", "종료", "종료 예정"],
        "source": "출처: OpenAI 발표, antihype.com.br 정리 (2026. 9. 30 기준)",
        "desc": "플러그인은 2023년 3월에 시작해 2024년 4월에 닫았다. GPTs와 GPT 스토어는 2023년 11월에 시작해 2026년 12월 11일에 닫는다. "
                "Apps SDK는 2025년 10월, 플러그인 익스텐션은 2026년 9월에 나왔다.",
    },
    "en": {
        "title": "ChatGPT's app platforms: four tries in three years",
        "sub": "From launch to shutdown (or planned shutdown)",
        "rows": [
            ("Plugins", "Mar 2023 → shut down Apr 2024", 2023 + 2 / 12, 2024 + 3 / 12, "end"),
            ("GPTs & GPT Store", "Nov 2023 → closing Dec 11, 2026", 2023 + 10 / 12, 2026 + 11.35 / 12, "planned"),
            ("Apps SDK", "Oct 2025 →", 2025 + 9 / 12, None, "live"),
            ("Plugin extensions", "Sep 2026, new", 2026 + 8.95 / 12, None, "new"),
        ],
        "now": "Now",
        "legend": ["Active", "Shut down", "Closing"],
        "source": "Sources: OpenAI announcements, antihype.com.br (as of Sep 30, 2026)",
        "desc": "Plugins launched in March 2023 and shut down in April 2024. GPTs and the GPT Store launched in November 2023 and close on "
                "December 11, 2026. The Apps SDK arrived in October 2025, and plugin extensions in September 2026.",
    },
}


def timeline(lang, wide):
    t = TIMELINE[lang]
    if wide:
        W, pad, ts, ss, ls, ds, rowh, bh, labw = 1200, 40, 30, 19, 20, 16, 74, 20, 250
    else:
        W, pad, ts, ss, ls, ds, rowh, bh, labw = 600, 32, 34, 21, 24, 19, 112, 22, 0
    x0, x1 = pad + labw, W - pad - (10 if wide else 0)
    y0, y1 = 2023.0, 2027.0
    now = 2026 + 8.97 / 12
    X = lambda v: x0 + (x1 - x0) * (v - y0) / (y1 - y0)
    out, y = [], pad + ts
    out.append(text(pad, y, t["title"], ts, weight=800))
    y += ss + 12
    out.append(text(pad, y, t["sub"], ss, MUTED))
    y += 46
    # 연도 눈금
    axis_y = y
    for yr in range(2023, 2028):
        out.append(f'<line x1="{X(yr)}" y1="{axis_y + 10}" x2="{X(yr)}" y2="{axis_y + 14 + rowh * 4}" stroke="{RULE}" stroke-width="1"/>')
        out.append(text(X(yr), axis_y, str(yr), ds, MUTED, anchor="middle" if pad < X(yr) < W - pad else ("end" if yr == 2027 else "start")))
    y = axis_y + 24
    for name, when, a, b, kind in t["rows"]:
        if wide:
            ly = y + rowh / 2
            out.append(text(pad, ly - 2, name, ls, weight=700))
            out.append(text(pad, ly + ds + 4, when, ds, MUTED))
            by = ly - bh / 2 - 4
        else:
            out.append(text(pad, y + ls, name, ls, weight=700))
            out.append(text(pad, y + ls + ds + 10, when, ds, MUTED))
            by = y + ls + ds + 26
        end = b if b else now
        xa, xb = X(a), max(X(end), X(a) + bh)
        if kind == "end":
            out.append(f'<rect x="{xa}" y="{by}" width="{xb - xa}" height="{bh}" rx="{bh / 2}" fill="none" stroke="{INK}" stroke-width="2"/>')
        elif kind == "planned":
            xn = X(now)
            out.append(f'<rect x="{xa}" y="{by}" width="{xn - xa}" height="{bh}" rx="{bh / 2}" fill="{INK}"/>')
            out.append(f'<rect x="{xn - bh / 2}" y="{by}" width="{xb - xn + bh / 2}" height="{bh}" rx="{bh / 2}" fill="none" '
                       f'stroke="{INK}" stroke-width="2" stroke-dasharray="5 4"/>')
            out.append(f'<rect x="{xa}" y="{by}" width="{xn - xa}" height="{bh}" rx="{bh / 2}" fill="{INK}"/>')
        else:
            out.append(f'<rect x="{xa}" y="{by}" width="{xb - xa}" height="{bh}" rx="{bh / 2}" fill="{INK}"/>')
        y += rowh
    # 지금 표시
    xn = X(now)
    out.append(f'<line x1="{xn}" y1="{axis_y + 10}" x2="{xn}" y2="{y + 4}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="3 4"/>')
    out.append(text(xn, y + 4 + ds + 6, t["now"], ds, INK, 700, "middle"))
    y += ds + 40
    # 범례
    lx = pad
    for k, label in enumerate(t["legend"]):
        if k == 0:
            sw = f'<rect x="{lx}" y="{y - 13}" width="34" height="16" rx="8" fill="{INK}"/>'
        elif k == 1:
            sw = f'<rect x="{lx + 1}" y="{y - 12}" width="32" height="14" rx="7" fill="none" stroke="{INK}" stroke-width="2"/>'
        else:
            sw = f'<rect x="{lx + 1}" y="{y - 12}" width="32" height="14" rx="7" fill="none" stroke="{INK}" stroke-width="2" stroke-dasharray="5 4"/>'
        out.append(sw)
        out.append(text(lx + 44, y, label, ds, BODY))
        lx += 44 + len(label) * ds * (0.62 if lang == "en" else 1.0) + 34
    y += 36
    out.append(f'<line x1="{pad}" y1="{y - 14}" x2="{W - pad}" y2="{y - 14}" stroke="{RULE}" stroke-width="1"/>')
    y += 10
    out.append(text(pad, y, t["source"], ds - 1 if not wide else ds, MUTED))
    return wrap(W, round(y + pad), t["title"], t["desc"], out)


# =========================================================
# 2. 챗GPT 안의 플러그인 익스텐션 구조도 (2026-09-30 데브데이 글)
# =========================================================
SCHEME = {
    "ko": {
        "title": "플러그인이 들어가는 세 자리",
        "sub": "발표 내용을 바탕으로 그린 구조도예요. 실제 화면과는 다릅니다.",
        "chat": ["배너 시안 세 개만 뽑아 줘", "세 가지 방향으로 만들었어요.", "오른쪽 패널에서 바로 고칠 수 있어요."],
        "input": "@Figma  지난주 랜딩 시안 찾아 줘",
        "panel": "사이드 패널",
        "panel_sub": "예: 캔바 편집 도구",
        "viewer": "파일 뷰어",
        "viewer_sub": "예: 이미지는 포토샵,\nPDF는 애크로뱃으로",
        "notes": [
            ("1", "사이드 패널", "대화 옆에 앱 화면을 띄움. 캔바가 디자인 도구를 여기에 넣었다."),
            ("2", "파일 뷰어", "대화 속 파일을 앱으로 연다. 어도비는 PDF를 애크로뱃, 이미지를 포토샵으로."),
            ("3", "@호출", "입력창에서 앱을 부른다. 피그마는 파일 검색을 여기에 넣었다."),
        ],
        "source": "출처: OpenAI 데브데이 발표, the-decoder, antihype.com.br",
        "desc": "챗GPT 화면에서 플러그인 익스텐션이 들어가는 세 자리. 대화 옆 사이드 패널(예: 캔바), 파일을 여는 파일 뷰어(예: 어도비 애크로뱃·포토샵), "
                "입력창의 @호출(예: 피그마 파일 검색).",
    },
    "en": {
        "title": "Three places a plugin can live",
        "sub": "A diagram based on the announcement. Not the actual interface.",
        "chat": ["Give me three banner drafts", "Here are three directions.", "You can edit them in the panel."],
        "input": "@Figma  find last week's landing draft",
        "panel": "Side panel",
        "panel_sub": "e.g. Canva's editor",
        "viewer": "File viewer",
        "viewer_sub": "e.g. images in Photoshop,\nPDFs in Acrobat",
        "notes": [
            ("1", "Side panel", "An app's screen next to the chat. Canva put its design tools here."),
            ("2", "File viewer", "Opens files from the chat in an app. Adobe: PDFs in Acrobat, images in Photoshop."),
            ("3", "@mention", "Call an app from the message box. Figma put file search here."),
        ],
        "source": "Sources: OpenAI DevDay, the-decoder, antihype.com.br",
        "desc": "Three places plugin extensions appear in ChatGPT: a side panel next to the chat (e.g. Canva), a file viewer that opens files "
                "(e.g. Adobe Acrobat and Photoshop), and @mentions in the message box (e.g. Figma file search).",
    },
}


def badge(x, y, n, r=15, size=17):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{INK}"/>'
            f'<text x="{x}" y="{y + size * 0.36}" font-size="{size}" font-weight="800" fill="{BG}" text-anchor="middle">{n}</text>')


def scheme(lang, wide):
    t = SCHEME[lang]
    if wide:
        W, pad, ts, ss, fs, ns = 1200, 40, 30, 19, 17, 17
    else:
        W, pad, ts, ss, fs, ns = 600, 32, 34, 21, 19, 20
    out, y = [], pad + ts
    out.append(text(pad, y, t["title"], ts, weight=800))
    y += ss + 12
    out.append(text(pad, y, t["sub"], ss, MUTED))
    y += 32
    # 창 틀
    wx, wy, ww = pad, y, W - pad * 2
    # 폰판은 대화 → 파일 카드 → 입력창 → 사이드 패널 순서로 위에서 아래로 쌓습니다
    wh = 420 if wide else 591
    out.append(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="16" fill="{BG}" stroke="{INK}" stroke-width="2"/>')
    out.append(f'<line x1="{wx}" y1="{wy + 40}" x2="{wx + ww}" y2="{wy + 40}" stroke="{RULE}" stroke-width="1.5"/>')
    for k in range(3):
        out.append(f'<circle cx="{wx + 24 + k * 18}" cy="{wy + 20}" r="5" fill="{RULE}"/>')
    out.append(text(wx + ww / 2, wy + 26, "ChatGPT", fs - 2, MUTED, 700, "middle"))
    if wide:
        chat_x, chat_w = wx + 24, ww * 0.52
        side_x, side_w = wx + ww * 0.56, ww * 0.44 - 20
        side_y, side_h = wy + 56, wh - 72
    else:
        chat_x, chat_w = wx + 20, ww - 40
        side_x, side_w = wx + 20, ww - 40
        side_y, side_h = wy + 371, 200
    # 대화
    cy = wy + 64
    bubbles = [(t["chat"][0], True), (t["chat"][1], False), (t["chat"][2], False)]
    for msg, me in bubbles:
        bw = min(len(msg) * fs * (0.56 if lang == "en" else 0.98) + 36, chat_w - 20)
        bx = chat_x + chat_w - bw if me else chat_x
        out.append(f'<rect x="{bx}" y="{cy}" width="{bw}" height="{fs + 22}" rx="{(fs + 22) / 2}" fill="{INK if me else SOFT}"/>')
        out.append(text(bx + 18, cy + fs + 5, msg, fs, BG if me else BODY))
        cy += fs + 34
    # 대화 속 파일 카드 (파일 뷰어로 열림)
    fy = cy + 4
    fw = min(chat_w, 300)
    out.append(f'<rect x="{chat_x}" y="{fy}" width="{fw}" height="56" rx="10" fill="{BG}" stroke="{INK}" stroke-width="1.5"/>')
    out.append(f'<rect x="{chat_x + 12}" y="{fy + 12}" width="32" height="32" rx="6" fill="{SOFT}" stroke="{RULE}"/>')
    out.append(text(chat_x + 56, fy + 25, "banner-a.psd" if wide or lang == "en" else "banner-a.psd", fs - 1, INK, 700))
    out.append(text(chat_x + 56, fy + 46, t["viewer"] + " →", fs - 3, MUTED))
    out.append(badge(chat_x + fw - 6, fy + 2, "2"))
    # 입력창
    iy = (wy + wh - 64) if wide else (fy + 56 + 20)
    out.append(f'<rect x="{chat_x}" y="{iy}" width="{chat_w}" height="44" rx="22" fill="{BG}" stroke="{INK}" stroke-width="1.5"/>')
    tag = t["input"].split("  ")
    out.append(f'<rect x="{chat_x + 10}" y="{iy + 9}" width="{len(tag[0]) * fs * 0.62 + 20}" height="26" rx="13" fill="{INK}"/>')
    out.append(text(chat_x + 20, iy + 28, tag[0], fs - 2, BG, 700))
    out.append(text(chat_x + 10 + len(tag[0]) * fs * 0.62 + 32, iy + 28, tag[1], fs - 2, BODY))
    out.append(badge(chat_x + 2, iy + 2, "3"))
    # 사이드 패널
    out.append(f'<rect x="{side_x}" y="{side_y}" width="{side_w}" height="{side_h}" rx="12" fill="{SOFT}" stroke="{INK}" stroke-width="1.5"/>')
    out.append(text(side_x + 20, side_y + 34, t["panel"], fs + 1, INK, 800))
    out.append(text(side_x + 20, side_y + 58, t["panel_sub"], fs - 2, MUTED))
    # 패널 안의 캔버스와 도구 막대
    cvx, cvy = side_x + 20, side_y + 76
    cvw, cvh = side_w - 40 - 44, side_h - 96
    out.append(f'<rect x="{cvx}" y="{cvy}" width="{cvw}" height="{cvh}" rx="8" fill="{BG}" stroke="{RULE}"/>')
    out.append(f'<rect x="{cvx + 16}" y="{cvy + 16}" width="{cvw * 0.55}" height="{max(cvh * 0.16, 10)}" rx="4" fill="{INK}"/>')
    out.append(f'<rect x="{cvx + 16}" y="{cvy + 22 + max(cvh * 0.16, 10)}" width="{cvw * 0.38}" height="8" rx="4" fill="{RULE}"/>')
    out.append(f'<circle cx="{cvx + cvw * 0.72}" cy="{cvy + cvh * 0.62}" r="{min(cvw, cvh) * 0.2}" fill="{RULE}"/>')
    for k in range(4 if wide else 3):
        out.append(f'<rect x="{cvx + cvw + 12}" y="{cvy + k * 36}" width="28" height="28" rx="6" fill="{BG}" stroke="{RULE}"/>')
    out.append(badge(side_x + side_w - 4, side_y + 4, "1"))
    y = wy + wh + 40
    # 번호 설명
    for n, head, body in t["notes"]:
        out.append(badge(pad + 15, y - ns * 0.36, n, 14, 16))
        if wide:
            out.append(text(pad + 40, y, head, ns, INK, 700))
            out.append(text(pad + 40 + (150 if lang == "ko" else 120), y, body, ns, BODY))
            y += ns + 18
        else:
            out.append(text(pad + 40, y, head, ns, INK, 700))
            # 폰판은 설명을 두 줄까지 나눕니다
            words, lines, cur = body.split(" "), [], ""
            limit = 26 if lang == "ko" else 44
            for w in words:
                if len(cur) + len(w) + 1 > limit and cur:
                    lines.append(cur)
                    cur = w
                else:
                    cur = (cur + " " + w).strip()
            lines.append(cur)
            for k, line in enumerate(lines):
                out.append(text(pad + 40, y + (k + 1) * (ns + 10), line, ns - 1, BODY))
            y += (len(lines) + 1) * (ns + 10) + 12
    y += 12
    out.append(f'<line x1="{pad}" y1="{y - 14}" x2="{W - pad}" y2="{y - 14}" stroke="{RULE}" stroke-width="1"/>')
    y += 10
    out.append(text(pad, y, t["source"], (ss - 3) if wide else (ss - 4), MUTED))
    return wrap(W, round(y + pad), t["title"], t["desc"], out)


# =========================================================
# 3. 테마 편집기와 캔버스 비교 (2026-10-01 쇼피파이 캔버스 글)
# =========================================================
CANVAS = {
    "ko": {
        "title": "같은 가게, 두 가지 작업대",
        "sub": "발표를 바탕으로 그린 구조도. 실제 화면과는 다르다.",
        "left": "지금까지: 테마 편집기",
        "left_note": ["한 번에 한 페이지.", "왼쪽 설정 칸을 하나씩 열어 고친다."],
        "right": "캔버스",
        "right_note": ["모든 페이지를 한 판에 펼친다.", "눌러서 고치거나 사이드킥에게 말한다."],
        "settings": ["헤더", "이미지 배너", "추천 상품", "뉴스레터", "푸터"],
        "page": "홈",
        "pages": ["홈", "상품", "컬렉션", "장바구니", "소개", "FAQ"],
        "chat": ["상품 사진을 더 크게,", "버튼은 검정으로"],
        "reply": "6개 페이지에 반영했어요",
        "source": "출처: Shopify 발표·변경 기록, TechCrunch (2026. 10. 1)",
        "desc": "기존 테마 편집기는 한 번에 한 페이지를 열고 왼쪽 설정 칸에서 고친다. 캔버스는 가게의 모든 페이지를 한 판에 펼쳐 놓고, "
                "요소를 눌러 직접 고치거나 사이드킥에게 말로 시킨다.",
    },
    "en": {
        "title": "Same store, two workbenches",
        "sub": "A diagram based on the announcement. Not the actual interface.",
        "left": "Until now: the theme editor",
        "left_note": ["One page at a time.", "Open settings on the left, one by one."],
        "right": "Canvas",
        "right_note": ["Every page laid out at once.", "Click to edit, or tell Sidekick."],
        "settings": ["Header", "Image banner", "Featured products", "Newsletter", "Footer"],
        "page": "Home",
        "pages": ["Home", "Product", "Collection", "Cart", "About", "FAQ"],
        "chat": ["Bigger product photos,", "black buttons"],
        "reply": "Applied to 6 pages",
        "source": "Sources: Shopify announcement and changelog, TechCrunch (Oct 1, 2026)",
        "desc": "The old theme editor opens one page at a time and edits it through a settings column on the left. Canvas lays out "
                "every page of the store at once; you click an element to edit it or ask Sidekick in chat.",
    },
}


def mini_page(x, y, w, h, label, fs, selected=False):
    """페이지 썸네일 하나. 머리 막대, 큰 그림, 글 줄 두 개."""
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{BG}" stroke="{INK if selected else RULE}" '
         f'stroke-width="{2.5 if selected else 1.2}"/>',
         f'<rect x="{x + 8}" y="{y + 8}" width="{w - 16}" height="6" rx="3" fill="{RULE}"/>',
         f'<rect x="{x + 8}" y="{y + 20}" width="{w - 16}" height="{h * 0.42}" rx="3" fill="{SOFT}"/>',
         f'<rect x="{x + 8}" y="{y + 28 + h * 0.42}" width="{(w - 16) * 0.7}" height="5" rx="2.5" fill="{RULE}"/>',
         f'<rect x="{x + 8}" y="{y + 38 + h * 0.42}" width="{(w - 16) * 0.45}" height="5" rx="2.5" fill="{RULE}"/>',
         text(x, y + h + fs + 6, label, fs, INK if selected else MUTED, 700 if selected else 400)]
    return o


def window(x, y, w, h):
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{BG}" stroke="{INK}" stroke-width="2"/>',
         f'<line x1="{x}" y1="{y + 34}" x2="{x + w}" y2="{y + 34}" stroke="{RULE}" stroke-width="1.5"/>']
    for k in range(3):
        o.append(f'<circle cx="{x + 20 + k * 16}" cy="{y + 17}" r="4.5" fill="{RULE}"/>')
    return o


def canvas_compare(lang, wide):
    t = CANVAS[lang]
    if wide:
        W, pad, ts, ss, hs, fs, ns = 1200, 40, 30, 19, 22, 14, 17
    else:
        W, pad, ts, ss, hs, fs, ns = 600, 32, 34, 21, 26, 17, 20
    out, y = [], pad + ts
    out.append(text(pad, y, t["title"], ts, weight=800))
    y += ss + 12
    out.append(text(pad, y, t["sub"], ss, MUTED))
    y += 44 if wide else 52
    gap = 48
    colw = (W - pad * 2 - gap) / 2 if wide else W - pad * 2
    winh = 330 if wide else 330

    def left_block(x, y0):
        o = [text(x, y0, t["left"], hs, INK, 800)]
        wy = y0 + 22
        o += window(x, wy, colw, winh)
        # 왼쪽 설정 칸
        sw = colw * 0.34
        o.append(f'<line x1="{x + sw}" y1="{wy + 34}" x2="{x + sw}" y2="{wy + winh}" stroke="{RULE}" stroke-width="1.5"/>')
        for k, name in enumerate(t["settings"]):
            ry = wy + 52 + k * 42
            sel = k == 2
            o.append(f'<rect x="{x + 12}" y="{ry}" width="{sw - 24}" height="32" rx="6" fill="{INK if sel else SOFT}"/>')
            o.append(text(x + 24, ry + 21, name, fs - 1 if lang == "en" and not wide else fs, BG if sel else BODY, 700 if sel else 400))
        # 한 페이지 미리보기
        px, pw = x + sw + 24, colw - sw - 48
        o += mini_page(px, wy + 56, pw, winh - 110, t["page"], fs, True)
        out_y = wy + winh + 30
        for k, line in enumerate(t["left_note"]):
            o.append(text(x, out_y + k * (ns + 10), line, ns, BODY))
        return o, out_y + len(t["left_note"]) * (ns + 10)

    def right_block(x, y0):
        o = [text(x, y0, t["right"], hs, INK, 800)]
        wy = y0 + 22
        o += window(x, wy, colw, winh)
        # 페이지 판 (3 x 2)
        chw = colw * 0.36
        gx, gw = x + 16, colw - chw - 32
        cols, rows = 3, 2
        cw = (gw - (cols - 1) * 14) / cols
        chh = (winh - 50 - 16 - rows * (fs + 16) - (rows - 1) * 10) / rows
        for k, name in enumerate(t["pages"]):
            cx = gx + (k % cols) * (cw + 14)
            cy = wy + 50 + (k // cols) * (chh + fs + 26)  # 줄 사이 = 이름 칸 + 여백
            o += mini_page(cx, cy, cw, chh, name, fs - 2 if not wide else fs - 1, k == 1)
        # 선택한 페이지 위 커서
        cx = gx + (cw + 14) + cw * 0.6
        cy = wy + 50 + chh * 0.45
        o.append(f'<path d="M{cx} {cy}l0 22l6-6l5 10l4-2l-5-10l8 0z" fill="{INK}" stroke="{BG}" stroke-width="1.5"/>')
        # 사이드킥 대화
        sx = x + colw - chw
        o.append(f'<line x1="{sx}" y1="{wy + 34}" x2="{sx}" y2="{wy + winh}" stroke="{RULE}" stroke-width="1.5"/>')
        o.append(text(sx + 14, wy + 60, "Sidekick", fs, INK, 800))
        by = wy + 78
        bh = len(t["chat"]) * (fs + 8) + 16
        o.append(f'<rect x="{sx + 12}" y="{by}" width="{chw - 24}" height="{bh}" rx="10" fill="{INK}"/>')
        for k, line in enumerate(t["chat"]):
            o.append(text(sx + 24, by + 10 + (k + 1) * (fs + 8) - 4, line, fs - 1, BG))
        ry = by + bh + 14
        o.append(f'<rect x="{sx + 12}" y="{ry}" width="{chw - 24}" height="{fs + 22}" rx="10" fill="{SOFT}"/>')
        o.append(text(sx + 24, ry + fs + 6, t["reply"], fs - 1 if wide else fs - 3, BODY))
        o.append(f'<rect x="{sx + 12}" y="{wy + winh - 50}" width="{chw - 24}" height="34" rx="17" fill="{BG}" stroke="{INK}" stroke-width="1.5"/>')
        out_y = wy + winh + 30
        for k, line in enumerate(t["right_note"]):
            o.append(text(x, out_y + k * (ns + 10), line, ns, BODY))
        return o, out_y + len(t["right_note"]) * (ns + 10)

    if wide:
        a, ya = left_block(pad, y)
        b, yb = right_block(pad + colw + gap, y)
        out += a + b
        y = max(ya, yb) + 20
    else:
        a, ya = left_block(pad, y)
        out += a
        b, yb = right_block(pad, ya + 40)
        out += b
        y = yb + 20
    out.append(f'<line x1="{pad}" y1="{y - 14}" x2="{W - pad}" y2="{y - 14}" stroke="{RULE}" stroke-width="1"/>')
    y += 14
    out.append(text(pad, y, t["source"], (ss - 3) if wide else (ss - 4), MUTED))
    return wrap(W, round(y + pad), t["title"], t["desc"], out)


# =========================================================
# 4. DESIGN.md 한 장의 생김새 (2026-10-02 DESIGN.md 글)
# =========================================================
DESIGNMD = {
    "ko": {
        "title": "DESIGN.md 한 장은 이렇게 생겼다",
        "sub": "이 사이트의 규칙을 옮겨 적은 예. 줄을 덜어냈다.",
        "lines": [
            ("---", "fence"), ("name: Design Hub", "k"), ("colors:", "k"), ('  ink: "#111111"', "v"),
            ('  muted: "#6B6B6B"', "v"), ('  faint: "#A3A3A3"', "v"), ("typography:", "k"),
            ("  caption: { fontFamily: Pretendard, fontSize: 12px }", "v"), ("rounded:", "k"), ("  md: 8px", "v"),
            ("components:", "k"), ('  row-tags: { textColor: "{colors.faint}" }', "v"), ("---", "fence"),
            ("## Overview", "h"), ("흑백만 쓴다. 강조는 색 대신 굵기와 채움으로.", "p"),
            ("## Do's and Don'ts", "h"), ("- 색으로 한쪽을 강조하지 않는다.", "p"),
        ],
        "split": 13,
        "a_head": "토큰", "a_body": ["정확한 값.", "기계가 읽는 YAML."],
        "b_head": "설명", "b_body": ["왜 그 값인지.", "사람도 읽는 글."],
        "source": "형식: google-labs-code/design.md (알파, Apache 2.0)",
        "desc": "DESIGN.md 파일은 위쪽 --- 사이에 색, 글자, 둥근 정도, 컴포넌트 같은 토큰을 YAML로 적고, 아래쪽에 왜 그런 값을 쓰는지 마크다운 글로 적는다.",
    },
    "en": {
        "title": "What a DESIGN.md file looks like",
        "sub": "This site's rules as an example, trimmed.",
        "lines": [
            ("---", "fence"), ("name: Design Hub", "k"), ("colors:", "k"), ('  ink: "#111111"', "v"),
            ('  muted: "#6B6B6B"', "v"), ('  faint: "#A3A3A3"', "v"), ("typography:", "k"),
            ("  caption: { fontFamily: Pretendard, fontSize: 12px }", "v"), ("rounded:", "k"), ("  md: 8px", "v"),
            ("components:", "k"), ('  row-tags: { textColor: "{colors.faint}" }', "v"), ("---", "fence"),
            ("## Overview", "h"), ("Black and white only. Emphasis by weight and fill, not color.", "p"),
            ("## Do's and Don'ts", "h"), ("- Never use color to favor one side.", "p"),
        ],
        "split": 13,
        "a_head": "Tokens", "a_body": ["Exact values.", "YAML for machines."],
        "b_head": "Rationale", "b_body": ["Why those values.", "Prose for people too."],
        "source": "Format: google-labs-code/design.md (alpha, Apache 2.0)",
        "desc": "A DESIGN.md file lists tokens such as colors, type, corner radius and components as YAML between --- fences at the top, "
                "and explains why those values exist in markdown prose below.",
    },
}

MONO = "'SF Mono', Menlo, Consolas, 'D2Coding', monospace"


def designmd(lang, wide):
    t = DESIGNMD[lang]
    if wide:
        W, pad, ts, ss, cs, lh, ns = 1200, 40, 30, 19, 17, 27, 18
    else:
        W, pad, ts, ss, cs, lh, ns = 600, 32, 34, 21, 15, 25, 20
    out, y = [], pad + ts
    out.append(text(pad, y, t["title"], ts, weight=800))
    y += ss + 12
    out.append(text(pad, y, t["sub"], ss, MUTED))
    y += 36
    fw = (W - pad * 2) * 0.68 if wide else W - pad * 2
    lines = t["lines"]
    if not wide:  # 폰판은 긴 줄을 줄여서 폭 안에 넣습니다
        lines = [(s.replace("  caption: { fontFamily: Pretendard, fontSize: 12px }", "  caption: { fontSize: 12px }")
                  .replace('  row-tags: { textColor: "{colors.faint}" }', '  row-tags: "{colors.faint}"'), k) for s, k in lines]
    fh = 52 + len(lines) * lh + 20
    fx, fy = pad, y
    out.append(f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="14" fill="{BG}" stroke="{INK}" stroke-width="2"/>')
    out.append(f'<line x1="{fx}" y1="{fy + 38}" x2="{fx + fw}" y2="{fy + 38}" stroke="{RULE}" stroke-width="1.5"/>')
    out.append(text(fx + 20, fy + 25, "DESIGN.md", cs, INK, 700))
    # 토큰 구간 바탕
    ty0 = fy + 52
    ty1 = ty0 + t["split"] * lh
    out.append(f'<rect x="{fx + 2}" y="{ty0 - 4}" width="{fw - 4}" height="{ty1 - ty0}" fill="{SOFT}"/>')
    for i, (s, kind) in enumerate(lines):
        ly = ty0 + i * lh + cs
        fill = MUTED if kind == "fence" else INK if kind in ("k", "h") else BODY
        weight = 700 if kind in ("k", "h") else 400
        fam = FONT if kind in ("h", "p") else MONO
        size = cs + 1 if kind in ("h", "p") else cs
        out.append(f'<text x="{fx + 20}" y="{ly}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
                   f'font-family="{fam}" xml:space="preserve">{e(s)}</text>')
    by1 = ty0 + len(lines) * lh

    def note(x, y0, y1, head, body, wide_mode):
        o = []
        if wide_mode:
            o.append(f'<path d="M{x} {y0 + 4}h12v{y1 - y0 - 8}h-12" fill="none" stroke="{INK}" stroke-width="2"/>')
            mid = (y0 + y1) / 2 - (len(body) * (ns + 8)) / 2
            o.append(text(x + 30, mid, head, ns + 4, INK, 800))
            for k, line in enumerate(body):
                o.append(text(x + 30, mid + (k + 1) * (ns + 8) + 4, line, ns, BODY))
        return o

    if wide:
        nx = fx + fw + 20
        out += note(nx, ty0 - 4, ty1 - 4, t["a_head"], t["a_body"], True)
        out += note(nx, ty1, by1 + 4, t["b_head"], t["b_body"], True)
        y = fy + fh + 40
    else:
        y = fy + fh + 40
        for head, body, filled in ((t["a_head"], t["a_body"], True), (t["b_head"], t["b_body"], False)):
            out.append(f'<rect x="{pad}" y="{y - ns}" width="22" height="22" rx="4" fill="{SOFT if filled else BG}" stroke="{INK}" stroke-width="1.5"/>')
            out.append(text(pad + 34, y, head, ns, INK, 800))
            out.append(text(pad + 34 + len(head) * ns * (1.05 if lang == "ko" else 0.62) + 14, y, " ".join(t["a_body" if filled else "b_body"]), ns - 1, BODY))
            y += ns + 20
        y += 16
    out.append(f'<line x1="{pad}" y1="{y - 14}" x2="{W - pad}" y2="{y - 14}" stroke="{RULE}" stroke-width="1"/>')
    y += 14
    out.append(text(pad, y, t["source"], (ss - 3) if wide else (ss - 4), MUTED))
    return wrap(W, round(y + pad), t["title"], t["desc"], out)


# =========================================================
# 5. 다시 뽑기와 고쳐 쓰기 (2026-10-03 이미지 편집 글)
# =========================================================
DRIFT = {
    "ko": {
        "title": "다시 뽑기와 고쳐 쓰기",
        "sub": "같은 그림을 세 번 고칠 때 바뀌는 자리. 개념을 그린 그림이다.",
        "rows": ["예전 방식: 매번 다시 그림", "이번 주 모델: 고른 자리만"],
        "cols": ["원본", "1차 수정", "2차 수정", "3차 수정"],
        "asks": ["", "제목 글자 바꾸기", "병 색 바꾸기", "그림자 지우기"],
        "legend": ["바뀐 자리"],
        "source": "출처: Ideogram 4.5 발표(9. 30), Black Forest Labs FLUX 3 Image 발표(10. 2)",
        "desc": "예전 방식은 한 군데를 고쳐 달라고 해도 매번 그림 전체가 조금씩 바뀌어 위치와 색이 틀어진다. 이번 주 나온 모델들은 고른 자리만 바꾸고 나머지는 그대로 둔다.",
    },
    "en": {
        "title": "Re-rolling vs. editing",
        "sub": "One image, edited three times. A conceptual sketch.",
        "rows": ["Before: redraws every time", "This week's models: only the chosen area"],
        "cols": ["Original", "Edit 1", "Edit 2", "Edit 3"],
        "asks": ["", "Change headline", "Recolor bottle", "Remove shadow"],
        "legend": ["Changed area"],
        "source": "Sources: Ideogram 4.5 (Sep 30), Black Forest Labs FLUX 3 Image (Oct 2)",
        "desc": "With older models, asking for one change subtly redraws the whole image, so positions and colors drift. This week's models change only the selected area and leave the rest alone.",
    },
}


def scene(x, y, w, h, k, drift, region):
    """간단한 광고 시안 한 장. drift 이면 차례마다 위치·크기가 조금씩 어긋납니다.
    region 은 이번 차례에 바뀐 자리(0 없음, 1 제목, 2 병, 3 그림자)."""
    dx = [0, 6, -5, 9][k] if drift else 0
    dy = [0, -4, 5, -2][k] if drift else 0
    ds = [1, 1.08, 0.92, 1.12][k] if drift else 1
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{SOFT if drift and k else BG}" stroke="{INK}" stroke-width="1.5"/>']
    # 제목 막대
    tw = w * (0.55 if (not drift and k >= 1) else 0.5) * (ds if drift else 1)
    o.append(f'<rect x="{x + 12 + dx * 0.5}" y="{y + 12 + dy * 0.3}" width="{tw}" height="{h * 0.09}" rx="3" fill="{INK}"/>')
    # 병
    bw, bh = w * 0.18 * ds, h * 0.48 * ds
    bx, by = x + w * 0.62 + dx, y + h * 0.36 + dy
    fill = BODY if (not drift and k >= 2) or (drift and k % 2) else INK
    o.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="{bw * 0.3}" fill="{fill}"/>')
    o.append(f'<rect x="{bx + bw * 0.3}" y="{by - h * 0.08}" width="{bw * 0.4}" height="{h * 0.1}" rx="2" fill="{fill}"/>')
    # 그림자
    if not (not drift and k >= 3):
        o.append(f'<ellipse cx="{bx + bw / 2 + dx * 0.3}" cy="{by + bh + 6}" rx="{bw * 0.9}" ry="5" fill="{RULE}"/>')
    # 해
    o.append(f'<circle cx="{x + w * 0.25 - dx}" cy="{y + h * 0.62 + dy}" r="{h * 0.14 * ds}" fill="{RULE}"/>')
    # 바뀐 자리 표시
    if drift and k:
        o.append(f'<rect x="{x + 3}" y="{y + 3}" width="{w - 6}" height="{h - 6}" rx="6" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="6 4"/>')
    elif region == 1:
        o.append(f'<rect x="{x + 6}" y="{y + 6}" width="{w * 0.62}" height="{h * 0.09 + 12}" rx="4" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="6 4"/>')
    elif region == 2:
        o.append(f'<rect x="{bx - 6}" y="{by - h * 0.08 - 6}" width="{bw + 12}" height="{bh + h * 0.08 + 12}" rx="4" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="6 4"/>')
    elif region == 3:
        o.append(f'<rect x="{bx - bw * 0.5}" y="{by + bh - 2}" width="{bw * 2}" height="18" rx="4" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="6 4"/>')
    return o


def drift(lang, wide):
    t = DRIFT[lang]
    if wide:
        W, pad, ts, ss, ls, fs = 1200, 40, 30, 19, 20, 16
    else:
        W, pad, ts, ss, ls, fs = 600, 32, 34, 21, 23, 17
    out, y = [], pad + ts
    out.append(text(pad, y, t["title"], ts, weight=800))
    y += ss + 12
    out.append(text(pad, y, t["sub"], ss, MUTED))
    y += 40
    gap = 20 if wide else 12
    cw = (W - pad * 2 - gap * 3) / 4
    ch = cw * 0.72
    # 열 머리
    for k, (c, a) in enumerate(zip(t["cols"], t["asks"])):
        cx = pad + k * (cw + gap)
        out.append(text(cx, y, c, fs, INK, 700))
        if a:
            out.append(text(cx, y + fs + 8, a, fs - 2, MUTED))
    y += fs * 2 + 22
    for r, label in enumerate(t["rows"]):
        out.append(text(pad, y, label, ls, INK, 800))
        y += 16
        for k in range(4):
            out += scene(pad + k * (cw + gap), y, cw, ch, k, r == 0, 0 if r == 0 else k)
        y += ch + 40
    # 범례
    out.append(f'<rect x="{pad}" y="{y - 16}" width="34" height="20" rx="4" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="6 4"/>')
    out.append(text(pad + 46, y, t["legend"][0], fs, BODY))
    y += 34
    out.append(f'<line x1="{pad}" y1="{y - 14}" x2="{W - pad}" y2="{y - 14}" stroke="{RULE}" stroke-width="1"/>')
    y += 14
    out.append(text(pad, y, t["source"], (ss - 3) if wide else (ss - 6), MUTED))
    return wrap(W, round(y + pad), t["title"], t["desc"], out)


# =========================================================
# 6. 상자로 먼저 배치하기 (2026-10-03 이미지 편집 글)
# =========================================================
BBOX = {
    "ko": {
        "title": "글보다 먼저, 상자로 자리를 잡는다",
        "sub": "FLUX 3 Image의 상자 배치. 발표를 바탕으로 그린 예이고 실제 형식과 다를 수 있다.",
        "code_title": "배치 (JSON)",
        "items": [("headline", "제목 글자", (0.06, 0.08, 0.6, 0.16)), ("product", "제품 (참고 이미지 1)", (0.6, 0.3, 0.3, 0.6)),
                  ("model", "모델 (참고 이미지 2)", (0.08, 0.32, 0.4, 0.6)), ("badge", "할인 딱지", (0.72, 0.06, 0.2, 0.18))],
        "canvas": "4K 캔버스 · 5456 × 3072",
        "source": "출처: Black Forest Labs 발표, the-decoder, Tech Times (2026. 10. 2)",
        "desc": "FLUX 3 Image는 그림을 그리기 전에 요소마다 상자로 자리와 크기를 정할 수 있다. 제목, 제품, 모델, 할인 딱지를 상자로 놓고 참고 이미지를 최대 10장까지 붙인다.",
    },
    "en": {
        "title": "Boxes first, then the picture",
        "sub": "Bounding-box layout in FLUX 3 Image. An illustrative example; the real format may differ.",
        "code_title": "Layout (JSON)",
        "items": [("headline", "Headline", (0.06, 0.08, 0.6, 0.16)), ("product", "Product (ref. 1)", (0.6, 0.3, 0.3, 0.6)),
                  ("model", "Model (ref. 2)", (0.08, 0.32, 0.4, 0.6)), ("badge", "Sale badge", (0.72, 0.06, 0.2, 0.18))],
        "canvas": "4K canvas · 5456 × 3072",
        "source": "Sources: Black Forest Labs, the-decoder, Tech Times (Oct 2, 2026)",
        "desc": "FLUX 3 Image lets you set each element's position and size with a box before generating. A headline, product, model and sale badge are placed as boxes, with up to ten reference images attached.",
    },
}


def bbox(lang, wide):
    t = BBOX[lang]
    if wide:
        W, pad, ts, ss, cs, lh, fs = 1200, 40, 30, 19, 14, 24, 16
    else:
        W, pad, ts, ss, cs, lh, fs = 600, 32, 34, 21, 15, 23, 17
    out, y = [], pad + ts
    out.append(text(pad, y, t["title"], ts, weight=800))
    y += ss + 12
    sub = t["sub"]
    if wide:
        out.append(text(pad, y, sub, ss, MUTED))
    else:  # 폰판은 두 줄로
        a, b = sub.split(". ", 1)
        out.append(text(pad, y, a + ".", ss, MUTED))
        y += ss + 10
        out.append(text(pad, y, b, ss, MUTED))
    y += 36
    lines = ["["]
    for i, (key, _, (bx, by, bw, bh)) in enumerate(t["items"]):
        comma = "," if i < len(t["items"]) - 1 else ""
        lines.append(f'  {{ "id": "{key}", "box": [{bx:.2f}, {by:.2f}, {bw:.2f}, {bh:.2f}] }}{comma}')
    lines.append("]")
    codew = (W - pad * 2) * 0.5 if wide else W - pad * 2
    codeh = 46 + len(lines) * lh + 14
    out.append(f'<rect x="{pad}" y="{y}" width="{codew}" height="{codeh}" rx="12" fill="{SOFT}" stroke="{INK}" stroke-width="1.5"/>')
    out.append(text(pad + 18, y + 28, t["code_title"], fs - 1, INK, 700))
    for i, ln in enumerate(lines):
        out.append(f'<text x="{pad + 18}" y="{y + 46 + (i + 1) * lh - 6}" font-size="{cs if wide else cs - 2}" fill="{BODY}" '
                   f'font-family="{MONO}" xml:space="preserve">{e(ln)}</text>')
    # 캔버스
    if wide:
        cx, cy = pad + codew + 40, y
        cw = W - pad - cx
    else:
        cx, cy = pad, y + codeh + 40
        cw = W - pad * 2
    chh = cw * 3072 / 5456
    out.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{chh}" rx="10" fill="{BG}" stroke="{INK}" stroke-width="2"/>')
    for i, (key, label, (bx, by, bw, bh)) in enumerate(t["items"]):
        rx, ry, rw, rh = cx + bx * cw, cy + by * chh, bw * cw, bh * chh
        filled = key in ("product", "model")
        out.append(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="6" fill="{SOFT if filled else BG}" stroke="{INK}" '
                   f'stroke-width="2" stroke-dasharray="{"0" if filled else "6 4"}"/>')
        out.append(text(rx + 10, ry + fs + 8, label, fs - 2 if not wide else fs - 1, INK, 700))
    bottom = max(y + codeh, cy + chh)
    out.append(text(cx, cy + chh + fs + 12, t["canvas"], fs - 2, MUTED))
    y = bottom + (60 if wide else 52)
    out.append(f'<line x1="{pad}" y1="{y - 14}" x2="{W - pad}" y2="{y - 14}" stroke="{RULE}" stroke-width="1"/>')
    y += 14
    out.append(text(pad, y, t["source"], (ss - 3) if wide else (ss - 6), MUTED))
    return wrap(W, round(y + pad), t["title"], t["desc"], out)


# =========================================================
# 7. InstructMesh 고치는 순서 (2026-10-04 3D 출력 글)
# =========================================================
MESHFLOW = {
    "ko": {
        "title": "AI 3D 모델을 출력하기 전에 고치는 순서",
        "sub": "MIT CSAIL의 InstructMesh. 논문과 발표를 바탕으로 정리했다.",
        "steps": [("만든다", ["글이나 사진으로", "3D 모델 생성", "(TRELLIS)"]),
                  ("고를 곳을 칠한다", ["문제가 보이는", "부위만 선택"]),
                  ("말로 고친다", ["\"손잡이를 두껍게\"", "구멍 열기·막기,", "슬라이더로 두께"]),
                  ("출력한다", ["고친 부위만 바뀌고", "나머지는 그대로"])],
        "source": "출처: MIT News(2026. 10. 1), arXiv 2608.28534",
        "desc": "InstructMesh는 글이나 사진으로 3D 모델을 만든 뒤, 문제가 보이는 부위만 칠해 고르고, 말이나 슬라이더로 두께를 바꾸거나 구멍을 열고 막는다. 고친 부위만 바뀐 채로 출력한다.",
    },
    "en": {
        "title": "Fixing an AI 3D model before you print it",
        "sub": "MIT CSAIL's InstructMesh, summarized from the paper and announcement.",
        "steps": [("Generate", ["A 3D model from", "text or a photo", "(TRELLIS)"]),
                  ("Paint the spot", ["Select only the", "region with a problem"]),
                  ("Say the fix", ["\"Thicken the handle\"", "Open or seal holes,", "sliders for thickness"]),
                  ("Print", ["Only the fixed part", "changes; the rest stays"])],
        "source": "Sources: MIT News (Oct 1, 2026), arXiv 2608.28534",
        "desc": "With InstructMesh, you generate a 3D model from text or a photo, paint the region with a problem, then thicken it, open or seal holes by describing the fix or using sliders. Only that region changes before printing.",
    },
}


def mug(x, y, s, thin, sel):
    """머그잔 옆모습. thin 이면 손잡이가 가늘다. sel 이면 손잡이 둘레에 선택 표시."""
    o = [f'<rect x="{x}" y="{y}" width="{s * 0.62}" height="{s * 0.8}" rx="{s * 0.08}" fill="{SOFT}" stroke="{INK}" stroke-width="2"/>']
    hw = 3 if thin else 9
    o.append(f'<path d="M{x + s * 0.62} {y + s * 0.2} C{x + s * 0.95} {y + s * 0.2} {x + s * 0.95} {y + s * 0.6} {x + s * 0.62} {y + s * 0.6}" '
             f'fill="none" stroke="{INK}" stroke-width="{hw}" stroke-linecap="round"/>')
    if sel:
        o.append(f'<ellipse cx="{x + s * 0.8}" cy="{y + s * 0.4}" rx="{s * 0.22}" ry="{s * 0.3}" fill="none" stroke="{INK}" '
                 f'stroke-width="2" stroke-dasharray="5 4"/>')
    return o


def meshflow(lang, wide):
    t = MESHFLOW[lang]
    if wide:
        W, pad, ts, ss, hs, fs = 1200, 40, 30, 19, 20, 16
    else:
        W, pad, ts, ss, hs, fs = 600, 32, 34, 21, 24, 19
    out, y = [], pad + ts
    out.append(text(pad, y, t["title"], ts, weight=800))
    y += ss + 12
    out.append(text(pad, y, t["sub"], ss, MUTED))
    y += 40
    n = len(t["steps"])
    if wide:
        gap = 44
        bw = (W - pad * 2 - gap * (n - 1)) / n
        bh = 300
        for i, (head, body) in enumerate(t["steps"]):
            bx = pad + i * (bw + gap)
            out.append(f'<rect x="{bx}" y="{y}" width="{bw}" height="{bh}" rx="14" fill="{BG}" stroke="{INK}" stroke-width="1.5"/>')
            out.append(badge(bx + 26, y + 28, str(i + 1)))
            out.append(text(bx + 50, y + 34, head, hs, INK, 800))
            s = 110
            out += mug(bx + bw / 2 - s * 0.45, y + 64, s, i in (0, 1), i == 1)
            for k, line in enumerate(body):
                out.append(text(bx + 20, y + 214 + k * (fs + 8), line, fs, BODY))
            if i < n - 1:
                ax = bx + bw + 8
                out.append(f'<path d="M{ax} {y + bh / 2}h{gap - 18}m-8 -7l8 7l-8 7" fill="none" stroke="{INK}" stroke-width="2"/>')
        y += bh + 50
    else:
        bh = 150
        for i, (head, body) in enumerate(t["steps"]):
            out.append(f'<rect x="{pad}" y="{y}" width="{W - pad * 2}" height="{bh}" rx="14" fill="{BG}" stroke="{INK}" stroke-width="1.5"/>')
            out.append(badge(pad + 28, y + 30, str(i + 1)))
            out.append(text(pad + 54, y + 38, head, hs, INK, 800))
            for k, line in enumerate(body):
                out.append(text(pad + 26, y + 76 + k * (fs + 8), line, fs, BODY))
            out += mug(W - pad - 150, y + 24, 100, i in (0, 1), i == 1)
            y += bh
            if i < n - 1:
                out.append(f'<path d="M{W / 2} {y + 6}v22m-7 -8l7 8l7 -8" fill="none" stroke="{INK}" stroke-width="2"/>')
                y += 34
        y += 50
    out.append(f'<line x1="{pad}" y1="{y - 14}" x2="{W - pad}" y2="{y - 14}" stroke="{RULE}" stroke-width="1"/>')
    y += 14
    out.append(text(pad, y, t["source"], (ss - 3) if wide else (ss - 4), MUTED))
    return wrap(W, round(y + pad), t["title"], t["desc"], out)


# =========================================================
# 8. 챗GPT 이미지 옆 광고 자리 (2026-10-05 광고 글)
# =========================================================
ADSPOT = {
    "ko": {
        "title": "그림이 그려지는 동안, 옆에 붙는 광고",
        "sub": "발표를 바탕으로 그린 구조도. 실제 화면과는 다를 수 있다.",
        "ask": "캠핑장 저녁 풍경, 따뜻한 조명으로 그려 줘",
        "mine": "내가 요청한 그림",
        "ad": "광고",
        "ad_brand": "브랜드 랜턴",
        "ad_copy": ["제품을 쓰는 장면,", "'영감'으로 제시"],
        "notes": [("1", "광고라고 분명히 표시"), ("2", "만든 그림과 떨어진 자리"), ("3", "답변 내용에는 영향 없음")],
        "source": "출처: OpenAI 발표(2026. 10. 5), TechCrunch",
        "desc": "챗GPT가 그림을 만드는 동안, 만든 그림과 떨어진 자리에 광고라고 표시된 이미지 광고가 붙는다. 제품을 쓰는 장면이나 관련 경험을 '영감'처럼 보여 주는 형식이다.",
    },
    "en": {
        "title": "An ad beside your new image",
        "sub": "Based on the announcement; not the real screen.",
        "ask": "A campsite at dusk, with warm lighting",
        "mine": "The image I asked for",
        "ad": "Ad",
        "ad_brand": "Brand lantern",
        "ad_copy": ["The product in use,", "shown as 'inspiration'"],
        "notes": [("1", "Clearly labeled as an ad"), ("2", "Kept apart from your image"), ("3", "Doesn't change the answer")],
        "source": "Sources: OpenAI (Oct 5, 2026), TechCrunch",
        "desc": "While ChatGPT generates an image, a labeled image ad appears in a separate spot from your image. It shows the product in use or a related experience, framed as inspiration.",
    },
}


def adspot(lang, wide):
    t = ADSPOT[lang]
    if wide:
        W, pad, ts, ss, fs, ns = 1200, 40, 30, 19, 17, 17
    else:
        W, pad, ts, ss, fs, ns = 600, 32, 34, 21, 18, 20
    out, y = [], pad + ts
    out.append(text(pad, y, t["title"], ts, weight=800))
    y += ss + 12
    out.append(text(pad, y, t["sub"], ss, MUTED))
    y += 32
    wx, ww = pad, W - pad * 2
    wh = 430 if wide else 760
    out.append(f'<rect x="{wx}" y="{y}" width="{ww}" height="{wh}" rx="16" fill="{BG}" stroke="{INK}" stroke-width="2"/>')
    out.append(f'<line x1="{wx}" y1="{y + 40}" x2="{wx + ww}" y2="{y + 40}" stroke="{RULE}" stroke-width="1.5"/>')
    for k in range(3):
        out.append(f'<circle cx="{wx + 24 + k * 18}" cy="{y + 20}" r="5" fill="{RULE}"/>')
    out.append(text(wx + ww / 2, y + 26, "ChatGPT", fs - 2, MUTED, 700, "middle"))
    # 요청 말풍선
    bw = min(len(t["ask"]) * fs * (0.56 if lang == "en" else 0.98) + 36, ww - 40)
    by = y + 60
    out.append(f'<rect x="{wx + ww - 20 - bw}" y="{by}" width="{bw}" height="{fs + 22}" rx="{(fs + 22) / 2}" fill="{INK}"/>')
    out.append(text(wx + ww - 20 - bw + 18, by + fs + 5, t["ask"], fs, BG))
    gy = by + fs + 44
    if wide:
        iw, ih = ww * 0.5, wh - (gy - y) - 30
        ix = wx + 24
        ax, aw = ix + iw + 60, ww - iw - 60 - 48
        ay, ah = gy, ih
    else:
        iw, ih = ww - 40, 300
        ix = wx + 20
        ax, aw = ix, iw
        ay, ah = gy + ih + 36, 250
    # 내가 만든 그림: 산과 텐트, 해
    out.append(f'<rect x="{ix}" y="{gy}" width="{iw}" height="{ih}" rx="12" fill="{SOFT}" stroke="{INK}" stroke-width="1.5"/>')
    out.append(f'<path d="M{ix} {gy + ih * 0.7}L{ix + iw * 0.3} {gy + ih * 0.35}L{ix + iw * 0.5} {gy + ih * 0.55}L{ix + iw * 0.72} {gy + ih * 0.3}L{ix + iw} {gy + ih * 0.65}V{gy + ih - 12}Q{ix + iw} {gy + ih} {ix + iw - 12} {gy + ih}H{ix + 12}Q{ix} {gy + ih} {ix} {gy + ih - 12}Z" fill="{RULE}"/>')
    out.append(f'<path d="M{ix + iw * 0.38} {gy + ih * 0.88}L{ix + iw * 0.48} {gy + ih * 0.62}L{ix + iw * 0.58} {gy + ih * 0.88}Z" fill="{INK}"/>')
    out.append(f'<circle cx="{ix + iw * 0.8}" cy="{gy + ih * 0.2}" r="{ih * 0.07}" fill="{BG}" stroke="{INK}" stroke-width="1.5"/>')
    out.append(text(ix + 16, gy + fs + 12, t["mine"], fs, INK, 700))
    # 광고 카드
    out.append(f'<rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" rx="12" fill="{BG}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="7 5"/>')
    tagw = len(t["ad"]) * fs * (1.05 if lang == "ko" else 0.62) + 24
    out.append(f'<rect x="{ax + 14}" y="{ay + 14}" width="{tagw}" height="{fs + 12}" rx="{(fs + 12) / 2}" fill="{INK}"/>')
    out.append(text(ax + 26, ay + 14 + fs + 2, t["ad"], fs - 2, BG, 800))
    # 제품 사진 자리: 랜턴
    px, py, pw, ph = ax + 14, ay + fs + 40, aw - 28, ah * 0.36
    out.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="8" fill="{SOFT}"/>')
    lx, lw = px + pw / 2 - 18, 36
    out.append(f'<rect x="{lx}" y="{py + ph * 0.25}" width="{lw}" height="{ph * 0.55}" rx="8" fill="{BG}" stroke="{INK}" stroke-width="2"/>')
    out.append(f'<path d="M{lx + 8} {py + ph * 0.25}Q{lx + lw / 2} {py + ph * 0.05} {lx + lw - 8} {py + ph * 0.25}" fill="none" stroke="{INK}" stroke-width="2"/>')
    out.append(text(px, py + ph + fs + 14, t["ad_brand"], fs, INK, 700))
    for k, line in enumerate(t["ad_copy"]):
        out.append(text(px, py + ph + fs + 14 + (k + 1) * (fs + 8), line, fs - 2, BODY))
    # 번호 표시
    out.append(badge(ax + aw - 4, ay + 4, "1"))
    if wide:
        out.append(badge(ix + iw + 30, gy + ih / 2, "2"))
        out.append(f'<line x1="{ix + iw + 8}" y1="{gy + ih / 2}" x2="{ix + iw + 14}" y2="{gy + ih / 2}" stroke="{INK}" stroke-width="2"/>')
        out.append(f'<line x1="{ix + iw + 46}" y1="{gy + ih / 2}" x2="{ax - 8}" y2="{gy + ih / 2}" stroke="{INK}" stroke-width="2"/>')
    else:
        out.append(badge(ix + iw / 2, gy + ih + 18, "2"))
    y += wh + 40
    for n, label in t["notes"]:
        out.append(badge(pad + 15, y - ns * 0.36, n, 14, 16))
        out.append(text(pad + 40, y, label, ns, BODY))
        y += ns + 18
    y += 10
    out.append(f'<line x1="{pad}" y1="{y - 14}" x2="{W - pad}" y2="{y - 14}" stroke="{RULE}" stroke-width="1"/>')
    y += 14
    out.append(text(pad, y, t["source"], (ss - 3) if wide else (ss - 4), MUTED))
    return wrap(W, round(y + pad), t["title"], t["desc"], out)


# =========================================================
# 9. 챗GPT 광고 흐름 (2026-10-05 광고 글)
# =========================================================
ADTIME = {
    "ko": {
        "title": "챗GPT 광고, 여덟 달 사이",
        "sub": "미국 기준. 글 광고에서 이미지 광고로",
        "events": [("2. 9", "글 광고 시작", "무료·Go 요금제"), ("5. 5", "광고 관리자 공개", "누구나 직접 집행"),
                   ("10. 5", "이미지 광고 발표", "그림 만들 때"), ("10월 말", "시험 시작", "일부 광고주")],
        "source": "출처: OpenAI 발표, TechCrunch, 업계 정리 (2026)",
        "desc": "챗GPT 광고는 2월 9일 미국 무료·Go 요금제에서 글 광고로 시작했고, 5월 5일 광고 관리자가 열렸다. 10월 5일 그림을 만들 때 붙는 이미지 광고를 발표했고, 10월 말 일부 광고주와 시험을 시작한다.",
    },
    "en": {
        "title": "ChatGPT ads, eight months in",
        "sub": "In the US. From text ads to image ads",
        "events": [("Feb 9", "Text ads begin", "Free and Go plans"), ("May 5", "Ads Manager opens", "Self-serve for all"),
                   ("Oct 5", "Image ads announced", "During image generation"), ("Late Oct", "Test begins", "First advertisers")],
        "source": "Sources: OpenAI, TechCrunch, industry coverage (2026)",
        "desc": "ChatGPT ads began as text ads on US Free and Go plans on February 9, and self-serve Ads Manager opened May 5. On October 5, image ads during image generation were announced, with a test starting in late October.",
    },
}


def adtime(lang, wide):
    t = ADTIME[lang]
    if wide:
        W, pad, ts, ss, hs, fs = 1200, 40, 30, 19, 20, 16
    else:
        W, pad, ts, ss, hs, fs = 600, 32, 34, 21, 23, 19
    out, y = [], pad + ts
    out.append(text(pad, y, t["title"], ts, weight=800))
    y += ss + 12
    out.append(text(pad, y, t["sub"], ss, MUTED))
    y += 56
    ev = t["events"]
    if wide:
        # 2월 9일(40일째) ~ 10월 말(300일째) 를 한 축에
        days = [40, 125, 278, 298]
        y += 50
        X = lambda d: pad + 40 + (W - pad * 2 - 160) * (d - 30) / (305 - 30)
        ly = y + 20
        out.append(f'<line x1="{pad}" y1="{ly}" x2="{W - pad}" y2="{ly}" stroke="{INK}" stroke-width="2"/>')
        for i, (d, (when, head, sub)) in enumerate(zip(days, ev)):
            x = X(d)
            new = i >= 2
            out.append(f'<circle cx="{x}" cy="{ly}" r="9" fill="{INK if new else BG}" stroke="{INK}" stroke-width="2.5"/>')
            up = i % 2 == 1
            ty = ly - 70 if up else ly + 44
            out.append(text(x, ty, when, fs, MUTED, 700, "middle"))
            out.append(text(x, ty + hs + 6, head, hs, INK, 800, "middle"))
            out.append(text(x, ty + hs + fs + 14, sub, fs, BODY, 400, "middle"))
        y = ly + 44 + hs + fs + 50
    else:
        for i, (when, head, sub) in enumerate(ev):
            new = i >= 2
            out.append(f'<circle cx="{pad + 12}" cy="{y}" r="10" fill="{INK if new else BG}" stroke="{INK}" stroke-width="2.5"/>')
            if i < len(ev) - 1:
                out.append(f'<line x1="{pad + 12}" y1="{y + 12}" x2="{pad + 12}" y2="{y + 98}" stroke="{INK}" stroke-width="2"/>')
            out.append(text(pad + 40, y - 14, when, fs, MUTED, 700))
            out.append(text(pad + 40, y + hs - 4, head, hs, INK, 800))
            out.append(text(pad + 40, y + hs + fs + 6, sub, fs, BODY))
            y += 110
        y += 10
    out.append(f'<line x1="{pad}" y1="{y - 14}" x2="{W - pad}" y2="{y - 14}" stroke="{RULE}" stroke-width="1"/>')
    y += 14
    out.append(text(pad, y, t["source"], (ss - 3) if wide else (ss - 4), MUTED))
    return wrap(W, round(y + pad), t["title"], t["desc"], out)


# =========================================================
# 10. 처음·끝 두 장 대 키프레임 열 장 (2026-10-06 클링 글)
# =========================================================
KEYS = {
    "ko": {
        "title": "처음과 끝 두 장에서, 열 장의 콘티로",
        "sub": "클링이 밝힌 사양을 바탕으로 그린 개념도",
        "rows": [("클링 3.0", "처음·끝 2장 · 최대 15초", 15, 2), ("클링 4.0", "키프레임 최대 10장 · 최대 30초", 30, 10)],
        "unit": "초",
        "fill": "사이는 AI가 채움",
        "source": "출처: 클링 4.0 사양 발표(2026. 9. 28), 업계 정리",
        "desc": "클링 3.0은 처음과 끝 두 장을 주면 최대 15초 사이를 AI가 채웠다. 클링 4.0은 최대 30초 길이에 키프레임을 10장까지 꽂아 장면 흐름을 정할 수 있다.",
    },
    "en": {
        "title": "Two frames become ten",
        "sub": "A conceptual sketch based on Kling's published specs",
        "rows": [("Kling 3.0", "First and last frame · up to 15 s", 15, 2), ("Kling 4.0", "Up to 10 keyframes · up to 30 s", 30, 10)],
        "unit": "s",
        "fill": "AI fills in between",
        "source": "Sources: Kling 4.0 spec sheet (Sep 28, 2026), industry coverage",
        "desc": "With Kling 3.0, you gave a first and last frame and the AI filled up to 15 seconds between. Kling 4.0 lets you pin up to 10 keyframes across up to 30 seconds to set the flow of a scene.",
    },
}


def keys(lang, wide):
    t = KEYS[lang]
    if wide:
        W, pad, ts, ss, hs, fs = 1200, 40, 30, 19, 21, 16
    else:
        W, pad, ts, ss, hs, fs = 600, 32, 34, 21, 24, 18
    out, y = [], pad + ts
    out.append(text(pad, y, t["title"], ts if wide or lang == "ko" else ts - 6, weight=800))
    y += ss + 12
    out.append(text(pad, y, t["sub"], ss, MUTED))
    y += 52
    x0, x1 = pad, W - pad
    X = lambda sec: x0 + (x1 - x0) * sec / 30
    fh = 52 if wide else 40
    for name, note, length, n in t["rows"]:
        out.append(text(pad, y, name, hs, INK, 800))
        out.append(text(pad + (130 if wide else 0), y + (0 if wide else fs + 10), note, fs, BODY))
        y += 22 if wide else fs + 32
        # 시간 막대
        out.append(f'<rect x="{x0}" y="{y + fh / 2 - 3}" width="{X(length) - x0}" height="6" rx="3" fill="{RULE}"/>')
        # 키프레임
        fw = min(fh * 1.4, (X(length) - x0) / n * 0.8)
        for k in range(n):
            cx = x0 + fw / 2 + (X(length) - fw - x0) * k / (n - 1)
            out.append(f'<rect x="{cx - fw / 2}" y="{y}" width="{fw}" height="{fh}" rx="5" fill="{INK}"/>')
            out.append(f'<circle cx="{cx - fw * 0.15}" cy="{y + fh * 0.55}" r="{fh * 0.16}" fill="{BG}"/>')
        if n == 2:
            out.append(text((X(0) + X(length)) / 2, y + fh / 2 - 10, t["fill"], fs - 1, MUTED, 400, "middle"))
        y += fh + 16
        # 눈금
        for sec in range(0, length + 1, 5):
            out.append(text(X(sec), y + fs, f"{sec}{t['unit']}", fs - 3, MUTED, 400, "middle" if 0 < sec < 30 else ("start" if sec == 0 else "end")))
        y += fs + 46
    out.append(f'<line x1="{pad}" y1="{y - 14}" x2="{W - pad}" y2="{y - 14}" stroke="{RULE}" stroke-width="1"/>')
    y += 14
    out.append(text(pad, y, t["source"], (ss - 3) if wide else (ss - 5), MUTED))
    return wrap(W, round(y + pad), t["title"], t["desc"], out)


# =========================================================
# 11. 지난 일주일 한눈에 (2026-10-07 주간 정리 글)
# =========================================================
WEEK = {
    "ko": {
        "title": "지난 일주일, 사람이 정하게 된 것",
        "sub": "9월 30일 ~ 10월 6일. 운에 맡기던 자리를 사람이 정하는 쪽으로",
        "cards": [("10. 1", "쇼피파이 캔버스", "가게 전체", "한 판에 펼쳐 놓고 고친다"),
                  ("10. 2", "DESIGN.md", "규칙", "AI가 읽는 디자인 규칙 한 장"),
                  ("9. 30 · 10. 2", "Ideogram 4.5 · FLUX 3", "고칠 자리", "고른 곳만 바뀌고 나머지는 그대로"),
                  ("10. 1", "InstructMesh", "고칠 부위", "3D 모델에서 문제 부위만 골라 고친다"),
                  ("10. 5", "챗GPT 이미지 광고", "광고 자리", "그림 옆에 붙는 새 지면"),
                  ("9. 28 ~", "클링 4.0", "장면 순서", "키프레임 열 장으로 콘티를 건넨다")],
        "source": "출처: 이 사이트 읽을거리 10월 1일 ~ 6일 글",
        "desc": "지난 일주일 나온 여섯 가지 소식. 쇼피파이 캔버스는 가게 전체, DESIGN.md는 규칙, Ideogram 4.5와 FLUX 3는 고칠 자리, InstructMesh는 3D의 고칠 부위, 챗GPT 이미지 광고는 새 광고 자리, 클링 4.0은 장면 순서를 다룬다.",
    },
    "en": {
        "title": "Last week: what you now decide",
        "sub": "Sep 30 – Oct 6. From leaving it to luck to deciding it yourself",
        "cards": [("Oct 1", "Shopify Canvas", "The whole store", "Lay it all out and edit"),
                  ("Oct 2", "DESIGN.md", "The rules", "One file of design rules for AI"),
                  ("Sep 30 · Oct 2", "Ideogram 4.5 · FLUX 3", "What to edit", "Only the chosen spot changes"),
                  ("Oct 1", "InstructMesh", "Which part to fix", "Fix only the flawed part of a 3D model"),
                  ("Oct 5", "ChatGPT image ads", "An ad slot", "A new placement beside images"),
                  ("Sep 28 –", "Kling 4.0", "Shot order", "Hand over a ten-frame storyboard")],
        "source": "Source: this site's articles, Oct 1–6",
        "desc": "Six stories from last week. Shopify Canvas covers the whole store, DESIGN.md the rules, Ideogram 4.5 and FLUX 3 what to edit, InstructMesh which 3D part to fix, ChatGPT image ads a new ad slot, and Kling 4.0 the order of shots.",
    },
}


def week(lang, wide):
    t = WEEK[lang]
    if wide:
        W, pad, ts, ss, ds, ns, ks, bs = 1200, 40, 30, 19, 15, 18, 26, 16
        cols, gap, ch = 3, 24, 170
    else:
        W, pad, ts, ss, ds, ns, ks, bs = 600, 32, 34, 21, 17, 20, 28, 18
        cols, gap, ch = 1, 16, 176
    out, y = [], pad + ts
    out.append(text(pad, y, t["title"], ts, weight=800))
    y += ss + 12
    sub = t["sub"]
    if wide:
        out.append(text(pad, y, sub, ss, MUTED))
    else:
        a, b = sub.split(". ", 1)
        out.append(text(pad, y, a + ".", ss, MUTED))
        y += ss + 10
        out.append(text(pad, y, b, ss, MUTED))
    y += 36
    cw = (W - pad * 2 - gap * (cols - 1)) / cols
    for i, (when, name, key, body) in enumerate(t["cards"]):
        cx = pad + (i % cols) * (cw + gap)
        cy = y + (i // cols) * (ch + gap)
        out.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="14" fill="{BG}" stroke="{INK}" stroke-width="1.5"/>')
        out.append(text(cx + 20, cy + 32, when, ds, MUTED, 700))
        out.append(text(cx + 20, cy + 32 + ns + 10, name, ns, INK, 700))
        out.append(f'<rect x="{cx + 20}" y="{cy + 32 + ns + 26}" width="{len(key) * ks * (1.0 if lang == "ko" else 0.56) + 24}" height="{ks + 16}" rx="{(ks + 16) / 2}" fill="{INK}"/>')
        out.append(text(cx + 32, cy + 32 + ns + 26 + ks + 2, key, ks, BG, 800))
        out.append(text(cx + 20, cy + ch - 20, body, bs, BODY))
    rows = -(-len(t["cards"]) // cols)
    y += rows * (ch + gap) + 30
    out.append(f'<line x1="{pad}" y1="{y - 14}" x2="{W - pad}" y2="{y - 14}" stroke="{RULE}" stroke-width="1"/>')
    y += 14
    out.append(text(pad, y, t["source"], (ss - 3) if wide else (ss - 4), MUTED))
    return wrap(W, round(y + pad), t["title"], t["desc"], out)


FIGS = {"openai-app-platforms": timeline, "chatgpt-plugin-extensions": scheme,
        "shopify-canvas-compare": canvas_compare, "design-md-anatomy": designmd,
        "image-edit-drift": drift, "flux3-bbox-layout": bbox, "instructmesh-flow": meshflow,
        "chatgpt-image-ad": adspot, "chatgpt-ads-timeline": adtime, "kling4-keyframes": keys,
        "week-1001-1006": week}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in FIGS.items():
        for lang in ("ko", "en"):
            base = name + ("-en" if lang == "en" else "")
            (OUT / f"{base}.svg").write_text(fn(lang, True), encoding="utf-8")
            (OUT / f"{base}-m.svg").write_text(fn(lang, False), encoding="utf-8")
            print(f"{base}.svg, {base}-m.svg")
