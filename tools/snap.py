#!/usr/bin/env python3
"""
HTML 한 장을 크롬(헤드리스)으로 찍어 PNG 로 저장합니다.
build-og.py(공유 이미지)와 build-cards.py(인스타 카드뉴스)가 같이 씁니다.
"""
import subprocess, tempfile, time

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def shoot(html_path, png_path, size=(1200, 630), timeout=40):
    """크롬으로 한 장 찍습니다.
    헤드리스 크롬은 파일을 다 쓰고도 종료하지 않고 멈춰 있을 때가 있어서,
    파일이 생기고 크기가 더 변하지 않으면 그 자리에서 닫습니다."""
    png_path.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory() as profile:
        proc = subprocess.Popen(
            [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
             "--force-device-scale-factor=1", f"--window-size={size[0]},{size[1]}",
             "--virtual-time-budget=6000", f"--user-data-dir={profile}",
             f"--screenshot={png_path}", html_path.as_uri()],
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
    if not png_path.exists() or png_path.stat().st_size == 0:
        raise SystemExit(f"이미지를 만들지 못했습니다: {png_path.name}")
