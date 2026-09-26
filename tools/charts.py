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
