#!/usr/bin/env python3
"""
디자인 허브 관리자 — 이 맥에서만 여는 관리 화면입니다.

  python3 tools/admin.py

브라우저가 열리면 거기서 사이트를 추가·수정하고, 읽을거리 글을 쓰고, '사이트에 올리기'를 누르면 됩니다.
(바탕화면 '클로드코드' 폴더의 '디자인허브 관리자.command' 를 두 번 눌러도 같습니다)

하는 일
- 사이트: js/data.js 의 SITES 와 js/data.en.js 의 SITES_EN 에 한 줄씩 넣고 고치고 지웁니다.
- 읽을거리: content/articles/<주소>.md (한국어) 와 content/articles-en/<주소>.md (영어) 를 씁니다.
- 올리기: 빌드 스크립트를 순서대로 돌리고, git 으로 커밋·푸시한 뒤 검색엔진에 알립니다.
  푸시하면 GitHub Actions 가 1~2분 안에 designrefs.com 에 반영합니다.
- 디자인 잡담: 게시판 서버(Cloudflare Worker)에 운영자 열쇠로 접속해 글을 고치고, 숨기고, 지웁니다.
  이쪽은 누르는 즉시 사이트에 반영됩니다 (올리기 필요 없음).

안전장치
- 127.0.0.1 에서만 열립니다. 같은 와이파이의 다른 기기에서도 들어올 수 없습니다.
- 실행할 때마다 새 열쇠(토큰)를 만들어, 이 창이 아닌 다른 웹페이지가 몰래 요청을 보내지 못하게 합니다.
- GitHub 토큰은 다루지 않습니다. 푸시는 이 맥에 이미 설정된 git 로그인을 그대로 씁니다.
- 게시판 운영자 열쇠(ADMIN_TOKEN)는 화면에서 직접 넣습니다. '이 맥에 기억'을 고르면
  저장소 밖(~/.config/designhub/talk-admin-token, 나만 읽을 수 있는 권한)에만 저장하고,
  화면이나 기록에 다시 보여 주지 않습니다.
"""
import base64, datetime, html, http.server, json, mimetypes, pathlib, re, secrets
import subprocess, sys, threading, urllib.parse, urllib.request, webbrowser

TOOLS = pathlib.Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
import articles as A  # noqa: E402  (본문 미리보기에 같은 변환기를 씁니다)

HOST, PORT = "127.0.0.1", 8787
if "--port" in sys.argv:          # 다른 포트로 띄울 때: python3 tools/admin.py --port 8788
    PORT = int(sys.argv[sys.argv.index("--port") + 1])
TOKEN = secrets.token_urlsafe(24)
DATA = ROOT / "js" / "data.js"
DATA_EN = ROOT / "js" / "data.en.js"
KO_DIR = ROOT / "content" / "articles"
EN_DIR = ROOT / "content" / "articles-en"
IMG_DIR = ROOT / "articles" / "img"
TAGS = ["한국", "무료", "유료", "AI", "유튜브", "인스타그램", "팟캐스트"]
KEY_FILE = pathlib.Path.home() / ".config" / "designhub" / "talk-admin-token"
TALK_KEY = {"value": None}      # 이번 실행 동안만 기억하는 운영자 열쇠
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LOCK = threading.Lock()          # 파일을 고치는 요청은 한 번에 하나씩


class Oops(Exception):
    """화면에 그대로 보여 줄 오류"""


# =========================================================
# data.js 읽고 쓰기 — 사이트 한 줄 = { name: '...', url: '...', ... },
# =========================================================
def js_str(s):
    return "'" + str(s).replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ") + "'"


def field(line, key):
    m = (re.search(rf"\b{key}: '((?:[^'\\]|\\.)*)'", line)
         or re.search(rf'\b{key}: "((?:[^"\\]|\\.)*)"', line))
    return m.group(1).replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\") if m else ""


def sites_span(src):
    """SITES 배열의 시작·끝 위치"""
    i = src.index("const SITES = [")
    return i, src.index("\n];", i)


def read_sites():
    src = DATA.read_text(encoding="utf-8")
    a, b = sites_span(src)
    out = []
    for line in src[a:b].split("\n"):
        if not line.lstrip().startswith("{ name:"):
            continue
        tags = re.search(r"tags: \[(.*?)\]", line)
        out.append({
            "name": field(line, "name"), "url": field(line, "url"), "desc": field(line, "desc"),
            "cat": field(line, "cat"), "sub": field(line, "sub"),
            "tags": re.findall(r"'([^']*)'", tags.group(1)) if tags else [],
        })
    return out


def read_meta():
    """카테고리, AI 소분류"""
    src = DATA.read_text(encoding="utf-8")
    i = src.index("const CATEGORIES = [")
    cats = [{"id": field(ln, "id"), "label": field(ln, "label")}
            for ln in src[i:src.index("\n];", i)].split("\n") if "{ id:" in ln]
    subs = re.findall(r"'([^']+)'", re.search(r"const AI_SUBS = \[(.*?)\]", src, re.S).group(1))
    return cats, subs


def site_line(s):
    parts = [f"name: {js_str(s['name'])}", f"url: {js_str(s['url'])}", f"desc: {js_str(s['desc'])}",
             f"cat: {js_str(s['cat'])}"]
    if s.get("sub"):
        parts.append(f"sub: {js_str(s['sub'])}")
    parts.append("tags: [" + ", ".join(js_str(t) for t in s.get("tags", [])) + "]")
    return "  { " + ", ".join(parts) + " },"


def en_map():
    src = DATA_EN.read_text(encoding="utf-8")
    i = src.index("const SITES_EN = {")
    body = src[src.index("\n", i) + 1:src.index("\n};", i)]
    rows = [ln.strip().rstrip(",") for ln in body.splitlines() if ln.strip().startswith('"')]
    return json.loads("{" + ",".join(rows) + "}")


def write_en(url, name_en, desc_en, old_url=None):
    """data.en.js 의 SITES_EN 에서 한 줄을 넣거나 바꾸거나 지웁니다 (desc_en 이 None 이면 지움)."""
    src = DATA_EN.read_text(encoding="utf-8")
    i = src.index("const SITES_EN = {")
    j = src.index("\n};", i)
    lines = src[i:j].split("\n")
    keys = {json.dumps(old_url or url), json.dumps(url)}
    lines = [ln for ln in lines if not any(ln.strip().startswith(k + ":") for k in keys)]
    if desc_en:
        lines.append(f"  {json.dumps(url)}: [{json.dumps(name_en) if name_en else 'null'}, "
                     f"{json.dumps(desc_en, ensure_ascii=False)}],")
    DATA_EN.write_text(src[:i] + "\n".join(lines) + src[j:], encoding="utf-8")


def save_site(p):
    s = {k: str(p.get(k, "")).strip() for k in ("name", "url", "desc", "cat", "sub", "name_en", "desc_en")}
    s["tags"] = [t for t in p.get("tags", []) if t in TAGS]
    old = (p.get("orig_url") or "").strip()
    cats, subs = read_meta()
    if not s["name"] or not s["desc"]:
        raise Oops("이름과 설명은 꼭 적어 주세요.")
    if not re.match(r"^https?://[^\s/$.?#].[^\s]*$", s["url"]):
        raise Oops("주소는 https:// 로 시작하는 전체 주소로 적어 주세요.")
    if s["cat"] not in {c["id"] for c in cats}:
        raise Oops("분야를 골라 주세요.")
    if s["cat"] == "ai" and s["sub"] not in subs:
        raise Oops("AI 분야는 소분류도 골라 주세요.")
    if s["cat"] != "ai":
        s["sub"] = ""
    sites = read_sites()
    if any(x["url"] == s["url"] for x in sites) and s["url"] != old:
        raise Oops("이미 같은 주소의 사이트가 있습니다.")
    if old and not any(x["url"] == old for x in sites):
        raise Oops("고치려던 사이트를 찾지 못했습니다. 화면을 새로 고쳐 주세요.")
    if s["name_en"] and not s["desc_en"]:
        raise Oops("영문 이름을 적었다면 영문 설명도 적어 주세요.")

    src = DATA.read_text(encoding="utf-8")
    a, b = sites_span(src)
    block = src[a:b].split("\n")
    new = site_line(s)
    placed = False
    if old:
        idx = next(k for k, ln in enumerate(block) if ln.lstrip().startswith("{ name:") and field(ln, "url") == old)
        if field(block[idx], "cat") == s["cat"]:
            block[idx], placed = new, True      # 같은 분야면 제자리에서 고칩니다
        else:
            del block[idx]                      # 분야가 바뀌면 새 분야 쪽으로 옮깁니다
    if not placed:
        # 같은 분야의 마지막 사이트 바로 아래에 넣습니다. 처음 쓰는 분야면 배열 맨 끝에.
        last = max((k for k, ln in enumerate(block)
                    if ln.lstrip().startswith("{ name:") and field(ln, "cat") == s["cat"]), default=len(block) - 1)
        block.insert(last + 1, new)
    DATA.write_text(src[:a] + "\n".join(block) + src[b:], encoding="utf-8")
    # 한국어 이름이 아닌데 영문 이름을 따로 적을 필요는 없습니다
    name_en = s["name_en"] if s["name_en"] and s["name_en"] != s["name"] else ""
    write_en(s["url"], name_en, s["desc_en"] or None, old_url=old or None)
    return {"ok": True, "message": "저장했습니다." + ("" if s["desc_en"] else " 영문 설명이 비어 있어 영문판에는 한국어로 보입니다.")}


def delete_site(p):
    url = (p.get("url") or "").strip()
    src = DATA.read_text(encoding="utf-8")
    a, b = sites_span(src)
    block = src[a:b].split("\n")
    keep = [ln for ln in block if not (ln.lstrip().startswith("{ name:") and field(ln, "url") == url)]
    if len(keep) == len(block):
        raise Oops("지울 사이트를 찾지 못했습니다.")
    DATA.write_text(src[:a] + "\n".join(keep) + src[b:], encoding="utf-8")
    write_en(url, None, None)
    return {"ok": True, "message": "지웠습니다."}


# =========================================================
# 읽을거리 — 맨 위 --- 정보 칸 + 마크다운 본문
# =========================================================
KO_KEYS = ["slug", "title", "desc", "date", "order", "tag", "related"]
EN_KEYS = ["slug", "title", "desc", "tag"]


def read_md(path):
    if not path.exists():
        return None
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if not m:
        return {"body": raw}
    meta = {}
    for line in m.group(1).split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    meta["body"] = m.group(2).strip()
    return meta


def write_md(path, meta, keys):
    head = "\n".join(f"{k}: {str(meta.get(k, '')).strip()}" for k in keys if str(meta.get(k, "")).strip())
    path.write_text(f"---\n{head}\n---\n\n{meta.get('body', '').strip()}\n", encoding="utf-8")


def list_articles():
    out = []
    for f in sorted(KO_DIR.glob("*.md")):
        m = read_md(f) or {}
        out.append({"slug": m.get("slug", f.stem), "title": m.get("title", ""), "date": m.get("date", ""),
                    "order": m.get("order", ""), "tag": m.get("tag", ""), "en": (EN_DIR / f.name).exists()})
    out.sort(key=lambda x: (x["date"], -int(x["order"] or 0)), reverse=True)
    return out


def get_article(slug):
    if not SLUG_RE.match(slug or ""):
        raise Oops("글 주소가 올바르지 않습니다.")
    ko = read_md(KO_DIR / f"{slug}.md")
    if ko is None:
        raise Oops("글을 찾지 못했습니다.")
    return {"ko": ko, "en": read_md(EN_DIR / f"{slug}.md")}


def one_line(v):
    return re.sub(r"\s+", " ", str(v or "")).strip()


def save_article(p):
    ko, en = p.get("ko") or {}, p.get("en") or {}
    slug = one_line(ko.get("slug")).lower()
    old = one_line(p.get("orig_slug")).lower()
    if not SLUG_RE.match(slug):
        raise Oops("글 주소는 영어 소문자, 숫자, 하이픈(-)만 쓸 수 있습니다. 예: color-for-beginners")
    for k, name in (("title", "제목"), ("desc", "한 줄 요약"), ("body", "본문")):
        if not str(ko.get(k, "")).strip():
            raise Oops(f"한국어 {name}을(를) 채워 주세요.")
    date = one_line(ko.get("date")) or datetime.date.today().isoformat()
    try:
        datetime.date.fromisoformat(date)
    except ValueError:
        raise Oops("날짜는 2026-09-29 처럼 적어 주세요.")
    order = one_line(ko.get("order"))
    if order and not order.isdigit():
        raise Oops("같은 날 순서는 숫자로 적어 주세요.")
    if slug != old and (KO_DIR / f"{slug}.md").exists():
        raise Oops("같은 주소의 글이 이미 있습니다.")
    related = [r for r in ko.get("related", []) if r in A.RELATED_LABEL]
    body_errors = check_body(ko.get("body", "")) + check_body(en.get("body", ""))
    if body_errors:
        raise Oops(" ".join(body_errors))

    meta = {"slug": slug, "title": one_line(ko["title"]), "desc": one_line(ko["desc"]), "date": date,
            "order": order, "tag": one_line(ko.get("tag")), "related": ", ".join(related),
            "body": ko["body"].replace("\r\n", "\n")}
    write_md(KO_DIR / f"{slug}.md", meta, KO_KEYS)
    en_has = any(str(en.get(k, "")).strip() for k in ("title", "desc", "body"))
    msg = "저장했습니다."
    if en_has:
        for k, name in (("title", "제목"), ("desc", "요약"), ("body", "본문")):
            if not str(en.get(k, "")).strip():
                raise Oops(f"한국어는 저장했습니다. 영문을 쓰려면 영문 {name}도 채워 주세요.")
        EN_DIR.mkdir(exist_ok=True)
        write_md(EN_DIR / f"{slug}.md", {"slug": slug, "title": one_line(en["title"]), "desc": one_line(en["desc"]),
                                         "tag": one_line(en.get("tag")), "body": en["body"].replace("\r\n", "\n")},
                 EN_KEYS)
    else:
        (EN_DIR / f"{slug}.md").unlink(missing_ok=True)
        msg += " 영문이 비어 있어 영문판에는 이 글이 없습니다."
    if old and old != slug:
        (KO_DIR / f"{old}.md").unlink(missing_ok=True)
        (EN_DIR / f"{old}.md").unlink(missing_ok=True)
        msg += f" 주소가 바뀌어 예전 주소(/articles/{old}/)는 올릴 때 사라집니다."
    return {"ok": True, "message": msg, "slug": slug}


def check_body(md):
    """본문에 넣은 그림 파일이 실제로 있는지 봅니다 (없으면 빌드가 멈춥니다)."""
    errs = []
    for src in re.findall(r"^!\[[^\]]*\]\(([^)\s]+)\)\s*$", md or "", re.M):
        if src.startswith(A.SITE) and not (ROOT / src[len(A.SITE):]).exists():
            errs.append(f"그림 파일이 없습니다: {src[len(A.SITE):]}")
    return errs


def delete_article(p):
    slug = one_line(p.get("slug")).lower()
    if not SLUG_RE.match(slug) or not (KO_DIR / f"{slug}.md").exists():
        raise Oops("지울 글을 찾지 못했습니다.")
    (KO_DIR / f"{slug}.md").unlink()
    (EN_DIR / f"{slug}.md").unlink(missing_ok=True)
    return {"ok": True, "message": "지웠습니다. 올리면 사이트에서도 사라집니다."}


def upload_image(p):
    name = re.sub(r"[^a-z0-9.-]+", "-", (p.get("name") or "image").lower()).strip("-.")
    stem, dot, ext = name.rpartition(".")
    if ext not in ("png", "jpg", "jpeg", "webp", "gif", "svg"):
        raise Oops("그림은 png, jpg, webp, gif, svg 만 올릴 수 있습니다.")
    data = base64.b64decode(p.get("data", "").split(",")[-1])
    if len(data) > 5 * 1024 * 1024:
        raise Oops("그림은 5MB 이하로 줄여서 올려 주세요.")
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    stem = stem or "image"
    out, n = IMG_DIR / f"{stem}.{ext}", 2
    while out.exists():
        out, n = IMG_DIR / f"{stem}-{n}.{ext}", n + 1
    out.write_bytes(data)
    url = f"{A.SITE}articles/img/{out.name}"
    return {"ok": True, "markdown": f"![그림 설명을 여기에]({url})", "url": url}


def check_url(p):
    url = (p.get("url") or "").strip()
    if not re.match(r"^https?://", url):
        raise Oops("https:// 로 시작하는 주소를 넣어 주세요.")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (DesignHub admin link check)"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read(200000).decode("utf-8", "ignore")
            t = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
            return {"ok": True, "status": r.status, "final": r.geturl(),
                    "title": html.unescape(t.group(1).strip())[:120] if t else ""}
    except urllib.error.HTTPError as err:
        return {"ok": err.code < 500 and err.code not in (404, 410), "status": err.code, "final": url, "title": ""}
    except Exception as err:  # 연결 실패, 시간 초과 등
        return {"ok": False, "status": 0, "final": url, "title": "", "error": str(err)[:160]}


# =========================================================
# 빌드 · 올리기
# =========================================================
BUILD = ["build-og.py", "build-pages.py", "build-articles.py", "build-seo.py", "build-en.py"]


def run(cmd, log):
    log.append("$ " + " ".join(cmd))
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if out:
        log.append(out)
    return r.returncode


def build(log):
    for s in BUILD:
        if run([sys.executable, str(TOOLS / s)], log) != 0:
            raise Oops(f"{s} 에서 멈췄습니다. 아래 기록을 확인해 주세요.")


def git_changes():
    r = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True)
    return [ln for ln in r.stdout.splitlines() if ln.strip()]


def source_changes():
    """사람이 고친 원본 파일만 (자동으로 다시 만들어지는 페이지는 뺍니다)"""
    keep = ("js/data.js", "js/data.en.js", "content/", "articles/img/")
    return [ln for ln in git_changes() if any(ln[3:].startswith(k) for k in keep)]


def publish(p):
    msg = one_line(p.get("message")) or "관리자에서 내용 업데이트"
    log = []
    build(log)
    if not git_changes():
        return {"ok": True, "message": "바뀐 내용이 없어서 올릴 것이 없습니다.", "log": "\n".join(log)}
    run(["git", "add", "-A"], log)
    if run(["git", "commit", "-q", "-m", msg], log) != 0:
        raise Oops("커밋하지 못했습니다. 아래 기록을 확인해 주세요.\n" + "\n".join(log))
    if run(["git", "push", "-q", "origin", "HEAD"], log) != 0:
        raise Oops("GitHub 에 올리지 못했습니다. 인터넷 연결이나 git 로그인을 확인해 주세요.\n" + "\n".join(log))
    run([sys.executable, str(TOOLS / "indexnow.py")], log)
    return {"ok": True, "message": "올렸습니다. 1~2분 뒤 designrefs.com 에 반영됩니다.", "log": "\n".join(log)}


def build_only(p):
    log = []
    build(log)
    return {"ok": True, "message": "빌드했습니다. '내 맥에서 미리보기'로 확인해 보세요.", "log": "\n".join(log)}


def state(_=None):
    cats, subs = read_meta()
    en = en_map()
    sites = read_sites()
    for s in sites:
        e = en.get(s["url"])
        s["name_en"], s["desc_en"] = (e[0] or "", e[1]) if e else ("", "")
    return {"cats": cats, "subs": subs, "tags": TAGS, "sites": sites, "articles": list_articles(),
            "related": [{"id": k, "label": v} for k, v in A.RELATED_LABEL.items()],
            "changes": source_changes(), "today": datetime.date.today().isoformat()}


def preview(p):
    # 방금 올린 그림은 아직 사이트에 없으니 내 맥의 파일로 보여 줍니다
    out = A.to_html(p.get("md", "")).replace(A.SITE + "articles/img/", "/articles/img/")
    return {"ok": True, "html": out}


# =========================================================
# 디자인 잡담 — 게시판 서버에 운영자 열쇠로 요청합니다
# =========================================================
def talk_api():
    # 시험할 때만: DESIGNHUB_TALK_API 로 다른 서버(로컬 wrangler dev 등)를 가리킬 수 있습니다
    import os
    if os.environ.get("DESIGNHUB_TALK_API"):
        return os.environ["DESIGNHUB_TALK_API"]
    m = re.search(r"const TALK_API = '([^']+)'", (ROOT / "js" / "talk.js").read_text(encoding="utf-8"))
    if not m:
        raise Oops("js/talk.js 에서 게시판 서버 주소를 찾지 못했습니다.")
    return m.group(1)


def talk_key():
    if TALK_KEY["value"]:
        return TALK_KEY["value"]
    if KEY_FILE.exists():
        TALK_KEY["value"] = KEY_FILE.read_text(encoding="utf-8").strip() or None
    return TALK_KEY["value"]


def talk_call(method, query, body=None, key=None):
    key = key or talk_key()
    if not key:
        raise Oops("운영자 열쇠를 먼저 넣어 주세요.")
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(f"{talk_api()}?{urllib.parse.urlencode(query)}", data=data, method=method,
                                 headers={"Authorization": "Bearer " + key, "Content-Type": "application/json",
                                          "User-Agent": "DesignHubAdmin"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        try:
            msg = json.loads(err.read().decode("utf-8")).get("error", "")
        except Exception:
            msg = ""
        if err.code == 403:
            raise Oops("운영자 열쇠가 맞지 않습니다. 다시 넣어 주세요.")
        raise Oops(msg or f"게시판 서버가 {err.code} 로 답했습니다.")
    except urllib.error.URLError as err:
        raise Oops(f"게시판 서버에 연결하지 못했습니다: {err.reason}")


def talk_status(_=None):
    return {"ok": True, "connected": bool(talk_key()), "remembered": KEY_FILE.exists()}


def talk_connect(p):
    key = str(p.get("key") or "").strip()
    if not key:
        raise Oops("열쇠를 넣어 주세요.")
    talk_call("GET", {"page": "talk", "all": "1"}, key=key)      # 맞는지 먼저 확인
    TALK_KEY["value"] = key
    if p.get("remember"):
        KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
        KEY_FILE.touch(mode=0o600, exist_ok=True)
        KEY_FILE.chmod(0o600)
        KEY_FILE.write_text(key, encoding="utf-8")
    else:
        KEY_FILE.unlink(missing_ok=True)
    return {"ok": True, "message": "게시판에 연결했습니다." + (" 이 맥에 기억해 두었습니다." if p.get("remember") else "")}


def talk_forget(_=None):
    TALK_KEY["value"] = None
    KEY_FILE.unlink(missing_ok=True)
    return {"ok": True, "message": "열쇠를 잊었습니다. 다음에 다시 넣어야 합니다."}


def talk_list(_=None):
    d = talk_call("GET", {"page": "talk", "all": "1"})
    return {"ok": True, "items": d.get("items", [])}


def talk_update(p):
    body = {k: p[k] for k in ("name", "body", "hidden") if k in p}
    d = talk_call("PATCH", {"id": int(p.get("id") or 0)}, body)
    return {"ok": True, "item": d.get("item"), "message": "고쳤습니다. 사이트에 바로 반영됩니다."}


def talk_delete(p):
    talk_call("DELETE", {"id": int(p.get("id") or 0)}, {})
    return {"ok": True, "message": "지웠습니다. 사이트에서도 바로 사라집니다."}


API = {"state": state, "site": save_site, "site-delete": delete_site, "article-get": lambda p: get_article(p.get("slug")),
       "article": save_article, "article-delete": delete_article, "upload": upload_image, "check-url": check_url,
       "preview": preview, "publish": publish, "build": build_only,
       "talk-status": talk_status, "talk-connect": talk_connect, "talk-forget": talk_forget,
       "talk-list": talk_list, "talk-update": talk_update, "talk-delete": talk_delete}


# =========================================================
# 서버
# =========================================================
class Handler(http.server.BaseHTTPRequestHandler):
    server_version = "DesignHubAdmin"

    def log_message(self, fmt, *args):
        pass  # 터미널을 조용하게

    def _host_ok(self):
        # 다른 주소(DNS 리바인딩)로 들어온 요청은 받지 않습니다
        return self.headers.get("Host", "") in (f"127.0.0.1:{PORT}", f"localhost:{PORT}")

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Frame-Options", "DENY")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if not self._host_ok():
            return self._send(403, "forbidden", "text/plain")
        path = urllib.parse.urlparse(self.path).path
        if path in ("/", "/index.html"):
            page = (TOOLS / "admin.html").read_text(encoding="utf-8").replace("__TOKEN__", TOKEN)
            return self._send(200, page, "text/html; charset=utf-8")
        if path.startswith("/site/") or path.startswith("/css/") or path.startswith("/articles/img/"):
            # 내 맥에서 미리보기: 저장소 폴더의 파일을 그대로 보여 줍니다
            rel = urllib.parse.unquote(path[len("/site/"):] if path.startswith("/site/") else path[1:])
            f = (ROOT / rel).resolve()
            if f.is_dir():
                f = f / "index.html"
            if ROOT not in f.parents or not f.is_file() or "/.git" in str(f):
                return self._send(404, "not found", "text/plain")
            ctype = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
            if ctype.startswith("text/") or ctype in ("application/javascript", "image/svg+xml"):
                ctype += "; charset=utf-8"
            return self._send(200, f.read_bytes(), ctype)
        return self._send(404, "not found", "text/plain")

    def do_POST(self):
        if not self._host_ok() or self.headers.get("X-Admin-Token") != TOKEN:
            return self._send(403, json.dumps({"ok": False, "message": "관리자 창을 새로 열어 주세요."}))
        name = urllib.parse.urlparse(self.path).path.removeprefix("/api/")
        fn = API.get(name)
        if not fn:
            return self._send(404, json.dumps({"ok": False, "message": "없는 기능입니다."}))
        try:
            size = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(size) or b"{}")
            with LOCK:
                result = fn(payload)
            self._send(200, json.dumps(result, ensure_ascii=False))
        except (Oops, SystemExit) as err:   # 빌드 도구가 멈추며 남긴 말도 그대로 보여 줍니다
            self._send(400, json.dumps({"ok": False, "message": str(err)}, ensure_ascii=False))
        except Exception as err:  # 예상 못 한 오류도 화면에 보여 줍니다
            self._send(500, json.dumps({"ok": False, "message": f"오류가 났습니다: {err}"}, ensure_ascii=False))


def main():
    try:
        srv = http.server.ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError:
        url = f"http://{HOST}:{PORT}/"
        print(f"관리자 창이 이미 열려 있는 것 같습니다. 브라우저에서 {url} 을 새로 고치거나,\n"
              "먼저 열어 둔 터미널 창을 닫고 다시 실행해 주세요.")
        sys.exit(1)
    url = f"http://{HOST}:{PORT}/"
    print(f"디자인 허브 관리자: {url}\n이 창을 닫거나 Ctrl+C 를 누르면 관리자가 꺼집니다.")
    if "--no-open" not in sys.argv:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n관리자를 껐습니다.")


if __name__ == "__main__":
    main()
