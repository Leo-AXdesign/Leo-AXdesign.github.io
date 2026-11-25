"""캡처 파일을 공개 GitHub 저장소에 올리고 jsDelivr CDN 주소를 돌려줌.
(Blogger API는 이미지·영상 업로드를 지원하지 않아서 외부 호스팅이 필요)
"""
import base64
import os
import time
from pathlib import Path

import requests

MAX_BYTES = 19 * 1024 * 1024  # jsDelivr 파일당 한도(약 20MB) 아래로


def upload(local: Path, repo_path: str, gh: dict) -> str:
    size = local.stat().st_size
    if size > MAX_BYTES:
        raise RuntimeError(f"{local.name} 이 너무 큽니다 ({size/1e6:.1f}MB). video_max_seconds를 줄이세요.")
    token = os.environ["GITHUB_TOKEN"]
    owner, repo, branch = gh["owner"], gh["repo"], gh.get("branch", "main")
    api = f"https://api.github.com/repos/{owner}/{repo}/contents/{repo_path}"
    r = requests.put(
        api,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
        json={
            "message": f"add {repo_path}",
            "content": base64.b64encode(local.read_bytes()).decode(),
            "branch": branch,
        },
        timeout=120,
    )
    if r.status_code not in (200, 201):
        raise RuntimeError(f"GitHub 업로드 실패 {r.status_code}: {r.text[:300]}")
    sha = r.json()["commit"]["sha"]
    # 커밋 고정 주소 → 캐시 문제 없이 영구적으로 같은 파일
    return f"https://cdn.jsdelivr.net/gh/{owner}/{repo}@{sha}/{repo_path}"


def is_reachable(url: str, tries: int = 3, wait: int = 10) -> bool:
    """주소가 실제로 열리는지 확인 (jsDelivr가 일시 장애일 때 깨진 이미지로 발행되는 것 방지)."""
    for i in range(tries):
        try:
            if requests.head(url, timeout=20, allow_redirects=True).status_code == 200:
                return True
        except requests.RequestException:
            pass
        if i < tries - 1:
            time.sleep(wait)
    return False


def raw_url(cdn_url: str) -> str:
    """jsDelivr 주소 → 같은 파일의 GitHub 원본 주소."""
    rest = cdn_url.split("/gh/", 1)[1]            # owner/repo@sha/path
    owner_repo, path = rest.split("/", 2)[:2], rest.split("/", 2)[2]
    owner, repo_sha = owner_repo
    repo, sha = repo_sha.split("@")
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{sha}/{path}"


def ensure_reachable(urls: dict, max_wait: int = 240) -> list:
    """jsDelivr 주소가 열릴 때까지 최대 max_wait초 기다리고, 끝내 안 열리면 GitHub 원본 주소로 바꿈.
    urls 를 직접 고치고, 그래도 안 되는 id 목록을 돌려줌."""
    pending = dict(urls)
    deadline = time.time() + max_wait
    while pending and time.time() < deadline:
        pending = {k: u for k, u in pending.items() if not is_reachable(u, tries=1)}
        if pending:
            time.sleep(20)
    failed = []
    for k, u in pending.items():
        r = raw_url(u)
        try:
            ok = requests.head(r, timeout=20)
            ctype = ok.headers.get("content-type", "")
            if ok.status_code == 200 and ctype.startswith(("image/", "video/")):
                urls[k] = r
                print(f"   jsDelivr 지연 → GitHub 원본 주소 사용: {k}")
                continue
        except requests.RequestException:
            pass
        failed.append(k)
    return failed
