"""로그인 상태 저장용: 브라우저를 열어두면 직접 로그인 → 터미널에서 Enter.

사용: python -m autopost.login https://chatgpt.com https://claude.ai https://gemini.google.com
"""
import sys
from pathlib import Path

import yaml
from playwright.sync_api import sync_playwright


def main():
    cfg = yaml.safe_load(Path("config.yaml").read_text(encoding="utf-8"))
    urls = sys.argv[1:] or ["https://chatgpt.com", "https://claude.ai", "https://gemini.google.com"]
    profile = Path(cfg.get("browser_profile", "browser_profile")).resolve()
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(str(profile), headless=False, locale="ko-KR")
        for i, u in enumerate(urls):
            page = ctx.pages[0] if (i == 0 and ctx.pages) else ctx.new_page()
            page.goto(u)
        input("각 탭에서 로그인을 마친 뒤 여기서 Enter를 누르세요...")
        ctx.close()
    print("로그인 상태가 저장됐습니다:", profile)


if __name__ == "__main__":
    main()
