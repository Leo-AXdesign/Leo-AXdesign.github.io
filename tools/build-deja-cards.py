#!/usr/bin/env python3
"""
'AI 디자인 기시감' 캐러셀 10장 (1080×1350)

  python3 tools/build-deja-cards.py

- 근거: 앤트로픽 frontend-design 스킬(github.com/anthropics/skills) 원문의
  'AI-generated design right now clusters around some traits' 목록과 'commonest tells' 목록 (2026-11-06 확인).
- 3~8장의 작은 화면은 그 목록을 보고 이 스크립트가 HTML로 다시 그린 예시입니다. 실제 사이트 캡처가 아닙니다.
- 카드 틀은 1탄(build-skills-cards.py)과 같고, 'mock' 카드만 여기서 더합니다.
- 결과: social/cards/ai-deja-vu/01.jpg … + caption.txt, social/cards/index.json 갱신
"""
import html, importlib.util, pathlib, re, tempfile

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec_ = importlib.util.spec_from_file_location("build_skills_cards", ROOT / "tools" / "build-skills-cards.py")
SC = importlib.util.module_from_spec(spec_)
spec_.loader.exec_module(SC)
BC = SC.BC
from snap import shoot

e = html.escape
SET_ID = "ai-deja-vu"
SC.KICKER = "AI 디자인 기시감"

SC.EXTRA_CSS += """
/* 예시 화면 카드: 위에 한 줄 요지, 가운데 작은 화면, 아래 설명 */
.mock .cap { margin-top: 64px; font-size: 70px; line-height: 1.22; font-weight: 800; letter-spacing: -0.045em; white-space: pre-line; }
.mock .screen { margin-top: 44px; height: 600px; border-radius: 24px; overflow: hidden; border: 2px solid #E4E4E4; position: relative; }
.mock .l3 { margin-top: 36px; }
.mock .note { margin-top: 14px; font-size: 30px; font-weight: 600; color: #8A8A8A; }
.mock .progress { margin-top: auto; }

/* 1. 크림 + 세리프 + 테라코타 */
.s-cream { background: #F4F1EA; color: #1F1B16; padding: 56px 60px; box-sizing: border-box; height: 100%; }
.s-cream .nav { display: flex; justify-content: space-between; font: 500 26px/1 -apple-system, sans-serif; color: #6B6257; }
.s-cream h1 { margin: 92px 0 0; font: 400 96px/1.02 Georgia, "Times New Roman", serif; letter-spacing: -0.02em; }
.s-cream p { margin: 28px 0 0; font: 400 28px/1.5 -apple-system, sans-serif; color: #6B6257; max-width: 560px; }
.s-cream .btn { display: inline-block; margin-top: 40px; padding: 20px 36px; border-radius: 999px; background: #D97757; color: #fff; font: 600 26px/1 -apple-system, sans-serif; }

/* 2. 검정 + 형광 포인트 하나 */
.s-acid { background: #0B0B0B; color: #F2F2F2; padding: 56px 60px; box-sizing: border-box; height: 100%; font-family: -apple-system, sans-serif; }
.s-acid .nav { display: flex; justify-content: space-between; font-size: 26px; color: #8A8A8A; }
.s-acid h1 { margin: 96px 0 0; font-size: 104px; line-height: 0.98; font-weight: 800; letter-spacing: -0.05em; }
.s-acid h1 em { font-style: normal; color: #C6FF3D; }
.s-acid .btn { display: inline-block; margin-top: 52px; padding: 22px 38px; background: #C6FF3D; color: #0B0B0B; font-size: 26px; font-weight: 700; }

/* 3. 신문 같은 단 */
.s-paper { background: #fff; color: #111; padding: 40px 48px; box-sizing: border-box; height: 100%; font-family: Georgia, serif; }
.s-paper .mast { font-size: 70px; font-weight: 700; text-align: center; letter-spacing: -0.02em; padding-bottom: 14px; border-bottom: 1px solid #111; }
.s-paper .date { display: flex; justify-content: space-between; font: 500 20px/1 -apple-system, sans-serif; padding: 12px 0; border-bottom: 1px solid #111; }
.s-paper .cols { display: grid; grid-template-columns: 1.4fr 1fr 1fr; gap: 0; margin-top: 22px; }
.s-paper .col { padding: 0 20px; border-left: 1px solid #111; } .s-paper .col:first-child { border-left: 0; padding-left: 0; }
.s-paper .col b { display: block; font-size: 38px; line-height: 1.1; margin-bottom: 16px; }
.s-paper .col i { display: block; height: 12px; margin: 0 0 12px; background: #CFCFCF; }

/* 4. 똑같은 카드 + 같은 그림자 + 그라데이션 */
.s-saas { background: #F7F7F8; padding: 48px 48px; box-sizing: border-box; height: 100%; font-family: -apple-system, sans-serif; position: relative; overflow: hidden; }
.s-saas::before { content: ""; position: absolute; width: 700px; height: 700px; left: 160px; top: -380px; border-radius: 50%;
                  background: radial-gradient(circle, rgba(140,120,255,.35), rgba(80,200,255,.0) 70%); }
.s-saas h1 { position: relative; margin: 10px 0 40px; font-size: 56px; font-weight: 700; letter-spacing: -0.03em; text-align: center; color: #111; }
.s-saas .grid { position: relative; display: grid; grid-template-columns: repeat(3, 1fr); gap: 22px; }
.s-saas .c { background: #fff; border-radius: 22px; padding: 28px; box-shadow: 0 4px 16px rgba(0,0,0,.1); height: 330px; box-sizing: border-box; }
.s-saas .c i { display: block; width: 64px; height: 64px; border-radius: 16px; background: linear-gradient(135deg, #8C78FF, #50C8FF); }
.s-saas .c b { display: block; margin-top: 26px; height: 20px; width: 70%; background: #222; border-radius: 6px; }
.s-saas .c s { display: block; margin-top: 18px; height: 12px; background: #DDD; border-radius: 6px; }

/* 5. 어디에나 붙는 장식 라벨 */
.s-chrome { background: #111; color: #EDEDED; padding: 64px 60px; box-sizing: border-box; height: 100%; font-family: -apple-system, sans-serif; }
.s-chrome .eyebrow { font-size: 22px; font-weight: 700; letter-spacing: 0.22em; color: #9A9A9A; }
.s-chrome h1 { margin: 18px 0 0; font-size: 70px; line-height: 1.05; font-weight: 700; letter-spacing: -0.04em; }
.s-chrome .meta2 { margin-top: 26px; font-size: 26px; color: #9A9A9A; }
.s-chrome .row2 { margin-top: 56px; display: flex; justify-content: space-between; align-items: center; padding-top: 26px; border-top: 1px solid #333; }
.s-chrome .row2 code { font: 500 22px/1 ui-monospace, Menlo, monospace; color: #9A9A9A; }
.s-chrome .row2 a { font-size: 28px; font-weight: 600; color: #EDEDED; }
.s-chrome .label2 { margin-top: 34px; font-size: 26px; color: #BDBDBD; }

/* 6. 글자의 티 */
.s-type { background: #fff; color: #111; padding: 56px 60px; box-sizing: border-box; height: 100%; font-family: -apple-system, sans-serif; }
.s-type .eyebrow { font-size: 22px; font-weight: 700; letter-spacing: 0.2em; color: #888; }
.s-type h1 { margin: 16px 0 0; font-size: 78px; line-height: 1.05; font-weight: 800; letter-spacing: -0.045em; }
.s-type h1 em { font-family: Georgia, serif; font-weight: 400; color: #6A5CFF; }
.s-type ol { list-style: none; margin: 50px 0 0; padding: 0; display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.s-type li { border-top: 2px solid #111; padding-top: 18px; }
.s-type li span { display: block; font: 600 22px/1 ui-monospace, Menlo, monospace; color: #888; }
.s-type li b { display: block; margin-top: 14px; font-size: 30px; }
.s-type li i { display: block; margin-top: 14px; height: 12px; background: #DDD; }
"""

SCREENS = {
    "cream": '<div class="s-cream"><div class="nav"><span>Studio</span><span>Work · About · Contact</span></div>'
             '<h1>Crafted with<br>quiet care.</h1><p>Thoughtful design for brands that value the details.</p>'
             '<span class="btn">Get started</span></div>',
    "acid": '<div class="s-acid"><div class="nav"><span>NOIR</span><span>Menu</span></div>'
            '<h1>Build the<br><em>future</em> faster.</h1><span class="btn">Join waitlist</span></div>',
    "paper": '<div class="s-paper"><div class="mast">The Daily Brief</div><div class="date"><span>Vol. 12</span><span>Thursday</span></div>'
             '<div class="cols"><div class="col"><b>A headline set in serif</b>' + "<i></i>" * 9 + '</div>'
             '<div class="col"><b>Second story</b>' + "<i></i>" * 10 + '</div><div class="col"><b>Notes</b>' + "<i></i>" * 10 + '</div></div></div>',
    "saas": '<div class="s-saas"><h1>Everything you need</h1><div class="grid">'
            + '<div class="c"><i></i><b></b><s></s><s></s><s style="width:60%"></s></div>' * 3 + '</div></div>',
    "chrome": '<div class="s-chrome"><div class="eyebrow">FEATURES</div><h1>Designed for teams<br>who ship.</h1>'
              '<div class="meta2">Design · AI · 5 min read</div><div class="label2">Workflow — made simple</div>'
              '<div class="row2"><code>v2.0 / beta</code><a>Learn more →</a></div></div>',
    "type": '<div class="s-type"><div class="eyebrow">HOW IT WORKS</div><h1>Design that feels <em>effortless</em></h1>'
            '<ol>' + "".join(f'<li><span>0{n}</span><b>{t}</b><i></i><i style="width:70%"></i></li>' for n, t in [(1, "Fast"), (2, "Simple"), (3, "Smart")]) + '</ol></div>',
}
NOTE = "스킬 원문의 목록을 보고 다시 그린 예시"


# 이 묶음은 'AI 티'를 다루는 글이라, 카드 틀 자체도 그 목록에 걸리지 않게 손봅니다 (2026-11-06 점검)
#  - 표지 단추 끝의 '→' 를 뺍니다
#  - 요약 장의 검은 알약 라벨(내용 위에 얹는 작은 라벨) 대신 큰 제목으로 씁니다
#  - 장 번호와 '피하는 법' 번호의 앞자리 0(01, 02 …)을 뺍니다
SC.EXTRA_CSS += """
.lead .lhead { margin-top: 104px; font-size: 92px; line-height: 1.15; font-weight: 800; letter-spacing: -0.045em; }
.lead .lhead + .text { margin-top: 40px; }
.tip li::before { content: counter(n); }
"""


def tidy(doc):
    doc = doc.replace('<div class="pill">넘겨서 보기 →</div>', '<div class="pill">옆으로 넘겨 보기</div>')
    return re.sub(r'<div class="page">0?(\d+) / (\d+)</div>', r'<div class="page">\1 / \2</div>', doc)


def render(card, i, total):
    if card["kind"] == "mock":
        body = (f'<div class="cap">{e(card["cap"])}</div><div class="screen">{SCREENS[card["screen"]]}</div>'
                f'<div class="l3">{e(card["text"])}</div><div class="note">{NOTE}</div>')
        return tidy(SC.head("mock", body, i, total))
    doc = SC.render(card, i, total)
    if card["kind"] == "lead":
        doc = doc.replace(f'<div class="pill">{e(card["label"])}</div>', f'<div class="lhead">{e(card["label"])}</div>', 1)
    return tidy(doc)


def main():
    cards = [
        {"kind": "cover", "title": "AI가 만든 사이트,\n왜 다 어디서\n본 것 같을까", "sub": "앤트로픽 공식 스킬에 적힌 AI 디자인의 기본값"},
        {"kind": "lead", "label": "기분 탓이 아니다",
         "text": "AI는 고르지 않고 기본값을 낸다.\n뭘 만들든 제일 흔한 답이 먼저 나온다.\n\n클로드가 디자인할 때 읽는 공식 스킬에 그 기본값 목록이 그대로 적혀 있다."},
        {"kind": "mock", "screen": "cream", "cap": "크림 배경에 세리프,\n테라코타 포인트",
         "text": "이건 클로드 자기 색이다. 스킬에도 '티가 난다'고 적혀 있다."},
        {"kind": "mock", "screen": "acid", "cap": "검정 배경에\n형광색 포인트 하나",
         "text": "형광 초록이나 주홍 한 가지로만 힘을 준다."},
        {"kind": "mock", "screen": "paper", "cap": "가는 선, 각진 모서리,\n신문 같은 단",
         "text": "모서리는 0, 칸은 가는 줄로 나눈 빽빽한 구성."},
        {"kind": "mock", "screen": "saas", "cap": "똑같은 둥근 카드에\n똑같은 그림자",
         "text": "내용을 같은 카드로 자르고, 그라데이션은 장식으로 깐다."},
        {"kind": "mock", "screen": "chrome", "cap": "주제와 상관없이\n붙는 장식들",
         "text": "제목 위 대문자 라벨, 가운뎃점으로 이은 메타, 끝에 붙는 →."},
        {"kind": "mock", "screen": "type", "cap": "글자에서도\n티가 난다",
         "text": "한 단어만 색 바꾸기, 전부 대문자 라벨, 순서도 아닌데 붙인 01 / 02 / 03."},
        {"kind": "tip", "title": "피하는 법",
         "points": [("먼저 글로 정하기", "만들기 전에 색 4~6개, 글꼴, 레이아웃을 정한다"),
                    ("흔한 답인지 따져 보기", "비슷한 다른 페이지에도 똑같이 나올 것 같으면 바꾼다"),
                    ("이유를 같이 주기", "레퍼런스와 '이 브랜드라서'를 붙여서 시킨다")]},
        {"kind": "outro", "title": "첫 결과물은 초안,\n고르는 건 디자이너", "url": "designrefs.com/skills/find-skills",
         "sub": "frontend-design 스킬 설치법"},
    ]
    tmp = pathlib.Path(tempfile.mkdtemp())
    out = BC.OUT / SET_ID
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.jpg"):
        old.unlink()
    for i, card in enumerate(cards, 1):
        page, png = tmp / f"{i:02d}.html", tmp / f"{i:02d}.png"
        page.write_text(render(card, i, len(cards)), encoding="utf-8")
        shoot(page, png, size=BC.SIZE)
        Image.open(png).convert("RGB").save(out / f"{i:02d}.jpg", "JPEG", quality=90, optimize=True)

    title = "AI가 만든 사이트, 왜 다 어디서 본 것 같을까"
    cap = "\n".join([
        "AI로 화면 만든다면 저장해 두자",
        "",
        "AI가 만든 디자인이 다 비슷해 보이는 데는 이유가 있다. 클로드가 디자인할 때 읽는 앤트로픽 공식 스킬(frontend-design)에 AI 디자인의 기본값 목록이 적혀 있다.",
        "",
        "1. 크림 배경 + 세리프 + 테라코타",
        "2. 검정 배경 + 형광색 포인트",
        "3. 신문 같은 단, 각진 모서리",
        "4. 똑같은 카드와 그림자",
        "5. 주제와 상관없이 붙는 장식 라벨",
        "",
        "#AI디자인 #클로드 #웹디자인 #UI디자인 #디자이너",
    ])
    (out / "caption.txt").write_text(cap + "\n", encoding="utf-8")
    BC.write_index([{
        "id": SET_ID, "title": title, "count": len(cards),
        "images": [f"{BC.SITE}social/cards/{SET_ID}/{i:02d}.jpg" for i in range(1, len(cards) + 1)],
        "caption": cap,
        "comment": "🔗 출처\n· frontend-design 스킬 — github.com/anthropics/skills\n\n설치법은 여기\ndesignrefs.com/skills/find-skills",
    }])
    print(f"{SET_ID}: {len(cards)}장 → {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
