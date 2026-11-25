"""Blogger API v3: 인증, 최근 글 조회, 글 등록. (같은 로그인으로 Search Console 도 사용)"""
import json
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/blogger",
          "https://www.googleapis.com/auth/webmasters"]  # 사이트맵 제출·색인 상태 조회


def get_creds(client_secret="client_secret.json", token_path="token.json", interactive=False):
    creds = None
    if Path(token_path).exists():
        granted = json.loads(Path(token_path).read_text()).get("scopes") or []
        if set(SCOPES) <= set(granted):  # 권한이 추가됐으면 다시 로그인해야 함
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        if not interactive:
            raise RuntimeError("구글 로그인이 필요합니다(만료 또는 권한 추가): python -m autopost.auth 를 실행하세요.")
        flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
        creds = flow.run_local_server(port=0)
    Path(token_path).write_text(creds.to_json())
    return creds


def get_service(**kw):
    return build("blogger", "v3", credentials=get_creds(**kw), cache_discovery=False)


def get_blog_id(svc, blog_url: str) -> str:
    return svc.blogs().getByUrl(url=blog_url).execute()["id"]


def recent_posts(svc, blog_id: str, n: int = 20) -> list:
    res = svc.posts().list(blogId=blog_id, maxResults=n, fetchBodies=False, status="LIVE").execute()
    return [{"title": i["title"], "url": i["url"]} for i in res.get("items", [])]


def create_post(svc, blog_id, title, html, labels, draft=True) -> dict:
    body = {"title": title, "content": html, "labels": labels}
    return svc.posts().insert(blogId=blog_id, body=body, isDraft=draft).execute()
