#!/usr/bin/env python3
"""
사이트 목록이 언제 어떻게 바뀌었는지를 git 기록에서 읽어 '업데이트 기록'을 만듭니다.

- js/data.js 가 바뀐 커밋마다 바로 앞 상태와 비교해서
  추가 · 삭제 · 분야 이동 · 주소 변경 · 태그 수정 · 설명 수정 · 소분류 정리를 찾습니다.
- 읽을거리는 글의 date 로 '발행'을 넣습니다.
- 손으로 적는 기록이 아니라서 빠지거나 틀릴 일이 없습니다. 커밋 메시지는 쓰지 않습니다.

build-pages.py 가 불러 씁니다 (업데이트 기록 페이지, 분야 페이지의 '마지막으로 고친 날').
"""
import re, subprocess, pathlib, collections, os

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = "js/data.js"


def _git(*args):
    env = dict(os.environ, TZ="Asia/Seoul")
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, env=env).stdout


def _block(src, name):
    i = src.find(f"const {name} = [")
    if i < 0:
        return []
    return src[i:src.index("\n];", i)].split("\n")


def _field(row, k):
    m = re.search(rf"\b{k}: '((?:[^'\\]|\\.)*)'", row) or re.search(rf'\b{k}: "((?:[^"\\]|\\.)*)"', row)
    return m.group(1).replace("\\'", "'") if m else ""


def _snapshot(src):
    sites = {}
    for row in _block(src, "SITES"):
        if "{ name:" not in row:
            continue
        u = _field(row, "url")
        tags = re.search(r"tags: \[([^\]]*)\]", row)
        sites[u] = {"name": _field(row, "name"), "cat": _field(row, "cat"), "sub": _field(row, "sub"),
                    "desc": _field(row, "desc"),
                    "tags": tuple(re.findall(r"'([^']+)'", tags.group(1))) if tags else ()}
    cats = [(_field(r, "id"), _field(r, "label")) for r in _block(src, "CATEGORIES") if "{ id:" in r]
    item = lambda r: r.lstrip().startswith("{") and re.search(r"\b(name|term): ", r)
    counts = {k: sum(1 for r in _block(src, k) if item(r)) for k in ("STYLES", "TRENDS", "GLOSSARY")}
    rows = {k: {r.strip() for r in _block(src, k) if item(r)} for k in ("STYLES", "TRENDS", "GLOSSARY")}
    return {"sites": sites, "cats": cats, "counts": counts, "rows": rows}


EXTRA = {"STYLES": "스타일 사전", "TRENDS": "2026 트렌드", "GLOSSARY": "용어 사전"}


def _diff(a, b):
    """두 상태의 차이를 (종류, 문장, 관련 분야 id 목록) 으로."""
    lab = dict(b["cats"]) | {k: v for k, v in a["cats"] if k not in dict(b["cats"])}
    out = []
    A, B = a["sites"], b["sites"]
    added = [u for u in B if u not in A]
    removed = [u for u in A if u not in B]
    # 이름이 같은데 주소만 바뀐 것
    renamed = []
    for u in list(added):
        old = next((v for v in removed if A[v]["name"] == B[u]["name"]), None)
        if old:
            renamed.append((old, u)); added.remove(u); removed.remove(old)
    new_cats = [c for c, _ in b["cats"] if c not in dict(a["cats"])]
    for c in new_cats:
        n = sum(1 for u in added if B[u]["cat"] == c)
        out.append(("new", f"새 분야 · {lab[c]} (사이트 {n}곳)", [c]))
    for u in added:
        if B[u]["cat"] in new_cats:
            continue
        out.append(("add", f"{B[u]['name']} → {lab.get(B[u]['cat'], B[u]['cat'])}", [B[u]["cat"]]))
    for u in removed:
        out.append(("del", f"{A[u]['name']} ({lab.get(A[u]['cat'], A[u]['cat'])})", [A[u]["cat"]]))
    for o, u in renamed:
        out.append(("edit", f"{B[u]['name']} 주소 변경", [B[u]["cat"]]))
    moved = [u for u in B if u in A and A[u]["cat"] != B[u]["cat"]]
    for u in moved:
        out.append(("move", f"{B[u]['name']} · {lab.get(A[u]['cat'])} → {lab.get(B[u]['cat'])}",
                    [A[u]["cat"], B[u]["cat"]]))
    for u in B:
        if u in A and A[u]["tags"] != B[u]["tags"] and u not in moved:
            out.append(("edit", f"{B[u]['name']} 태그 · {', '.join(A[u]['tags']) or '없음'} → {', '.join(B[u]['tags'])}",
                        [B[u]["cat"]]))
    desc = collections.Counter(B[u]["cat"] for u in B if u in A and A[u]["desc"] != B[u]["desc"])
    for c, n in desc.items():
        out.append(("edit", f"{lab.get(c, c)} · 사이트 설명 {n}곳", [c]))
    sub = collections.Counter(B[u]["cat"] for u in B if u in A and A[u]["sub"] != B[u]["sub"] and u not in moved)
    for c, n in sub.items():
        if not any(A[u]["sub"] for u in A if A[u]["cat"] == c):
            names = list(dict.fromkeys(B[u]["sub"] for u in B if B[u]["cat"] == c and B[u]["sub"]))
            out.append(("edit", f"{lab.get(c, c)} · 소분류 {len(names)}개로 나눔 ({', '.join(x.replace(' · ', '·') for x in names)})", [c]))
        else:
            out.append(("edit", f"{lab.get(c, c)} · 소분류 정리 ({n}곳)", [c]))
    if [c for c, _ in a["cats"] if c in dict(b["cats"])] != [c for c, _ in b["cats"] if c in dict(a["cats"])]:
        out.append(("edit", "분야 순서 변경", []))
    for k, name in EXTRA.items():
        new, old = b["rows"][k], a["rows"][k]
        plus = b["counts"][k] - a["counts"][k]
        changed = len(new - old) - max(plus, 0)
        if plus > 0:
            out.append(("add", f"{name} · {plus}개", []))
        elif plus < 0:
            out.append(("del", f"{name} · {-plus}개", []))
        if changed > 0:
            out.append(("edit", f"{name} · {changed}개 내용 수정", []))
    return out


def history():
    """[(날짜 'YYYY-MM-DD', [(종류, 문장, [분야 id])...]), ...] 최신 날짜가 먼저."""
    log = _git("log", "--reverse", "--format=%H %ad", "--date=format-local:%Y-%m-%d", "--", DATA).split("\n")
    days = collections.OrderedDict()
    prev = None
    for line in filter(None, log):
        h, day = line.split()
        snap = _snapshot(_git("show", f"{h}:{DATA}"))
        if prev is None:
            n = len(snap["sites"])
            items = [("new", f"디자인 허브 공개 · 사이트 {n}곳, 분야 {len(snap['cats'])}개, "
                             f"스타일 사전 {snap['counts']['STYLES']}가지, 용어 사전 {snap['counts']['GLOSSARY']}개", [])]
        else:
            items = _diff(prev, snap)
        prev = snap
        if items:
            days.setdefault(day, []).extend(items)
    # 아직 커밋하지 않은 지금 상태도 반영합니다
    cur = _snapshot((ROOT / DATA).read_text(encoding="utf-8"))
    if prev is not None:
        items = _diff(prev, cur)
        if items:
            import datetime
            days.setdefault(datetime.date.today().isoformat(), []).extend(items)
    return sorted(((d, _merge(v)) for d, v in days.items()), reverse=True)


def _merge(items):
    """같은 날 같은 대상의 'N개 내용 수정' 이 여러 커밋에 나뉘면 하나로 (큰 수를 남깁니다)."""
    out, seen = [], {}
    for k, t, c in items:
        m = re.match(r"^(.*) · (\d+)(개 내용 수정|곳)$", t) if k == "edit" else None
        if m:
            key = (m.group(1), m.group(3))
            if key in seen:
                i = seen[key]
                n = max(int(m.group(2)), int(re.search(r"(\d+)(개 내용 수정|곳)$", out[i][1]).group(1)))
                out[i] = (k, f"{m.group(1)} · {n}{m.group(3)}", c)
                continue
            seen[key] = len(out)
        out.append((k, t, c))
    return out


def last_changed():
    """분야 id -> 그 분야 사이트가 마지막으로 바뀐 날짜. 공개 뒤 손댄 적 없으면 공개한 날."""
    h = history()
    out = {}
    for day, items in h:
        for _, _, cats in items:
            for c in cats:
                out.setdefault(c, day)
    first = h[-1][0] if h else ""
    return collections.defaultdict(lambda: first, out)


if __name__ == "__main__":
    for day, items in history()[:8]:
        print(day)
        for k, t, c in items:
            print("  ", k, t)
