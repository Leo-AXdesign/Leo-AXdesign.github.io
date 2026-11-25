"""설정 점검: python -m autopost.check

GitHub 미디어 저장소, Blogger 연결, 글 작성용 claude 로그인을 차례로 확인합니다.
아무것도 올리거나 바꾸지 않습니다(읽기만).
"""
import json
import os
import subprocess
from pathlib import Path

import requests
import yaml
from dotenv import load_dotenv


def ok(msg):
    print(f"  ✅ {msg}")


def bad(msg, fix):
    print(f"  ❌ {msg}\n     → {fix}")
    return False


def check_github(cfg):
    print("■ GitHub 미디어 저장소")
    gh = cfg.get("github", {})
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        return bad(".env 에 GITHUB_TOKEN 이 비어 있어요", "토큰을 만들어 .env 에 붙여넣기")
    if gh.get("owner", "YOUR_GITHUB_ID") == "YOUR_GITHUB_ID":
        return bad("config.yaml 의 github.owner 가 그대로예요", "본인 GitHub 아이디로 바꾸기")
    r = requests.get(f"https://api.github.com/repos/{gh['owner']}/{gh['repo']}",
                     headers={"Authorization": f"Bearer {token}"}, timeout=20)
    if r.status_code == 401:
        return bad("토큰이 유효하지 않아요", "토큰을 다시 복사했는지, 만료되지 않았는지 확인")
    if r.status_code == 404:
        return bad(f"{gh['owner']}/{gh['repo']} 저장소가 안 보여요",
                   "저장소 이름·아이디 철자, 토큰의 Repository access 에 이 저장소가 있는지 확인")
    repo = r.json()
    if repo.get("private"):
        return bad("저장소가 비공개예요", "jsDelivr 는 공개 저장소만 됩니다. Settings → Change visibility → Public")
    if not repo.get("permissions", {}).get("push"):
        return bad("토큰에 쓰기 권한이 없어요", "토큰 Permissions → Contents: Read and write")
    b = requests.get(f"https://api.github.com/repos/{gh['owner']}/{gh['repo']}/branches/{gh.get('branch', 'main')}",
                     headers={"Authorization": f"Bearer {token}"}, timeout=20)
    if b.status_code != 200:
        return bad(f"'{gh.get('branch', 'main')}' 브랜치가 없어요", "저장소 만들 때 README 추가에 체크(빈 저장소면 README 하나 만들기)")
    ok(f"{gh['owner']}/{gh['repo']} 공개 저장소, 쓰기 권한 확인")
    return True


def check_blogger(cfg):
    print("■ Blogger")
    if not Path("client_secret.json").exists():
        return bad("client_secret.json 이 없어요", "구글 클라우드에서 OAuth 클라이언트 JSON 을 받아 이 폴더에 저장")
    if not Path("token.json").exists():
        return bad("아직 구글 로그인을 안 했어요", "python -m autopost.auth 실행")
    from . import blogger
    try:
        svc = blogger.get_service()
        blog_id = blogger.get_blog_id(svc, cfg["blog_url"])
        n = len(blogger.recent_posts(svc, blog_id, 5))
    except Exception as e:
        return bad(f"연결 실패: {str(e)[:200]}",
                   "config.yaml 의 blog_url 이 내 블로그 주소인지 확인. 로그인이 풀렸다면 python -m autopost.auth 다시 실행")
    ok(f"{cfg['blog_url']} 연결됨 (블로그 ID {blog_id}, 최근 글 {n}개 읽음)")
    return True


def check_search_console(cfg):
    print("■ 구글 색인 (Search Console)")
    from . import indexing
    try:
        if not indexing.has_site(cfg["blog_url"]):
            return bad("Search Console 에 블로그가 소유자로 등록돼 있지 않아요",
                       "search.google.com/search-console 에서 블로그 주소를 속성으로 추가")
    except Exception as e:
        return bad(f"조회 실패: {str(e)[:200]}",
                   "구글 클라우드에서 Search Console API 사용 설정, 또는 python -m autopost.auth 다시 실행")
    ok("블로그 소유 확인 → 발행할 때마다 사이트맵 제출")
    return True


def check_writer(cfg):
    print("■ 글 작성(Claude)")
    if cfg.get("writer", "cli") == "api":
        if not os.environ.get("ANTHROPIC_API_KEY"):
            return bad("writer: api 인데 ANTHROPIC_API_KEY 가 비어 있어요", ".env 에 키 넣기 또는 writer: cli 로")
        ok("API 키 있음")
        return True
    from .writer import _claude_bin
    try:
        out = subprocess.run([_claude_bin(), "auth", "status"], capture_output=True, text=True, timeout=30)
        if not json.loads(out.stdout).get("loggedIn"):
            return bad("claude 로그인이 안 돼 있어요", "터미널에서 claude 실행 후 로그인")
    except Exception as e:
        return bad(f"claude 확인 실패: {e}", "curl -fsSL https://claude.ai/install.sh | bash")
    ok("claude 로그인됨 (구독으로 작성)")
    return True


def main():
    load_dotenv(".env")
    cfg = yaml.safe_load(Path("config.yaml").read_text(encoding="utf-8"))
    results = [check_writer(cfg), check_github(cfg), check_blogger(cfg)]
    if results[-1]:
        results.append(check_search_console(cfg))
    print("\n모두 준비됐어요! 매일 9시·18시에 자동으로 발행됩니다." if all(results)
          else "\n❌ 표시된 것만 고치고 다시 실행하세요.")


if __name__ == "__main__":
    main()
