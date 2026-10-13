#!/usr/bin/env python3
"""
HTML 한 장을 크롬(헤드리스)으로 찍어 PNG 로 저장합니다.
build-og.py(공유 이미지), build-cards.py(인스타 카드뉴스), build-reels.py(릴스)가 같이 씁니다.
html_path 자리에 웹 주소(문자열)를 넣으면 그 페이지를 찍습니다.
"""
import os, shutil, subprocess, tempfile, time

# 맥 기본 경로. GitHub Actions(리눅스)처럼 다른 곳에서는 CHROME_PATH 로 바꿉니다.
CHROME = os.environ.get("CHROME_PATH", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


def shoot(html_path, png_path, size=(1200, 630), timeout=40, scale=1):
    """크롬으로 한 장 찍습니다.
    헤드리스 크롬은 파일을 다 쓰고도 종료하지 않고 멈춰 있을 때가 있어서,
    파일이 생기고 크기가 더 변하지 않으면 그 자리에서 닫습니다."""
    png_path.unlink(missing_ok=True)
    # 크롬이 닫히는 중에도 프로필 폴더에 파일을 쓰는 일이 있어서, 지울 때 오류는 무시합니다
    profile = tempfile.mkdtemp()
    try:
        proc = subprocess.Popen(
            [CHROME, *os.environ.get("CHROME_FLAGS", "").split(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
             f"--force-device-scale-factor={scale}", f"--window-size={size[0]},{size[1]}",
             "--virtual-time-budget=6000", f"--user-data-dir={profile}",
             f"--screenshot={png_path}", html_path if isinstance(html_path, str) else html_path.as_uri()],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        start, last = time.time(), -1
        try:
            while time.time() - start < timeout:
                if proc.poll() is not None:
                    break
                size = png_path.stat().st_size if png_path.exists() else 0
                if size and size == last:
                    break
                last = size
                time.sleep(0.5)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    if not png_path.exists() or png_path.stat().st_size == 0:
        raise SystemExit(f"이미지를 만들지 못했습니다: {png_path.name}")
