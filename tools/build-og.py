#!/usr/bin/env python3
"""
읽을거리 글마다 카톡·SNS 미리보기 이미지(1200×630 PNG)를 만듭니다.

  python3 tools/build-og.py            # 이미지가 없는 글만
  python3 tools/build-og.py --all      # 전부 다시

- 크롬(헤드리스)으로 HTML 카드를 찍어서 og/<slug>.png 로 저장합니다.
- 글을 새로 쓰거나 제목을 바꿨으면 이걸 돌린 다음 build-articles.py 를 다시 돌리세요.
  (build-articles.py 가 이미지가 있는 글에만 og:image 를 겁니다)
"""
import html, pathlib, sys, tempfile

import articles as A
from snap import shoot

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "og"
e = html.escape

TEMPLATE = """<!doctype html><html lang="ko"><head><meta charset="utf-8">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<style>
  html, body {{ margin: 0; width: 1200px; height: 630px; overflow: hidden; background: #fff; }}
  body {{ font-family: "Pretendard Variable", Pretendard, "Apple SD Gothic Neo", sans-serif; color: #111;
         -webkit-font-smoothing: antialiased; }}
  .card {{ box-sizing: border-box; width: 1200px; height: 630px; padding: 64px 80px 60px;
          display: flex; flex-direction: column; }}
  .top {{ display: flex; align-items: baseline; justify-content: space-between; }}
  .logo {{ font-size: 48px; font-weight: 800; letter-spacing: -0.04em; }}
  .logo span {{ color: #A3A3A3; }}
  .kicker {{ font-size: 24px; color: #6B6B6B; }}
  .title {{ margin-top: auto; font-size: {size}px; line-height: 1.2; font-weight: 800;
           letter-spacing: -0.04em; word-break: keep-all; text-wrap: balance; }}
  .rule {{ height: 4px; background: #111; margin: 40px 0 22px; }}
  .foot {{ display: flex; justify-content: space-between; font-size: 24px; color: #6B6B6B; }}
  .foot b {{ color: #111; font-weight: 700; }}
  .nb {{ white-space: nowrap; }}
</style></head><body><div class="card">
  <div class="top"><div class="logo">d<span>.</span></div><div class="kicker">읽을거리 · {tag}</div></div>
  <div class="title">{title}</div>
  <div class="rule"></div>
  <div class="foot"><span><b>디자인 허브</b> · 디자이너를 위한 레퍼런스 모음</span><span>designrefs.com</span></div>
</div></body></html>"""


def title_size(t):
    """제목 길이에 따라 글자 크기를 정합니다. 세 줄을 넘지 않게."""
    n = len(t)
    return 78 if n <= 16 else 68 if n <= 26 else 60


def main():
    redo = "--all" in sys.argv
    OUT.mkdir(exist_ok=True)
    made = []
    with tempfile.TemporaryDirectory() as tmp:
        for x in A.load():
            png = OUT / f"{x['slug']}.png"
            if png.exists() and not redo:
                continue
            page = pathlib.Path(tmp) / f"{x['slug']}.html"
            page.write_text(TEMPLATE.format(title=A.nobreak(e(x["title"])), tag=e(x.get("tag", "")),
                                            size=title_size(x["title"])), encoding="utf-8")
            shoot(page, png)
            made.append(png.name)
    print(f"공유 이미지 {len(made)}장: " + (", ".join(made) if made else "새로 만들 것 없음"))


if __name__ == "__main__":
    main()
