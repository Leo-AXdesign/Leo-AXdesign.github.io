#!/usr/bin/env python3
"""
content/articles/*.md 를 읽어 글 목록을 돌려줍니다.

build-articles.py 와 build-seo.py 가 같이 씁니다.

글 파일 형식
------------
    ---
    slug: ai-design-tools-where-they-help
    title: AI 디자인 툴은 어디까지 해주나
    desc: 한 줄 요약. 검색 결과와 목록에 그대로 보입니다.
    date: 2026-09-25
    tag: AI 디자인
    order: 1                    (선택) 같은 날짜 안에서의 순서. 작을수록 위
    related: ai, tools          (선택) 연결할 카테고리 페이지 슬러그
    ---

    본문은 마크다운으로 씁니다. 쓸 수 있는 문법은 아래가 전부입니다.

    ## 중간 제목 / ### 작은 제목
    - 목록 / 1. 번호 목록
    > 인용
    **굵게**, [링크](https://...), `코드`
    ![그림 설명](https://designrefs.com/articles/img/파일.svg)   한 줄을 통째로 써야 그림이 됩니다.
                                                              설명은 그림 아래 캡션으로 나옵니다.
"""
import re, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "content" / "articles"
e = html.escape

# 본문에서 다른 목록 페이지로 연결할 때 쓰는 이름표
RELATED_LABEL = {
    "ui-ux": "UI/UX 레퍼런스", "graphic": "그래픽·브랜딩", "color": "컬러 팔레트",
    "font": "폰트·타이포", "assets": "아이콘·에셋", "dev": "디자인 시스템·개발",
    "tools": "디자인 툴", "freelance": "외주·프리랜서", "jobs": "디자이너 채용",
    "ai": "AI 디자인 툴", "community": "커뮤니티·매거진", "creators": "유튜버·크리에이터",
    "styles": "스타일 사전", "trends": "2026 트렌드", "glossary": "용어 사전",
}


def inline(t):
    """한 줄 안의 강조·링크·코드를 HTML 로 바꿉니다. 이스케이프를 먼저 합니다."""
    t = e(t.strip())
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
               lambda m: f'<a href="{m.group(2)}"'
                         + ('' if m.group(2).startswith(('#', 'https://designrefs.com', '/', 'mailto:'))
                            else ' target="_blank" rel="noopener"')
                         + f'>{m.group(1)}</a>', t)
    return t


SITE = "https://designrefs.com/"


def _svg_size(src):
    """사이트 안 SVG 의 viewBox 를 읽어 width/height 속성으로 돌려줍니다."""
    if not (src.startswith(SITE) and src.endswith(".svg")):
        return ""
    f = ROOT / src[len(SITE):]
    if not f.exists():
        raise SystemExit(f"그림 파일이 없습니다: {f}")
    vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', f.read_text(encoding="utf-8"))
    return f' width="{round(float(vb.group(1)))}" height="{round(float(vb.group(2)))}"' if vb else ""


def figure(caption, src):
    """그림 한 장. 크기를 미리 적어 두면 그림이 늦게 떠도 글이 아래로 밀리지 않습니다.
    같은 폴더에 '이름-m.svg' 가 있으면 폰(640px 이하)에서는 그 그림을 씁니다.
    넓은 그림을 폰 폭으로 줄이면 글씨가 읽을 수 없을 만큼 작아지기 때문입니다."""
    alt = e(re.sub(r"[*`]", "", caption))
    img = f'<img src="{e(src)}" alt="{alt}"{_svg_size(src)} loading="lazy" decoding="async" />'
    mobile = src[:-4] + "-m.svg" if src.endswith(".svg") else ""
    if mobile and (ROOT / mobile[len(SITE):]).exists():
        img = (f'<picture><source media="(max-width: 640px)" srcset="{e(mobile)}"{_svg_size(mobile)} />'
               + img + '</picture>')
    return ('    <figure class="art__fig">\n'
            f'      {img}\n'
            f'      <figcaption>{inline(caption)}</figcaption>\n'
            '    </figure>')


def to_html(md):
    """마크다운 일부 문법을 본문 HTML 로 바꿉니다."""
    out, buf, mode = [], [], None

    def flush():
        nonlocal buf, mode
        if not buf:
            mode = None
            return
        if mode == "p":
            out.append(f'    <p class="ptext">{inline(" ".join(buf))}</p>')
        elif mode in ("ul", "ol"):
            cls = "ptext-list"
            out.append(f'    <{mode} class="{cls}">')
            out.extend(f"      <li>{inline(x)}</li>" for x in buf)
            out.append(f"    </{mode}>")
        elif mode == "quote":
            out.append(f'    <blockquote class="art__quote">{inline(" ".join(buf))}</blockquote>')
        buf, mode = [], None

    for raw in md.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            flush()
            continue
        img = re.match(r"^!\[([^\]]*)\]\(([^)\s]+)\)$", line.strip())
        if img:
            flush()
            out.append(figure(img.group(1), img.group(2)))
        elif line.startswith("## "):
            flush()
            out.append(f'    <h2 class="psub">{inline(line[3:])}</h2>')
        elif line.startswith("### "):
            flush()
            out.append(f'    <h3 class="art__h3">{inline(line[4:])}</h3>')
        elif line.startswith("> "):
            if mode != "quote":
                flush()
            mode = "quote"
            buf.append(line[2:])
        elif re.match(r"^- ", line):
            if mode != "ul":
                flush()
            mode = "ul"
            buf.append(line[2:])
        elif re.match(r"^\d+\. ", line):
            if mode != "ol":
                flush()
            mode = "ol"
            buf.append(re.sub(r"^\d+\. ", "", line))
        else:
            if mode != "p":
                flush()
            mode = "p"
            buf.append(line.strip())
    flush()
    return "\n".join(out)


def to_text(md):
    """llms-full.txt 에 넣을 평문. 마크다운 기호만 걷어냅니다."""
    t = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"(그림: \1)", md)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    t = re.sub(r"[*`>]", "", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def load():
    """날짜 내림차순(최신 글이 앞)으로 글 목록을 돌려줍니다."""
    items = []
    for f in sorted(SRC.glob("*.md")):
        raw = f.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
        if not m:
            raise SystemExit(f"{f.name}: 맨 위 --- 사이의 정보 칸이 없습니다")
        meta = {}
        for line in m.group(1).split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = m.group(2).strip()
        text = to_text(body)
        need = {"slug", "title", "desc", "date"} - set(meta)
        if need:
            raise SystemExit(f"{f.name}: {', '.join(sorted(need))} 항목이 없습니다")
        meta["body"] = to_html(body)
        meta["text"] = text
        meta["chars"] = len(re.sub(r"\s", "", text))
        # 한국어는 분당 600자 정도로 봅니다
        meta["min"] = max(1, round(meta["chars"] / 600))
        meta["related"] = [x.strip() for x in meta.get("related", "").split(",") if x.strip()]
        meta["file"] = f.name
        items.append(meta)
    # 최신 날짜가 위. 같은 날 올린 글은 order 값이 작은 것이 위입니다.
    items.sort(key=lambda x: (x["date"], -int(x.get("order", 0) or 0)), reverse=True)
    return items
