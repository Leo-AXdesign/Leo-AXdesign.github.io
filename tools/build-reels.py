#!/usr/bin/env python3
"""
인스타그램 릴스(1080×1920, 세로 영상)를 만듭니다.

  python3 tools/build-reels.py cards:fonts-pick    # 카드뉴스를 넘겨 보는 영상 (어디서나)
  python3 tools/build-reels.py tour:fonts-pick     # 사이트 화면을 스크롤하는 투어 영상 (인터넷 필요)

- cards: social/cards/<묶음>/*.jpg 를 한 장씩 천천히 확대하며 넘깁니다. 먼저 build-cards.py 로 카드를 만드세요.
- tour:  build-cards.py 의 레퍼런스 묶음(사이트 카드가 있는 것)에서 사이트를 골라
         모바일 화면으로 찍고, 위에서 아래로 스크롤하는 영상을 만듭니다.
         바깥 사이트에 접속해야 해서 GitHub Actions(Build reels)에서 돌립니다.
- 결과: social/reels/<묶음>-<cards|tour>.mp4 + 같은 이름의 .jpg(커버) + social/reels/index.json
  → https://designrefs.com/social/reels/<이름>.mp4 (인스타 릴스 API 는 공개 주소의 영상만 받습니다)
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
    for t in sys.argv[1:]:
        kind, _, sid = t.partition(":")
        if kind == "cards":
            built.append(reel_cards(sid))
        elif kind == "tour":
            built.append(reel_tour(sid))
        else:
            raise SystemExit(f"cards:<묶음> 또는 tour:<묶음> 으로 적어 주세요: {t}")
    write_index(built)
