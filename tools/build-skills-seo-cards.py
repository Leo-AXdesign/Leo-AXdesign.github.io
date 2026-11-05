#!/usr/bin/env python3
"""
클로드 스킬 2탄(SEO·AEO·GEO) 캐러셀 8장 (1080×1350)

  python3 tools/build-skills-seo-cards.py [스크린샷 폴더]

- 카드 틀은 1탄(build-skills-cards.py)을 그대로 씁니다. 말투는 스레드 글에 맞춰 다체.
- 스크린샷 폴더에는 skillssh-seo-audit.png(skills.sh seo-audit 페이지, 1280×1010 2배율)와
  find-seo.png(터미널에서 npx skills find seo 를 실행한 결과를 창 모양으로 찍은 것)를 둡니다.
  skills.sh 쪽은 없으면 이 스크립트가 직접 찍습니다.
- 결과: social/cards/claude-skills-seo/01.jpg … + caption.txt, social/cards/index.json 갱신
- 숫자는 2026-11-05 에 skills.sh 와 npx skills find 로 확인한 값입니다.
"""
import importlib.util, pathlib, sys, tempfile

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec_ = importlib.util.spec_from_file_location("build_skills_cards", ROOT / "tools" / "build-skills-cards.py")
SC = importlib.util.module_from_spec(spec_)
spec_.loader.exec_module(SC)
BC = SC.BC
from snap import shoot

SET_ID = "claude-skills-seo"
CHECKED = "2026. 11. 5 확인"
SC.KICKER = "클로드 스킬 2탄"


def main():
    shots = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(tempfile.mkdtemp())
    ss, term = shots / "skillssh-seo-audit.png", shots / "find-seo.png"
    if not ss.exists():
        shoot("https://skills.sh/coreyhaines31/marketingskills/seo-audit", ss, size=(1280, 1010), scale=2)
    if not term.exists():
        raise SystemExit(f"{term} 가 없습니다. npx skills find seo 결과 화면을 먼저 찍어 두세요.")
    tmp = pathlib.Path(tempfile.mkdtemp())
    # skills.sh: 스킬 이름부터 보안 점검(Snyk)까지. 카드 틀 비율(약 1.44:1)에 맞춰 잘라야 아래가 안 잘립니다
    ss_c = SC.crop(ss, tmp / "ss.png", (150, 290, 2460, 1890))
    # 터미널: 창의 제목 줄은 카드 틀이 대신 그리므로 빼고 본문만
    term_c = SC.crop(term, tmp / "term.png", (60, 144, 2420, 1250))

    cards = [
        {"kind": "cover", "title": "만든 사이트,\n검색에도 AI 답변에도\n안 나온다면", "sub": "클로드 코드 스킬 2탄 · SEO·AEO·GEO"},
        {"kind": "lead", "label": "세 가지로 나눠 부른다",
         "text": "SEO: 검색 결과에서 상위권으로\nAEO: AI 답변에 내 문장이 뽑히게\nGEO: AI가 내 사이트를 출처로 달게\n\n클로드 코드에 스킬 하나 깔아 두면 셋 다 점검할 수 있다."},
        {"kind": "shot", "cap": "npx skills find seo\n한 줄이면 후보가 나온다",
         "facts": ["seo-audit 24.6만", "ai-seo 15.8만", "programmatic-seo 15.6만"],
         "url": "터미널 · npx skills find seo", "img": term_c, "src": f"npx skills find seo 결과 · {CHECKED}"},
        {"kind": "tip", "title": "딱 하나만 깐다면",
         "points": [("seo-audit · 24.6만", "색인, 제목·설명 태그, 내부 링크, 이미지까지 훑고 급한 것부터 뽑아 준다"),
                    ("ai-seo · 15.8만", "챗GPT·퍼플렉시티·구글 AI 개요에 인용되게 쓰는 법을 봐 준다"),
                    ("같은 묶음 marketingskills", "깃허브 별 5.8만 개")]},
        {"kind": "shot", "cap": "설치 24.6만,\n보안 점검도 같이 본다",
         "facts": ["설치 246.5K", "깃허브 별 58.5K", "!Snyk 주의 1건"],
         "url": "skills.sh/coreyhaines31/marketingskills/seo-audit", "img": ss_c, "src": f"skills.sh · {CHECKED}"},
        {"kind": "tip", "title": "AI 검색까지 챙기려면",
         "points": [("seo-geo · 5.5만", "구글 검색과 AI 검색을 한 번에. AI 봇이 막혀 있는지도 본다"),
                    ("seo · 5.4만", "라이트하우스 기준 점검. 순위는 약속하지 않는다고 적어 뒀다"),
                    ("seo-aeo-best-practices · 7.5천", "메타 태그·사이트맵·구조화 데이터 원칙 정리")]},
        {"kind": "code", "title": "설치는 한 줄", "sub": "깔고 나서 “이 사이트 SEO 점검해 줘” 한마디면 끝",
         "cmd": "npx skills add \\\n  coreyhaines31/marketingskills \\\n  --skill seo-audit -g",
         "flags": [("-g", "어느 폴더에서 열어도 쓰이게"), ("묶음", "marketingskills 중 seo-audit만 설치")]},
        {"kind": "outro", "title": "스킬 5개 표와 캡처,\n사이트에 정리했다", "url": "designrefs.com/skills/seo",
         "sub": "1탄 find-skills도 같은 곳에"},
    ]

    out = BC.OUT / SET_ID
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.jpg"):
        old.unlink()
    for i, card in enumerate(cards, 1):
        page, png = tmp / f"{i:02d}.html", tmp / f"{i:02d}.png"
        page.write_text(SC.render(card, i, len(cards)), encoding="utf-8")
        shoot(page, png, size=BC.SIZE)
        Image.open(png).convert("RGB").save(out / f"{i:02d}.jpg", "JPEG", quality=90, optimize=True)

    title = "만든 사이트, 검색에도 AI 답변에도 안 나온다면"
    cap = "\n".join([
        "사이트를 만들었다면 저장해 두자",
        "",
        "클로드 코드 스킬 2탄. SEO·AEO·GEO를 점검해 주는 스킬을 skills.sh 설치 수 기준으로 골랐다.",
        "",
        "1. seo-audit: SEO 스킬 설치 수 1위 (24.6만)",
        "2. ai-seo: AI 답변에 인용되게 쓰는 법",
        "3. seo-geo · seo · seo-aeo-best-practices",
        "4. 설치는 터미널 한 줄",
        "",
        "#클로드 #클로드코드 #클로드스킬 #SEO #AI디자인",
    ])
    (out / "caption.txt").write_text(cap + "\n", encoding="utf-8")
    BC.write_index([{
        "id": SET_ID, "title": title, "count": len(cards),
        "images": [f"{BC.SITE}social/cards/{SET_ID}/{i:02d}.jpg" for i in range(1, len(cards) + 1)],
        "caption": cap,
        "comment": "🔗 소개한 곳 주소\n· seo-audit — skills.sh/coreyhaines31/marketingskills/seo-audit\n· ai-seo — skills.sh/coreyhaines31/marketingskills/ai-seo\n\n표와 캡처는 여기\ndesignrefs.com/skills/seo",
    }])
    print(f"{SET_ID}: {len(cards)}장 → {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
