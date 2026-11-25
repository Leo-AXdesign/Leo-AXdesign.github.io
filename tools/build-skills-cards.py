#!/usr/bin/env python3
"""
클로드 스킬(find-skills) 소개 캐러셀 8장 (1080×1350)

  python3 tools/build-skills-cards.py [스크린샷 폴더]

- 카드 틀과 글자 체계는 build-cards.py 와 같습니다 (표지·요약·정리·마무리는 그쪽 render 를 그대로 씁니다).
- 여기서 더한 카드: shot(실제 화면 캡처 + 위에 핵심 숫자), code(설치 명령)
- 스크린샷 폴더에는 gh-skills.png(github.com/vercel-labs/skills), skillssh-find.png(skills.sh find-skills 페이지)를
  2배율로 찍어 둡니다. 없으면 이 스크립트가 직접 찍습니다.
- 결과: social/cards/claude-skills/01.jpg … + caption.txt, social/cards/index.json 갱신
- 숫자는 2026-11-04 에 두 페이지에서 확인한 값입니다. 다시 만들 때는 화면 속 숫자와 맞춰 고치세요.
"""
import html, importlib.util, pathlib, sys, tempfile

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec_ = importlib.util.spec_from_file_location("build_cards", ROOT / "tools" / "build-cards.py")
BC = importlib.util.module_from_spec(spec_)
spec_.loader.exec_module(BC)
from snap import shoot

e = html.escape
SET_ID = "claude-skills"
KICKER = "클로드 스킬"
CHECKED = "2026. 11. 4 확인"

EXTRA_CSS = """
/* 실제 화면: 위에 핵심 한 줄과 숫자, 아래에 캡처 */
.shot .cap { margin-top: 72px; font-size: 64px; line-height: 1.25; font-weight: 800; letter-spacing: -0.04em; white-space: pre-line; }
.shot .facts { display: flex; gap: 14px; margin-top: 32px; flex-wrap: wrap; }
.shot .fact { font-size: 34px; font-weight: 700; padding: 12px 26px; border: 3px solid #111; border-radius: 999px; }
.shot .fact.warn { border-color: #B45309; color: #B45309; }
.shot .frame { margin-top: 44px; flex: 1; min-height: 0; border-radius: 22px; overflow: hidden; border: 2px solid #E4E4E4;
               background: #0D1117; display: flex; flex-direction: column; }
.shot .bar { flex: none; height: 52px; display: flex; align-items: center; gap: 12px; padding: 0 22px; background: #F2F2F2; }
.shot .bar i { width: 16px; height: 16px; border-radius: 50%; background: #CFCFCF; }
.shot .bar span { margin-left: 14px; font-size: 26px; font-weight: 600; color: #767676; }
.shot .frame img { flex: 1; min-height: 0; width: 100%; object-fit: cover; object-position: top left; }
.shot .src { margin-top: 18px; font-size: 30px; font-weight: 600; color: #767676; }
.shot .progress { margin-top: 36px; }

/* 요약 카드의 줄바꿈 살리기 */
.lead .text { white-space: pre-line; }

/* 설치 명령 */
.code .title { margin-top: 96px; font-size: 104px; font-weight: 800; letter-spacing: -0.05em; }
.code .sub { margin-top: 20px; font-size: 42px; color: #555; font-weight: 500; letter-spacing: -0.02em; }
.code pre { margin: 56px 0 0; padding: 44px 44px; border-radius: 24px; background: #111; color: #fff;
            font: 600 36px/1.6 ui-monospace, "SF Mono", Menlo, monospace; white-space: pre; }
.code pre b { color: #8A8A8A; font-weight: 600; }
.code dl { margin: 52px 0 0; display: grid; grid-template-columns: 170px 1fr; row-gap: 26px; }
.code dt { font: 700 40px/1.4 ui-monospace, "SF Mono", Menlo, monospace; }
.code dd { margin: 0; font-size: 40px; line-height: 1.4; color: #555; letter-spacing: -0.02em; }
.code .progress { margin-top: auto; }
"""


def head(k, body, i, total):
    top = (f'<div class="top"><div class="logo">d<span>.</span></div><div class="kicker">{e(KICKER)}</div>'
           f'<div class="page">{i:02d} / {total:02d}</div></div>')
    bar = '<div class="progress">' + "".join(f'<i class="{"on" if j == i else ""}"></i>' for j in range(1, total + 1)) + "</div>"
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/'
            'dist/web/variable/pretendardvariable-dynamic-subset.min.css">'
            f'<style>{BC.CSS}{EXTRA_CSS}</style></head><body><div class="card {k}">{top}{body}{bar}</div></body></html>')


def render(card, i, total):
    k = card["kind"]
    if k == "shot":
        facts = "".join(f'<span class="fact{" warn" if f.startswith("!") else ""}">{e(f.lstrip("!"))}</span>' for f in card["facts"])
        body = (f'<div class="cap">{e(card["cap"])}</div><div class="facts">{facts}</div>'
                f'<div class="frame"><div class="bar"><i></i><i></i><i></i><span>{e(card["url"])}</span></div>'
                f'<img src="{card["img"].as_uri()}"></div><div class="src">{e(card["src"])}</div>')
        return head(k, body, i, total)
    if k == "code":
        flags = "".join(f"<dt>{e(a)}</dt><dd>{e(b)}</dd>" for a, b in card["flags"])
        body = (f'<div class="title">{e(card["title"])}</div><div class="sub">{e(card["sub"])}</div>'
                f'<pre><b>$ </b>{e(card["cmd"])}</pre><dl>{flags}</dl>')
        return head(k, body, i, total)
    # 표지·요약·정리·마무리는 build-cards.py 그대로, 여기 CSS 만 덧붙입니다
    return BC.render(card, i, total, 0, KICKER).replace("</style>", EXTRA_CSS + "</style>", 1)


def crop(src, dst, box):
    im = Image.open(src)
    im.crop(box).save(dst)
    return dst


def main():
    shots = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(tempfile.mkdtemp())
    gh, ss = shots / "gh-skills.png", shots / "skillssh-find.png"
    if not gh.exists():
        shoot("https://github.com/vercel-labs/skills", gh, size=(1280, 1100), scale=2)
    if not ss.exists():
        shoot("https://skills.sh/vercel-labs/skills/find-skills", ss, size=(1280, 1100), scale=2)
    tmp = pathlib.Path(tempfile.mkdtemp())
    # 깃허브: 저장소 이름·별·포크·라이선스가 보이는 윗부분
    gh_c = crop(gh, tmp / "gh.png", (0, 140, 2560, 1600))
    # skills.sh: 설치 명령, 설치 수, 별, 보안 점검이 보이는 부분
    ss_c = crop(ss, tmp / "ss.png", (150, 180, 2460, 1900))

    cards = [
        {"kind": "cover", "title": "클로드 스킬,\n찾는 데만\n반나절 걸린다면", "sub": "스킬을 대신 찾아 주는 스킬, find-skills"},
        {"kind": "lead", "label": "스킬 고르기가 어려운 이유",
         "text": "공개된 스킬은 수십만 개.\n이름만 같은 복사본도 많아요.\n\n스킬은 클로드가 그대로 따르는 지시문이라, 아무거나 깔면 그 지시를 그대로 따라요."},
        {"kind": "shot", "cap": "버셀(Vercel)이 만든\n무료 저장소에 들어 있어요",
         "facts": ["깃허브 별 3.8만", "MIT 라이선스", "기여자 168명"],
         "url": "github.com/vercel-labs/skills", "img": gh_c, "src": f"github.com/vercel-labs/skills · {CHECKED}"},
        {"kind": "tip", "title": "이렇게 골라 줘요",
         "points": [("말로 부탁하기", "“피그마 시안을 코드로 옮기는 스킬 찾아 줘”"),
                    ("알아서 거르기", "설치 수 1천 이상, 만든 곳, 깃허브 별을 보고 후보를 추려요"),
                    ("한마디로 설치", "“설치해 줘” 하면 설치 명령까지 실행해요")]},
        {"kind": "shot", "cap": "설치 420만 번,\n보안 점검도 같이 보여요",
         "facts": ["설치 4.2M", "Gen · Socket 통과", "!Snyk 경고 1건"],
         "url": "skills.sh/vercel-labs/skills/find-skills", "img": ss_c, "src": f"skills.sh · {CHECKED}"},
        {"kind": "code", "title": "설치는 한 줄", "sub": "터미널에 붙여 넣고, 클로드 코드를 새로 열면 끝",
         "cmd": "npx skills add vercel-labs/skills \\\n  --skill find-skills \\\n  -g -a claude-code -y",
         "flags": [("-g", "어느 폴더에서 열어도 쓰이게"), ("-a", "클로드 코드에 설치 (코덱스·커서도 돼요)"), ("-y", "확인 질문 건너뛰기")]},
        {"kind": "tip", "title": "디자이너라면 이것부터",
         "points": [("frontend-design · 110만", "템플릿 느낌 없이 글꼴·색·여백을 고르게 해요"),
                    ("extract-design-system · 13.1만", "사이트 주소만 주면 색·글꼴 토큰을 뽑아요"),
                    ("accessibility · 6.7만", "대비·키보드 이동 같은 접근성을 점검해요"),
                    ("figma-use · 피그마 공식", "피그마 파일을 직접 읽고 고쳐요")]},
        {"kind": "outro", "title": "디자이너용 스킬 10개,\n한 페이지에 정리했어요", "url": "designrefs.com/skills",
         "sub": "댓글에 ‘스킬’ 남기면 DM으로 보내드려요"},
    ]

    out = BC.OUT / SET_ID
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.jpg"):
        old.unlink()
    for i, card in enumerate(cards, 1):
        page, png = tmp / f"{i:02d}.html", tmp / f"{i:02d}.png"
        page.write_text(render(card, i, len(cards)), encoding="utf-8")
        shoot(page, png, size=BC.SIZE)
        Image.open(png).convert("RGB").save(out / f"{i:02d}.jpg", "JPEG", quality=90, optimize=True)

    title = "클로드 스킬, 찾는 데만 반나절 걸린다면"
    cap = "\n".join([
        "클로드 스킬 고를 때 저장해 두세요",
        "",
        "find-skills는 스킬을 대신 찾아 주는 스킬이에요. 하고 싶은 일을 말하면 설치 수, 만든 곳, 깃허브 별을 보고 걸러서 설치까지 해 줘요.",
        "",
        "1. 버셀이 만든 무료 저장소 (깃허브 별 3.8만, MIT)",
        "2. skills.sh 설치 420만 번",
        "3. 설치는 터미널 한 줄",
        "4. 디자이너가 먼저 볼 스킬: frontend-design, extract-design-system, accessibility, figma-use",
        "",
        "💬 댓글에 '스킬' 남기면 디자이너용 스킬 10개 가이드를 DM으로 보내드려요",
        "",
        "#클로드 #클로드코드 #클로드스킬 #AI디자인 #디자이너",
    ])
    (out / "caption.txt").write_text(cap + "\n", encoding="utf-8")
    BC.write_index([{
        "id": SET_ID, "title": title, "count": len(cards),
        "images": [f"{BC.SITE}social/cards/{SET_ID}/{i:02d}.jpg" for i in range(1, len(cards) + 1)],
        "caption": cap,
        "comment": "🔗 소개한 곳 주소\n· find-skills — skills.sh/vercel-labs/skills/find-skills\n· 저장소 — github.com/vercel-labs/skills\n\n가이드 전체는 여기\ndesignrefs.com/skills",
    }])
    print(f"{SET_ID}: {len(cards)}장 → {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
