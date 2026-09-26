#!/usr/bin/env python3
"""
js/data.js 를 읽어 파이썬 쪽에서 쓰기 좋은 형태로 돌려줍니다.

빌드 스크립트 세 개(build-pages, build-articles, build-seo)와 nav.py 가 같이 씁니다.
data.js 는 사람이 손으로 고치는 파일이라 JSON 이 아니라서, 필요한 값만 정규식으로 꺼냅니다.
"""
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = (ROOT / "js" / "data.js").read_text(encoding="utf-8")

# 카테고리 id -> 정적 페이지 주소 슬러그
CAT_SLUG = {
    "uiux": "ui-ux", "graphic": "graphic", "color": "color", "typo": "font",
    "asset": "assets", "mockup": "mockups", "dev": "dev", "tool": "tools", "freelance": "freelance",
    "job": "jobs", "ai": "ai", "community": "community", "creator": "creators",
}


def block(name, src=SRC):
    i = src.index(f"const {name} = [")
    return src[i:src.index("\n];", i)]


def fields(chunk, keys):
    out = []
    for m in re.finditer(r"\{[^{}]*\}", chunk):
        row, item = m.group(0), {}
        for k in keys:
            # 값이 작은따옴표 또는 큰따옴표로 감싸인 두 경우를 모두 처리
            v = (re.search(rf"\b{k}: '((?:[^'\\]|\\.)*)'", row)
                 or re.search(rf'\b{k}: "((?:[^"\\]|\\.)*)"', row))
            if v:
                item[k] = v.group(1).replace("\\'", "'").replace('\\"', '"')
        if item.get(keys[0]):
            out.append(item)
    return out


def ai_subs():
    """AI 카테고리 소분류의 표시 순서"""
    m = re.search(r"const AI_SUBS = \[(.*?)\]", SRC, re.S)
    return re.findall(r"'([^']+)'", m.group(1)) if m else []


cats = fields(block("CATEGORIES"), ["id", "label", "desc"])
sites = fields(block("SITES"), ["name", "url", "desc", "cat", "sub"])
styles = fields(block("STYLES"), ["name", "en", "era", "desc", "traits", "people"])
trends = fields(block("TRENDS"), ["name", "area", "desc"])
terms = fields(block("GLOSSARY"), ["term", "en", "group", "desc"])
gloss_groups = fields(block("GLOSSARY_GROUPS"), ["id", "label"])


def counts():
    out = {}
    for s in sites:
        out[s.get("cat", "")] = out.get(s.get("cat", ""), 0) + 1
    return out
