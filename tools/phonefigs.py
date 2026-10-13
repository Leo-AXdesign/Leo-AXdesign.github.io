#!/usr/bin/env python3
"""
읽을거리 그림을 인스타 카드(1080×1350)용 세로 그림으로 다시 그립니다.

글에 들어간 SVG 를 줄여 넣으면 휴대폰에서 그림 속 글자가 너무 작아집니다(약 0.36배).
그래서 같은 데이터(figures.py, charts.py)를 그대로 가져와, 카드 크기에 맞춰 HTML 로 새로 그립니다.
글자 크기는 build-cards.py 의 위계를 따릅니다: 핵심 44~56px, 설명 34~40px, 가장 작아도 30px.

  RENDER[그림 이름](card) → (제목, 본문 HTML, 출처)   # build-cards.py 의 figure 카드가 씁니다
  없는 그림은 build-cards.py 가 원래 SVG 를 줄여 넣습니다.
"""
import html, importlib.util, pathlib

HERE = pathlib.Path(__file__).resolve().parent
e = html.escape


def _load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


F = _load("figures")
C = _load("charts")

CSS = """
.pf { flex: 1; min-height: 0; display: flex; flex-direction: column; margin-top: 36px; }
.pf-title { font-size: 60px; line-height: 1.22; font-weight: 800; letter-spacing: -0.04em; text-wrap: balance; }
.pf-sub { margin-top: 16px; font-size: 36px; line-height: 1.4; color: #555; text-wrap: pretty; }
.pf-body { flex: 1; min-height: 0; margin-top: 40px; display: flex; flex-direction: column; }
.pf-src { margin-top: 24px; font-size: 30px; line-height: 1.35; color: #767676; }
.pf-label { font-size: 32px; font-weight: 800; color: #767676; letter-spacing: -0.01em; }

/* 빙산: 위에 보이는 것, 물결, 아래 남은 일 */
.ice-top { display: flex; align-items: center; gap: 28px; margin-top: 14px; }
.ice-img { width: 150px; height: 100px; border: 4px solid #111; border-radius: 16px; background: #F2F2F2; flex: none; }
.ice-top b { font-size: 46px; font-weight: 800; letter-spacing: -0.03em; }
.wave { margin: 22px 0 18px; height: 24px; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 14px; }
.box { background: #111; color: #fff; border-radius: 18px; padding: 20px 24px; display: flex; flex-direction: column; }
.box b { font-size: 40px; font-weight: 800; letter-spacing: -0.03em; }
.box span { margin-top: 6px; font-size: 30px; line-height: 1.32; color: #CFCFCF; }

/* 단계 */
.steps { display: flex; flex-direction: column; gap: 16px; flex: 1; }
.step { flex: 1; display: flex; align-items: center; gap: 30px; border: 4px solid #111; border-radius: 22px; padding: 0 32px; }
.step .no { flex: none; width: 76px; height: 76px; border-radius: 50%; background: #111; color: #fff;
            display: flex; align-items: center; justify-content: center; font-size: 40px; font-weight: 800; }
.step b { display: block; font-size: 50px; font-weight: 800; letter-spacing: -0.03em; }
.step span { display: block; margin-top: 6px; font-size: 33px; line-height: 1.35; color: #555; }

/* 막대 */
.bars { display: flex; flex-direction: column; gap: 22px; }
.bars + .bars { margin-top: 40px; }
.bar-row { display: grid; grid-template-columns: 360px 1fr; align-items: center; gap: 22px; }
.bar-row .lb { font-size: 36px; font-weight: 700; letter-spacing: -0.02em; }
.bar-row .tr { display: flex; align-items: center; gap: 16px; }
.bar-row .bar { height: 46px; border-radius: 8px; background: #111; min-width: 8px; }
.bar-row .bar.dim { background: #BDBDBD; }
.bar-row .v { font-size: 38px; font-weight: 800; white-space: nowrap; }
.bars.big { gap: 40px; }
.bars.big .bar-row .lb { font-size: 42px; }
.bars.big .bar-row .bar { height: 64px; }
.bars.big .bar-row .v { font-size: 46px; }
.bars.big .bars-head b { font-size: 46px; }
.bars-head { display: flex; align-items: baseline; gap: 16px; margin-bottom: 4px; }
.bars-head b { font-size: 40px; font-weight: 800; }
.bars-head span { font-size: 32px; color: #767676; }

/* 다시 뽑기 vs 고쳐 쓰기 */
.drift-row { margin-top: 10px; }
.drift-row + .drift-row { margin-top: 44px; }
.drift-row .pf-label { color: #111; font-size: 40px; }
.drift-row svg { display: block; width: 100%; margin-top: 18px; }
.asks { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-top: 12px; }
.asks span { font-size: 30px; line-height: 1.3; color: #555; text-align: center; }

/* 상자 배치 */
.canvas { position: relative; width: 100%; aspect-ratio: 16 / 9; border: 4px solid #111; border-radius: 18px; margin-top: 18px; }
.canvas div { position: absolute; border: 4px dashed #111; border-radius: 12px; display: flex; align-items: center;
              justify-content: center; text-align: center; font-size: 32px; font-weight: 800; line-height: 1.25; padding: 6px; box-sizing: border-box; }
.legend { display: grid; grid-template-columns: 1fr; gap: 14px; margin-top: 34px; }
.legend p { margin: 0; font-size: 36px; line-height: 1.35; }
.legend code { font-family: 'SF Mono', Menlo, Consolas, monospace; font-size: 32px; background: #F2F2F2; padding: 4px 12px; border-radius: 8px; }

/* DESIGN.md */
.code { background: #F2F2F2; border-radius: 20px; padding: 26px 32px; font-family: 'SF Mono', Menlo, Consolas, monospace;
        font-size: 30px; line-height: 1.38; white-space: pre-wrap; word-break: break-all; }
.code .k { font-weight: 800; } .code .h { font-weight: 800; font-family: Pretendard, sans-serif; }
.code .p { font-family: Pretendard, sans-serif; color: #444; } .code .f { color: #8A8A8A; }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 24px; }
.two div { border: 4px solid #111; border-radius: 18px; padding: 18px 24px; }
.two b { display: block; font-size: 38px; font-weight: 800; }
.two span { display: block; margin-top: 4px; font-size: 30px; color: #555; line-height: 1.35; }
"""


def iceberg(lang="ko"):
    d = F.ICEBERG[lang]
    boxes = "".join(f'<div class="box"><b>{e(h)}</b><span>{e(t)}</span></div>' for h, t in d["below"])
    path = "M0,14 " + "".join(f"Q{i * 30 - 15},{2 if i % 2 else 26} {i * 30},14 " for i in range(1, 31))
    wave = f'<svg class="wave" viewBox="0 0 900 28" preserveAspectRatio="none"><path d="{path}" fill="none" stroke="#111" stroke-width="4"/></svg>'
    body = (f'<div class="pf-label">{e(d["top_head"])}</div>'
            f'<div class="ice-top"><div class="ice-img"></div><b>{e(d["top"])}</b></div>{wave}'
            f'<div class="pf-label">{e(d["below_head"])}</div><div class="grid2">{boxes}</div>')
    return d["title"], d["sub"], body, d["source"]


def aisteps(lang="ko"):
    d = F.AISTEPS[lang]
    rows = "".join(f'<div class="step"><div class="no">{i}</div><div><b>{e(h)}</b><span>{e(" · ".join(ls))}</span></div></div>'
                   for i, (h, ls) in enumerate(d["steps"], 1))
    return d["title"], d["sub"], f'<div class="steps">{rows}</div>', d["source"]


def drift(lang="ko"):
    d = F.DRIFT[lang]
    w, h, gap = 210, 168, 20
    rows = ""
    for r, is_drift in enumerate((True, False)):
        parts = []
        for k in range(4):
            parts += F.scene(k * (w + gap), 4, w, h, k, is_drift, 0 if is_drift else k)
        svg = f'<svg viewBox="-4 0 {4 * w + 3 * gap + 8} {h + 12}">{"".join(parts)}</svg>'
        rows += f'<div class="drift-row"><div class="pf-label">{e(d["rows"][r])}</div>{svg}</div>'
    asks = "".join(f"<span>{e(a or d['cols'][0])}</span>" for a in d["asks"])
    body = f'{rows}<div class="asks">{asks}</div>'
    return d["title"], d["sub"], body, d["source"]


def bbox(lang="ko"):
    d = F.BBOX[lang]
    boxes = "".join(f'<div style="left:{x * 100}%;top:{y * 100}%;width:{w * 100}%;height:{h * 100}%">{e(label)}</div>'
                    for _, label, (x, y, w, h) in d["items"])
    note = ("요소마다 상자로 자리와 크기를 먼저 정하고, 상자에 참고 이미지를 붙인다." if lang == "ko"
            else "Set each element's position and size with a box first, then attach reference images.")
    body = (f'<div class="canvas">{boxes}</div><div class="pf-src" style="margin-top:14px">{e(d["canvas"])}</div>'
            f'<div class="legend"><p>{e(note)}</p></div>')
    return d["title"], d["sub"], body, d["source"]


def designmd(lang="ko"):
    d = F.DESIGNMD[lang]
    cls = {"fence": "f", "k": "k", "v": "", "h": "h", "p": "p"}
    # 카드에 들어가도록 글자·둥근 정도 줄은 뺍니다 (원래 그림에는 있습니다)
    drop = ("typography:", "fontFamily", "rounded:", "md: 8px")
    keep = [l for l in d["lines"] if not any(x in l[0] for x in drop)]
    code = "\n".join(f'<span class="{cls[t]}">{e(s)}</span>' for s, t in keep)
    two = (f'<div class="two"><div><b>{e(d["a_head"])}</b><span>{e(" ".join(d["a_body"]))}</span></div>'
           f'<div><b>{e(d["b_head"])}</b><span>{e(" ".join(d["b_body"]))}</span></div></div>')
    return d["title"], d["sub"], f'<div class="code">{code}</div>{two}', d["source"]


def chart(name, panels=None, sub=None):
    """panels: 보여 줄 패널 번호. 카드에 다 안 들어가거나 지난 정보(끝난 할인 등)는 뺍니다."""
    def render(lang="ko"):
        c = C.CHARTS[name if lang == "ko" else f"{name}-en"]
        use = [c["panels"][i] for i in panels] if panels else c["panels"]
        out = ""
        for pi, p in enumerate(use):
            top = max(v for _, v, _ in p["rows"])   # 패널마다 단위가 달라서(점수·달러 등) 따로 잽니다
            rows = ""
            for label, v, shown in p["rows"]:
                pct = max(1.5, v / top * 100)
                dim = " dim" if pi > 0 else ""
                rows += (f'<div class="bar-row"><div class="lb">{e(label)}</div><div class="tr">'
                         f'<div class="bar{dim}" style="width:{pct * 0.62:.1f}%"></div><div class="v">{e(shown)}</div></div></div>')
            head = f'<div class="bars-head"><b>{e(p["title"])}</b><span>{e(p.get("hint", ""))}</span></div>'
            out += f'<div class="bars">{head}{rows}</div>'
        rows = sum(len(p["rows"]) for p in use)
        if rows <= 6:   # 줄이 적으면 막대와 글자를 키워 카드를 채웁니다
            out = out.replace('class="bars"', 'class="bars big"')
        return c["title"], sub or c["sub"], out, " ".join(c["source"])
    return render


RENDER = {
    "ai-draft-iceberg": iceberg,
    "ai-draft-steps": aisteps,
    "image-edit-drift": drift,
    "flux3-bbox-layout": bbox,
    "design-md-anatomy": designmd,
    "flux3-price": chart("flux3-price", panels=[0], sub="API 한 장 값 · 정가 기준 (발표 할인은 10월 8일에 끝남)"),   # 발표 할인(10/8까지)은 끝나서 정가만
    "designmd-contrast": chart("designmd-contrast"),
}


# 막대 차트는 모양이 같아서, 작은 차트는 손대지 않아도 자동으로 다시 그립니다.
for _n, _c in C.CHARTS.items():
    # 줄 수 + 패널 수가 7 이하일 때만 카드에 여유 있게 들어갑니다. 넘으면 원래 SVG 를 씁니다.
    if not _n.endswith("-en") and _n not in RENDER and sum(len(p["rows"]) + 1 for p in _c["panels"]) <= 7:
        RENDER[_n] = chart(_n)


def card_body(name):
    """figure 카드 본문. 다시 그린 그림이 없으면 None."""
    fn = RENDER.get(name)
    if not fn:
        return None
    title, sub, body, src = fn()
    return (f'<div class="pf"><div class="pf-title">{e(title)}</div><div class="pf-sub">{e(sub)}</div>'
            f'<div class="pf-body">{body}</div><div class="pf-src">{e(src)}</div></div>')
