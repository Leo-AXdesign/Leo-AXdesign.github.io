#!/usr/bin/env python3
"""
읽을거리에 넣는 비교 차트(SVG)를 만듭니다.

  python3 tools/charts.py

- 단위가 다른 지표는 한 축에 섞지 않고 작은 차트 여러 개로 나눕니다.
- 넓은 화면용(articles/img/<이름>.svg)과 폰용(<이름>-m.svg)을 같이 만듭니다.
  글 변환기가 폰에서는 -m 판을 자동으로 씁니다.
- 막대는 모두 같은 검정입니다. 모델 이름을 축에 적어서, 색으로 한쪽을 강조하지 않습니다.
- 막대 끝 4px 둥글게, 기준선 쪽은 각지게, 값은 막대 끝에. (차트 가이드의 막대 규격)

새 차트는 아래 CHARTS 에 하나 추가하면 됩니다.
"""
import html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "articles" / "img"
e = html.escape

INK, BODY, MUTED, RULE, BG = "#111111", "#444444", "#6B6B6B", "#D9D9D9", "#FFFFFF"
FONT = "Pretendard, 'Apple SD Gothic Neo', 'Malgun Gothic', 'Noto Sans KR', sans-serif"

CHARTS = {
    "fable-astra-cost": {
        "title": "같은 점수, 다른 비용",
        "sub": "Artificial Analysis 종합 지수 v4.3 · 두 모델 모두 최대 추론 설정",
        # 폰판에서는 한 항목이 한 줄, 넓은 판에서는 이어 붙입니다
        "source": ["출처: Artificial Analysis (2026. 9. 9).", "비용과 토큰은 지수 과제 하나당 평균."],
        "desc": "종합 지수는 Claude Fable 5.1과 GPT-6 아스트라 모두 53점. 과제 하나당 비용은 Fable 5.1 7.63달러, 아스트라 3.26달러. "
                "과제 하나당 출력 토큰은 Fable 5.1 약 7만 8천 개, 아스트라 약 2만 7천 개.",
        "panels": [
            {"title": "종합 지수", "hint": "높을수록 좋음",
             "rows": [("Claude Fable 5.1", 53, "53"), ("GPT-6 아스트라", 53, "53")]},
            {"title": "과제당 비용", "hint": "낮을수록 좋음",
             "rows": [("Claude Fable 5.1", 7.63, "$7.63"), ("GPT-6 아스트라", 3.26, "$3.26")]},
            {"title": "과제당 출력 토큰", "hint": "낮을수록 좋음",
             "rows": [("Claude Fable 5.1", 78, "7.8만"), ("GPT-6 아스트라", 27, "2.7만")]},
        ],
    },
    # 영문판 글(content/articles-en/claude-fable-5-1-vs-gpt-6-astra.md)에 쓰는 같은 차트
    "fable-astra-cost-en": {
        "title": "Same score, different cost",
        "sub": "Artificial Analysis Intelligence Index v4.3 · both at maximum reasoning",
        "source": ["Source: Artificial Analysis (Sep 9, 2026).", "Cost and tokens are averages per index task."],
        "desc": "Both Claude Fable 5.1 and GPT-6 Astra score 53 on the index. Cost per task: Fable 5.1 $7.63, Astra $3.26. "
                "Output tokens per task: Fable 5.1 about 78,000, Astra about 27,000.",
        "panels": [
            {"title": "Intelligence Index", "hint": "higher is better",
             "rows": [("Claude Fable 5.1", 53, "53"), ("GPT-6 Astra", 53, "53")]},
            {"title": "Cost per task", "hint": "lower is better",
             "rows": [("Claude Fable 5.1", 7.63, "$7.63"), ("GPT-6 Astra", 3.26, "$3.26")]},
            {"title": "Output tokens per task", "hint": "lower is better",
             "rows": [("Claude Fable 5.1", 78, "78k"), ("GPT-6 Astra", 27, "27k")]},
        ],
    },
    # ---- 2026-09-29 'Claude Sonnet 5.5' 글 ----
    "sonnet55-lowtide": {
        "title": "같은 페이지를 만드는 데 든 것",
        "sub": "한 페이지짜리 행사 사이트 'Low Tide' · Claude Code, 높은 노력 설정 · 결과 순위: Opus 5.5 → Sonnet 5.5 → Sonnet 5",
        "source": ["출처: Thomas Wiegold 블로그의 Sonnet 5.5 리뷰.", "과제 한 번씩 돌린 개인 시험이라 참고용."],
        "desc": "같은 과제에 든 비용은 Opus 5.5 1.94달러, Sonnet 5.5 1.35달러, Sonnet 5 1.08달러. 시간은 9분, 8분, 6분. 출력 토큰은 4만 5천, 5만 8천, 2만 5천 개.",
        "panels": [
            {"title": "비용", "hint": "낮을수록 좋음",
             "rows": [("Opus 5.5", 1.94, "$1.94"), ("Sonnet 5.5", 1.35, "$1.35"), ("Sonnet 5", 1.08, "$1.08")]},
            {"title": "걸린 시간", "hint": "낮을수록 좋음",
             "rows": [("Opus 5.5", 9, "9분"), ("Sonnet 5.5", 8, "8분"), ("Sonnet 5", 6, "6분")]},
            {"title": "출력 토큰", "hint": "말의 양",
             "rows": [("Opus 5.5", 45.1, "4.5만"), ("Sonnet 5.5", 57.8, "5.8만"), ("Sonnet 5", 25, "2.5만")]},
        ],
    },
    "sonnet55-lowtide-en": {
        "title": "What it took to build the same page",
        "sub": "One-page event site 'Low Tide' · Claude Code, high effort · Ranking: Opus 5.5 → Sonnet 5.5 → Sonnet 5",
        "source": ["Source: Thomas Wiegold's Sonnet 5.5 review.", "A personal test, one run each. For reference only."],
        "desc": "Cost for the same task: Opus 5.5 $1.94, Sonnet 5.5 $1.35, Sonnet 5 $1.08. Time: 9, 8 and 6 minutes. Output tokens: 45k, 58k, 25k.",
        "panels": [
            {"title": "Cost", "hint": "lower is better",
             "rows": [("Opus 5.5", 1.94, "$1.94"), ("Sonnet 5.5", 1.35, "$1.35"), ("Sonnet 5", 1.08, "$1.08")]},
            {"title": "Time", "hint": "lower is better",
             "rows": [("Opus 5.5", 9, "9 min"), ("Sonnet 5.5", 8, "8 min"), ("Sonnet 5", 6, "6 min")]},
            {"title": "Output tokens", "hint": "how much it said",
             "rows": [("Opus 5.5", 45.1, "45k"), ("Sonnet 5.5", 57.8, "58k"), ("Sonnet 5", 25, "25k")]},
        ],
    },
    "price-tiers-0929": {
        "title": "100만 토큰당 가격, 9월 29일 기준",
        "sub": "각 회사 발표 가격 · 막대가 짧을수록 쌈",
        "source": ["출처: Anthropic, OpenAI 발표.", "캐시·할인 가격은 뺀 기본 가격."],
        "desc": "입력 가격은 Sonnet 5.5와 GPT-6 Sol이 2달러, Opus 5.5 4달러, Fable 5.1과 GPT-6 아스트라 10달러. 출력 가격은 각각 10달러, 20달러, 50달러.",
        "panels": [
            {"title": "입력", "hint": "읽는 값",
             "rows": [("Claude Sonnet 5.5", 2, "$2"), ("GPT-6 Sol", 2, "$2"), ("Claude Opus 5.5", 4, "$4"),
                      ("Claude Fable 5.1", 10, "$10"), ("GPT-6 아스트라", 10, "$10")]},
            {"title": "출력", "hint": "쓰는 값",
             "rows": [("Claude Sonnet 5.5", 10, "$10"), ("GPT-6 Sol", 10, "$10"), ("Claude Opus 5.5", 20, "$20"),
                      ("Claude Fable 5.1", 50, "$50"), ("GPT-6 아스트라", 50, "$50")]},
        ],
    },
    "price-tiers-0929-en": {
        "title": "Price per 1M tokens, as of Sep 29",
        "sub": "List prices from each company · shorter bar is cheaper",
        "source": ["Sources: Anthropic and OpenAI announcements.", "Base prices, excluding cache and discounts."],
        "desc": "Input: Sonnet 5.5 and GPT-6 Sol $2, Opus 5.5 $4, Fable 5.1 and GPT-6 Astra $10. Output: $10, $20 and $50 respectively.",
        "panels": [
            {"title": "Input", "hint": "reading",
             "rows": [("Claude Sonnet 5.5", 2, "$2"), ("GPT-6 Sol", 2, "$2"), ("Claude Opus 5.5", 4, "$4"),
                      ("Claude Fable 5.1", 10, "$10"), ("GPT-6 Astra", 10, "$10")]},
            {"title": "Output", "hint": "writing",
             "rows": [("Claude Sonnet 5.5", 10, "$10"), ("GPT-6 Sol", 10, "$10"), ("Claude Opus 5.5", 20, "$20"),
                      ("Claude Fable 5.1", 50, "$50"), ("GPT-6 Astra", 50, "$50")]},
        ],
    },
    # ---- 2026-09-30 '데브데이' 글 ----
    "devday-sol-cost": {
        "title": "점수는 비슷하게, 값은 5분의 1로",
        "sub": "Artificial Analysis 종합 지수와 지수 과제 하나당 비용",
        "source": ["출처: Artificial Analysis 수치(데브데이 발표 정리, DEV Community 인용).", "9월 29일 기준. 지수는 자주 개편됨."],
        "desc": "종합 지수는 Claude Opus 5.5 58점, GPT-6 아스트라 53점, GPT-6.1 Sol 52점. 과제 하나당 비용은 5.98달러, 3.26달러, 0.72달러.",
        "panels": [
            {"title": "종합 지수", "hint": "높을수록 좋음",
             "rows": [("Claude Opus 5.5", 58, "58"), ("GPT-6 아스트라", 53, "53"), ("GPT-6.1 Sol", 52, "52")]},
            {"title": "과제당 비용", "hint": "낮을수록 좋음",
             "rows": [("Claude Opus 5.5", 5.98, "$5.98"), ("GPT-6 아스트라", 3.26, "$3.26"), ("GPT-6.1 Sol", 0.72, "$0.72")]},
        ],
    },
    "devday-sol-cost-en": {
        "title": "A similar score at a fifth of the price",
        "sub": "Artificial Analysis Intelligence Index and cost per index task",
        "source": ["Source: Artificial Analysis figures (as compiled in a DevDay roundup on DEV Community).", "As of Sep 29. The index is revised often."],
        "desc": "Index score: Claude Opus 5.5 58, GPT-6 Astra 53, GPT-6.1 Sol 52. Cost per task: $5.98, $3.26, $0.72.",
        "panels": [
            {"title": "Intelligence Index", "hint": "higher is better",
             "rows": [("Claude Opus 5.5", 58, "58"), ("GPT-6 Astra", 53, "53"), ("GPT-6.1 Sol", 52, "52")]},
            {"title": "Cost per task", "hint": "lower is better",
             "rows": [("Claude Opus 5.5", 5.98, "$5.98"), ("GPT-6 Astra", 3.26, "$3.26"), ("GPT-6.1 Sol", 0.72, "$0.72")]},
        ],
    },
    # ---- 2026-10-01 '쇼피파이 캔버스' 글 ----
    "canvas-store-time": {
        "title": "가게 하나를 여는 데 걸린 시간",
        "sub": "쇼피파이 프로덕트 디렉터 벤 셀의 말 · 같은 가게를 같은 조건으로 잰 기록은 아님",
        "source": ["출처: Shopify 캔버스 발표(2026. 10. 1), TechCrunch 인용.", "2주는 달력으로 14일(2만 160분)로 계산."],
        "desc": "벤 셀은 12년 전 코딩을 할 줄 알면서도 Kotn 가게의 기본 모습을 만드는 데 2주가 걸렸고, 지금은 캔버스로 완전히 맞춤형 가게를 20분 만에 만든다고 말했다.",
        "panels": [
            {"title": "걸린 시간", "hint": "분으로 바꿔 같은 축에",
             "rows": [("2014년, Kotn 직접 코딩", 20160, "약 2주"), ("2026년, 캔버스와 사이드킥", 20, "약 20분")]},
        ],
    },
    "canvas-store-time-en": {
        "title": "Time to get a store up",
        "sub": "As told by Shopify Director of Product Ben Sehl · not a like-for-like measurement",
        "source": ["Source: Shopify's Canvas announcement (Oct 1, 2026), as quoted by TechCrunch.", "Two weeks counted as 14 calendar days (20,160 min)."],
        "desc": "Ben Sehl said that 12 years ago, even knowing how to code, it took him two weeks to get a rough Kotn store working, and that a fully custom store now takes about twenty minutes with Canvas.",
        "panels": [
            {"title": "Time taken", "hint": "both in minutes, same axis",
             "rows": [("2014, Kotn, hand-coded", 20160, "~2 weeks"), ("2026, Canvas + Sidekick", 20, "~20 min")]},
        ],
    },
    # ---- 2026-10-02 'DESIGN.md' 글 ----
    "designmd-contrast": {
        "title": "흰 바탕 위 글자색 대비",
        "sub": "이 사이트의 회색 넷과 후보 하나 · 본문 글자는 4.5 : 1 이상이어야 WCAG AA 통과",
        "source": ["design.md lint 0.4.0 으로 확인. 값은 WCAG 대비율.", "#767676 은 바꿔 볼 후보."],
        "desc": "흰 바탕 위 대비율. #111111 18.9, #2C2C2C 14.0, #6B6B6B 5.3, #767676 4.5, #A3A3A3 2.5. 4.5보다 낮은 #A3A3A3만 본문 글자 기준을 넘지 못한다.",
        "panels": [
            {"title": "대비율", "hint": "높을수록 읽기 쉬움",
             "rows": [("#111111 제목", 18.88, "18.9"), ("#2C2C2C 본문", 13.97, "14.0"), ("#6B6B6B 설명", 5.33, "5.3"),
                      ("#767676 후보", 4.54, "4.5"), ("#A3A3A3 주소·태그", 2.52, "2.5 ✕")]},
        ],
    },
    "designmd-contrast-en": {
        "title": "Text contrast on white",
        "sub": "Four grays on this site plus one candidate · body text needs 4.5 : 1 or more to pass WCAG AA",
        "source": ["Checked with design.md lint 0.4.0. Values are WCAG contrast ratios.", "#767676 is a candidate replacement."],
        "desc": "Contrast on white: #111111 18.9, #2C2C2C 14.0, #6B6B6B 5.3, #767676 4.5, #A3A3A3 2.5. Only #A3A3A3 falls below 4.5.",
        "panels": [
            {"title": "Contrast ratio", "hint": "higher is easier to read",
             "rows": [("#111111 headings", 18.88, "18.9"), ("#2C2C2C body", 13.97, "14.0"), ("#6B6B6B descriptions", 5.33, "5.3"),
                      ("#767676 candidate", 4.54, "4.5"), ("#A3A3A3 domains, tags", 2.52, "2.5 ✕")]},
        ],
    },
}


def bar(x, y, w, h, r):
    """오른쪽 끝만 둥근 막대 (기준선 쪽은 각지게)."""
    r = min(r, w / 2, h / 2)
    return (f'<path d="M{x} {y}H{x + w - r}A{r} {r} 0 0 1 {x + w} {y + r}V{y + h - r}'
            f'A{r} {r} 0 0 1 {x + w - r} {y + h}H{x}Z" fill="{INK}"/>')


def panel(p, x, y, width, s):
    """작은 차트 하나. s 는 글자·막대 크기 묶음."""
    out = [f'<text x="{x}" y="{y + s["t"]}" font-size="{s["t"]}" font-weight="700" fill="{INK}">{e(p["title"])}</text>',
           f'<text x="{x}" y="{y + s["t"] + s["gap"] + s["h"]}" font-size="{s["h"]}" fill="{MUTED}">{e(p["hint"])}</text>']
    top = y + s["t"] + s["gap"] + s["h"] + s["head"]
    peak = max(v for _, v, _ in p["rows"])
    room = width - s["valroom"]
    for i, (name, v, label) in enumerate(p["rows"]):
        ly = top + i * s["row"] + s["l"]
        by = ly + s["lgap"]
        w = max(room * v / peak, s["bh"])
        out.append(f'<text x="{x}" y="{ly}" font-size="{s["l"]}" fill="{BODY}">{e(name)}</text>')
        out.append(bar(x, by, w, s["bh"], s["r"]))
        out.append(f'<text x="{x + w + s["vgap"]}" y="{by + s["bh"] / 2 + s["v"] * 0.36}" font-size="{s["v"]}" '
                   f'font-weight="700" fill="{INK}">{e(label)}</text>')
    bottom = top + len(p["rows"]) * s["row"]
    out.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{bottom}" stroke="{RULE}" stroke-width="{s["axis"]}"/>')
    return "\n    ".join(out), bottom


def svg(c, wide):
    if wide:   # 본문 폭 720px 에 0.6 배로 들어갑니다
        W, pad, gap = 1200, 40, 60
        s = dict(t=24, h=18, gap=10, head=26, l=18, lgap=10, bh=30, row=78, r=7, v=22, vgap=12, valroom=96, axis=1.6)
        cols = len(c["panels"])
        pw = (W - pad * 2 - gap * (cols - 1)) / cols
    else:      # 폰 본문 폭 335px 에 0.56 배로 들어갑니다
        W, pad = 600, 32
        s = dict(t=30, h=22, gap=10, head=30, l=23, lgap=12, bh=36, row=94, r=7, v=28, vgap=14, valroom=120, axis=1.8)
        pw = W - pad * 2
    title_s, sub_s, src_s = (30, 19, 16) if wide else (36, 22, 19)
    parts, y = [], pad + title_s
    parts.append(f'<text x="{pad}" y="{y}" font-size="{title_s}" font-weight="800" fill="{INK}" letter-spacing="-0.5">{e(c["title"])}</text>')
    # 폰판은 폭이 좁아서 부제를 ' · ' 기준으로 줄을 나눕니다
    for line in ([c["sub"]] if wide else c["sub"].split(" · ")):
        y += sub_s + 12
        parts.append(f'<text x="{pad}" y="{y}" font-size="{sub_s}" fill="{MUTED}">{e(line)}</text>')
    y += 40
    bottoms = []
    for i, p in enumerate(c["panels"]):
        if wide:
            g, b = panel(p, pad + i * (pw + gap), y, pw, s)
        else:
            g, b = panel(p, pad, y, pw, s)
            y = b + 44
        parts.append(g)
        bottoms.append(b)
    y = (max(bottoms) if wide else bottoms[-1]) + (44 if wide else 40)
    parts.append(f'<line x1="{pad}" y1="{y - 22}" x2="{W - pad}" y2="{y - 22}" stroke="{RULE}" stroke-width="1"/>')
    src = [" ".join(c["source"])] if wide else c["source"]
    for k, line in enumerate(src):
        parts.append(f'<text x="{pad}" y="{y + 4 + k * (src_s + 10)}" font-size="{src_s}" fill="{MUTED}">{e(line)}</text>')
    y += (len(src) - 1) * (src_s + 10)
    H = round(y + pad)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">\n'
            f'  <title id="t">{e(c["title"])}</title>\n  <desc id="d">{e(c["desc"])}</desc>\n'
            f'  <rect width="{W}" height="{H}" rx="20" fill="{BG}"/>\n'
            f'  <g font-family="{FONT}">\n    ' + "\n    ".join(parts) + "\n  </g>\n</svg>\n")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, c in CHARTS.items():
        (OUT / f"{name}.svg").write_text(svg(c, True), encoding="utf-8")
        (OUT / f"{name}-m.svg").write_text(svg(c, False), encoding="utf-8")
        print(f"{name}.svg, {name}-m.svg")
