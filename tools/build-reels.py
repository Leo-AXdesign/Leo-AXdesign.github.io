#!/usr/bin/env python3
"""
인스타그램 릴스(1080×1920, 세로 영상)를 만듭니다.

  python3 tools/build-reels.py cards:fonts-pick    # 카드뉴스를 넘겨 보는 영상 (어디서나)
  python3 tools/build-reels.py tour:fonts-pick     # 사이트 화면을 스크롤하는 투어 영상 (인터넷 필요)
  python3 tools/build-reels.py motion:fonts-pick   # 글자가 움직이는 모션 릴스 + 박자 맞춘 배경음악 (Remotion)

- cards: social/cards/<묶음>/*.jpg 를 한 장씩 천천히 확대하며 넘깁니다. 먼저 build-cards.py 로 카드를 만드세요.
- tour:  build-cards.py 의 레퍼런스 묶음(사이트 카드가 있는 것)에서 사이트를 골라
         모바일 화면으로 찍고, 위에서 아래로 스크롤하는 영상을 만듭니다.
         바깥 사이트에 접속해야 해서 GitHub Actions(Build reels)에서 돌립니다.
- 결과: social/reels/<묶음>-<cards|tour>.mp4 + 같은 이름의 .jpg(커버) + social/reels/index.json
  → https://designrefs.com/social/reels/<이름>.mp4 (인스타 릴스 API 는 공개 주소의 영상만 받습니다)
- motion: video/ 의 Remotion 으로 장면마다 글자·숫자가 움직이는 영상을 만들고, 장면 전환 박자에 맞춘
          배경음악(코드로 직접 만든 소리, 저작권 걱정 없음)을 넣습니다. Node.js 와 `npm ci --prefix video` 가 필요합니다.
          내 음원을 쓰려면 --music=video/music/파일.mp3 (저작권이 확인된 음원만).
- 영상 규격: H.264, 30fps, yuv420p, 무음 AAC 트랙(인스타가 소리 트랙을 요구하는 경우가 있어서).
  배경음악은 인스타 앱에서 넣는 게 저작권상 안전합니다. API 로는 음악을 붙일 수 없습니다.
"""
import html, importlib.util, json, pathlib, re, subprocess, sys, tempfile

from PIL import Image

from snap import shoot

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "social" / "reels"
CARDS = ROOT / "social" / "cards"
SITE = "https://designrefs.com/"
W, H = 1080, 1920
FPS = 30
FADE = 0.35
e = html.escape

_spec = importlib.util.spec_from_file_location("build_cards", pathlib.Path(__file__).with_name("build-cards.py"))
BC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(BC)

FONT = ('<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/'
        'dist/web/variable/pretendardvariable-dynamic-subset.min.css">')
BASE = """
html, body { margin: 0; overflow: hidden; }
body { font-family: "Pretendard Variable", Pretendard, "Apple SD Gothic Neo", sans-serif; -webkit-font-smoothing: antialiased; }
.logo { font-weight: 800; letter-spacing: -0.04em; } .logo span { color: #8A8A8A; }
"""


def page(body, css, w=W, h=H):
    return (f'<!doctype html><html lang="ko"><head><meta charset="utf-8">{FONT}'
            f'<style>{BASE} html, body {{ width: {w}px; height: {h}px; }} {css}</style></head><body>{body}</body></html>')


def render(tmp, name, doc, size=(W, H)):
    f = pathlib.Path(tmp) / f"{name}.html"
    f.write_text(doc, encoding="utf-8")
    png = pathlib.Path(tmp) / f"{name}.png"
    shoot(f, png, size=size)
    return png


# ---------- 화면 틀 ----------
# 릴스는 위쪽 약 220px, 아래쪽 약 400px 를 인스타 화면(아이디·캡션·버튼)이 가립니다.
# 중요한 글자는 그 사이에 둡니다.

def hook_frame(title, sub):
    return page(
        f'<div class="w"><div class="logo">d<span>.</span></div><div class="t">{e(title)}</div>'
        f'<div class="s">{e(sub)}</div></div>',
        """body { background: #111; color: #fff; }
           .w { box-sizing: border-box; height: 1920px; padding: 260px 88px 460px; display: flex; flex-direction: column; }
           .logo { font-size: 64px; }
           .t { margin-top: auto; font-size: 112px; line-height: 1.15; font-weight: 800; letter-spacing: -0.045em;
                white-space: pre-line; word-break: keep-all; }
           .s { margin-top: 40px; font-size: 40px; color: #A3A3A3; }""")


def card_frame(img, label):
    # 카드(1080×1350)를 가운데 두고 위아래 띠에 묶음 제목과 안내를 적습니다
    return page(
        f'<div class="top">{e(label)}</div><img src="{img.as_uri()}"><div class="bot">저장해 두고 꺼내 보세요 · designrefs.com</div>',
        """body { background: #111; color: #fff; }
           .top { height: 285px; box-sizing: border-box; padding: 0 88px 36px; display: flex; align-items: flex-end;
                  font-size: 36px; font-weight: 700; letter-spacing: -0.02em; }
           img { display: block; width: 1080px; height: 1350px; }
           .bot { padding: 36px 88px 0; font-size: 30px; color: #A3A3A3; }""")


def tour_header(n, name, host, when):
    return page(
        f'<div class="h"><div class="n">{n:02d}</div><div class="name">{e(name)}</div>'
        f'<div class="host">{e(host)}</div><div class="when">{e(when)}</div></div>',
        """body { background: #fff; color: #111; }
           .h { box-sizing: border-box; height: 520px; padding: 210px 72px 0; border-bottom: 4px solid #111; }
           .n { font-size: 28px; font-weight: 700; color: #8A8A8A; }
           .name { margin-top: 6px; font-size: 76px; line-height: 1.1; font-weight: 800; letter-spacing: -0.045em; white-space: nowrap;
                   overflow: hidden; text-overflow: ellipsis; }
           .host { display: inline-block; margin-top: 8px; font-size: 28px; color: #8A8A8A; }
           .when { margin-top: 18px; font-size: 36px; font-weight: 700; letter-spacing: -0.02em; white-space: nowrap;
                   overflow: hidden; text-overflow: ellipsis; }""", h=520)


def outro_frame(title, url):
    return page(
        f'<div class="w"><div class="logo">d<span>.</span></div><div class="t">{e(title)}</div>'
        f'<div class="u">{e(url)}</div><div class="s">프로필 링크에서 전체 목록을 볼 수 있어요</div></div>',
        """body { background: #111; color: #fff; }
           .w { box-sizing: border-box; height: 1920px; padding: 260px 88px 460px; display: flex; flex-direction: column; }
           .logo { font-size: 64px; }
           .t { margin-top: auto; font-size: 96px; line-height: 1.18; font-weight: 800; letter-spacing: -0.045em;
                white-space: pre-line; word-break: keep-all; }
           .u { margin-top: 56px; align-self: flex-start; font-size: 44px; font-weight: 700; padding: 22px 40px;
                border-radius: 999px; background: #fff; color: #111; }
           .s { margin-top: 32px; font-size: 34px; color: #A3A3A3; }""")



# ---------- 사이트 화면 찍기 ----------

MOBILE_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
             "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
# 쿠키 동의 버튼 글자 (대소문자 무시)
CONSENT = re.compile(r"^\s*(accept( all)?( cookies)?|allow( all)?( cookies)?|i agree|agree|got it|ok|okay|"
                     r"모두 허용|모두 동의|동의(합니다)?|확인)\s*$", re.I)
# 버튼을 못 눌렀을 때를 위해, 흔한 쿠키 배너는 화면에서 숨깁니다
HIDE_BANNERS = """
#onetrust-consent-sdk, #onetrust-banner-sdk, #CybotCookiebotDialog, .cc-window, .cc-banner, #usercentrics-root,
.osano-cm-window, #truste-consent-track, .fc-consent-root, #didomi-host, .qc-cmp2-container,
[id*="cookie-banner" i], [class*="cookie-banner" i], [id*="cookie-consent" i], [class*="cookie-consent" i],
[id*="cookieconsent" i], [class*="cookieconsent" i], [aria-label*="cookie" i][role="dialog"],
[aria-label*="cookie" i][role="region"] { display: none !important; }
"""


BOT_WALL = ("just a moment", "verify you are human", "checking your browser", "보안 확인 수행", "사람인지 확인",
            "attention required", "access denied", "are you a robot", "captcha")


def capture(url, out, max_h=4500):
    """사이트를 모바일 화면(폭 432, 2.5배 → 1080px)으로 위에서부터 길게 찍습니다.
    Playwright 가 있으면 페이지가 뜰 때까지 기다리고, 쿠키 동의 창을 닫고, 아래까지 한 번 내려
    늦게 뜨는 이미지까지 불러온 뒤 찍습니다. 없으면 크롬 스크린샷으로 찍습니다."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        shoot(url, out, size=(432, 1500), timeout=60, scale=2.5)
        return
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            ctx = browser.new_context(viewport={"width": 432, "height": 900}, device_scale_factor=2.5,
                                      is_mobile=True, has_touch=True, locale="ko-KR", user_agent=MOBILE_UA)
            page = ctx.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            try:
                page.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass
            try:
                page.get_by_role("button", name=CONSENT).first.click(timeout=1500)
            except Exception:
                pass
            try:
                page.add_style_tag(content=HIDE_BANNERS)
            except Exception:
                pass
            # 할인·뉴스레터 같은 팝업도 닫습니다: Esc, 그리고 화면에 보이는 '닫기' 버튼
            page.wait_for_timeout(1500)
            for _ in range(2):
                try:
                    page.keyboard.press("Escape")
                    btn = page.locator('[aria-label*="close" i]:visible, [aria-label*="닫기"]:visible, '
                                       'button[class*="close" i]:visible').first
                    btn.click(timeout=800)
                except Exception:
                    pass
                page.wait_for_timeout(400)
            for y in range(0, 2400, 300):   # 늦게 뜨는 이미지를 불러오려고 한 번 훑습니다
                page.evaluate(f"window.scrollTo(0, {y})")
                page.wait_for_timeout(120)
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(1200)
            # 봇 확인(Cloudflare 등) 화면이면 찍지 않고 글자 장면으로 대신하게 합니다
            text = (page.title() + " " + page.inner_text("body", timeout=3000)[:2000]).lower()
            if any(k in text for k in BOT_WALL):
                raise RuntimeError("봇 확인 화면이 떠서 찍지 않음")
            page.screenshot(path=str(out), full_page=True, timeout=30000)
        finally:
            browser.close()
    im = Image.open(out)
    if im.height > max_h:
        im.crop((0, 0, im.width, max_h)).save(out)

# ---------- ffmpeg ----------

def ffmpeg(args):
    r = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit("ffmpeg 오류:\n" + r.stderr[-2000:])


def still_clip(png, dur, out, zoom=True):
    """정지 이미지 한 장 → dur 초짜리 클립. 아주 천천히 확대해서 움직임을 줍니다."""
    frames = round(dur * FPS)
    if zoom:
        vf = (f"scale={W * 2}:{H * 2},zoompan=z='1+0.03*on/{frames}':d={frames}"
              f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}")
        ffmpeg(["-i", str(png), "-vf", vf, "-frames:v", str(frames), "-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "18", str(out)])
    else:
        ffmpeg(["-loop", "1", "-framerate", str(FPS), "-t", f"{dur}", "-i", str(png), "-vf", f"scale={W}:{H}",
                "-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "18", str(out)])


def scroll_clip(header_png, shot_png, dur, out):
    """사이트 전체 화면 캡처를 위에서 아래로 부드럽게 훑는 클립. 위에는 사이트 이름 머리띠."""
    view = H - 520
    hgt = Image.open(shot_png).height
    travel = max(0, min(hgt - view, 2600))
    y = f"{travel}*(0.5-0.5*cos(PI*min(t/{dur - 0.6},1)))"
    flt = (f"[1:v]scale={W}:-2,crop={W}:{view}:0:'{y}'[s];[0:v][s]vstack=inputs=2,format=yuv420p[v]")
    ffmpeg(["-loop", "1", "-framerate", str(FPS), "-t", f"{dur}", "-i", str(header_png),
            "-loop", "1", "-framerate", str(FPS), "-t", f"{dur}", "-i", str(shot_png),
            "-filter_complex", flt, "-map", "[v]", "-r", str(FPS), "-c:v", "libx264", "-crf", "20", str(out)])


def join(clips, durs, out):
    """클립들을 짧은 디졸브로 잇고, 무음 소리 트랙을 붙입니다."""
    args = []
    for c in clips:
        args += ["-i", str(c)]
    total = sum(durs) - FADE * (len(durs) - 1)
    chain, last, off = [], "0:v", 0.0
    for i in range(1, len(clips)):
        off += durs[i - 1] - FADE
        tag = f"x{i}"
        chain.append(f"[{last}][{i}:v]xfade=transition=fade:duration={FADE}:offset={off:.3f}[{tag}]")
        last = tag
    flt = ";".join(chain) if chain else "[0:v]null[x0]"
    last = last if chain else "x0"
    ffmpeg([*args, "-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
            "-filter_complex", flt, "-map", f"[{last}]", "-map", f"{len(clips)}:a",
            "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(out)])
    return total


# ---------- 릴스 두 종류 ----------

def reel_cards(set_id):
    src = CARDS / set_id
    imgs = sorted(src.glob("*.jpg"))
    if not imgs:
        raise SystemExit(f"카드가 없습니다: social/cards/{set_id} (먼저 build-cards.py {set_id})")
    meta = json.loads((CARDS / "index.json").read_text(encoding="utf-8"))
    info = next((s for s in meta["sets"] if s["id"] == set_id), {"title": set_id, "caption": ""})
    cover = next((c for c in BC.SETS.get(set_id, {}).get("cards", []) if c["kind"] == "cover"), None)
    hook_title = cover["title"] if cover else info["title"]   # 표지 줄바꿈을 그대로 씁니다
    with tempfile.TemporaryDirectory() as tmp:
        clips, durs = [], []
        hook = render(tmp, "hook", hook_frame(hook_title, "넘기지 말고 끝까지 · 저장 추천"))
        clips.append(pathlib.Path(tmp) / "c00.mp4"); durs.append(2.2)
        still_clip(hook, 2.2, clips[-1])
        for i, img in enumerate(imgs[1:], 1):   # 첫 장(표지)은 위 훅 화면이 대신합니다
            fr = render(tmp, f"f{i:02d}", card_frame(img, info["title"]))
            d = 3.2 if i < len(imgs) - 1 else 3.0
            clips.append(pathlib.Path(tmp) / f"c{i:02d}.mp4"); durs.append(d)
            still_clip(fr, d, clips[-1])
        return finish(f"{set_id}-cards", clips, durs, hook, info)


def reel_tour(set_id):
    spec = BC.SETS.get(set_id)
    if not spec:
        raise SystemExit(f"레퍼런스 묶음이 아닙니다: {set_id} (있는 것: {', '.join(BC.SETS)})")
    sites = [c for c in spec["cards"] if c["kind"] == "site"]
    if not sites:
        raise SystemExit(f"사이트 카드가 없는 묶음입니다: {set_id}")
    outro = next((c for c in spec["cards"] if c["kind"] == "outro"), {"title": "레퍼런스 394곳", "url": "designrefs.com"})
    with tempfile.TemporaryDirectory() as tmp:
        clips, durs = [], []
        cover = next((c for c in spec["cards"] if c["kind"] == "cover"), {"title": spec["title"]})
        hook = render(tmp, "hook", hook_frame(cover["title"], f"사이트 {len(sites)}곳을 화면으로 바로 보기"))
        clips.append(pathlib.Path(tmp) / "c00.mp4"); durs.append(2.2)
        still_clip(hook, 2.2, clips[-1])
        for i, c in enumerate(sites, 1):
            s = BC.find_site(c["name"])
            hdr = render(tmp, f"h{i}", tour_header(i, s["name"], BC.host(s["url"]), c.get("when") or s["desc"]), size=(W, 520))
            shot = pathlib.Path(tmp) / f"s{i}.png"
            clips.append(pathlib.Path(tmp) / f"c{i:02d}.mp4")
            try:
                if c.get("tour") == "card":   # 팝업 등으로 화면이 지저분한 사이트는 카드로 보여 줍니다
                    raise RuntimeError("SETS 에서 카드로 보여 주도록 지정함")
                capture(s["url"], shot)
                durs.append(4.6)
                scroll_clip(hdr, shot, 4.6, clips[-1])
                print(f"  {i}. {s['name']} 찍음")
            except (Exception, SystemExit) as ex:
                # 막혀 있거나 너무 느린 사이트는 카드 이미지로 대신합니다
                card = CARDS / set_id / f"{spec['cards'].index(c) + 1:02d}.jpg"
                if not card.exists():
                    raise SystemExit(f"{s['name']} 화면을 찍지 못했고 대신할 카드도 없습니다: {ex}")
                fr = render(tmp, f"f{i}", card_frame(card, spec["title"]))
                durs.append(3.2)
                still_clip(fr, 3.2, clips[-1])
                print(f"  {i}. {s['name']} 화면을 못 찍어 카드로 대신함 ({str(ex)[:120]})")
        end = render(tmp, "end", outro_frame(outro["title"], outro["url"]))
        clips.append(pathlib.Path(tmp) / "c99.mp4"); durs.append(3.0)
        still_clip(end, 3.0, clips[-1])
        info = {"title": spec["title"], "caption": BC.caption(set_id, spec)}
        return finish(f"{set_id}-tour", clips, durs, hook, info)


def finish(name, clips, durs, cover_png, info):
    OUT.mkdir(parents=True, exist_ok=True)
    mp4 = OUT / f"{name}.mp4"
    total = join(clips, durs, mp4)
    Image.open(cover_png).convert("RGB").save(OUT / f"{name}.jpg", "JPEG", quality=90)
    print(f"{name}: {total:.1f}초, {mp4.stat().st_size / 1e6:.1f}MB → social/reels/{mp4.name}")
    return {"id": name, "title": info["title"], "seconds": round(total, 1),
            "video": f"{SITE}social/reels/{name}.mp4", "cover": f"{SITE}social/reels/{name}.jpg",
            "caption": info.get("caption", "")}


# ---------- 모션 릴스 (Remotion) ----------

def motion_props(set_id):
    """카드 묶음 설명(build-cards.py)을 모션 릴스 장면 목록으로 바꿉니다."""
    if set_id.startswith("article-"):
        spec = BC.article_set(set_id.removeprefix("article-"))
    else:
        spec = BC.SETS.get(set_id)
        if not spec:
            raise SystemExit(f"없는 묶음입니다: {set_id}")
    cards = spec["cards"]
    items = [c for c in cards if c["kind"] in ("site", "term")]
    scenes, n = [], 0
    for i, c in enumerate(cards, 1):
        k = c["kind"]
        if k == "cover":
            scenes.append({"type": "hook", "title": c["title"],
                           "sub": f"{len(items)}곳 끝까지 보고 저장해 두세요" if items else "끝까지 보고 저장해 두세요"})
        elif k == "site":
            n += 1
            st = BC.find_site(c["name"])
            scenes.append({"type": "site", "n": n, "total": len(items), "name": st["name"], "host": BC.host(st["url"]),
                           "text": c.get("when") or st["desc"], "tags": BC.site_tags(st["name"])[:3]})
        elif k == "term":
            n += 1
            t = BC.find_term(c["name"])
            scenes.append({"type": "term", "n": n, "total": len(items), "label": "용어", "name": t["term"],
                           "text": BC.first_sentence(t["desc"], 80)})
        elif k == "lead":
            scenes.append({"type": "lead", "label": c.get("label", ""), "text": c["text"]})
        elif k == "figure":
            img = CARDS / set_id / f"{i:02d}.jpg"
            if img.exists():
                scenes.append({"type": "figure", "image": str(img.relative_to(ROOT))})
        elif k == "tip":
            pts = [x[0] if isinstance(x, (list, tuple)) else x for x in c.get("points", [])][:3]
            scenes.append({"type": "tip", "title": c.get("title", "그래서 지금은"), "points": pts})
        elif k == "outro":
            scenes.append({"type": "outro", "title": c["title"], "url": c.get("url", "designrefs.com")})
    if not scenes or scenes[0]["type"] != "hook":
        scenes.insert(0, {"type": "hook", "title": spec["title"], "sub": "끝까지 보고 저장해 두세요"})
    return spec, {"kicker": spec.get("kicker", ""), "scenes": scenes}


def motion_ready():
    import shutil
    return bool(shutil.which("node")) and (ROOT / "video" / "node_modules" / "remotion").exists()


def render_motion(name, props, title, caption):
    """props 로 video/render.mjs 를 돌려 social/reels/<name>.mp4 와 커버 .jpg 를 만듭니다."""
    import shutil
    if not shutil.which("node"):
        raise SystemExit("모션 릴스에는 Node.js 가 필요합니다. (Claude 데스크톱 연결에 쓰는 것과 같은 것)")
    if not motion_ready():
        raise SystemExit("영상 엔진이 설치되지 않았습니다. 터미널에서: npm ci --prefix video")
    OUT.mkdir(parents=True, exist_ok=True)
    mp4, jpg = OUT / f"{name}.mp4", OUT / f"{name}.jpg"
    with tempfile.TemporaryDirectory() as tmp:
        pf = pathlib.Path(tmp) / "props.json"
        pf.write_text(json.dumps(props, ensure_ascii=False), encoding="utf-8")
        proc = subprocess.Popen([shutil.which("node"), str(ROOT / "video" / "render.mjs"), str(pf), str(mp4), str(jpg)],
                                cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        seconds, tail = 0.0, []
        for line in proc.stdout:
            line = line.rstrip()
            if line.startswith("PROGRESS ") or line.startswith("DONE "):
                print(line, flush=True)
                if line.startswith("DONE "):
                    seconds = float(line.split()[1])
            elif line:
                tail.append(line)
        if proc.wait() != 0 or not mp4.exists():
            raise SystemExit("모션 릴스를 만들지 못했습니다.\n" + "\n".join(tail[-30:]))
    print(f"{name}: {seconds:.1f}초, {mp4.stat().st_size / 1e6:.1f}MB → social/reels/{mp4.name}")
    return {"id": name, "title": title, "seconds": round(seconds, 1),
            "video": f"{SITE}social/reels/{name}.mp4", "cover": f"{SITE}social/reels/{name}.jpg", "caption": caption}


def set_caption(set_id, spec):
    meta = json.loads((CARDS / "index.json").read_text(encoding="utf-8")) if (CARDS / "index.json").exists() else {"sets": []}
    info = next((x for x in meta["sets"] if x["id"] == set_id), None)
    return info["caption"] if info else BC.caption(set_id, spec)


def reel_motion(set_id, music="auto"):
    spec, props = motion_props(set_id)
    props["music"] = music
    return render_motion(f"{set_id}-motion", props, spec["title"], set_caption(set_id, spec))


def reel_tour_motion(set_id, music="auto"):
    """사이트 투어 (모션): 사이트마다 실제 모바일 화면을 찍어 폰 화면 안에서 스크롤합니다. 바깥 사이트 접속 필요."""
    spec = BC.SETS.get(set_id)
    if not spec:
        raise SystemExit(f"레퍼런스 묶음이 아닙니다: {set_id} (있는 것: {', '.join(BC.SETS)})")
    sites = [c for c in spec["cards"] if c["kind"] == "site"]
    if not sites:
        raise SystemExit(f"사이트 카드가 없는 묶음입니다: {set_id}")
    cover = next((c for c in spec["cards"] if c["kind"] == "cover"), {"title": spec["title"]})
    outro = next((c for c in spec["cards"] if c["kind"] == "outro"), {"title": "레퍼런스 394곳", "url": "designrefs.com"})
    scenes = [{"type": "hook", "title": cover["title"], "sub": f"사이트 {len(sites)}곳, 실제 화면으로 바로 보기"}]
    with tempfile.TemporaryDirectory() as tmp:
        for i, c in enumerate(sites, 1):
            st = BC.find_site(c["name"])
            base = {"n": i, "total": len(sites), "name": st["name"], "host": BC.host(st["url"]),
                    "text": c.get("when") or st["desc"], "tags": BC.site_tags(st["name"])[:3]}
            shot = pathlib.Path(tmp) / f"s{i}.png"
            try:
                if c.get("tour") == "card":   # 팝업 등으로 화면이 지저분한 사이트는 글자 장면으로
                    raise RuntimeError("SETS 에서 카드로 보여 주도록 지정함")
                capture(st["url"], shot)
                scenes.append({"type": "shot", "shot": str(shot), "shot_h": Image.open(shot).height, **base})
                print(f"  {i}. {st['name']} 찍음", flush=True)
            except (Exception, SystemExit) as ex:
                scenes.append({"type": "site", **base})
                print(f"  {i}. {st['name']} 화면을 못 찍어 글자 장면으로 대신함 ({str(ex)[:120]})", flush=True)
        scenes.append({"type": "outro", "title": outro["title"], "url": outro.get("url", "designrefs.com")})
        props = {"kicker": spec.get("kicker", ""), "scenes": scenes, "music": music}
        return render_motion(f"{set_id}-tour", props, spec["title"], set_caption(set_id, spec))


def write_index(built):
    path = OUT / "index.json"
    reels = {r["id"]: r for r in (json.loads(path.read_text(encoding="utf-8"))["reels"] if path.exists() else [])}
    reels.update({r["id"]: r for r in built})
    reels = {k: v for k, v in reels.items() if (OUT / f"{k}.mp4").exists()}
    path.write_text(json.dumps({"reels": sorted(reels.values(), key=lambda r: r["id"])}, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    built = []
    music = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--music=")), "auto")
    for t in [a for a in sys.argv[1:] if not a.startswith("--")]:
        kind, _, sid = t.partition(":")
        if kind == "cards":
            built.append(reel_cards(sid))
        elif kind == "tour":
            # 영상 엔진이 있으면 모션 투어(음악 포함), 없으면 예전 방식(ffmpeg)
            built.append(reel_tour_motion(sid, None if music == "none" else music) if motion_ready() else reel_tour(sid))
        elif kind == "motion":
            built.append(reel_motion(sid, None if music == "none" else music))
        else:
            raise SystemExit(f"cards:<묶음>, tour:<묶음>, motion:<묶음> 중 하나로 적어 주세요: {t}")
    write_index(built)
