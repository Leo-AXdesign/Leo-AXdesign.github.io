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


FIGS = {"openai-app-platforms": timeline, "chatgpt-plugin-extensions": scheme,
        "shopify-canvas-compare": canvas_compare, "design-md-anatomy": designmd}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in FIGS.items():
        for lang in ("ko", "en"):
            base = name + ("-en" if lang == "en" else "")
            (OUT / f"{base}.svg").write_text(fn(lang, True), encoding="utf-8")
            (OUT / f"{base}-m.svg").write_text(fn(lang, False), encoding="utf-8")
            print(f"{base}.svg, {base}-m.svg")
