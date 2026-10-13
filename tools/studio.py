#!/usr/bin/env python3
"""
디자인 허브 스튜디오 — 인스타 캐러셀·릴스와 스레드 글을 '만들기 → 발행' 두 번으로 올리는 화면입니다.

  python3 tools/studio.py

브라우저가 열리면
  1) 오늘 올릴 것을 추천받거나, 캐러셀 / 릴스 / 스레드 중에서 고르고
  2) 재료(읽을거리 글, 레퍼런스 묶음, 용어, 스레드 초안)를 고른 뒤 '만들기'
  3) 미리보기와 캡션을 확인하고 '발행'
을 누르면 됩니다.

발행할 때 하는 일
- 새로 만든 이미지·영상을 GitHub 에 올리고(사이트 배포), 공개 주소에서 열릴 때까지 기다립니다.
  인스타그램 API 는 공개된 주소의 이미지·영상만 받기 때문입니다.
- 인스타그램(graph.instagram.com)과 스레드(graph.threads.net)에 게시하고, 링크를 보여 줍니다.
- 무엇을 언제 올렸는지 ~/.config/designhub/studio-history.json 에 남겨, 같은 걸 두 번 올리지 않게 합니다.

토큰
- Claude 데스크톱 설정(designhub MCP 서버)에 넣어 둔 인스타그램·스레드 토큰을 그대로 읽어 씁니다.
  화면이나 기록에는 토큰을 보여 주지 않고, 메타 서버 말고는 어디에도 보내지 않습니다.

AI 편집장
- 'AI 편집장' 탭에서 발행된 글을 Claude(coach.py)에게 검토받고, 제안을 [적용]한 뒤 '사이트에 반영'을 누릅니다.
- 캡션·스레드 글 옆의 'AI로 다듬기'로 발행 전에 글을 다듬습니다.

안전장치는 관리자(admin.py)와 같습니다: 127.0.0.1 에서만 열리고, 실행할 때마다 새 열쇠를 만듭니다.
"""
import datetime, http.server, importlib.util, json, mimetypes, pathlib, secrets, shutil
import subprocess, sys, threading, time, urllib.error, urllib.parse, urllib.request, webbrowser

TOOLS = pathlib.Path(__file__).resolve().parent
ROOT = TOOLS.parent
SITE = "https://designrefs.com/"
HOST, PORT = "127.0.0.1", 8790
if "--port" in sys.argv:
    PORT = int(sys.argv[sys.argv.index("--port") + 1])
TOKEN = secrets.token_urlsafe(24)
CONF_DIR = pathlib.Path.home() / ".config" / "designhub"
HISTORY = CONF_DIR / "studio-history.json"
DRAFTS = CONF_DIR / "threads-drafts.json"          # 내가 고친 스레드 초안만 (id → 글)
CLAUDE_CONF = pathlib.Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
CARDS = ROOT / "social" / "cards"
REELS = ROOT / "social" / "reels"
IG = "https://graph.instagram.com/v23.0"
TH = "https://graph.threads.net/v1.0"
LOCK = threading.Lock()
JOBS = {}


class Oops(Exception):
    """화면에 그대로 보여 줄 오류"""


# =========================================================
# 재료 목록
# =========================================================
def _cards_module():
    spec = importlib.util.spec_from_file_location("build_cards", TOOLS / "build-cards.py")
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(TOOLS))
    spec.loader.exec_module(mod)
    return mod


def read_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def articles():
    sys.path.insert(0, str(TOOLS))
    import articles as A
    out = []
    for a in sorted(A.load(), key=lambda a: a["date"], reverse=True):
        out.append({"slug": a["slug"], "title": a["title"], "date": str(a["date"])[:10],
                    "desc": a.get("desc", ""), "url": f"{SITE}articles/{a['slug']}/"})
    return out


def history():
    return read_json(HISTORY, [])


def add_history(item):
    CONF_DIR.mkdir(parents=True, exist_ok=True)
    h = history()
    h.insert(0, item)
    HISTORY.write_text(json.dumps(h[:300], ensure_ascii=False, indent=2), encoding="utf-8")


def published_keys():
    return {f'{h["type"]}:{h["id"]}' for h in history()}


def drafts():
    """스레드 초안: 저장소의 최신 초안(tools/threads_drafts.json) 위에, 내가 고친 글만 덮어씁니다.
    그래서 초안을 새로 고쳐 올리면 맥에서도 바로 새 초안이 보입니다."""
    seed = read_json(TOOLS / "threads_drafts.json", [])
    mine = read_json(DRAFTS, {})
    if not isinstance(mine, dict):   # 예전 형식(초안 전체를 복사해 두던 것)은 버리고 새로 시작
        mine = {}
    return [dict(d, text=mine.get(d["id"], d["text"])) for d in seed]


def save_draft(p):
    mine = read_json(DRAFTS, {})
    if not isinstance(mine, dict):
        mine = {}
    mine[p["id"]] = p["text"]
    CONF_DIR.mkdir(parents=True, exist_ok=True)
    DRAFTS.write_text(json.dumps(mine, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True}


# =========================================================
# 토큰 (Claude 데스크톱 설정에서 읽기)
# =========================================================
def tokens():
    conf = read_json(CLAUDE_CONF, {})
    for s in (conf.get("mcpServers") or {}).values():
        if any("designhub-social" in str(a) for a in s.get("args", [])):
            env = s.get("env", {})
            return env.get("INSTAGRAM_ACCESS_TOKEN", ""), env.get("THREADS_ACCESS_TOKEN", "")
    return "", ""


def hide(text):
    s = str(text)
    for t in tokens():
        if t:
            s = s.replace(t, "[토큰]")
    return s


def meta(base, token, method, path, params=None):
    if not token:
        raise Oops("토큰이 없습니다. Claude 데스크톱에 designhub 서버가 설정돼 있는지 확인해 주세요.")
    q = dict(params or {}, access_token=token)
    url = base + path
    data = None
    if method == "GET":
        url += "?" + urllib.parse.urlencode(q)
    else:
        data = urllib.parse.urlencode(q).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, method=method), timeout=60) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as err:
        body = read_err(err)
        e = body.get("error", {})
        raise Oops(hide(f"메타 API 오류 {e.get('code', err.code)}: {e.get('error_user_msg') or e.get('message') or err.reason}"))
    except (urllib.error.URLError, TimeoutError) as err:
        raise Oops(f"인스타그램·스레드 서버에 연결하지 못했습니다. 인터넷 연결을 확인해 주세요. ({err})")


def read_err(err):
    try:
        return json.loads(err.read() or b"{}")
    except ValueError:
        return {}


# =========================================================
# 만들기
# =========================================================
def run(cmd, log, env=None):
    log.append("$ " + " ".join(str(c) for c in cmd))
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=env)
    out = (r.stdout + r.stderr).strip()
    if out:
        log.append(out[-3000:])
    return r.returncode


def need_tools(reel=False):
    missing = []
    try:
        import PIL  # noqa: F401
    except ImportError:
        missing.append(("Pillow", f"{sys.executable} -m pip install --user pillow"))
    if reel and not shutil.which("ffmpeg"):
        missing.append(("ffmpeg", "brew install ffmpeg"))
    if missing:
        raise Oops("만들려면 먼저 설치가 필요합니다. 터미널에서 아래를 실행해 주세요.\n\n"
                   + "\n".join(f"· {name}: {cmd}" for name, cmd in missing))


def card_set_id(source):
    return f"article-{source.split(':', 1)[1]}" if source.startswith("article:") else source


def set_info(sid):
    idx = read_json(CARDS / "index.json", {"sets": []})
    return next((s for s in idx["sets"] if s["id"] == sid), None)


def reel_info(rid):
    idx = read_json(REELS / "index.json", {"reels": []})
    return next((r for r in idx["reels"] if r["id"] == rid), None)


def local(url):
    """공개 주소 → 이 화면에서 볼 수 있는 내 맥 주소"""
    return "/" + url.removeprefix(SITE) + f"?v={int(time.time())}"


def make(p):
    kind, source = p.get("type"), p.get("source", "")
    log = []
    if kind == "carousel":
        need_tools()
        sid = card_set_id(source)
        if p.get("rebuild") or not (CARDS / sid / "01.jpg").exists():
            if run([sys.executable, str(TOOLS / "build-cards.py"), source], log) != 0:
                raise Oops("캐러셀을 만들지 못했습니다.\n" + "\n".join(log))
        info = set_info(sid)
        if not info:
            raise Oops("만든 캐러셀을 찾지 못했습니다.\n" + "\n".join(log))
        return {"ok": True, "type": kind, "id": sid, "title": info["title"], "caption": info["caption"],
                "images": [local(u) for u in info["images"]], "link": info.get("article", SITE),
                "published": f"carousel:{sid}" in published_keys(), "log": "\n".join(log)}
    if kind == "reel":
        rid = source
        if rid.endswith("-tour"):
            info = reel_info(rid)
            if not info:
                raise Oops("사이트 투어 릴스는 GitHub Actions 에서 만듭니다. 아래 '투어 만들기'를 눌러 주세요.")
        else:
            need_tools(reel=True)
            sid = rid.removesuffix("-cards")
            if not (CARDS / sid / "01.jpg").exists():
                if run([sys.executable, str(TOOLS / "build-cards.py"), "article:" + sid.removeprefix("article-")
                        if sid.startswith("article-") else sid], log) != 0:
                    raise Oops("카드를 먼저 만들지 못했습니다.\n" + "\n".join(log))
            if p.get("rebuild") or not (REELS / f"{sid}-cards.mp4").exists():
                if run([sys.executable, str(TOOLS / "build-reels.py"), f"cards:{sid}"], log) != 0:
                    raise Oops("릴스를 만들지 못했습니다.\n" + "\n".join(log))
            rid = f"{sid}-cards"
            info = reel_info(rid)
        if not info:
            raise Oops("만든 릴스를 찾지 못했습니다.\n" + "\n".join(log))
        return {"ok": True, "type": kind, "id": rid, "title": info["title"], "caption": info["caption"],
                "video": local(info["video"]), "cover": local(info["cover"]), "seconds": info["seconds"],
                "link": SITE, "published": f"reel:{rid}" in published_keys(), "log": "\n".join(log)}
    if kind == "thread":
        if source.startswith("article:"):
            a = next((x for x in articles() if x["slug"] == source.split(":", 1)[1]), None)
            if not a:
                raise Oops("없는 글입니다.")
            text = f"{a['title']}\n\n{a['desc']}"
            return {"ok": True, "type": kind, "id": source, "title": a["title"], "text": text, "link": a["url"],
                    "published": f"thread:{source}" in published_keys()}
        if source.startswith("draft:"):
            d = next((x for x in drafts() if x["id"] == source.split(":", 1)[1]), None)
            if not d:
                raise Oops("없는 초안입니다.")
            return {"ok": True, "type": kind, "id": source, "title": d["label"], "text": d["text"],
                    "link": d.get("link", ""), "draft": d["id"], "published": f"thread:{source}" in published_keys()}
        return {"ok": True, "type": kind, "id": "custom:" + datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
                "title": "직접 쓰기", "text": "", "link": "", "published": False}
    raise Oops("무엇을 만들지 골라 주세요.")


def tour(p):
    """사이트 투어 릴스는 바깥 사이트 화면을 찍어야 해서 GitHub Actions 에서 만듭니다."""
    sid = p.get("source", "")
    url = "https://github.com/Leo-AXdesign/Leo-AXdesign.github.io/actions/workflows/reels.yml"
    if shutil.which("gh"):
        log = []
        if run(["gh", "workflow", "run", "reels.yml", "-f", f"targets=tour:{sid}"], log) == 0:
            return {"ok": True, "message": f"GitHub Actions 에서 '{sid}' 투어 릴스를 만들기 시작했습니다. "
                                            "10분쯤 뒤 '새로 고침'을 누르면 목록에 나옵니다."}
    webbrowser.open(url)
    return {"ok": True, "message": f"GitHub Actions 화면을 열었습니다. 'Run workflow' 를 누르고 targets 에 tour:{sid} 를 넣어 주세요."}


# =========================================================
# 발행
# =========================================================
def git_publish(paths, msg, log):
    r = subprocess.run(["git", "status", "--porcelain", "--", *paths], cwd=ROOT, capture_output=True, text=True)
    if not r.stdout.strip():
        log.append("새로 올릴 파일이 없습니다 (이미 사이트에 있음).")
        return False
    if run(["git", "add", "--", *paths], log) != 0 or run(["git", "commit", "-q", "-m", msg, "--", *paths], log) != 0:
        raise Oops("커밋하지 못했습니다.")
    if run(["git", "pull", "-q", "--rebase", "--autostash", "origin", "main"], log) != 0:
        run(["git", "rebase", "--abort"], log)
        raise Oops("GitHub 의 최신 내용을 받아 오지 못했습니다.")
    if run(["git", "push", "-q", "origin", "HEAD"], log) != 0:
        raise Oops("GitHub 에 올리지 못했습니다. 인터넷이나 git 로그인을 확인해 주세요.")
    return True


def wait_public(urls, step, timeout=360):
    """사이트 배포가 끝나 공개 주소에서 파일이 열릴 때까지 기다립니다."""
    start = time.time()
    left = list(urls)
    while left and time.time() - start < timeout:
        u = left[0]
        try:
            req = urllib.request.Request(f"{u}?check={int(time.time())}", method="HEAD")
            with urllib.request.urlopen(req, timeout=15) as r:
                if r.status == 200:
                    left.pop(0)
                    continue
        except (urllib.error.URLError, TimeoutError):
            pass
        step(f"사이트 배포를 기다리는 중… ({int(time.time() - start)}초)")
        time.sleep(8)
    if left:
        raise Oops("6분이 지나도 사이트에서 파일이 열리지 않습니다. 잠시 뒤 다시 '발행'을 눌러 주세요.")


def ig_wait(ig, cid, step, tries=150):
    for i in range(tries):
        s = meta(IG, ig, "GET", f"/{cid}", {"fields": "status_code,status"})
        if s.get("status_code") == "FINISHED":
            return
        if s.get("status_code") in ("ERROR", "EXPIRED"):
            raise Oops(f"인스타그램이 미디어를 처리하지 못했습니다: {s.get('status') or s.get('status_code')}")
        if i % 5 == 4:
            step(f"인스타그램이 처리하는 중… ({i * 2}초)")
        time.sleep(2)
    raise Oops("인스타그램 처리가 너무 오래 걸립니다. 잠시 뒤 인스타그램 앱에서 올라갔는지 확인해 주세요.")


def ig_publish(kind, info, caption, step):
    ig, _ = tokens()
    uid = meta(IG, ig, "GET", "/me", {"fields": "user_id"})["user_id"]
    if kind == "carousel":
        children = []
        for n, url in enumerate(info["images"], 1):
            step(f"인스타그램에 이미지 올리는 중 ({n}/{len(info['images'])})")
            c = meta(IG, ig, "POST", f"/{uid}/media", {"image_url": url, "is_carousel_item": "true"})
            ig_wait(ig, c["id"], step, 30)
            children.append(c["id"])
        parent = meta(IG, ig, "POST", f"/{uid}/media", {"media_type": "CAROUSEL", "children": ",".join(children), "caption": caption})
    else:
        step("인스타그램에 영상 올리는 중 (몇 분 걸릴 수 있어요)")
        parent = meta(IG, ig, "POST", f"/{uid}/media", {"media_type": "REELS", "video_url": info["video"],
                                                        "cover_url": info["cover"], "caption": caption, "share_to_feed": "true"})
    ig_wait(ig, parent["id"], step)
    post = meta(IG, ig, "POST", f"/{uid}/media_publish", {"creation_id": parent["id"]})
    return meta(IG, ig, "GET", f"/{post['id']}", {"fields": "permalink"}).get("permalink", "")


def th_publish(text, link, step):
    _, th = tokens()
    if len(text) > 500:
        raise Oops(f"스레드 글은 500자까지입니다. 지금 {len(text)}자예요.")
    uid = meta(TH, th, "GET", "/me", {"fields": "id"})["id"]
    params = {"media_type": "TEXT", "text": text}
    if link:
        params["link_attachment"] = link
    step("스레드에 올리는 중")
    c = meta(TH, th, "POST", f"/{uid}/threads", params)
    for _ in range(30):
        s = meta(TH, th, "GET", f"/{c['id']}", {"fields": "status,error_message"})
        if s.get("status") == "FINISHED":
            break
        if s.get("status") in ("ERROR", "EXPIRED"):
            raise Oops(f"스레드가 글을 처리하지 못했습니다: {s.get('error_message') or s.get('status')}")
        time.sleep(2)
    post = meta(TH, th, "POST", f"/{uid}/threads_publish", {"creation_id": c["id"]})
    return meta(TH, th, "GET", f"/{post['id']}", {"fields": "permalink"}).get("permalink", "")


def check_text(text):
    if "[" in text and "]" in text:
        raise Oops("초안에 [ ] 로 비워 둔 자리가 남아 있어요. 실제 경험으로 바꾸거나 지운 뒤 발행해 주세요.")


def do_publish(job, p):
    def step(msg):
        job["steps"].append(msg)

    kind, rid = p["type"], p["id"]
    links = {}
    if kind in ("carousel", "reel"):
        info = set_info(rid) if kind == "carousel" else reel_info(rid)
        caption = p.get("caption", "").strip()
        if len(caption) > 2200:
            raise Oops("인스타 캡션은 2,200자까지입니다.")
        step("1. 이미지·영상을 사이트에 올리는 중")
        paths = ["social/cards", "social/reels"]
        if git_publish(paths, f"SNS 발행 준비: {rid}", job["log"]):
            step("GitHub 에 올렸습니다. 사이트 배포를 기다립니다.")
        urls = info["images"] if kind == "carousel" else [info["video"], info["cover"]]
        wait_public(urls, step)
        step("2. 공개 주소 확인 완료. 인스타그램에 게시합니다.")
        links["instagram"] = ig_publish(kind, info, caption, step)
        step("인스타그램 게시 완료")
        if p.get("also_thread") and p.get("thread_text", "").strip():
            check_text(p["thread_text"])
            links["threads"] = th_publish(p["thread_text"].strip(), p.get("link") or SITE, step)
            step("스레드 게시 완료")
    elif kind == "thread":
        text = p.get("text", "").strip()
        if not text:
            raise Oops("올릴 글이 비어 있어요.")
        check_text(text)
        links["threads"] = th_publish(text, p.get("link", ""), step)
        step("스레드 게시 완료")
        if p.get("draft"):
            save_draft({"id": p["draft"], "text": text})
    add_history({"type": kind, "id": rid, "title": p.get("title", rid), "at": datetime.datetime.now().isoformat(timespec="minutes"),
                 "links": links})
    job["links"] = links


def publish(p):
    if p.get("type") not in ("carousel", "reel", "thread"):
        raise Oops("무엇을 발행할지 모르겠어요.")
    jid = secrets.token_hex(6)
    job = JOBS[jid] = {"done": False, "ok": None, "steps": [], "log": [], "links": {}, "message": "", "data": None}

    def work():
        try:
            with LOCK:
                do_publish(job, p)
            job["ok"], job["message"] = True, "발행했습니다."
        except (Oops, SystemExit) as err:
            job["ok"], job["message"] = False, hide(str(err))
        except Exception as err:   # 예상 못 한 오류도 화면에 보여 줍니다
            job["ok"], job["message"] = False, hide(f"오류가 났습니다: {err}")
        job["done"] = True

    threading.Thread(target=work, daemon=True).start()
    return {"ok": True, "job": jid}


def job_status(p):
    job = JOBS.get(p.get("job"))
    if not job:
        raise Oops("작업을 찾을 수 없습니다.")
    # ok 는 '이 확인 요청이 잘 됐는지', success 는 '작업 결과' (진행 중이면 None)
    return {"ok": True, "success": job.get("ok"), **{k: job.get(k) for k in ("done", "steps", "links", "message", "data")},
            "log": hide("\n".join(job["log"]))[-4000:]}


# =========================================================
# 오늘의 추천 — 기획서의 주간 일정대로
# =========================================================
PLAN = {0: ("carousel", "ref", "월요일 · 레퍼런스 캐러셀"), 1: ("thread", "draft", "화요일 · 스레드 (경험 → 생각)"),
        2: ("carousel", "article", "수요일 · AI 인사이트 캐러셀"), 3: ("thread", "draft", "목요일 · 스레드 (질문)"),
        4: ("reel", "reel", "금요일 · 릴스"), 5: ("thread", "draft", "토요일 · 스레드 (짧은 관찰)"), 6: (None, None, "일요일 · 쉬는 날")}


def recommend(sources):
    done = published_keys()
    wd = datetime.datetime.now().weekday()
    kind, pool, label = PLAN[wd]
    if not kind:
        return {"label": label, "note": "기획대로라면 오늘은 쉽니다. 그래도 올리고 싶으면 아래에서 골라 주세요."}
    if pool == "ref":
        cands = [(s["id"], s["title"]) for s in sources["refs"] if f"carousel:{s['id']}" not in done]
        src = lambda c: c[0]
    elif pool == "article":
        cands = [(f"article:{a['slug']}", a["title"]) for a in sources["articles"] if f"carousel:article-{a['slug']}" not in done]
        src = lambda c: c[0]
    elif pool == "reel":
        cands = [(r["id"], r["title"] + (" (사이트 투어)" if r["id"].endswith("-tour") else " (카드)"))
                 for r in sources["reels"] if f"reel:{r['id']}" not in done]
        src = lambda c: c[0]
    else:
        cands = [(f"draft:{d['id']}", d["label"]) for d in sources["drafts"] if f"thread:draft:{d['id']}" not in done]
        src = lambda c: c[0]
    if not cands:
        return {"label": label, "note": "추천할 재료를 다 올렸어요. 새 글이나 묶음을 만들어 주세요."}
    c = cands[0]
    return {"label": label, "type": kind, "source": src(c), "title": c[1]}


def state(_=None):
    bc = _cards_module()
    refs = [{"id": k, "title": v["title"], "kicker": v.get("kicker", "")} for k, v in bc.SETS.items()]
    reels = read_json(REELS / "index.json", {"reels": []})["reels"]
    reel_opts = [{"id": r["id"], "title": r["title"], "seconds": r["seconds"]} for r in reels]
    # 아직 릴스가 없는 카드 묶음도 '카드 릴스'로 만들 수 있게 보여 줍니다
    have = {r["id"] for r in reels}
    for s in read_json(CARDS / "index.json", {"sets": []})["sets"]:
        if f"{s['id']}-cards" not in have:
            reel_opts.append({"id": f"{s['id']}-cards", "title": s["title"], "seconds": None, "new": True})
    sources = {"articles": articles(), "refs": refs, "reels": reel_opts, "drafts": drafts()}
    ig, th = tokens()
    return {"ok": True, **sources, "history": history()[:30], "published": sorted(published_keys()),
            "tokens": {"instagram": bool(ig), "threads": bool(th)},
            "tools": {"ffmpeg": bool(shutil.which("ffmpeg")), "gh": bool(shutil.which("gh"))},
            "recommend": recommend(sources)}


# =========================================================
# AI 편집장 (coach.py) — 발행된 글 검토, SNS 글 다듬기
# =========================================================
sys.path.insert(0, str(TOOLS))
import coach  # noqa: E402


def background(fn):
    """오래 걸리는 일을 뒤에서 돌리고, 화면은 job 으로 진행을 확인합니다."""
    jid = secrets.token_hex(6)
    job = JOBS[jid] = {"done": False, "ok": None, "steps": [], "log": [], "links": {}, "message": "", "data": None}

    def work():
        try:
            job["data"] = fn(job)
            job["ok"] = True
        except (Oops, coach.CoachError, SystemExit) as err:
            job["ok"], job["message"] = False, hide(str(err))
        except Exception as err:
            job["ok"], job["message"] = False, hide(f"오류가 났습니다: {err}")
        job["done"] = True

    threading.Thread(target=work, daemon=True).start()
    return {"ok": True, "job": jid}


def coach_state(_=None):
    sdk, key = coach.ready()
    return {"ok": True, "sdk": sdk, "key": key, "modes": {k: v["label"] for k, v in coach.MODES.items()},
            "default": coach.DEFAULT}


def coach_key(p):
    key = (p.get("key") or "").strip()
    if not key.startswith("sk-ant-"):
        raise Oops("Anthropic API 키는 sk-ant- 로 시작합니다. console.anthropic.com 의 API Keys 에서 만들 수 있어요.")
    coach.save_key(key)
    return {"ok": True}


def coach_forget(_=None):
    coach.forget_key()
    return {"ok": True}


def coach_article(p):
    slug, mode, web = p.get("slug", ""), p.get("mode"), int(p.get("web", 3))
    return background(lambda job: coach.review_article(slug, mode=mode, web=max(0, min(web, 5))))


def coach_apply(p):
    with LOCK:
        return coach.apply(p.get("slug", ""), p.get("suggestion") or {})


def coach_post(p):
    return background(lambda job: coach.review_post(p.get("kind", "thread"), p.get("text", ""), mode=p.get("mode")))


def coach_edit_article(p):
    return background(lambda job: coach.edit_article(p.get("slug", ""), p.get("request", ""), mode=p.get("mode")))


def coach_edit_post(p):
    return background(lambda job: coach.edit_post(p.get("kind", "thread"), p.get("text", ""), p.get("request", ""), mode=p.get("mode")))


def site_publish(p):
    """고친 글을 사이트에 반영 (관리자의 '사이트에 올리기'와 같은 과정)"""
    spec = importlib.util.spec_from_file_location("admin", TOOLS / "admin.py")
    admin = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(admin)

    def work(job):
        job["steps"].append("빌드하고 GitHub 에 올리는 중… (1분쯤)")
        with LOCK:
            r = admin.publish({"message": f"AI 편집장 제안 반영: {p.get('slug', '')}"})
        job["message"] = r.get("message", "")
        job["log"].append(r.get("log", ""))
        return r
    return background(work)


API = {"state": state, "make": make, "publish": publish, "job": job_status, "tour": tour, "save_draft": save_draft,
       "coach_state": coach_state, "coach_key": coach_key, "coach_forget": coach_forget, "coach_article": coach_article,
       "coach_apply": coach_apply, "coach_post": coach_post, "site_publish": site_publish,
       "coach_edit_article": coach_edit_article, "coach_edit_post": coach_edit_post}


# =========================================================
# 서버
# =========================================================
class Handler(http.server.BaseHTTPRequestHandler):
    server_version = "DesignHubStudio"

    def log_message(self, fmt, *args):
        pass

    def _host_ok(self):
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
            page = (TOOLS / "studio.html").read_text(encoding="utf-8").replace("__TOKEN__", TOKEN)
            return self._send(200, page, "text/html; charset=utf-8")
        if path.startswith("/social/"):   # 미리보기: 만든 이미지·영상
            f = (ROOT / urllib.parse.unquote(path[1:])).resolve()
            if (ROOT / "social") not in f.parents or not f.is_file():
                return self._send(404, "not found", "text/plain")
            return self._send(200, f.read_bytes(), mimetypes.guess_type(f.name)[0] or "application/octet-stream")
        return self._send(404, "not found", "text/plain")

    def do_POST(self):
        if not self._host_ok() or self.headers.get("X-Studio-Token") != TOKEN:
            return self._send(403, json.dumps({"ok": False, "message": "스튜디오 창을 새로 열어 주세요."}))
        fn = API.get(urllib.parse.urlparse(self.path).path.removeprefix("/api/"))
        if not fn:
            return self._send(404, json.dumps({"ok": False, "message": "없는 기능입니다."}))
        try:
            size = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(size) or b"{}")
            if fn is make:
                with LOCK:
                    result = fn(payload)
            else:
                result = fn(payload)
            self._send(200, json.dumps(result, ensure_ascii=False))
        except (Oops, coach.CoachError, SystemExit) as err:
            self._send(400, json.dumps({"ok": False, "message": hide(str(err))}, ensure_ascii=False))
        except Exception as err:
            self._send(500, json.dumps({"ok": False, "message": hide(f"오류가 났습니다: {err}")}, ensure_ascii=False))


def main():
    try:
        srv = http.server.ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError:
        print(f"스튜디오가 이미 열려 있는 것 같습니다. 브라우저에서 http://{HOST}:{PORT}/ 을 새로 고쳐 주세요.")
        sys.exit(1)
    url = f"http://{HOST}:{PORT}/"
    print(f"디자인 허브 스튜디오: {url}\n이 창을 닫거나 Ctrl+C 를 누르면 꺼집니다.")
    if "--no-open" not in sys.argv:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n스튜디오를 껐습니다.")


if __name__ == "__main__":
    main()
