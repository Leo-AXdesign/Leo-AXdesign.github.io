"""Playwright로 스크린샷/화면녹화 생성.

로그인이 필요한 화면은 browser_profile 폴더에 저장된 로그인 상태를 재사용합니다.
(python -m autopost.login 으로 한 번 직접 로그인해두면 됨)
"""
import re
import shutil
import subprocess
import time
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

BLOCKED_WORDS = ("결제", "구매", "가입하기", "sign up", "subscribe", "purchase", "pay", "send", "전송")


COOKIE_REJECT = re.compile(r"^\s*(reject all|reject|decline|necessary only|모두 거부|거부|필수.*만)", re.I)


def _dismiss_cookie_banner(page):
    """쿠키 동의 팝업이 화면을 가리지 않도록 '거부'로 닫음 (없으면 그냥 넘어감)."""
    try:
        btn = page.get_by_role("button", name=COOKIE_REJECT).first
        if btn.is_visible(timeout=1500):
            btn.click(timeout=3000)
            page.wait_for_timeout(600)
    except Exception:
        pass


BOT_CHECK = ("보안 확인 수행 중", "사람인지 확인", "just a moment", "verify you are human",
             "checking your browser", "are you a robot", "access denied", "unusual traffic")


def _assert_not_blocked(page):
    """봇 확인·차단 화면이 찍히면 실패로 처리.
    (캡차는 우회하지 않음. mockup_html 이 있으면 재현 화면으로 대체됨)"""
    try:
        body = page.inner_text("body", timeout=3000)
    except Exception:
        body = ""
    text = (page.title() + " " + body[:3000]).lower()
    hit = next((w for w in BOT_CHECK if w in text), None)
    # 확인 위젯이 iframe(그림자 DOM 안)에 있으면 본문 글자로는 안 잡히므로 프레임 주소도 확인
    if not hit and any("challenges.cloudflare.com" in (f.url or "") for f in page.frames):
        hit = "cloudflare 확인 위젯"
    if not hit and len(body.strip()) < 30:
        hit = "내용이 거의 없는 화면"
    if hit:
        raise RuntimeError(f"봇 확인 화면에 막힘 ({hit})")


def _run_actions(page, actions, deadline=None):
    for a in actions or []:
        if deadline and time.time() > deadline:
            break
        kind = a.get("do")
        if kind == "wait":
            page.wait_for_timeout(int(a.get("ms", 1000)))
            continue
        if kind == "click":
            label = (a.get("text") or "").lower()
            if any(w in label for w in BLOCKED_WORDS):
                print(f"   ! 안전상 건너뜀: '{a.get('text')}' 클릭")
                continue
            if a.get("selector"):
                page.locator(a["selector"]).first.click(timeout=8000)
            else:
                page.get_by_text(a["text"], exact=False).first.click(timeout=8000)
        elif kind == "scroll":
            page.mouse.wheel(0, int(a.get("y", 600)))
        elif kind == "hover":
            page.get_by_text(a["text"], exact=False).first.hover(timeout=8000)
        elif kind == "type":
            page.locator(a["selector"]).first.type(a["value"], delay=70)
        page.wait_for_timeout(800)


def _to_webp(png: Path) -> Path:
    out = png.with_suffix(".webp")
    Image.open(png).save(out, "WEBP", quality=85)
    png.unlink()
    return out


def _ffmpeg() -> str:
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    try:  # brew 없이도 되도록 pip 패키지에 든 ffmpeg 사용
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        raise RuntimeError("ffmpeg가 없습니다. (pip install imageio-ffmpeg 또는 brew install ffmpeg)")


def _to_mp4(webm: Path, out: Path, max_seconds: int) -> Path:
    subprocess.run(
        [_ffmpeg(), "-y", "-loglevel", "error", "-i", str(webm), "-t", str(max_seconds),
         "-vf", "scale=1280:-2", "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-crf", "28", "-movflags", "+faststart", "-an", str(out)],
        check=True,
    )
    webm.unlink(missing_ok=True)
    return out


MOCKUP_PAGE = """<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:">
<style>html,body{{margin:0;width:100%;height:100%;overflow:hidden;background:#fff;
font-family:-apple-system,"Apple SD Gothic Neo","Noto Sans KR",sans-serif;}}</style></head>
<body>{body}</body></html>"""


def _capture_mockup(p, m: dict, out_dir: Path, viewport: dict) -> Path:
    """재현 화면(mockup_html)을 인터넷·스크립트가 차단된 브라우저에서 찍음."""
    browser = p.chromium.launch(headless=True)
    try:
        ctx = browser.new_context(viewport=viewport, device_scale_factor=2,
                                  java_script_enabled=False, locale="ko-KR")
        ctx.route("**/*", lambda route: route.abort())  # 외부 요청 전부 차단
        page = ctx.new_page()
        page.set_content(MOCKUP_PAGE.format(body=m["mockup_html"]), wait_until="load")
        png = out_dir / f"{m['id']}.png"
        # 내용이 끝나는 곳까지만 잘라서 아래 빈 공간을 없앰 (최소 360px)
        bottom = page.evaluate("""() => {
            let b = 0; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            while (w.nextNode()) { if (!w.currentNode.textContent.trim()) continue;
              const r = document.createRange(); r.selectNodeContents(w.currentNode);
              b = Math.max(b, r.getBoundingClientRect().bottom); }
            document.querySelectorAll('input,textarea,button').forEach(e => b = Math.max(b, e.getBoundingClientRect().bottom));
            return b; }""")
        h = int(min(viewport["height"], max(360, bottom + 48)))
        page.screenshot(path=str(png), clip={"x": 0, "y": 0, "width": viewport["width"], "height": h})
        return _to_webp(png)
    finally:
        browser.close()


def capture_all(media: list, out_dir: Path, cfg: dict) -> dict:
    """media 항목별로 캡처. 반환: {id: 로컬파일경로 또는 None(실패)}"""
    out_dir.mkdir(parents=True, exist_ok=True)
    profile = Path(cfg.get("browser_profile", "browser_profile")).resolve()
    viewport = cfg.get("viewport", {"width": 1280, "height": 800})
    max_sec = int(cfg.get("video_max_seconds", 20))
    results = {}

    with sync_playwright() as p:
        for m in media:
            mid, kind = m["id"], m.get("kind", "screenshot")
            print(f" - [{kind}] {mid}: {m['url']}")
            video_tmp = out_dir / f"_{mid}_rec"
            opts = dict(
                headless=cfg.get("headless", True),
                viewport=viewport,
                locale="ko-KR",
                device_scale_factor=1 if kind == "video" else 2,
            )
            if kind == "video":
                opts["record_video_dir"] = str(video_tmp)
                opts["record_video_size"] = viewport
            ctx = None
            try:
                ctx = p.chromium.launch_persistent_context(str(profile), **opts)
                page = ctx.pages[0] if ctx.pages else ctx.new_page()
                page.goto(m["url"], wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2500)
                _assert_not_blocked(page)
                _dismiss_cookie_banner(page)
                _run_actions(page, m.get("actions"), time.time() + max_sec)
                _assert_not_blocked(page)

                if kind == "video":
                    page.wait_for_timeout(1200)
                    video = page.video
                    ctx.close(); ctx = None
                    results[mid] = _to_mp4(Path(video.path()), out_dir / f"{mid}.mp4", max_sec)
                    shutil.rmtree(video_tmp, ignore_errors=True)
                else:
                    png = out_dir / f"{mid}.png"
                    page.screenshot(path=str(png), full_page=bool(m.get("full_page")))
                    results[mid] = _to_webp(png)
            except Exception as e:  # 실패해도 글 전체는 계속 진행
                print(f"   ! 캡처 실패: {e}")
                results[mid] = None
            finally:
                if ctx:
                    ctx.close()
                shutil.rmtree(video_tmp, ignore_errors=True)

            if results[mid] is None and m.get("mockup_html"):
                try:
                    results[mid] = _capture_mockup(p, m, out_dir, viewport)
                    m["mockup"] = True        # render 에서 '예시 화면(재현)' 표시
                    m["kind"] = "screenshot"  # 영상 자리도 정지 화면으로 대체
                    print("   → 재현 화면으로 대체")
                except Exception as e:
                    print(f"   ! 재현 화면도 실패: {e}")
    return results
