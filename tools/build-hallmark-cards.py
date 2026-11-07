#!/usr/bin/env python3
"""
클로드 스킬 3탄(hallmark) 캐러셀 11장 (1080×1350)

  python3 tools/build-hallmark-cards.py 스크린샷폴더

- 스크린샷 폴더에는 1280px 폭, 2배율로 찍은 세 장을 둡니다.
  trend.png  github.com/trending?since=weekly (hallmark 줄이 화면 가운데쯤 오게 스크롤)
  ss.png     skills.sh/nutlope/hallmark/hallmark (1280×1010)
  site.png   usehallmark.com 첫 화면 (1280×800)
- 내용 근거: github.com/Nutlope/hallmark 의 SKILL.md, references/gates.md, scripts/sloplint-render.mjs,
  GitHub 주간 트렌딩, skills.sh (모두 2026-11-07 확인)
- 이 카드는 'AI 티'를 다루는 글이라 기시감 카드(build-deja-cards.py)의 정리 규칙을 그대로 씁니다.
  가운뎃점으로 이은 메타, 끝에 붙는 →, 앞자리 0 번호는 쓰지 않습니다.
- 결과: social/cards/claude-skills-hallmark/01.jpg … + caption.txt, social/cards/index.json 갱신
"""
import importlib.util, pathlib, sys, tempfile

from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec_ = importlib.util.spec_from_file_location("build_deja_cards", ROOT / "tools" / "build-deja-cards.py")
DJ = importlib.util.module_from_spec(spec_)
spec_.loader.exec_module(DJ)
SC, BC = DJ.SC, DJ.BC
from snap import shoot

SET_ID = "claude-skills-hallmark"
CHECKED = "2026. 11. 7 확인"
SC.KICKER = "클로드 스킬 3탄"


def main():
    if len(sys.argv) < 2:
        raise SystemExit("스크린샷 폴더를 넘겨 주세요 (trend.png, ss.png, site.png)")
    shots = pathlib.Path(sys.argv[1])
    tmp = pathlib.Path(tempfile.mkdtemp())

    # 트렌딩: worktrunk 아래부터. hallmark 줄에 검은 테두리를 둘러 눈에 띄게
    trend = Image.open(shots / "trend.png").convert("RGB")
    ImageDraw.Draw(trend).rounded_rectangle((304, 790, 2255, 1008), radius=18, outline="#111111", width=8)
    c = trend.crop((300, 563, 2259, 1795))
    # 카드 틀 비율(약 1.44:1)에 맞게 아래를 흰 바탕으로 채워야 오른쪽 별 수가 안 잘립니다
    pad = Image.new("RGB", (c.width, 1360), "white")
    pad.paste(c, (0, 0))
    pad.save(tmp / "trend.png")
    ss_c = SC.crop(shots / "ss.png", tmp / "ss.png", (150, 290, 2460, 1890))
    site_c = SC.crop(shots / "site.png", tmp / "site.png", (0, 0, 2560, 1600))

    cards = [
        {"kind": "cover", "title": "AI 티 잡아 주는 스킬이\n깃허브에서 터졌다", "sub": "클로드 코드 스킬 3탄, hallmark"},
        {"kind": "shot", "cap": "이번 주 깃허브\n트렌딩 5위",
         "facts": ["이번 주 별 6,900개", "전체 별 4.9만"],
         "url": "github.com/trending", "img": tmp / "trend.png", "src": f"GitHub 주간 트렌딩, {CHECKED}"},
        {"kind": "lead", "label": "AI 티를 규칙으로 막는다",
         "text": "디자인할 때 AI가\n꺼내 읽는 스킬이다.\n\n기본값으로 흘러가지 않게 바닥 규칙을 깔고, 매번 다른 방향을 뽑아 주고, 다 만든 화면은 브라우저에 띄워서 검사까지 한다."},
        {"kind": "tip", "title": "만들기 전에",
         "points": [("프로젝트부터 읽는다", "쓰던 글꼴, 색, 프레임워크. design.md가 있으면 그게 1순위"),
                    ("딱 한 번 묻는다", "보여 줄 재료, 누구를 위한지, 할 일 하나, 톤. '깔끔하고 모던하게'는 톤이 아니라고 적혀 있다"),
                    ("테마 50개 중 3개", "지난 작업과 안 겹치게 뽑고 그중 하나를 고른다")]},
        {"kind": "tip", "title": "만들 때",
         "points": [("첫 화면부터", "제목 일곱 단어, 문장 하나, 버튼 한두 개. 띄워 보고 통과해야 아래를 만든다"),
                    ("한 화면에 80단어", "꽉 찬 느낌은 글이 아니라 크기와 사진으로 낸다"),
                    ("지어내지 않는다", "없는 숫자, 후기, 로고는 빈칸으로 남긴다")]},
        {"kind": "tip", "title": "절대 못 넘기는 것",
         "points": [("라벨", "제목 위 작은 라벨, 자간 넓힌 대문자 라벨"),
                    ("장식", "가운뎃점으로 이은 메타, 링크 끝에 붙인 화살표"),
                    ("제목과 색", "한 단어만 기울인 제목, 보라에서 파랑 그라데이션, 카드 안의 카드, 이모지 아이콘")]},
        {"kind": "tip", "title": "다 만들면 검사",
         "points": [("sloplint", "화면 폭 8개(320~1920)로 띄워서 규칙을 하나씩 잰다"),
                    ("세 단계 판정", "바닥 규칙은 무조건 고치고, 습관은 이유를 적으면 넘어가고, 마감은 알려만 준다"),
                    ("마지막은 새 눈", "작업 내용을 모르는 에이전트가 처음 보는 눈으로 한 번 더 본다")]},
        {"kind": "shot", "cap": "정작 공식 사이트는\n크림 배경에 세리프",
         "facts": ["습관 규칙", "이유가 있으면 통과"],
         "url": "usehallmark.com", "img": site_c, "src": f"usehallmark.com 첫 화면, {CHECKED}"},
        {"kind": "shot", "cap": "설치 9.4만,\n보안 점검 하나는 주의",
         "facts": ["설치 94.5K", "!Gen Agent Trust Hub 주의"],
         "url": "skills.sh/nutlope/hallmark", "img": ss_c, "src": f"skills.sh, {CHECKED}"},
        {"kind": "code", "title": "설치는 한 줄", "sub": "깔고 나서 /hallmark 뒤에 만들 걸 적으면 시작",
         "cmd": "npx skills add \\\n  nutlope/hallmark \\\n  -g --agent claude-code",
         "flags": [("-g", "어느 폴더에서 열어도 쓰이게"), ("audit", "이미 만든 페이지는 점검만 받기")]},
        {"kind": "outro", "title": "돌아가는 방식 전체는\n사이트에 정리했다", "url": "designrefs.com/skills/hallmark",
         "sub": "1탄 find-skills, 2탄 SEO도 같은 곳에"},
    ]

    out = BC.OUT / SET_ID
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.jpg"):
        old.unlink()
    for i, card in enumerate(cards, 1):
        page, png = tmp / f"{i:02d}.html", tmp / f"{i:02d}.png"
        page.write_text(DJ.render(card, i, len(cards)), encoding="utf-8")
        shoot(page, png, size=BC.SIZE)
        Image.open(png).convert("RGB").save(out / f"{i:02d}.jpg", "JPEG", quality=90, optimize=True)

    title = "AI 티 잡아 주는 스킬, hallmark"
    cap = "\n".join([
        "AI로 화면 만든다면 저장해 두자",
        "",
        "클로드 코드 스킬 3탄. 이번 주 깃허브 트렌딩 5위에 오른 디자인 스킬 hallmark가 어떻게 돌아가는지 정리했다.",
        "",
        "1. 만들기 전에 프로젝트부터 읽고 딱 한 번 묻는다",
        "2. 테마 50개 중 3개를 뽑아 방향을 정한다",
        "3. 바닥 규칙, 습관, 마감 세 단계로 검사한다",
        "4. 설치는 터미널 한 줄",
        "",
        "#클로드 #클로드코드 #클로드스킬 #AI디자인 #웹디자인",
    ])
    (out / "caption.txt").write_text(cap + "\n", encoding="utf-8")
    BC.write_index([{
        "id": SET_ID, "title": title, "count": len(cards),
        "images": [f"{BC.SITE}social/cards/{SET_ID}/{i:02d}.jpg" for i in range(1, len(cards) + 1)],
        "caption": cap,
        "comment": "출처\ngithub.com/Nutlope/hallmark\nskills.sh/nutlope/hallmark/hallmark\n\n작동 방식 정리는 여기\ndesignrefs.com/skills/hallmark",
    }])
    print(f"{SET_ID}: {len(cards)}장 → {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
